import unittest
from strato_backend_import import APP, START, HEALTH, CAPABLE, import_block, patch_application
from strato_sftp_check import CheckError


class BackendImportTests(unittest.TestCase):
    def setUp(self):
        self.tested = APP.read_text(encoding='utf-8')
        self.old = self.tested.replace(import_block(self.tested), '').replace(CAPABLE, HEALTH)

    def test_only_import_route_and_health_capability_are_added(self):
        patched = patch_application(self.old, self.tested)
        self.assertEqual(patched, self.tested.replace(HEALTH, CAPABLE))
        self.assertEqual(patch_application(patched, self.tested), patched)

    def test_drifted_security_or_existing_route_is_never_replaced(self):
        for source in [self.old.replace("$u['role'] !== 'admin'", "$u['role'] !== 'user'"),
                       self.tested.replace('count($rows)>2000', 'count($rows)>5000')]:
            with self.subTest(source=source[:30]), self.assertRaises(CheckError):
                patch_application(source, self.tested)


if __name__ == '__main__':
    unittest.main()
