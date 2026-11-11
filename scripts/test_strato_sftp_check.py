"""Check credential handling and read-only scope without a real network connection."""
import stat
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from strato_sftp_check import CheckError, fingerprint, inspect_session, inspect_target, validate_host, validate_root


class Key:
    def asbytes(self):
        return b'example-public-key'

    def get_name(self):
        return 'ssh-ed25519'


class ReadOnlySFTP:
    def __init__(self, symlink=None):
        self.paths = []
        self.closed = False
        self.symlink = symlink
        self.channel = Mock()

    def lstat(self, path):
        self.paths.append(path)
        mode = stat.S_IFREG if path.endswith('index.php') else stat.S_IFDIR
        return SimpleNamespace(st_mode=stat.S_IFLNK if path == self.symlink else mode)

    def get_channel(self):
        return self.channel

    def close(self):
        self.closed = True


class PreflightTests(unittest.TestCase):
    def transport(self):
        return Mock(get_remote_server_key=Mock(return_value=Key()))

    def test_fingerprint_never_authenticates(self):
        transport, factory = self.transport(), Mock()
        report = inspect_session(transport, 'fingerprint', '', '', '', '/immocheck-web', factory)
        self.assertTrue(any(fingerprint(Key()) in line for line in report))
        transport.auth_password.assert_not_called()
        factory.assert_not_called()

    def test_untrusted_key_never_receives_credentials(self):
        for pin in ['', 'SHA256:' + 'A' * 43]:
            transport, factory = self.transport(), Mock()
            with self.assertRaises(CheckError):
                inspect_session(transport, 'check', pin, 'example-user', 'example-password', '/immocheck-web', factory)
            transport.auth_password.assert_not_called()
            factory.assert_not_called()

    def test_verified_connection_reads_only_known_metadata(self):
        transport, sftp = self.transport(), ReadOnlySFTP()
        report = inspect_session(transport, 'check', fingerprint(Key()), 'example-user', 'example-password', '/immocheck-web', lambda _: sftp)
        transport.auth_password.assert_called_once_with('example-user', 'example-password', fallback=False)
        self.assertEqual(sftp.paths, ['/immocheck-web', '/immocheck-web/api', '/immocheck-web/api/index.php'])
        self.assertTrue(sftp.closed)
        self.assertNotIn('example-password', '\n'.join(report))

    def test_symlink_is_not_followed(self):
        for path in ['/immocheck-web', '/immocheck-web/api', '/immocheck-web/api/index.php']:
            with self.assertRaises(CheckError):
                inspect_target(ReadOnlySFTP(symlink=path), '/immocheck-web')

    def test_host_and_root_are_constrained(self):
        self.assertEqual(validate_host('123.ssh.w1.strato.hosting'), '123.ssh.w1.strato.hosting')
        self.assertEqual(validate_root('/immocheck-web'), '/immocheck-web')
        for host in ['https://123.ssh.w1.strato.hosting', 'other.example.com', '123.ssh.w1.strato.hosting/']:
            with self.assertRaises(CheckError):
                validate_host(host)
        for root in ['/', '/immocheck-private', '/a/../immocheck-web', 'immocheck-web']:
            with self.assertRaises(CheckError):
                validate_root(root)


if __name__ == '__main__':
    unittest.main()
