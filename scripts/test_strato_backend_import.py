import unittest
from unittest.mock import patch
from strato_backend_import import APP, START, HEALTH, CAPABLE, SETTINGS_CAPABLE, VIS_START, VIS_END, import_block, patch_application, cache_refresher
from strato_sftp_check import CheckError
from test_strato_stage import MemorySFTP, ROOT


class BackendImportTests(unittest.TestCase):
    def setUp(self):
        self.tested = APP.read_text(encoding='utf-8')
        self.old = self.tested.replace(import_block(self.tested), '').replace(SETTINGS_CAPABLE, HEALTH)
        begin = self.old.index(VIS_START)
        end = self.old.index(VIS_END, begin)
        self.old = self.old[:begin] + self.old[end:]
        self.old = self.old.replace(",'navigationVisibility','seoIndexing'", '')
        self.old = self.old.replace(",'seoIndexing'] as $key", "] as $key")

    def test_only_import_route_and_health_capability_are_added(self):
        patched = patch_application(self.old, self.tested)
        self.assertEqual(patched, self.tested)
        self.assertEqual(patch_application(patched, self.tested), patched)

    def test_settings_are_added_without_replacing_unrelated_backend_code(self):
        installed = self.old.replace("function nic_clean_settings", "// retained server comment\nfunction nic_clean_settings", 1)
        patched = patch_application(installed, self.tested)
        self.assertIn("// retained server comment", patched)
        self.assertIn("settingsVisibilityVersion", patched)
        self.assertEqual(patch_application(patched, self.tested), patched)

    def test_unknown_menu_validation_refuses_write(self):
        unsafe = self.tested.replace("    $allowedMenuKeys = ['budget','own','rent','flip','finance','settlement'];",
                                      "    $allowedMenuKeys = ['budget'];")
        with self.assertRaises(CheckError):
            patch_application(unsafe, self.tested)

    def test_drifted_security_or_existing_route_is_never_replaced(self):
        for source in [self.old.replace("$u['role'] !== 'admin'", "$u['role'] !== 'user'"),
                       self.tested.replace('count($rows)>2000', 'count($rows)>5000')]:
            with self.subTest(source=source[:30]), self.assertRaises(CheckError):
                patch_application(source, self.tested)

    def test_cache_refresh_is_secret_protected_narrow_and_removed_after_use(self):
        sftp = MemorySFTP()
        sftp.chmod = lambda *args: None
        def request(host, ip, path, method, preview_token=None):
            return (403, {}, b'{}', {}) if preview_token is None else (200, {}, b'{"ok":true,"invalidated":true}', {})
        with patch('strato_backend_import.secrets.token_hex', side_effect=['a'*64, 'b'*16]), patch('strato_backend_import.origin_request', side_effect=request):
            with cache_refresher(sftp, ROOT, '123-1', ['1.1.1.1']) as refresh:
                files = [name for name in sftp.files if 'nic-import-refresh-' in name]
                self.assertEqual(len(files), 1)
                code = sftp.files[files[0]].decode()
                self.assertNotIn('a'*64, code)
                self.assertIn('hash_equals', code)
                self.assertIn('time() >', code)
                self.assertIn("'/immocheck-private/app.php'", code)
                self.assertNotIn('opcache_reset', code)
                refresh()
            self.assertNotIn(files[0], sftp.files)


if __name__ == '__main__':
    unittest.main()
