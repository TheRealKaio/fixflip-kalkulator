"""Exercise the exact production .htaccess in an isolated local Apache + TLS."""
import hashlib
import http.client
import os
from pathlib import Path
import pwd
import grp
import socket
import ssl
import subprocess
import tempfile
import time
from urllib.parse import urlsplit

from strato_activate import APEX, WWW, render_rules
from strato_stage import ACTIVE_GUARD, REQUIRED, STORE


def free_port():
    with socket.socket() as stream:
        stream.bind(('127.0.0.1', 0))
        return stream.getsockname()[1]


def main(internal_mapping=False):
    with tempfile.TemporaryDirectory(prefix='nic-apache-') as directory:
        temp = Path(directory)
        root = temp / 'www'
        root.mkdir()
        release = 'a' * 40 + '-123-1'
        store = root / STORE
        target = store / release
        target.mkdir(parents=True)
        (store / '.htaccess').write_bytes(ACTIVE_GUARD)
        manifest = {'release': release, 'files': {}}
        for name in REQUIRED | {'sample.js'}:
            payload = ('test release ' + name).encode()
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            manifest['files'][name] = {'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload)}
        (target / '.ready.json').write_text('not public')
        (root / '.htaccess').write_bytes(render_rules(manifest, '123-1'))
        (root / 'api').mkdir()
        (root / 'api/index.php').write_text('existing API')
        (root / '.well-known').mkdir()
        (root / '.well-known/test.txt').write_text('certificate challenge')
        key, cert = temp / 'key.pem', temp / 'cert.pem'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1',
                        '-subj','/CN='+WWW,'-addext','subjectAltName=DNS:'+WWW+',DNS:'+APEX+',IP:127.0.0.1',
                        '-keyout',str(key),'-out',str(cert)], check=True, capture_output=True)
        port, http_port = free_port(), free_port()
        user, group = pwd.getpwuid(os.getuid()).pw_name, grp.getgrgid(os.getgid()).gr_name
        config = temp / 'apache.conf'
        modules = '\n'.join('LoadModule '+name+'_module /usr/lib/apache2/modules/mod_'+name+'.so'
                            for name in ['mpm_event','authz_core','authz_host','rewrite','dir','mime','ssl','headers','alias'])
        default_root = temp / 'default-root'
        default_root.mkdir()
        mapping = 'Alias / "' + str(root) + '/"' if internal_mapping else ''
        document_root = default_root if internal_mapping else root
        config.write_text(f'''ServerRoot "/etc/apache2"
ServerName {WWW}
PidFile "{temp}/apache.pid"
DefaultRuntimeDir "{temp}"
Mutex file:{temp} default
User {user}
Group {group}
Listen 127.0.0.1:{port}
Listen 127.0.0.1:{http_port}
{modules}
ErrorLog "{temp}/error.log"
LogLevel warn
TypesConfig /etc/mime.types
<Directory "{root}">
  AllowOverride All
  Options FollowSymLinks
  Require all granted
</Directory>
<VirtualHost 127.0.0.1:{port}>
  DocumentRoot "{document_root}"
  {mapping}
  SSLEngine on
  SSLCertificateFile "{cert}"
  SSLCertificateKeyFile "{key}"
</VirtualHost>
<VirtualHost 127.0.0.1:{http_port}>
  DocumentRoot "{document_root}"
  {mapping}
</VirtualHost>
''')
        process = subprocess.Popen(['/usr/sbin/apache2','-f',str(config),'-DFOREGROUND'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        context = ssl.create_default_context(cafile=str(cert))
        def request(path, host=WWW, preview=None):
            connection = http.client.HTTPSConnection('127.0.0.1', port, context=context, timeout=5)
            try:
                headers = {'Host':host}
                if preview is not None:
                    headers['X-NIC-Origin-Release'] = preview
                connection.request('GET', path, headers=headers)
                response = connection.getresponse()
                return response.status, dict(response.getheaders()), response.read()
            finally:
                connection.close()
        try:
            deadline = time.monotonic() + 10
            while True:
                try:
                    request('/')
                    break
                except OSError:
                    if process.poll() is not None or time.monotonic() > deadline:
                        raise RuntimeError('Apache did not start: '+(temp/'error.log').read_text())
                    time.sleep(.1)
            assert request('/')[2] == b'test release index.html'
            for name in REQUIRED:
                path = '/' + name[:-len('index.html')] if name.endswith('/index.html') else '/' + name
                status, _, body = request(path)
                assert status == 200 and body == ('test release '+name).encode(), (path,status)
            status, headers, _ = request('/budget?test=1')
            assert status == 302 and urlsplit(headers['Location']).path == '/budget/'
            assert urlsplit(headers['Location']).query == 'test=1'
            status, headers, _ = request('/budget/?test=1', APEX)
            assert status == 302 and headers['Location'] == 'https://'+WWW+'/budget/?test=1'
            assert request('/api/index.php?r=health', APEX)[2] == b'existing API'
            assert request('/.well-known/test.txt')[2] == b'certificate challenge'
            for path in ['/'+STORE+'/'+release+'/index.html','/%2enic-releases/'+release+'/.ready.json','/.htaccess','/budget/.secret']:
                assert request(path)[0] == 403, path
            assert request('/no-such-page/')[0] == 404
            assert request('/sample.js')[2] == b'test release sample.js'
            # The initial release can be checked on the apex while www remains
            # on GitHub. Ordinary requests must still canonicalize to www.
            status, headers, body = request('/', APEX, release)
            assert status == 200 and body == b'test release index.html'
            assert headers.get('Cache-Control') == 'no-store'
            assert headers.get('X-Robots-Tag') == 'noindex, nofollow'
            assert 'X-NIC-Origin-Release' in headers.get('Vary','')
            assert request('/', APEX)[0] == 302
            assert request('/', APEX, 'wrong-release')[0] == 302
            assert request('/budget/', APEX, release)[2] == b'test release budget/index.html'
            assert request('/no-such-page/', APEX, release)[0] == 404
            assert request('/'+STORE+'/'+release+'/.ready.json', APEX, release)[0] == 403
            assert request('/api/index.php?r=health', APEX, release)[2] == b'existing API'
            connection = http.client.HTTPConnection('127.0.0.1', http_port, timeout=5)
            connection.request('GET','/budget/?test=1',headers={'Host':WWW})
            response = connection.getresponse()
            assert response.status == 302 and response.getheader('Location') == 'https://'+WWW+'/budget/?test=1'
            connection.close()
            print('Apache release rules passed (' + ('internal domain mapping' if internal_mapping else 'direct document root') + '): TLS routes, public redirects, API exclusion, query preservation, HTTPS, hidden storage and 404.')
        finally:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    main()
    main(internal_mapping=True)
