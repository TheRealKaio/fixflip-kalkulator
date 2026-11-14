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


def import_block(source):
    return source[source.index(START):source.index(ANCHOR, source.index(START))]


def functions(source):
    matches = list(re.finditer(r'^function\s+(\w+)\(', source, re.M))
    return {match[1]: source[match.start():matches[i+1].start() if i+1 < len(matches) else len(source)].strip()
            for i, match in enumerate(matches)}


def patch_application(installed, tested):
    local, remote = functions(tested), functions(installed)
    for name in ['nic_query', 'nic_now', 'nic_email', 'nic_name', 'nic_session', 'nic_admin', 'nic_audit']:
        if remote.get(name) != local.get(name):
            raise CheckError('Installierter Schutz-/Datenbankhelfer weicht ab: ' + name + '. Nicht automatisch ersetzen.')
    if installed.count(ANCHOR) != 1 or installed.count(ADMIN) != 1 or installed.index(ADMIN) > installed.index(ANCHOR):
        raise CheckError('Admin-geschuetzter Einfuegepunkt fehlt oder ist mehrdeutig.')
    block = import_block(tested)
    if START in installed:
        if installed.count(START) != 1 or import_block(installed) != block:
            raise CheckError('Vorhandene Import-Implementierung weicht ab; nicht ueberschreiben.')
        patched = installed
    else:
        patched = installed.replace(ANCHOR, block + ANCHOR, 1)
    if HEALTH in patched:
        patched = patched.replace(HEALTH, CAPABLE, 1)
    elif CAPABLE not in patched:
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
            if require_import and health.get('usersImportVersion') != 1:
                raise CheckError('Aktualisierte Import-Route noch nicht bestaetigt: ' + host)


def main():
    try:
        mode = os.environ.get('STRATO_BACKEND_IMPORT_MODE', 'inspect')
        if mode not in {'inspect', 'apply'}:
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
            patched = patch_application(text, APP.read_text(encoding='utf-8')).encode()
            print('Gezielte Ergaenzung und vorhandene Admin-/CSRF-Pruefungen kompatibel.', flush=True)
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
            private_replace(sftp, path, patched, token, permissions)
            try:
                for attempt in range(10):
                    try:
                        verify_health(ips, require_import=True)
                        break
                    except CheckError:
                        if attempt == 9:
                            raise
                        time.sleep(2)  # Allow the existing PHP opcode cache to observe the atomic rename.
            except Exception:
                if read_regular(sftp, path, 500000) != patched:
                    raise CheckError('API extern geaendert; Ruecknahme nicht automatisch ueberschreiben.')
                private_replace(sftp, path, original, token + '0', permissions)
                verify_health(ips)
                raise CheckError('Import-Aktivierung nicht bestaetigt; vorherige API atomar wiederhergestellt und geprueft.')
            print('Admin-Import-Route atomar aktiviert; HTTP-Faehigkeit auf Hauptdomain und www bestaetigt.')
            print('Keine Nutzerdaten importiert; Datenbank, Konfiguration, Berechtigungen und andere API-Routen unveraendert.')
        return 0
    except Exception as error:
        print(str(error) if isinstance(error, CheckError) else 'Backend-Pruefung fehlgeschlagen: ' + type(error).__name__)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
