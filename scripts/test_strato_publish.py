"""Production publication preserves working pages, cached assets and private data."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import test_strato_stage as fixtures
from test_strato_stage import MemorySFTP, ROOT, RELEASE, STORE
from strato_stage import collect_files, stage
from strato_activate import switch, verify_known_rules, direct_version, stored_assets
from strato_publish import deploy, connection
from strato_sftp_check import CheckError
from test_strato_sftp_check import Key

NEW = 'b' * 40 + '-456-1'
ASSET = 'app.0123456789abcdef.js'


class PublishTests(unittest.TestCase):
    def setUp(self):
        fixtures.StagingTests.setUp(self)
        self.sftp = MemorySFTP()
        self.sftp.files[ROOT + '/.htaccess'] = Path('server/webspace/immocheck-web/.htaccess').read_bytes()
        stage(self.sftp, ROOT, RELEASE, collect_files(self.site))
        switch(self.sftp, ROOT, 'prepare', RELEASE, '321-1', [], http_verify=Mock())
        self.original = dict(self.sftp.files)

    def publish(self, verify=None, token='456-1', release=NEW, **kwargs):
        return deploy(self.sftp, ROOT, collect_files(self.site), release, token, [],
                      http_verify=verify or Mock(), **kwargs)

    def change(self):
        (self.site / ASSET).write_text('new javascript')
        (self.site / 'index.html').write_text('<html><script src="/' + ASSET + '"></script>new</html>')

    def assert_private_unchanged(self):
        for name in ['api/index.php', 'config.php']:
            self.assertEqual(self.sftp.files[ROOT + '/' + name], self.original[ROOT + '/' + name])

    def test_identical_build_upgrades_rules_without_uploading_frontend(self):
        stage_mock = Mock()
        report = self.publish(stage_release=stage_mock)
        stage_mock.assert_not_called()
        self.assertIn('bytegleich', '\n'.join(report))
        self.assertEqual(direct_version(self.sftp.files[ROOT + '/.htaccess']), 2)
        self.assertEqual(verify_known_rules(self.sftp, ROOT, self.sftp.files[ROOT + '/.htaccess'])['release'], RELEASE)
        for name in collect_files(self.site):
            self.assertEqual(self.sftp.files[ROOT + '/' + name], self.original[ROOT + '/' + name])
        self.assert_private_unchanged()

    def test_asset_installed_and_allowed_before_html_changes(self):
        self.change()
        rename = self.sftp.posix_rename
        seen = []
        def observe(source, destination):
            if destination == ROOT + '/index.html':
                self.assertEqual(self.sftp.files[ROOT + '/' + ASSET], b'new javascript')
                self.assertIn(b'\\.[a-f0-9]{16}', self.sftp.files[ROOT + '/.htaccess'])
                self.assertIn(RELEASE.encode(), self.sftp.files[ROOT + '/.htaccess'])
                seen.append(destination)
            rename(source, destination)
        self.sftp.posix_rename = observe
        self.publish()
        self.assertEqual(len(seen), 1)
        manifest = verify_known_rules(self.sftp, ROOT, self.sftp.files[ROOT + '/.htaccess'])
        self.assertEqual(manifest['release'], NEW)
        self.assertEqual(self.sftp.files[ROOT + '/index.html'], (self.site / 'index.html').read_bytes())
        self.assert_private_unchanged()

    def test_failed_http_restores_pages_but_keeps_cached_assets(self):
        self.change()
        def verify(ips, manifest):
            if manifest['release'] == NEW:
                raise CheckError('new HTTP failure')
        with self.assertRaisesRegex(CheckError, 'Vorheriges Frontend wiederhergestellt'):
            self.publish(verify=verify)
        self.assertEqual(self.sftp.files[ROOT + '/index.html'], self.original[ROOT + '/index.html'])
        self.assertIn(ROOT + '/' + ASSET, self.sftp.files)
        self.assertEqual(verify_known_rules(self.sftp, ROOT, self.sftp.files[ROOT + '/.htaccess'])['release'], RELEASE)
        self.assert_private_unchanged()

    def test_interrupted_html_copy_restores_previous_pages(self):
        self.change()
        rename = self.sftp.posix_rename
        interrupted = False
        def fail_once(source, destination):
            nonlocal interrupted
            if destination == ROOT + '/index.html' and not interrupted:
                interrupted = True
                raise OSError('interrupted connection')
            rename(source, destination)
        self.sftp.posix_rename = fail_once
        with self.assertRaisesRegex(CheckError, 'Vorheriges Frontend wiederhergestellt'):
            self.publish()
        self.assertTrue(interrupted)
        self.assertEqual(self.sftp.files[ROOT + '/index.html'], self.original[ROOT + '/index.html'])
        self.assert_private_unchanged()

    def test_external_edit_is_never_overwritten_during_recovery(self):
        self.change()
        def verify(ips, manifest):
            if manifest['release'] == NEW:
                self.sftp.files[ROOT + '/index.html'] = b'external edit'
                raise CheckError('bad HTTP')
        with self.assertRaisesRegex(CheckError, 'Ruecknahme fehlgeschlagen'):
            self.publish(verify=verify)
        self.assertEqual(self.sftp.files[ROOT + '/index.html'], b'external edit')
        self.assert_private_unchanged()

    def test_manual_rollback_on_strato_needs_no_dns_change(self):
        self.change()
        self.publish()
        switch(self.sftp, ROOT, 'rollback', NEW, '457-1', [])
        self.assertEqual(self.sftp.files[ROOT + '/index.html'], self.original[ROOT + '/index.html'])
        self.assertIn(ROOT + '/' + ASSET, self.sftp.files)
        self.assertEqual(verify_known_rules(self.sftp, ROOT, self.sftp.files[ROOT + '/.htaccess'])['release'], RELEASE)
        self.assert_private_unchanged()

    def test_failed_rules_upgrade_leaves_original_rules(self):
        with self.assertRaisesRegex(CheckError, 'vorherige Root-Regeln wiederhergestellt'):
            self.publish(verify=Mock(side_effect=CheckError('bad rules')))
        self.assertEqual(self.sftp.files[ROOT + '/.htaccess'], self.original[ROOT + '/.htaccess'])

    def test_stored_assets_reject_html_private_paths_and_duplicates(self):
        for names in ['index.html', 'api/index.php', 'a.png\n# NIC-RETAIN-ASSET: a.png']:
            with self.subTest(names=names), self.assertRaises(CheckError):
                stored_assets(('# NIC-RETAIN-ASSET: ' + names + '\n').encode())

    def test_untrusted_host_never_receives_password(self):
        transport = Mock(get_remote_server_key=Mock(return_value=Key()))
        paramiko = Mock(Transport=Mock(return_value=transport))
        env = {'STRATO_SFTP_HOST': '512220664.ssh.w1.strato.hosting',
               'STRATO_SFTP_FINGERPRINT': 'SHA256:' + 'A' * 43,
               'STRATO_SFTP_USER': 'user', 'STRATO_SFTP_PASSWORD': 'password'}
        with patch.dict('os.environ', env), patch.dict(sys.modules, {'paramiko': paramiko}), \
             patch('strato_publish.socket.create_connection', return_value=Mock(__enter__=Mock(), __exit__=Mock(return_value=False))), \
             self.assertRaises(CheckError):
            with connection():
                self.fail('untrusted connection opened')
        transport.auth_password.assert_not_called()
        paramiko.SFTPClient.from_transport.assert_not_called()


if __name__ == '__main__':
    unittest.main()
