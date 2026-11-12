"""Publish a fully tested main build to STRATO; retain versioned assets and rollback."""
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import socket

from strato_sftp_check import CheckError, fingerprint, inspect_target, validate_host, validate_root
from strato_stage import (STORE, collect_files, ensure_directory, read_regular,
                          stage, validate_release, write_new)
from strato_activate import (atomic_replace, backup_direct_files, direct_delivery,
                             direct_version, fingerprinted, install_direct_files,
                             managed_header, operation_id, origin_ips, preflight,
                             render_rules, restore_direct_files, retained_assets,
                             stored_assets, verify_direct_files, verify_http,
                             verify_known_rules)


@contextmanager
def connection():
    import paramiko
    host = validate_host(os.environ.get('STRATO_SFTP_HOST', ''))
    expected = os.environ.get('STRATO_SFTP_FINGERPRINT', '').strip().rstrip('=')
    if not re.fullmatch(r'SHA256:[A-Za-z0-9+/]{43}', expected):
        raise CheckError('Bestaetigter SFTP-Server-Fingerabdruck fehlt.')
    username = os.environ.get('STRATO_SFTP_USER', '')
    password = os.environ.get('STRATO_SFTP_PASSWORD', '')
    if not username or not password:
        raise CheckError('SFTP-Zugangsdaten fehlen.')
    with socket.create_connection((host, 22), timeout=15) as raw:
        transport = paramiko.Transport(raw)
        transport.banner_timeout = 15
        transport.auth_timeout = 15
        try:
            transport.start_client(timeout=20)
            if not hmac.compare_digest(fingerprint(transport.get_remote_server_key()), expected):
                raise CheckError('SFTP-Server-Fingerabdruck stimmt nicht ueberein. Kein Passwort gesendet.')
            transport.auth_password(username, password, fallback=False)
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                sftp.get_channel().settimeout(30)
                yield sftp
        finally:
            transport.close()


def build_manifest(files, release):
    validate_release(release)
    contents = {name: path.read_bytes() for name, path in files.items()}
    manifest = {'release': release, 'commit': release[:40], 'files': {
        name: {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        for name, data in contents.items()}}
    return manifest, contents


def root_backup(sftp, root, original, token):
    operation_id(token)
    directory = root + '/' + STORE + '/.backups'
    ensure_directory(sftp, directory)
    path = directory + '/' + token + '.htaccess'
    write_new(sftp, path, original)
    if read_regular(sftp, path, len(original)) != original:
        raise CheckError('Root-Sicherung konnte nicht bestaetigt werden.')


def upgrade_rules(sftp, root, original, manifest, token, ips, http_verify):
    """One-time V1 -> V2 upgrade without changing any frontend bytes."""
    if direct_version(original) == 2:
        return original
    root_backup(sftp, root, original, token)
    write_new(sftp, root + '/' + STORE + '/.backups/' + token + '.files.json',
              (json.dumps({'operation': token, 'changes': {}}) + '\n').encode())
    upgraded = render_rules(manifest, token, direct=True, version=2,
                            retained=retained_assets(manifest['files']))
    if read_regular(sftp, root + '/.htaccess', 200_000) != original:
        raise CheckError('Root-Regeln extern geaendert; Upgrade gestoppt.')
    atomic_replace(sftp, root + '/.htaccess', upgraded, token)
    try:
        http_verify(ips, manifest)
    except Exception as failure:
        if read_regular(sftp, root + '/.htaccess', 200_000) != upgraded:
            raise CheckError('Root-Regeln extern geaendert; Upgrade-Rueckweg nicht automatisch ausgefuehrt.') from None
        atomic_replace(sftp, root + '/.htaccess', original, token + '0')
        raise CheckError('V2-HTTP-Pruefung fehlgeschlagen; vorherige Root-Regeln wiederhergestellt (' + type(failure).__name__ + ').') from None
    print('Auslieferungsregeln V2 geprueft: alte und neue Fingerprint-Assets bleiben erreichbar.', flush=True)
    return upgraded


def deploy(sftp, root, files, release, token, ips, http_verify=verify_http, stage_release=stage):
    validate_root(root)
    validate_release(release)
    operation_id(token)
    inspect_target(sftp, root)
    original = read_regular(sftp, root + '/.htaccess', 200_000)
    if not direct_delivery(original):
        raise CheckError('Oeffentliche STRATO-Erstbereitstellung noch nicht abgeschlossen. Keine automatische Auslieferung.')
    current = verify_known_rules(sftp, root, original)
    verify_direct_files(sftp, root, current)
    desired, contents = build_manifest(files, release)
    # Mutation lock is held by the workflow for the entire build/deploy.
    original = upgrade_rules(sftp, root, original, current, token + '1', ips, http_verify)
    if current['files'] == desired['files']:
        http_verify(ips, current)
        return ['Frontend unveraendert: Build und aktive Dateien sind bytegleich.',
                'Aktiver Release: `' + current['release'] + '`.',
                'Keine erneute Dateiuebertragung erforderlich; www-Auslieferung und API erfolgreich geprueft.']

    # Stage and hash-verify ALL new files before touching public files.
    print('Geprueften Build in isolierten STRATO-Release uebertragen.', flush=True)
    stage_release(sftp, root, release, files)
    uploaded = json.loads(read_regular(sftp, root + '/' + STORE + '/' + release + '/.ready.json', 500_000))
    if uploaded != desired:
        raise CheckError('Uebertragener Release stimmt nicht mit dem getesteten Build ueberein.')
    op = token + '2'
    root_backup(sftp, root, original, op)
    snapshot = backup_direct_files(sftp, root, desired, op)
    final_assets = retained_assets(stored_assets(original), current['files'], desired['files'])
    transitional = render_rules(current, op, direct=True, version=2, retained=final_assets)
    final = render_rules(desired, op, direct=True, version=2, retained=final_assets)
    assets = [name for name in snapshot['changes']
              if fingerprinted(name) or Path(name).suffix.lower() not in {'.html', '.js', '.css'}]
    entrypoints = sorted((name for name in snapshot['changes'] if name not in assets),
                         key=lambda name: (name.endswith('.html'), name))
    try:
        install_direct_files(sftp, root, snapshot, contents, op, names=assets)
        if read_regular(sftp, root + '/.htaccess', 200_000) != original:
            raise CheckError('Root-Regeln waehrend Asset-Uebertragung extern geaendert.')
        # Old pages stay usable; both generations of assets are now allowed.
        atomic_replace(sftp, root + '/.htaccess', transitional, op)
        install_direct_files(sftp, root, snapshot, contents, op, names=entrypoints)
        if read_regular(sftp, root + '/.htaccess', 200_000) != transitional:
            raise CheckError('Root-Regeln waehrend Seiten-Uebertragung extern geaendert.')
        atomic_replace(sftp, root + '/.htaccess', final, op + '1')
        http_verify(ips, desired)
    except Exception as failure:
        try:
            active = read_regular(sftp, root + '/.htaccess', 200_000)
            if active not in {original, transitional, final}:
                raise CheckError('Root-Regeln extern geaendert.')
            # Restore old pages while both asset generations remain available.
            restore_direct_files(sftp, root, op, preserve_assets=True)
            previous_header = managed_header(original)
            rollback_rules = render_rules(current, previous_header[1], direct=True, version=2,
                                          retained=final_assets)
            atomic_replace(sftp, root + '/.htaccess', rollback_rules, op + '0')
            http_verify(ips, current)
        except Exception:
            raise CheckError('Auslieferung und vollstaendige automatische Ruecknahme fehlgeschlagen. Sicherungen unter .nic-releases/.backups/' + op + ' pruefen; API und DNS wurden nicht geaendert.') from None
        reason = str(failure) if isinstance(failure, CheckError) else type(failure).__name__
        raise CheckError('Neue Auslieferung fehlgeschlagen (' + reason + '). Vorheriges Frontend wiederhergestellt und per HTTP geprueft.') from None
    return ['Release veroeffentlicht: `' + release + '`.',
            str(len(snapshot['changes'])) + ' Frontend-Dateien atomar ersetzt; Assets vor den HTML-Einstiegsseiten.',
            'www-Seiten, Startseiten-Hash, HTTPS, Canonical, Schutz und API erfolgreich geprueft.',
            'Rueckweg: `.nic-releases/.backups/' + op + '.htaccess` und `.files.json`.',
            'API-Dateien, private Konfiguration, Datenbank und DNS unveraendert.']


def run():
    site = Path(os.environ.get('STRATO_SITE', '_site'))
    files = collect_files(site)  # No network/mutation before validating local scope.
    root = validate_root(os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/'))
    release = validate_release(os.environ.get('STRATO_RELEASE_ID', ''))
    token = operation_id(os.environ.get('STRATO_OPERATION_ID', ''))
    ips = origin_ips()
    lines = preflight(ips)  # BOTH www TLS and www API must work in production.
    with connection() as sftp:
        lines += deploy(sftp, root, files, release, token, ips)
    return ['Getesteter main-Commit: `' + release[:40] + '`.'] + lines


def main():
    try:
        lines, result = run(), 0
    except CheckError as exc:
        lines, result = [str(exc)], 1
    except Exception as exc:
        lines, result = ['STRATO-Auslieferung gestoppt (' + type(exc).__name__ + '). Keine ungepruefte Version freigeben; Job-Schritt und Sicherungen pruefen.'], 1
    report = '## STRATO Veroeffentlichung\n\n' + '\n'.join('- ' + line for line in lines) + '\n'
    print(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as stream:
            stream.write(report)
    return result


if __name__ == '__main__':
    raise SystemExit(main())
