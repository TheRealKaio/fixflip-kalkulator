"""Activation failures must retain or restore the previous root rules."""
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import Mock, patch

from strato_sftp_check import CheckError
from strato_stage import ACTIVE_GUARD, collect_files, stage
from strato_activate import (APEX, WWW, atomic_replace, origin_ips, preflight,
                             render_rules, switch, verify_http)
from test_strato_stage import MemorySFTP, RELEASE, ROOT, STORE
import test_strato_stage as fixtures


class ActivationTests(unittest.TestCase):
    # Reuse only the existing realistic build fixture, not the staging test cases.
    def setUp(self):
        fixtures.StagingTests.setUp(self)

    def fixture(self):
        sftp = MemorySFTP()
        sftp.files[ROOT + '/.htaccess'] = Path('server/webspace/immocheck-web/.htaccess').read_bytes()
        stage(sftp, ROOT, RELEASE, collect_files(self.site))
        sftp.writes.clear()
        sftp.renames.clear()
        return sftp

    def test_check_performs_no_writes(self):
        sftp = self.fixture()
        before = dict(sftp.files)
        switch(sftp, ROOT, 'check', RELEASE, '321-1', [])
        self.assertEqual(sftp.writes, [])
        self.assertEqual(sftp.files, before)

    def test_activate_preserves_api_and_snapshots_original(self):
        sftp = self.fixture()
        before = dict(sftp.files)
        verify = Mock()
        switch(sftp, ROOT, 'activate', RELEASE, '321-1', [], http_verify=verify)
        self.assertEqual(sftp.files[STORE + '/.backups/321-1.htaccess'], before[ROOT + '/.htaccess'])
        self.assertEqual(sftp.files[STORE + '/.htaccess'], ACTIVE_GUARD)
        self.assertIn(RELEASE.encode(), sftp.files[ROOT + '/.htaccess'])
        self.assertEqual(sftp.files[ROOT + '/api/index.php'], before[ROOT + '/api/index.php'])
        self.assertEqual(sftp.files[ROOT + '/config.php'], before[ROOT + '/config.php'])
        verify.assert_called_once()
        allowed = {ROOT + '/.htaccess', ROOT + '/.htaccess.next-321-1',
                   STORE + '/.htaccess', STORE + '/.htaccess.next-321-1',
                   STORE + '/.backups', STORE + '/.backups/321-1.htaccess'}
        self.assertTrue(set(sftp.writes).issubset(allowed))

    def test_failed_http_restores_original_atomically(self):
        sftp = self.fixture()
        original = sftp.files[ROOT + '/.htaccess']
        with self.assertRaisesRegex(CheckError, 'automatisch atomar wiederhergestellt'):
            switch(sftp, ROOT, 'activate', RELEASE, '321-1', [], http_verify=Mock(side_effect=CheckError('broken HTTP')))
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], original)
        self.assertEqual(sftp.removals, [ROOT + '/.nic-releases/' + RELEASE + '/.rename-target'])

    def test_prepare_retains_original_backup_for_later_activation(self):
        sftp = self.fixture()
        original = sftp.files[ROOT + '/.htaccess']
        result = switch(sftp, ROOT, 'prepare', RELEASE, '321-1', [], http_verify=Mock())
        self.assertIn('vor der DNS-Umstellung', '\n'.join(result))
        self.assertEqual(sftp.files[STORE + '/.backups/321-1.htaccess'], original)
        prepared = sftp.files[ROOT + '/.htaccess']
        switch(sftp, ROOT, 'activate', RELEASE, '322-1', [], http_verify=Mock())
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], prepared)
        self.assertEqual(sftp.files[STORE + '/.backups/321-1.htaccess'], original)
        second = 'b' * 40 + '-124-1'
        stage(sftp, ROOT, second, collect_files(self.site))
        with self.assertRaisesRegex(CheckError, 'ersten Umzug'):
            switch(sftp, ROOT, 'prepare', second, '323-1', [], http_verify=Mock())
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], prepared)

    def test_failed_preparation_restores_original(self):
        sftp = self.fixture()
        original = sftp.files[ROOT + '/.htaccess']
        with self.assertRaisesRegex(CheckError, 'automatisch atomar wiederhergestellt'):
            switch(sftp, ROOT, 'prepare', RELEASE, '321-1', [], http_verify=Mock(side_effect=CheckError('probe failed')))
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], original)

    def test_preparation_http_checks_use_apex_but_activation_requires_www(self):
        sftp = self.fixture()
        manifest = json.loads(sftp.files[STORE + '/' + RELEASE + '/.ready.json'])
        index = (self.site / 'index.html').read_bytes()
        cert = {'notAfter':'2027'}
        calls = []
        def request(host, ip, path='/', method='HEAD', preview_release=None):
            calls.append((host, path, preview_release))
            if path == '/api/index.php?r=health':
                return (200, {}, b'{"ok":true,"ready":true}', cert) if host == APEX else (404, {}, b'not mapped', cert)
            if preview_release:
                self.assertEqual(host, APEX)
                self.assertEqual(preview_release, RELEASE)
                status = 403 if path.startswith('/.nic-releases/') else 404 if path == '/nic-unknown-page-test/' else 200
                return status, {}, index if path == '/' else b'', cert
            if host == APEX:
                return 302, {'location':'https://'+WWW+path}, b'', cert
            return 200, {}, b'different www webspace', cert
        verify_http(['1.1.1.1'], manifest, request, preparation=True)
        self.assertTrue(any(preview == RELEASE for _,_,preview in calls))
        with self.assertRaises(CheckError):
            verify_http(['1.1.1.1'], manifest, request)

    def test_unsupported_atomic_replace_never_deletes_live_file(self):
        sftp = self.fixture()
        before = sftp.files[ROOT + '/.htaccess']
        sftp.atomic_supported = False
        with self.assertRaises(OSError):
            atomic_replace(sftp, ROOT + '/.htaccess', b'new', '321-1')
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], before)

    def test_first_rollback_requires_dns_restoration(self):
        sftp = self.fixture()
        before = sftp.files[ROOT + '/.htaccess']
        switch(sftp, ROOT, 'activate', RELEASE, '321-1', [], http_verify=Mock())
        with self.assertRaisesRegex(CheckError, 'zuerst www-DNS'):
            switch(sftp, ROOT, 'rollback', RELEASE, '322-1', [])
        switch(sftp, ROOT, 'rollback', RELEASE, '322-1', [], dns_restored=True)
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], before)

    def test_second_release_can_roll_back_without_dns_change(self):
        sftp = self.fixture()
        switch(sftp, ROOT, 'activate', RELEASE, '321-1', [], http_verify=Mock())
        first = sftp.files[ROOT + '/.htaccess']
        second = 'b' * 40 + '-124-1'
        stage(sftp, ROOT, second, collect_files(self.site))
        switch(sftp, ROOT, 'activate', second, '322-1', [], http_verify=Mock())
        # A broken CURRENT release must not prevent returning to the good one.
        sftp.files[STORE + '/' + second + '/index.html'] = b'broken current frontend'
        switch(sftp, ROOT, 'rollback', second, '323-1', [])
        self.assertEqual(sftp.files[ROOT + '/.htaccess'], first)

    def test_unknown_root_rules_and_modified_release_are_rejected(self):
        sftp = self.fixture()
        sftp.files[ROOT + '/.htaccess'] = b'custom rules'
        with self.assertRaises(CheckError):
            switch(sftp, ROOT, 'activate', RELEASE, '321-1', [])
        self.assertEqual(sftp.writes, [])
        sftp = self.fixture()
        sftp.files[STORE + '/' + RELEASE + '/index.html'] = b'changed after staging'
        with self.assertRaises(CheckError):
            switch(sftp, ROOT, 'activate', RELEASE, '321-1', [])
        self.assertEqual(sftp.writes, [])


class OriginTests(unittest.TestCase):
    def test_www_is_checked_on_apex_ips_not_its_github_dns(self):
        cert = {'notAfter': 'Apr 16 00:00:00 2027 GMT'}
        def request(host, ip, path='/', method='HEAD'):
            self.assertEqual(ip, '1.1.1.1')
            body = b'{"ok":true,"ready":true}' if method == 'GET' else b''
            return 200, {}, body, cert
        request = Mock(side_effect=request)
        preflight(['1.1.1.1'], request)
        self.assertEqual(request.call_args_list[0].args, (APEX, '1.1.1.1'))
        self.assertEqual(request.call_args_list[1].args, (WWW, '1.1.1.1'))

    def test_origin_resolution_is_fixed_and_rejects_private_addresses(self):
        with patch('strato_activate.socket.getaddrinfo', return_value=[(None,None,None,None,('1.1.1.1',443))]) as resolver:
            self.assertEqual(origin_ips(), ['1.1.1.1'])
            resolver.assert_called_once_with(APEX,443,socket.AF_INET,socket.SOCK_STREAM)
        with patch('strato_activate.socket.getaddrinfo', return_value=[(None,None,None,None,('127.0.0.1',443))]):
            with self.assertRaises(CheckError):
                origin_ips()

    def test_unready_api_prevents_activation(self):
        response = (200, {}, b'{"ok":true,"ready":false}', {'notAfter':'2027'})
        with self.assertRaises(CheckError):
            preflight(['1.1.1.1'], Mock(return_value=response))

    def test_www_certificate_alone_does_not_prove_the_webspace_mapping(self):
        cert = {'notAfter':'2027'}
        def request(host, ip, path='/', method='HEAD'):
            if method == 'HEAD':
                return 200, {}, b'', cert
            if host == APEX:
                return 200, {}, b'{"ok":true,"ready":true}', cert
            return 404, {}, b'<html>different webspace</html>', cert
        with self.assertRaisesRegex(CheckError, 'Verzeichniszuordnung'):
            preflight(['1.1.1.1'], request)
        report = preflight(['1.1.1.1'], request, require_www=False)
        self.assertIn('Nur Vorbereitung', '\n'.join(report))


if __name__ == '__main__':
    unittest.main()
