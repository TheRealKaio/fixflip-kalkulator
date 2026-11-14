"""Exercise real PHP router + DOM filtering with a fixed settings provider, no production DB."""
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from strato_release_publish import router_bytes, router_name


def main():
    release = 'a' * 40 + '-123-1'
    secret = 'b' * 64
    with tempfile.TemporaryDirectory(prefix='nic-php-') as temporary:
        parent = Path(temporary)
        root = parent / 'public'
        stored = root / '.nic-releases' / release
        stored.mkdir(parents=True)
        private = parent / 'immocheck-private'
        private.mkdir()
        (private / 'config.php').write_text("<?php return ['db'=>['host'=>'fixture','name'=>'fixture','user'=>'fixture','password'=>'fixture']];")
        # Only database transport is replaced; path selection, parser, removal,
        # output headers and router integrity checks use the production code.
        gate = Path('server/webspace/immocheck-web/content-gate.php').read_text()
        gate = gate.replace('new PDO(', 'new NICFixturePDO(')
        provider = '''
class NICFixturePDO {
    public function __construct(...$args) {}
    public function query($sql) { return $this; }
    public function fetchColumn() { return '{"contentSections":{"fixture.disabled":{"visible":false}}}'; }
}
'''
        gate = gate.replace("ini_set('display_errors', '0');", provider + "\nini_set('display_errors', '0');")
        script = "window.nicFixture={dash:'–',state:'Hamburg · 5,5 %',status:'🟡 Noch verhandeln oder prüfen',literal:'&uuml;',comparison:'a < b && c > d'};"
        style = '.fixture::after { content: "ü · – 🟡"; }'
        html = ('<!doctype html><html><head><meta charset="utf-8">'
                '<style data-note=">">' + style + '</style>'
                '<script data-note=">">' + script + '</script></head><body>'
                '<section data-nic-content-key="fixture.disabled">SECRET_DISABLED'
                '<script>window.removed="SECRET_DISABLED_SCRIPT";</script></section>'
                '<script data-nic-content-key="fixture.disabled">window.removed="SECRET_DISABLED_DIRECT";</script>'
                '<p>Visible content: prüfen · 5,5 %</p></body></html>').encode()
        files = {'index.html': html, 'sample.js': b'window.fixture = true;', 'content-gate.php': gate.encode()}
        manifest = {'release': release, 'files': {name: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)} for name, data in files.items()}}
        for name, data in files.items():
            (stored / name).write_bytes(data)
        (stored / '.ready.json').write_text(json.dumps(manifest))
        (root / router_name(release)).write_bytes(router_bytes(release, secret))
        (root / '.htaccess').write_text('# previous active release\n')
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        process = subprocess.Popen(['php', '-S', '127.0.0.1:' + str(port), '-t', str(root)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def request(path, token=None):
            req = Request('http://127.0.0.1:' + str(port) + '/' + router_name(release) + '?path=' + path,
                          headers={} if token is None else {'X-NIC-Preview-Token': token})
            try:
                response = urlopen(req, timeout=5)
            except HTTPError as response_error:
                response = response_error
            return response.status, dict((k.lower(), v) for k, v in response.headers.items()), response.read()
        try:
            deadline = time.monotonic() + 10
            while True:
                try:
                    request('index.html')
                    break
                except OSError:
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('PHP fixture did not start')
                    time.sleep(.1)
            assert request('index.html')[0] == 404
            assert request('index.html', 'c' * 64)[0] == 404
            status, headers, body = request('index.html', secret)
            assert status == 200, (status, body)
            assert b'SECRET_DISABLED' not in body and b'Visible content' in body
            assert script.encode() in body, 'JavaScript raw text was changed by HTML serialization'
            assert style.encode() in body, 'CSS raw text was changed by HTML serialization'
            assert b'NIC_RAW_' not in body, 'Unrestored raw-text placeholder'
            assert headers['x-nic-source-sha256'] == hashlib.sha256(html).hexdigest()
            assert headers['x-nic-filtered'] == '1'
            assert body != html  # Filtering must not fail the source verification.
            assert headers['x-robots-tag'] == 'noindex, nofollow'
            for path in ['content-gate.php', '../index.html', 'missing.html', 'api/index.php', 'index.html%00']:
                assert request(path, secret)[0] == 404, path
            (root / '.htaccess').write_text('# NIC-RELEASE: ' + release + '\n')
            assert request('index.html')[0] == 200
            status, headers, body = request('sample.js')
            assert status == 200 and body == files['sample.js']
            assert headers['content-type'].startswith('text/javascript')
            (stored / 'sample.js').write_text('tampered')
            assert request('sample.js')[0] == 503
            print('PHP release router passed: protected preview, disabled content/scripts absent, Unicode and intentional entities preserved in JS/CSS, source identity, asset MIME, traversal/source blocking and tamper rejection.')
        finally:
            process.terminate()
            process.wait(timeout=5)


if __name__ == '__main__':
    main()
