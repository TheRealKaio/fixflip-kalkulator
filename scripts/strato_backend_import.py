"""Inspect or narrowly activate the existing admin CSV-import route, no data import."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import time
import secrets
from contextlib import contextmanager

from strato_activate import APEX, WWW, operation_id, origin_ips, origin_request
from strato_publish import connection
from strato_sftp_check import CheckError, validate_root
from strato_stage import existing, read_regular, write_new

APP = Path('server/webspace/immocheck-private/app.php')
ANCHOR = "    if ($route==='user-action' && $method==='POST') {"
START = "    if ($route==='users-import' && $method==='POST') {"
ADMIN = '$admin=nic_admin($db,$c);'
HEALTH = "nic_reply(['ok'=>true,'ready'=>$ready,'version'=>'8.360']);"
CAPABLE = "nic_reply(['ok'=>true,'ready'=>$ready,'version'=>'8.360','usersImportVersion'=>1]);"
SETTINGS_CAPABLE = "nic_reply(['ok'=>true,'ready'=>$ready,'version'=>'8.360','usersImportVersion'=>1,'settingsVisibilityVersion'=>1]);"
VIS_START = "    $visibility = $s['navigationVisibility'] ?? [];"
VIS_END = '    // Inputs are public website settings, never server configuration or account data.'


def import_block(source):
    return source[source.index(START):source.index(ANCHOR, source.index(START))]


def functions(source):
    matches = list(re.finditer(r'^function\s+(\w+)\(', source, re.M))
    return {match[1]: source[match.start():matches[i+1].start() if i+1 < len(matches) else len(source)].strip()
            for i, match in enumerate(matches)}


def patch_settings_persistence(installed, tested):
    """Add only known missing menu/SEO fields; preserve other PHP server logic."""
    remote = functions(installed).get('nic_clean_settings')
    local = functions(tested).get('nic_clean_settings')
    if not remote or not local:
        raise CheckError('Server-Einstellungsvalidierung fehlt.')
    expected = local[local.index(VIS_START):local.index(VIS_END)]
    if VIS_START in remote:
        if VIS_END not in remote or remote[remote.index(VIS_START):remote.index(VIS_END)] != expected:
            raise CheckError('Unbekannte Menüvalidierung auf STRATO; nicht überschreiben.')
        patched = remote
    else:
        if remote.count(VIS_END) != 1 or "'contentSections'" not in remote:
            raise CheckError('Alte Einstellungsstruktur unbekannt; keine Änderung.')
        patched = remote.replace(VIS_END, expected + VIS_END, 1)
    whitelist = next((line for line in patched.splitlines() if line.startswith('    $keys = [')), None)
    if not whitelist or not whitelist.endswith('];') or "'contentSections'" not in whitelist:
        raise CheckError('Unbekannte Server-Whitelist.')
    desired = whitelist
    for key in ('navigationVisibility', 'seoIndexing'):
        if "'" + key + "'" not in desired:
            if ",'mediaLibrary'" in desired:
                desired = desired.replace(",'mediaLibrary'", ",'" + key + "','mediaLibrary'", 1)
            else:
                desired = desired[:-2] + ",'" + key + "'];"
    patched = patched.replace(whitelist, desired, 1)
    validation = next((line for line in patched.splitlines() if "Ungültiges Einstellungsfeld: " in line), None)
    if not validation or "'] as $key)" not in validation:
        raise CheckError('Unbekannte Einstellungsvalidierung.')
    if "'seoIndexing'" not in validation:
        patched = patched.replace(validation, validation.replace('] as $key)', ",'seoIndexing'] as $key)"), 1)
    if patched == remote:
        return installed
    if installed.count(remote) != 1:
        raise CheckError('Einstellungsfunktion nicht eindeutig.')
    return installed.replace(remote, patched, 1)


def patch_application(installed, tested):
    local, remote = functions(tested), functions(installed)
    for name in ['nic_query', 'nic_now', 'nic_email', 'nic_name', 'nic_session', 'nic_admin', 'nic_audit']:
        if remote.get(name) != local.get(name):
            raise CheckError('Installierter Schutz-/Datenbankhelfer weicht ab: ' + name + '. Nicht automatisch ersetzen.')
    anchor_at = installed.find(ANCHOR)
    admin_at = installed.rfind(ADMIN, 0, anchor_at) if anchor_at >= 0 else -1
    if installed.count(ANCHOR) != 1 or admin_at < 0:
        raise CheckError('Admin-geschuetzter Einfuegepunkt fehlt oder ist mehrdeutig.')
    block = import_block(tested)
    if START in installed:
        if installed.count(START) != 1 or import_block(installed) != block:
            raise CheckError('Vorhandene Import-Implementierung weicht ab; nicht ueberschreiben.')
        patched = installed
    else:
        patched = installed.replace(ANCHOR, block + ANCHOR, 1)
    patched = patch_settings_persistence(patched, tested)
    if HEALTH in patched:
        patched = patched.replace(HEALTH, SETTINGS_CAPABLE, 1)
    elif CAPABLE in patched:
        patched = patched.replace(CAPABLE, SETTINGS_CAPABLE, 1)
    elif SETTINGS_CAPABLE not in patched:
        raise CheckError('Bekannter Health-Einstieg fehlt; keine Aktivierung.')
    return patched


def private_replace(sftp, path, payload, token, mode):
    temporary = path + '.next-' + operation_id(token)
    write_new(sftp, temporary, payload)
    sftp.chmod(temporary, mode)
    if read_regular(sftp, temporary, 500000) != payload:
        raise CheckError('Vorbereitete API-Datei stimmt nicht mit dem geprueften Stand ueberein.')
    sftp.posix_rename(temporary, path)


def verify_health(ips, require_import=False):
    for ip in ips:
        for host in [APEX, WWW]:
            status, _, body, _ = origin_request(host, ip, '/api/index.php?r=health', 'GET')
            health = json.loads(body)
            if status != 200 or health.get('ok') is not True or health.get('ready') is not True:
                raise CheckError('API nicht bereit: ' + host)
            if require_import and (health.get('usersImportVersion') != 1 or health.get('settingsVisibilityVersion') != 1):
                raise CheckError('Aktualisierte Import-Route noch nicht bestaetigt: ' + host)


@contextmanager
def cache_refresher(sftp, root, token, ips):
    """Invalidate this app's opcode cache through a temporary secret-protected endpoint."""
    secret = secrets.token_hex(32)
    name = 'nic-import-refresh-' + token + '-' + secrets.token_hex(8) + '.php'
    path = root + '/api/' + name
    digest = hashlib.sha256(secret.encode()).hexdigest()
    code = ('''<?php
declare(strict_types=1);
ini_set('display_errors', '0');
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, private');
header('X-Content-Type-Options: nosniff');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'GET' || time() > EXPIRY ||
    !hash_equals('DIGEST', hash('sha256', $_SERVER['HTTP_X_NIC_PREVIEW_TOKEN'] ?? ''))) {
    http_response_code(403); echo '{"error":"Nicht verfuegbar"}'; exit;
}
$target = dirname(__DIR__, 2) . '/immocheck-private/app.php';
clearstatcache(true, $target);
$invalidated = function_exists('opcache_invalidate') ? opcache_invalidate($target, true) : false;
echo json_encode(['ok'=>true,'invalidated'=>$invalidated]);
'''.replace('EXPIRY', str(int(time.time()) + 300)).replace('DIGEST', digest)).encode()
    write_new(sftp, path, code)
    try:
        if read_regular(sftp, path, 20000) != code:
            raise CheckError('Geschuetzter Cache-Refresh nicht vollstaendig uebertragen.')
        for ip in ips:
            for host in [APEX, WWW]:
                if origin_request(host, ip, '/api/' + name, 'GET')[0] != 403:
                    raise CheckError('Cache-Refresh ist nicht gegen unbestaetigte Aufrufe geschuetzt.')
        def refresh():
            for ip in ips:
                for host in [APEX, WWW]:
                    status, _, body, _ = origin_request(host, ip, '/api/' + name, 'GET', preview_token=secret)
                    result = json.loads(body)
                    if status != 200 or result.get('ok') is not True:
                        raise CheckError('Geschuetzter Cache-Refresh fehlgeschlagen: ' + host)
                    print(host + ': Cache der API-Anwendungsdatei invalidiert=' + str(result.get('invalidated')), flush=True)
        yield refresh
    finally:
        if read_regular(sftp, path, 20000) == code:
            sftp.remove(path)
        else:
            raise CheckError('Temporaerer Cache-Refresh extern geaendert; nicht automatisch entfernen.')


def apply_media_patch(original):
    # This release upgrades the inspected production revision only.
    if hashlib.sha256(original).hexdigest() != 'efc1d7fac9a7b571474f1b1cd1aea687406684869386555eda55372a12c7bab4':
        raise CheckError('Medienupdate: installierter PHP-Stand hat sich geändert.')
    patch = Path(__file__).with_name('strato_media_v1.patch').resolve()
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory) / 'app.php'
        target.write_bytes(original)
        result = subprocess.run(['patch', '--batch', '--forward', '--fuzz=0', str(target), '-i', str(patch)], capture_output=True)
        if result.returncode:
            raise CheckError('Medienupdate passt nicht zum installierten PHP-Code.')
        return target.read_bytes()


def verify_media(ips):
    for ip in ips:
        for host in (APEX, WWW):
            status, _, body, _ = origin_request(host, ip, '/api/index.php?r=media', 'GET')
            if status != 404 or json.loads(body).get('error') != 'Datei nicht gefunden.':
                raise CheckError('Medienroute auf ' + host + ' nicht aktiv.')


def main():
    try:
        mode = os.environ.get('STRATO_BACKEND_IMPORT_MODE', 'inspect')
        if mode not in {'inspect', 'apply', 'media'}:
            raise CheckError('Unbekannter Backend-Modus.')
        root = validate_root(os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/'))
        private = root.rsplit('/', 1)[0] + '/immocheck-private'
        path = private + '/app.php'
        token = operation_id(os.environ['STRATO_OPERATION_ID'])
        ips = origin_ips()
        verify_health(ips)
        with connection() as sftp:
            guard = read_regular(sftp, private + '/.htaccess', 4096).decode()
            if not re.search(r'^\s*Require\s+all\s+denied\s*$', guard, re.M):
                raise CheckError('Schutz des privaten API-Ordners nicht bestaetigt.')
            entry = read_regular(sftp, root + '/api/index.php', 20000).decode()
            if not re.search(r"require(?:_once)?\s+dirname\(__DIR__,\s*2\)\s*\.\s*'/immocheck-private/app.php'", entry):
                raise CheckError('API-Einstieg verwendet einen anderen privaten Anwendungspfad.')
            original = read_regular(sftp, path, 500000)
            text = original.decode('utf-8')
            print(json.dumps({'mode': mode, 'installed_sha256': hashlib.sha256(original).hexdigest(),
                              'import_route_present': START in text}), flush=True)
            patched = apply_media_patch(original) if mode == 'media' else patch_application(text, APP.read_text(encoding='utf-8')).encode()
            print('Menü-/SEO-Speicherung, Nutzerimport und Admin-/CSRF-Schutz geprüft.', flush=True)
            if mode == 'inspect':
                print('Nur API-Quellcode geprueft; keine Dateien, Konten oder Einstellungen geaendert.')
                return 0
            with tempfile.TemporaryDirectory() as directory:
                local = Path(directory) / 'app.php'
                local.write_bytes(patched)
                lint = subprocess.run(['php', '-l', str(local)], capture_output=True)
                if lint.returncode:
                    raise CheckError('Syntaxpruefung des gezielt ergaenzten API-Codes fehlgeschlagen.')
            if patched == original:
                verify_health(ips, require_import=True)
                print('Import-Route bereits aktuell und per HTTP bestaetigt.')
                return 0
            directory = private + '/.nic-import-backups'
            item = existing(sftp, directory)
            if item is None:
                sftp.mkdir(directory, mode=0o700)
            elif not stat.S_ISDIR(item.st_mode) or stat.S_ISLNK(item.st_mode):
                raise CheckError('API-Sicherungsordner ist kein normaler Ordner.')
            backup = directory + '/' + token + '.php'
            write_new(sftp, backup, original)
            sftp.chmod(backup, 0o600)
            if read_regular(sftp, backup, 500000) != original or read_regular(sftp, path, 500000) != original:
                raise CheckError('API-Sicherung oder unveraenderter Ausgangsstand nicht bestaetigt.')
            permissions = stat.S_IMODE(sftp.lstat(path).st_mode)
            with cache_refresher(sftp, root, token, ips) as refresh:
                private_replace(sftp, path, patched, token, permissions)
                try:
                    refresh()
                    for attempt in range(10):
                        try:
                            verify_health(ips, require_import=True)
                            if mode == 'media':
                                verify_media(ips)
                            break
                        except CheckError:
                            if attempt == 9:
                                raise
                            time.sleep(2)
                except Exception as failure:
                    if read_regular(sftp, path, 500000) != patched:
                        raise CheckError('API extern geaendert; Ruecknahme nicht automatisch ueberschreiben.')
                    private_replace(sftp, path, original, token + '0', permissions)
                    refresh()
                    verify_health(ips)
                    raise CheckError('Import-Aktivierung nicht bestaetigt; vorherige API atomar wiederhergestellt und geprueft. Grund: ' + str(failure))
            print('Admin-Import-Route atomar aktiviert; HTTP-Faehigkeit auf Hauptdomain und www bestaetigt.')
            print('Keine Nutzerdaten importiert; Datenbank, Konfiguration, Berechtigungen und andere API-Routen unveraendert.')
        return 0
    except Exception as error:
        print(str(error) if isinstance(error, CheckError) else 'Backend-Pruefung fehlgeschlagen: ' + type(error).__name__)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
