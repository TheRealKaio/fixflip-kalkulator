"""Pinned SFTP activation, direct-origin TLS/HTTP checks and atomic rollback."""
import hashlib
import hmac
import http.client
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import ssl
import stat

from strato_sftp_check import CheckError, fingerprint, inspect_target, validate_host, validate_root
from strato_stage import (ACTIVE_GUARD, GUARD, REQUIRED, STORE, ensure_directory,
                          read_regular, validate_file, validate_release, write_new)

APEX = 'neustart-immocheck.de'
WWW = 'www.' + APEX
DEFAULT_RELEASE = '6093643fb0a68d874481899dabd3af814659f7dd-43093243842-2'


def real_directory(sftp, path):
    if not stat.S_ISDIR(sftp.lstat(path).st_mode):
        raise CheckError('Release- oder Sicherungsordner ist kein normaler Ordner.')


def operation_id(value):
    if not re.fullmatch(r'[1-9][0-9]*-[1-9][0-9]*', value):
        raise CheckError('Vorgangs-ID muss Workflow-Lauf und Versuch enthalten.')
    return value


def origin_ips():
    # Resolve ONLY the confirmed STRATO apex, never www (still on GitHub).
    ips = sorted({x[4][0] for x in socket.getaddrinfo(APEX, 443, socket.AF_INET, socket.SOCK_STREAM)})
    if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise CheckError('Keine oeffentliche IPv4 der Hauptdomain gefunden.')
    return ips


def origin_request(host, ip, path='/', method='HEAD', limit=12_000_000):
    if host not in {APEX, WWW} or not ipaddress.ip_address(ip).is_global or method not in {'GET', 'HEAD'}:
        raise CheckError('Unerwartetes HTTP-Pruefziel.')
    context = ssl.create_default_context()
    # Mandatory trusted chain, time validity AND hostname verification via SNI.
    with socket.create_connection((ip, 443), timeout=20) as raw:
        with context.wrap_socket(raw, server_hostname=host) as tls:
            certificate = tls.getpeercert()
            tls.sendall((method + ' ' + path + ' HTTP/1.1\r\nHost: ' + host
                         + '\r\nAccept-Encoding: identity\r\nConnection: close\r\n\r\n').encode('ascii'))
            response = http.client.HTTPResponse(tls, method=method)
            response.begin()
            body = response.read(limit + 1)
            if len(body) > limit:
                raise CheckError('HTTP-Pruefantwort ist unerwartet gross.')
            return response.status, dict((k.lower(), v) for k, v in response.getheaders()), body, certificate


def preflight(ips, request=origin_request):
    lines = []
    for ip in ips:
        for host in [APEX, WWW]:
            status, _, _, cert = request(host, ip)
            lines.append(host + ': Zertifikatskette, Laufzeit und Name am STRATO-Ziel geprueft; gueltig bis ' + cert['notAfter'] + '; HTTP ' + str(status) + '.')
        status, _, body, _ = request(APEX, ip, '/api/index.php?r=health', 'GET')
        health = json.loads(body)
        if status != 200 or health.get('ok') is not True or health.get('ready') is not True:
            raise CheckError('Bestehende API meldet keinen bereiten Zustand. Nicht umschalten.')
        # A valid www certificate does not prove that its virtual host points to
        # immocheck-web. The same physical api/index.php must be reachable there
        # before rewriting any frontend URLs into the stored release.
        status, _, body, _ = request(WWW, ip, '/api/index.php?r=health', 'GET')
        try:
            www_health = json.loads(body)
        except (ValueError, UnicodeError):
            www_health = {}
        if status != 200 or not isinstance(www_health, dict) or www_health.get('ok') is not True or www_health.get('ready') is not True:
            raise CheckError('www hat ein gueltiges Zertifikat, zeigt am STRATO-Ziel aber nicht auf dieselbe bereite API (HTTP ' + str(status) + '). Interne www-Verzeichniszuordnung zu immocheck-web pruefen. Keine Umschaltung oder DNS-Aenderung ausgefuehrt.')
    return lines


def load_release(sftp, root, release):
    validate_release(release)
    target = root + '/' + STORE + '/' + release
    # Each known directory must be real, never a symlink into private storage.
    for directory in [root + '/' + STORE, target]:
        real_directory(sftp, directory)
    manifest = json.loads(read_regular(sftp, target + '/.ready.json', 500_000))
    files = manifest.get('files', {})
    if manifest.get('release') != release or manifest.get('commit') != release[:40] or not REQUIRED.issubset(files) or len(files) > 1000:
        raise CheckError('Fertig-Markierung des Release fehlt oder ist unvollstaendig.')
    checked_dirs = {target}
    for name, meta in files.items():
        validate_file(name)
        parent = target
        for part in name.split('/')[:-1]:
            parent += '/' + part
            if parent not in checked_dirs:
                real_directory(sftp, parent)
                checked_dirs.add(parent)
        if not isinstance(meta.get('bytes'), int) or not 0 <= meta['bytes'] <= 12_000_000 or not re.fullmatch('[a-f0-9]{64}', meta.get('sha256', '')):
            raise CheckError('Ungueltige Release-Pruefsummen.')
        payload = read_regular(sftp, target + '/' + name, meta['bytes'])
        if len(payload) != meta['bytes'] or not hmac.compare_digest(hashlib.sha256(payload).hexdigest(), meta['sha256']):
            raise CheckError('Release-Dateien stimmen nicht mit dem erfolgreichen Upload ueberein.')
    config = json.loads(read_regular(sftp, target + '/backend-config.json', 4096))
    if config.get('enabled') is not True or config.get('apiUrl') != 'https://' + APEX + '/api/index.php':
        raise CheckError('Release verwendet eine abweichende API-Konfiguration.')
    return manifest


def render_rules(manifest, backup):
    release = validate_release(manifest['release'])
    operation_id(backup)
    files = manifest['files']
    rules = ['# NIC-RELEASE: ' + release, '# NIC-ROLLBACK: ' + backup,
             'Options -Indexes', 'DirectoryIndex index.html', 'RewriteEngine On',
             'RewriteRule ^api(?:/|$) - [L]',
             'RewriteRule ^\\.well-known(?:/|$) - [L]',
             # Apache matches decoded paths, including encoded dot characters.
             'RewriteRule (^|/)\\. - [F,END]',
             'RewriteCond %{HTTP_HOST} !^www\\.neustart-immocheck\\.de$ [NC]',
             'RewriteRule ^(.*)$ https://' + WWW + '/$1 [R=302,L]',
             'RewriteCond %{HTTPS} !=on',
             'RewriteRule ^(.*)$ https://' + WWW + '/$1 [R=302,L]']
    for name in sorted(files):
        validate_file(name)
        if name.endswith('/index.html'):
            directory = name[:-len('/index.html')]
            rules += ['RewriteRule ^' + re.escape(directory) + '$ /' + directory + '/ [R=302,L]',
                      'RewriteRule ^' + re.escape(directory) + '/$ ' + STORE + '/' + release + '/' + name + ' [END]']
        pattern = '(?:index\\.html)?' if name == 'index.html' else re.escape(name)
        rules.append('RewriteRule ^' + pattern + '$ ' + STORE + '/' + release + '/' + name + ' [END]')
    rules.append('RewriteRule ^ - [R=404,END]')
    return ('\n'.join(rules) + '\n').encode()


def managed_header(payload):
    match = re.match(rb'# NIC-RELEASE: ([a-f0-9]{40}-[1-9][0-9]*-[1-9][0-9]*)\n# NIC-ROLLBACK: ([1-9][0-9]*-[1-9][0-9]*)\n', payload)
    return (match[1].decode(), match[2].decode()) if match else None


def legacy_rules(payload):
    def normalize(value):
        return [' '.join(line.split()) for line in value.decode().splitlines() if line.strip() and not line.lstrip().startswith('#')]
    reference = Path('server/webspace/immocheck-web/.htaccess').read_bytes()
    return normalize(payload) == normalize(reference)


def verify_known_rules(sftp, root, payload):
    if legacy_rules(payload):
        return
    header = managed_header(payload)
    if not header:
        raise CheckError('Unbekannte Root-.htaccess; nicht automatisch ueberschreiben.')
    manifest = load_release(sftp, root, header[0])
    if render_rules(manifest, header[1]) != payload:
        raise CheckError('Verwaltete Root-.htaccess wurde ausserhalb des Workflows geaendert.')


def atomic_replace(sftp, path, payload, token):
    operation_id(token)
    temporary = path + '.next-' + token
    write_new(sftp, temporary, payload)
    if read_regular(sftp, temporary, len(payload)) != payload:
        raise CheckError('Vorbereiteter Dateitausch konnte nicht verifiziert werden.')
    # No delete+rename fallback. A failure must leave the old file in place.
    sftp.posix_rename(temporary, path)


def verify_http(ips, manifest, request=origin_request):
    release = manifest['release']
    for ip in ips:
        status, _, body, _ = request(WWW, ip, '/', 'GET')
        if status != 200 or hashlib.sha256(body).hexdigest() != manifest['files']['index.html']['sha256']:
            raise CheckError('STRATO liefert nicht den aktivierten Startseiten-Release aus.')
        for name in manifest['files']:
            if name.endswith('/index.html'):
                path = '/' + name[:-len('index.html')]
                status, _, _, _ = request(WWW, ip, path)
                if status != 200:
                    raise CheckError('Direkter Inhalts- oder Rechneraufruf fehlgeschlagen.')
        for path in ['/service-worker.js', '/backend-config.json']:
            if request(WWW, ip, path)[0] != 200:
                raise CheckError('Zentrales Frontend-Asset nicht erreichbar.')
        for path, expected in [('/nic-unknown-page-test/', 404), ('/.' + 'nic-releases/' + release + '/.ready.json', 403)]:
            if request(WWW, ip, path)[0] != expected:
                raise CheckError('Unbekannte Pfade oder Release-Schutz funktionieren nicht wie erwartet.')
        status, headers, _, _ = request(APEX, ip, '/budget/?nic=check')
        if status != 302 or headers.get('location') != 'https://' + WWW + '/budget/?nic=check':
            raise CheckError('Canonical-Weiterleitung bewahrt Pfad und Query nicht korrekt.')
    preflight(ips, request)


def switch(sftp, root, mode, release, token, ips, dns_restored=False,
           http_verify=verify_http):
    validate_root(root)
    operation_id(token)
    inspect_target(sftp, root)
    live_path = root + '/.htaccess'
    original = read_regular(sftp, live_path, 200_000)
    store = root + '/' + STORE
    real_directory(sftp, store)
    guard_path = store + '/.htaccess'
    guard = read_regular(sftp, guard_path, 4096)
    if guard not in {GUARD, ACTIVE_GUARD}:
        raise CheckError('Unbekannter Zugriffsschutz im Release-Speicher.')
    if mode == 'rollback':
        header = managed_header(original)
        if not header:
            raise CheckError('Kein aktivierter STRATO-Release mit Rueckweg vorhanden.')
        real_directory(sftp, store + '/.backups')
        previous = read_regular(sftp, store + '/.backups/' + header[1] + '.htaccess', 200_000)
        verify_known_rules(sftp, root, previous)
        if legacy_rules(previous) and not dns_restored:
            raise CheckError('Erster Rueckweg fuehrt zu GitHub: zuerst www-DNS zuruecksetzen und original_dns_restored bestaetigen.')
        if read_regular(sftp, live_path, 200_000) != original:
            raise CheckError('Root-Regeln zwischenzeitlich geaendert; Rueckweg gestoppt.')
        atomic_replace(sftp, live_path, previous, token)
        return ['Vorherige Root-Regeln atomar wiederhergestellt.', 'API und DNS unveraendert.']
    verify_known_rules(sftp, root, original)
    manifest = load_release(sftp, root, release)
    if mode == 'check':
        return ['Release-Dateien vollstaendig per SHA256 geprueft.',
                'Root-Regeln und Zugriffsschutz entsprechen dem erwarteten Stand.',
                'Nur gelesen: keine Dateien oder DNS-Eintraege geaendert.']
    if mode != 'activate':
        raise CheckError('Unbekannter Modus.')
    if managed_header(original) and managed_header(original)[0] == release:
        http_verify(ips, manifest)
        return ['Release ist bereits aktiv; HTTP-Pruefung erfolgreich.']
    ensure_directory(sftp, store + '/.backups')
    backup = store + '/.backups/' + token + '.htaccess'
    write_new(sftp, backup, original)
    if read_regular(sftp, backup, len(original)) != original:
        raise CheckError('Root-Sicherung konnte nicht bestaetigt werden.')
    replacement = render_rules(manifest, token)
    if read_regular(sftp, live_path, 200_000) != original:
        raise CheckError('Root-Regeln wurden zwischenzeitlich geaendert; nicht ueberschreiben.')
    # The old root still redirects all storage requests. New root blocks decoded
    # dot paths BEFORE rewriting public URLs, so this guard swap exposes no files.
    if guard == GUARD:
        atomic_replace(sftp, guard_path, ACTIVE_GUARD, token)
    atomic_replace(sftp, live_path, replacement, token)
    try:
        http_verify(ips, manifest)
    except Exception:
        try:
            if read_regular(sftp, live_path, 200_000) != replacement:
                raise CheckError('Root-Regeln extern geaendert.')
            atomic_replace(sftp, live_path, original, token + '0')
        except Exception:
            raise CheckError('HTTP-Pruefung UND automatische Ruecknahme fehlgeschlagen. DNS nicht umstellen; Root-Sicherung in .nic-releases/.backups wiederherstellen.') from None
        raise CheckError('HTTP-Pruefung fehlgeschlagen. Vorherige Root-Regeln automatisch atomar wiederhergestellt; DNS unveraendert.') from None
    return ['Release auf STRATO aktiviert: `' + release + '`.',
            'Startseiten-Inhalt, direkte Routen, Weiterleitung, Zugriffsschutz und API am STRATO-Ziel erfolgreich geprueft.',
            'Root-Sicherung: `.nic-releases/.backups/' + token + '.htaccess`.',
            'DNS NICHT geaendert. www bleibt bis zur manuellen Umstellung auf GitHub Pages.']


def run():
    mode = os.environ.get('STRATO_MODE', 'check')
    if mode not in {'check', 'activate', 'rollback'}:
        raise CheckError('Unbekannter Modus.')
    root = validate_root(os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/'))
    release = validate_release(os.environ.get('STRATO_RELEASE_ID', DEFAULT_RELEASE))
    token = operation_id(os.environ.get('STRATO_OPERATION_ID', ''))
    ips = origin_ips() if mode != 'rollback' else []
    # A rollback must remain available even if the current frontend/TLS is broken.
    lines = preflight(ips) if mode != 'rollback' else []
    import paramiko
    host = validate_host(os.environ.get('STRATO_SFTP_HOST', ''))
    pin = os.environ.get('STRATO_SFTP_FINGERPRINT', '').strip().rstrip('=')
    if not re.fullmatch(r'SHA256:[A-Za-z0-9+/]{43}', pin):
        raise CheckError('Bestaetigter SFTP-Fingerabdruck fehlt.')
    with socket.create_connection((host, 22), timeout=15) as raw:
        transport = paramiko.Transport(raw)
        transport.banner_timeout = 15
        transport.auth_timeout = 15
        try:
            transport.start_client(timeout=20)
            if not hmac.compare_digest(fingerprint(transport.get_remote_server_key()), pin):
                raise CheckError('SFTP-Server-Schluessel abweichend. Keine Zugangsdaten gesendet.')
            username, password = os.environ.get('STRATO_SFTP_USER', ''), os.environ.get('STRATO_SFTP_PASSWORD', '')
            if not username or not password:
                raise CheckError('SFTP-Zugangsdaten fehlen.')
            transport.auth_password(username, password, fallback=False)
            with paramiko.SFTPClient.from_transport(transport) as sftp:
                sftp.get_channel().settimeout(30)
                lines += switch(sftp, root, mode, release, token, ips,
                                os.environ.get('STRATO_ORIGINAL_DNS_RESTORED') == 'true')
        finally:
            transport.close()
    return lines


def main():
    try:
        lines, result = run(), 0
    except ssl.SSLCertVerificationError as exc:
        lines, result = ['Zertifikatspruefung am STRATO-Ziel fehlgeschlagen: ' + exc.verify_message,
                         'Keine Umschaltung. DNS unveraendert.'], 1
    except CheckError as exc:
        lines, result = [str(exc)], 1
    except Exception as exc:
        lines, result = ['Pruefung gestoppt (' + type(exc).__name__ + '). Protokoll und Zielkonfiguration pruefen; DNS nicht umstellen.'], 1
    report = '## STRATO Umschaltung\n\n' + '\n'.join('- ' + line for line in lines) + '\n'
    print(report)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as stream:
            stream.write(report)
    return result


if __name__ == '__main__':
    raise SystemExit(main())
