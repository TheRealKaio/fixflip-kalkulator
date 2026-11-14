"""Upload one isolated, verified frontend release; NEVER activate it or change DNS."""
import argparse
import errno
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import socket
import stat

from strato_sftp_check import CheckError, fingerprint, inspect_target, validate_host, validate_root


STORE = '.nic-releases'
GUARD = b'''# ImmoCheck managed staging storage: no HTTP access before activation.
Options -Indexes
Require all denied
'''
ACTIVE_GUARD = b'''# ImmoCheck managed release storage; the root rules block direct access.
Options -Indexes
'''
REQUIRED = {'index.html', 'service-worker.js', 'backend-config.json',
            'budget/index.html', 'finanzierungsrechner/index.html',
            'eigennutzung/index.html', 'vermietung/index.html', 'fix-flip/index.html',
            'nebenkostenabrechnung/index.html', 'preise/index.html', 'warum-immocheck/index.html', 'content-gate.php'}
EXTENSIONS = {'.html', '.js', '.css', '.json', '.svg', '.png', '.jpg', '.jpeg',
              '.webp', '.gif', '.avif', '.ico', '.woff', '.woff2', '.ttf', '.txt',
              '.xml', '.webmanifest', '.pdf', '.map', '.php'}
SKIP_FILES = {'CNAME', '.nojekyll', '.release-version', '.asset-manifest.json',
              '.calculator-css-baseline.json'}


def validate_file(relative):
    if (Path(relative).suffix.lower() not in EXTENSIONS
            or any(not re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*', part)
                   or part.lower() in {'api', 'immocheck-private'}
                   for part in relative.split('/'))
            or Path(relative).name.lower() in {'config.json', 'config.php', 'install.php'}
            or (Path(relative).suffix.lower() == '.php' and Path(relative).name != 'content-gate.php')):
        raise CheckError('Build enthaelt unerlaubte Dateien; nur statisches Frontend wird hochgeladen.')


def validate_release(release):
    if not re.fullmatch(r'[a-f0-9]{40}-[1-9][0-9]*-[1-9][0-9]*', release):
        raise CheckError('Release-ID muss aus Commit, Workflow-Lauf und Versuch bestehen.')
    return release


def collect_files(site):
    """Refuse server/config/symlink payloads before connecting or writing anything."""
    if site.is_symlink() or not site.is_dir():
        raise CheckError('Build-Verzeichnis fehlt oder ist ein symbolischer Link.')
    files = {}
    for path in sorted(site.rglob('*')):
        relative = path.relative_to(site).as_posix()
        if path.is_symlink():
            raise CheckError('Build enthaelt symbolische Links; Upload gestoppt.')
        if relative.split('/')[0] == '_checks':
            continue
        if path.is_dir():
            if path.name.startswith('.') or path.name.lower() in {'api', 'immocheck-private'}:
                raise CheckError('Build enthaelt ein unerlaubtes Verzeichnis.')
            continue
        if relative in SKIP_FILES:
            continue
        if not path.is_file():
            raise CheckError('Build enthaelt keine regulaere Datei.')
        validate_file(relative)
        files[relative] = path
    if not REQUIRED.issubset(files):
        raise CheckError('Build ist unvollstaendig: Startseite, Rechner oder Informationsseiten fehlen.')
    config = json.loads(files['backend-config.json'].read_text(encoding='utf-8'))
    if config.get('enabled') is not True or config.get('apiUrl') != 'https://neustart-immocheck.de/api/index.php':
        raise CheckError('API-Adresse oder Aktivierung weicht vom bestehenden Betrieb ab.')
    return files


def existing(sftp, path):
    try:
        return sftp.lstat(path)
    except OSError as exc:
        if exc.errno != errno.ENOENT:
            raise
        return None


def ensure_directory(sftp, path):
    entry = existing(sftp, path)
    if entry is None:
        sftp.mkdir(path, mode=0o755)
    elif not stat.S_ISDIR(entry.st_mode) or stat.S_ISLNK(entry.st_mode):
        raise CheckError('Release-Verzeichnis ist kein normaler Ordner; keine Links verfolgen.')


def write_new(sftp, path, payload):
    # Exclusive creation: do not overwrite even unexpected files in our store.
    with sftp.open(path, 'wx') as stream:
        stream.write(payload)


def read_regular(sftp, path, limit=None):
    entry = sftp.lstat(path)
    if not stat.S_ISREG(entry.st_mode) or stat.S_ISLNK(entry.st_mode):
        raise CheckError('Release-Datei hat einen unerwarteten Typ.')
    if limit is not None and entry.st_size > limit:
        raise CheckError('Release-Metadaten sind unerwartet gross.')
    with sftp.open(path, 'rb') as stream:
        return stream.read() if limit is None else stream.read(limit + 1)


def stage(sftp, root, release, files):
    validate_root(root)
    validate_release(release)
    for relative in files:
        validate_file(relative)
    inspect_target(sftp, root)
    store = root + '/' + STORE
    ensure_directory(sftp, store)
    guard = store + '/.htaccess'
    if existing(sftp, guard) is None:
        write_new(sftp, guard, GUARD)
    elif read_regular(sftp, guard, 4096) not in {GUARD, ACTIVE_GUARD}:
        raise CheckError('Unbekannter Zugriffsschutz im Release-Ordner; nicht ueberschreiben.')
    target = store + '/' + release
    if existing(sftp, target) is not None:
        raise CheckError('Release existiert bereits. Workflow als neuen Versuch starten.')
    sftp.mkdir(target, mode=0o755)

    # Capability check strictly inside the NEW release, never against live files.
    # Activation will need atomic replacement; do not emulate it with delete+rename.
    source, destination = target + '/.rename-source', target + '/.rename-target'
    write_new(sftp, source, b'new')
    write_new(sftp, destination, b'old')
    try:
        sftp.posix_rename(source, destination)
    except OSError:
        raise CheckError('Server unterstuetzt atomaren Dateitausch nicht. Bestehende Auslieferung unveraendert; Aktivierung separat planen.') from None
    if read_regular(sftp, destination, 16) != b'new':
        raise CheckError('Atomarer Dateitausch konnte nicht bestaetigt werden.')
    # Only our probe file; never remove any previous release or production path.
    sftp.remove(destination)

    manifest = {'release': release, 'commit': release[:40], 'files': {}}
    directories = {target}
    for relative, local in files.items():
        remote = target + '/' + relative
        parent = remote.rsplit('/', 1)[0]
        parts = parent[len(target):].strip('/').split('/') if parent != target else []
        current = target
        for part in parts:
            current += '/' + part
            if current not in directories:
                ensure_directory(sftp, current)
                directories.add(current)
        payload = local.read_bytes()
        write_new(sftp, remote, payload)
        digest = hashlib.sha256(payload).hexdigest()
        actual = hashlib.sha256(read_regular(sftp, remote)).hexdigest()
        if not hmac.compare_digest(digest, actual):
            raise CheckError('Uebertragungspruefung fehlgeschlagen. Release wird nicht als fertig markiert.')
        manifest['files'][relative] = {'sha256': digest, 'bytes': len(payload)}
    # Only a complete hash-verified upload receives this marker. No live pointer.
    write_new(sftp, target + '/.ready.json', (json.dumps(manifest, indent=2) + '\n').encode())
    return ['Release: `' + release + '`',
            str(len(files)) + ' Frontend-Dateien hochgeladen und per SHA256 gegengeprueft.',
            'Atomarer Dateitausch im Testordner erfolgreich.',
            'Testversion vorbereitet, NICHT aktiviert.',
            'Bestehende Root-.htaccess, API, private Daten und DNS unveraendert.',
            'Naechster Schritt: HTTPS/www pruefen und Aktivierung vorbereiten.']


def stage_session(transport, expected, username, password, root, release, files, factory):
    expected = expected.strip().rstrip('=')
    if not re.fullmatch(r'SHA256:[A-Za-z0-9+/]{43}', expected):
        raise CheckError('STRATO_SFTP_FINGERPRINT fehlt oder ist ungueltig.')
    if not hmac.compare_digest(fingerprint(transport.get_remote_server_key()), expected):
        raise CheckError('Server-Fingerabdruck stimmt nicht ueberein. Keine Anmeldedaten gesendet.')
    if not username or not password:
        raise CheckError('SFTP-Benutzer oder Passwort fehlt.')
    validate_root(root)
    validate_release(release)
    transport.auth_password(username, password, fallback=False)
    sftp = factory(transport)
    try:
        sftp.get_channel().settimeout(30)
        return stage(sftp, root, release, files)
    finally:
        sftp.close()


def run(site):
    # Validate the complete local payload BEFORE any server operation.
    files = collect_files(site)
    release = validate_release(os.environ.get('STRATO_RELEASE_ID', ''))
    root = validate_root(os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/'))
    host = validate_host(os.environ.get('STRATO_SFTP_HOST', ''))
    import paramiko
    sock = socket.create_connection((host, 22), timeout=15)
    transport = paramiko.Transport(sock)
    transport.banner_timeout = 15
    transport.auth_timeout = 15
    try:
        transport.start_client(timeout=20)
        return stage_session(transport, os.environ.get('STRATO_SFTP_FINGERPRINT', ''),
                             os.environ.get('STRATO_SFTP_USER', ''),
                             os.environ.get('STRATO_SFTP_PASSWORD', ''),
                             root, release, files, paramiko.SFTPClient.from_transport)
    finally:
        transport.close()
        sock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=Path('_site'))
    args = parser.parse_args()
    try:
        lines = run(args.site)
    except CheckError as exc:
        print('Upload gestoppt: ' + str(exc))
        return 1
    except Exception as exc:
        print('Upload fehlgeschlagen (' + type(exc).__name__ + '). Bestehende Auslieferung bleibt aktiv; keinen unvollstaendigen Release aktivieren.')
        return 1
    report = '## STRATO Testversion\n\n' + '\n'.join('- ' + line for line in lines) + '\n'
    print(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as stream:
            stream.write(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
