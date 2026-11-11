"""Manual STRATO preflight: inspect a host key, then optionally authenticate read-only."""
import argparse
import base64
import hashlib
import hmac
import os
from pathlib import Path
import re
import socket
import stat


class CheckError(Exception):
    """A safe, actionable message which never includes credentials."""


def fingerprint(key):
    digest = hashlib.sha256(key.asbytes()).digest()
    return 'SHA256:' + base64.b64encode(digest).decode('ascii').rstrip('=')


def validate_host(host):
    host = host.strip().rstrip('.')
    if not re.fullmatch(r'[0-9]+\.ssh\.w[a-z0-9]+\.strato\.hosting', host, re.I):
        raise CheckError('STRATO_SFTP_HOST muss den kopierten STRATO-Servernamen ohne Protokoll oder Pfad enthalten.')
    return host


def validate_root(root):
    if not re.fullmatch(r'(?:/[A-Za-z0-9_-]+)*/immocheck-web', root):
        raise CheckError('Zielpfad muss ein absoluter Pfad zum Ordner immocheck-web sein; kein Root- oder Privatverzeichnis.')
    return root


def inspect_target(sftp, root):
    # Only metadata for three known public paths; never read private/config files.
    for path, predicate in [(root, stat.S_ISDIR), (root + '/api', stat.S_ISDIR),
                            (root + '/api/index.php', stat.S_ISREG)]:
        try:
            mode = sftp.lstat(path).st_mode
        except OSError:
            raise CheckError('Oeffentlicher Zielordner oder vorhandener API-Einstieg nicht gefunden. Startverzeichnis und Zielpfad pruefen.') from None
        if stat.S_ISLNK(mode) or not predicate(mode):
            raise CheckError('Zielstruktur ist unerwartet oder verwendet einen symbolischen Link. Vor dem Upload die Ordnerzuordnung pruefen.')
    return ['SFTP-Anmeldung erfolgreich.', 'Oeffentlicher Ordner und api/index.php vorhanden.',
            'Nur Metadaten gelesen; keine Dateien geaendert.']


def inspect_session(transport, mode, expected, username, password, root, sftp_factory):
    key = transport.get_remote_server_key()
    actual = fingerprint(key)
    if mode == 'fingerprint':
        return ['Server-Schluesseltyp: ' + key.get_name(), 'Server-Fingerabdruck: ' + actual,
                'Noch kein Vertrauensnachweis: mit vorhandenem vertrauenswuerdigem SFTP-Eintrag oder STRATO abgleichen.',
                'Keine Passwortanmeldung; keine Dateien gelesen oder veraendert.']
    expected = expected.strip().rstrip('=')
    if not re.fullmatch(r'SHA256:[A-Za-z0-9+/]{43}', expected):
        raise CheckError('STRATO_SFTP_FINGERPRINT fehlt oder ist ungueltig. Zuerst den Fingerabdruck abgleichen und hinterlegen.')
    if not hmac.compare_digest(actual, expected):
        raise CheckError('Server-Fingerabdruck stimmt nicht ueberein. Keine Anmeldedaten gesendet.')
    if not username or not password:
        raise CheckError('STRATO_SFTP_USER oder STRATO_SFTP_PASSWORD fehlt.')
    validate_root(root)
    # Verify the pinned host key BEFORE any password authentication.
    transport.auth_password(username, password, fallback=False)
    sftp = sftp_factory(transport)
    try:
        sftp.get_channel().settimeout(20)
        return inspect_target(sftp, root)
    finally:
        sftp.close()


def run(mode):
    import paramiko
    host = validate_host(os.environ.get('STRATO_SFTP_HOST', ''))
    root = os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/')
    sock = socket.create_connection((host, 22), timeout=15)
    transport = paramiko.Transport(sock)
    transport.banner_timeout = 15
    transport.auth_timeout = 15
    try:
        transport.start_client(timeout=20)
        return inspect_session(transport, mode, os.environ.get('STRATO_SFTP_FINGERPRINT', ''),
                               os.environ.get('STRATO_SFTP_USER', ''), os.environ.get('STRATO_SFTP_PASSWORD', ''),
                               root, paramiko.SFTPClient.from_transport)
    finally:
        transport.close()
        sock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['fingerprint', 'check'], default='fingerprint')
    args = parser.parse_args()
    try:
        lines = run(args.mode)
    except CheckError as exc:
        print('Pruefung gestoppt: ' + str(exc))
        return 1
    except Exception as exc:
        # Never print a raw connection exception or a traceback containing secrets.
        print('Verbindungspruefung fehlgeschlagen (' + type(exc).__name__ + '). Serveradresse, SFTP-Freigabe und Zugangsdaten pruefen.')
        return 1
    report = '## STRATO SFTP-Pruefung\n\n' + '\n'.join('- ' + line for line in lines) + '\n'
    print(report)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with Path(summary).open('a', encoding='utf-8') as stream:
            stream.write(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
