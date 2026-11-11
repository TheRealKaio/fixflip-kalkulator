"""Exercise interrupted transfers and strict write scope without a real server."""
import errno
import io
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from strato_sftp_check import CheckError, fingerprint
from test_strato_sftp_check import Key
from strato_stage import (GUARD, REQUIRED, collect_files, stage, stage_session,
                          validate_release)


ROOT = '/immocheck-web'
RELEASE = 'a' * 40 + '-123-1'
STORE = ROOT + '/.nic-releases'
TARGET = STORE + '/' + RELEASE


class MemoryFile(io.BytesIO):
    def __init__(self, sftp, path, mode):
        self.sftp, self.path, self.writing = sftp, path, 'w' in mode
        if self.writing and path in sftp.files:
            raise FileExistsError(path)
        if not self.writing and path not in sftp.files:
            raise FileNotFoundError(errno.ENOENT, 'missing')
        super().__init__(b'' if self.writing else sftp.files[path])

    def close(self):
        if self.writing and not self.closed:
            value = self.getvalue()
            if self.sftp.corrupt and self.path.endswith('/index.html'):
                value += b'corrupt'
            self.sftp.files[self.path] = value
            self.sftp.writes.append(self.path)
        super().close()


class MemorySFTP:
    def __init__(self):
        self.directories = {ROOT, ROOT + '/api'}
        self.files = {ROOT + '/.htaccess': b'original live redirects',
                      ROOT + '/api/index.php': b'private API placeholder',
                      ROOT + '/config.php': b'do not touch'}
        self.links, self.writes, self.removals = set(), [], []
        self.renames = []
        self.atomic_supported, self.corrupt, self.closed = True, False, False

    def lstat(self, path):
        if path in self.links:
            return SimpleNamespace(st_mode=stat.S_IFLNK, st_size=0)
        if path in self.directories:
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_size=0)
        if path in self.files:
            return SimpleNamespace(st_mode=stat.S_IFREG, st_size=len(self.files[path]))
        raise FileNotFoundError(errno.ENOENT, 'missing')

    def mkdir(self, path, mode):
        if path in self.directories or path in self.files:
            raise FileExistsError(path)
        self.directories.add(path)
        self.writes.append(path)

    def open(self, path, mode):
        return MemoryFile(self, path, mode)

    def posix_rename(self, source, destination):
        if not self.atomic_supported:
            raise OSError('not supported')
        self.renames.append((source, destination))
        self.files[destination] = self.files.pop(source)

    def remove(self, path):
        self.removals.append(path)
        del self.files[path]

    def get_channel(self):
        return Mock()

    def close(self):
        self.closed = True


class StagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        for name in REQUIRED:
            path = self.site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('<html>test</html>')
        (self.site / 'backend-config.json').write_text(json.dumps({
            'enabled': True, 'apiUrl': 'https://neustart-immocheck.de/api/index.php'}))

    def test_complete_transfer_never_changes_live_files(self):
        sftp = MemorySFTP()
        original = dict(sftp.files)
        report = stage(sftp, ROOT, RELEASE, collect_files(self.site))
        self.assertIn('NICHT aktiviert', '\n'.join(report))
        for path, value in original.items():
            self.assertEqual(sftp.files[path], value)
        self.assertTrue(all(path == STORE or path.startswith(STORE + '/') for path in sftp.writes))
        self.assertEqual(sftp.renames, [(TARGET + '/.rename-source', TARGET + '/.rename-target')])
        self.assertEqual(sftp.removals, [TARGET + '/.rename-target'])
        marker = json.loads(sftp.files[TARGET + '/.ready.json'])
        self.assertEqual(set(marker['files']), REQUIRED)
        self.assertEqual(marker['commit'], 'a' * 40)
        self.assertEqual(sftp.files[STORE + '/.htaccess'], GUARD)

    def test_corrupt_transfer_never_marks_release_ready(self):
        sftp = MemorySFTP()
        sftp.corrupt = True
        with self.assertRaises(CheckError):
            stage(sftp, ROOT, RELEASE, collect_files(self.site))
        self.assertNotIn(TARGET + '/.ready.json', sftp.files)
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], b'original live redirects')

    def test_no_unsafe_fallback_if_atomic_replace_not_supported(self):
        sftp = MemorySFTP()
        sftp.atomic_supported = False
        with self.assertRaises(CheckError):
            stage(sftp, ROOT, RELEASE, collect_files(self.site))
        self.assertEqual(sftp.removals, [])
        self.assertNotIn(TARGET + '/.ready.json', sftp.files)
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], b'original live redirects')

    def test_existing_store_guard_or_release_not_overwritten(self):
        for variant in ['guard', 'release', 'symlink']:
            with self.subTest(variant=variant):
                sftp = MemorySFTP()
                sftp.directories.add(STORE)
                if variant == 'guard':
                    sftp.files[STORE + '/.htaccess'] = b'unknown custom rules'
                else:
                    sftp.files[STORE + '/.htaccess'] = GUARD
                if variant == 'release':
                    sftp.directories.add(TARGET)
                if variant == 'symlink':
                    sftp.links.add(STORE)
                with self.assertRaises(CheckError):
                    stage(sftp, ROOT, RELEASE, collect_files(self.site))
                self.assertEqual(sftp.writes, [])

    def test_untrusted_key_never_authenticates_or_opens_sftp(self):
        for pin in ['', 'SHA256:' + 'A' * 43]:
            transport = Mock(get_remote_server_key=Mock(return_value=Key()))
            factory = Mock()
            with self.assertRaises(CheckError):
                stage_session(transport, pin, 'user', 'password', ROOT, RELEASE,
                              collect_files(self.site), factory)
            transport.auth_password.assert_not_called()
            factory.assert_not_called()

    def test_verified_key_authenticates_and_closes(self):
        transport = Mock(get_remote_server_key=Mock(return_value=Key()))
        sftp = MemorySFTP()
        stage_session(transport, fingerprint(Key()), 'user', 'password', ROOT, RELEASE,
                      collect_files(self.site), lambda _: sftp)
        transport.auth_password.assert_called_once_with('user', 'password', fallback=False)
        self.assertTrue(sftp.closed)

    def test_reject_server_files_links_incomplete_build_or_changed_api(self):
        for name in ['install.php', 'api/index.php', 'config.json', '.htaccess', 'backup.sql']:
            with self.subTest(name=name):
                path = self.site / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('do not deploy')
                with self.assertRaises(CheckError):
                    collect_files(self.site)
                path.unlink()
                if name.startswith('api/'):
                    path.parent.rmdir()
        (self.site / 'index.html').unlink()
        with self.assertRaises(CheckError):
            collect_files(self.site)
        (self.site / 'index.html').symlink_to(self.site / 'budget/index.html')
        with self.assertRaises(CheckError):
            collect_files(self.site)
        (self.site / 'index.html').unlink()
        (self.site / 'index.html').write_text('restored')
        (self.site / 'backend-config.json').write_text('{"enabled": false}')
        with self.assertRaises(CheckError):
            collect_files(self.site)

    def test_test_pages_and_pages_metadata_are_not_uploaded(self):
        (self.site / '_checks').mkdir()
        (self.site / '_checks/test.html').write_text('test harness')
        (self.site / 'CNAME').write_text('www.neustart-immocheck.de')
        (self.site / '.nojekyll').touch()
        self.assertEqual(set(collect_files(self.site)), REQUIRED)

    def test_release_id_and_file_paths_cannot_escape(self):
        for release in ['../api', '/immocheck-private', 'a' * 40, RELEASE + '/../../api']:
            with self.assertRaises(CheckError):
                validate_release(release)
        for name in ['../index.html', '/api/index.html', 'api/index.html', 'x/../index.html']:
            sftp = MemorySFTP()
            with self.assertRaises(CheckError):
                stage(sftp, ROOT, RELEASE, {name: self.site / 'index.html'})
            self.assertEqual(sftp.writes, [])


if __name__ == '__main__':
    unittest.main()
