"""Atomic publication: interrupted preview/switch never replaces live page files."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import Mock
from urllib.parse import parse_qs, urlsplit

import test_strato_publish as fixtures
from test_strato_publish import NEW
from test_strato_stage import ROOT, RELEASE, STORE
from strato_stage import collect_files
from strato_activate import managed_header
from strato_release_publish import publish, check_source, known_release, release_rules, release_assets, check_raw_text
from strato_sftp_check import CheckError


class AtomicTests(unittest.TestCase):
    setUp = fixtures.PublishTests.setUp
    change = fixtures.PublishTests.change
    assert_private_unchanged = fixtures.PublishTests.assert_private_unchanged
    def atomic(self, fail=None):
        def request(host, ip, path='/', method='HEAD', preview_token=None):
            cert = {'notAfter': '2027'}
            if path == '/api/index.php?r=health':
                return 200, {}, b'{"ok":true,"ready":true}', cert
            if path.startswith('/.nic-releases/'):
                return 403, {}, b'', cert
            if path == '/nic-unknown-page-test/':
                return 404, {}, b'', cert
            active = managed_header(self.sftp.files[ROOT + '/.htaccess'])[0]
            is_preview = path.startswith('/nic-release-')
            if is_preview and preview_token is None:
                return 404, {}, b'', cert
            selected = NEW if is_preview else active
            manifest = json.loads(self.sftp.files[STORE + '/' + selected + '/.ready.json'])
            if fail == 'preview' and is_preview:
                return 503, {}, b'', cert
            if fail == 'live' and active == NEW and not is_preview:
                return 503, {}, b'', cert
            if is_preview:
                name = parse_qs(urlsplit(path).query)['path'][0]
            else:
                name = 'index.html' if path == '/' else path.strip('/') + '/index.html' if path.endswith('/') else path.lstrip('/')
            data = self.sftp.files[STORE + '/' + selected + '/' + name]
            headers = {'x-nic-release': selected, 'x-nic-source-sha256': manifest['files'][name]['sha256'], 'x-nic-filtered': '1'}
            body = b'<html data-calculator="home">filtered output</html>' if name.endswith('.html') else data
            return 200, headers, body, cert
        return publish(self.sftp, ROOT, collect_files(self.site), NEW, '456-1', ['1.1.1.1'], request=request)

    def test_whole_release_switch_leaves_every_public_page_byte_unchanged(self):
        self.change()
        self.atomic()
        for name in collect_files(self.site):
            if ROOT + '/' + name in self.original:
                self.assertEqual(self.sftp.files[ROOT + '/' + name], self.original[ROOT + '/' + name])
        root_swaps = [destination for _, destination in self.sftp.renames if destination == ROOT + '/.htaccess']
        # Fixture preparation + additive preview rules + one active release switch.
        self.assertEqual(len(root_swaps), 3)
        self.assertEqual(known_release(self.sftp, ROOT, self.sftp.files[ROOT + '/.htaccess'])['release'], NEW)
        self.assert_private_unchanged()

    def test_failed_preview_and_failed_live_both_restore_original_rules(self):
        for phase in ['preview', 'live']:
            with self.subTest(phase=phase):
                self.setUp()
                self.change()
                with self.assertRaisesRegex(CheckError, 'per HTTP wieder bestaetigt'):
                    self.atomic(fail=phase)
                self.assertEqual(self.sftp.files[ROOT + '/.htaccess'], self.original[ROOT + '/.htaccess'])
                self.assertEqual(self.sftp.files[ROOT + '/index.html'], self.original[ROOT + '/index.html'])
                self.assert_private_unchanged()

    def test_filtered_html_uses_verified_source_and_successful_filter_marker(self):
        manifest = {'release': NEW, 'files': {'index.html': {'sha256': 'a' * 64}}}
        headers = {'x-nic-release': NEW, 'x-nic-source-sha256': 'a' * 64, 'x-nic-filtered': '1'}
        check_source(headers, b'<html>deliberately filtered output</html>', manifest, 'index.html')
        for key in headers:
            invalid = dict(headers, **{key: 'wrong'})
            with self.subTest(key=key), self.assertRaises(CheckError):
                check_source(invalid, b'<html>filtered</html>', manifest, 'index.html')

    def test_future_release_recognizes_retained_fingerprinted_assets(self):
        manifest = {'release': NEW, 'files': {}}
        name = 'app.0123456789abcdef.js'
        rules = release_rules(manifest, '456-1', 'a' * 64, [name])
        self.assertEqual(release_assets(rules), [name])
        for invalid in ['index.html', 'api/index.php', 'app.js']:
            with self.subTest(name=invalid), self.assertRaises(CheckError):
                release_assets(('# NIC-RETAIN-ASSET: ' + invalid + '\n').encode())

    def test_html_filter_must_preserve_raw_scripts_and_styles_exactly(self):
        visible = '<script>const text="🟡 prüfen · – &uuml;";</script><style>.x:after{content:"ü"}</style>'
        removed = '<script>const disabled="secret";</script>'
        check_raw_text(visible + removed, visible)
        for output in [visible.replace('ü', '&uuml;'), visible.replace('🟡', '&#128993;'),
                       visible.replace('–', '&ndash;'), visible.replace('&uuml;', 'ü')]:
            with self.subTest(output=output), self.assertRaises(CheckError):
                check_raw_text(visible, output)


if __name__ == '__main__':
    unittest.main()
