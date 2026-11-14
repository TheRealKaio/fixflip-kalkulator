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
                          existing, read_regular, validate_file, validate_release, write_new)

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


def origin_request(host, ip, path='/', method='HEAD', limit=12_000_000, preview_release=None):
    if host not in {APEX, WWW} or not ipaddress.ip_address(ip).is_global or method not in {'GET', 'HEAD'}:
        raise CheckError('Unerwartetes HTTP-Pruefziel.')
    context = ssl.create_default_context()
    preview_header = ''
    if preview_release is not None:
        validate_release(preview_release)
        if host != APEX:
            raise CheckError('Technische Origin-Pruefung nur auf der Hauptdomain erlaubt.')
        preview_header = 'X-NIC-Origin-Release: ' + preview_release + '\r\n'
    # Mandatory trusted chain, time validity AND hostname verification via SNI.
    with socket.create_connection((ip, 443), timeout=20) as raw:
        with context.wrap_socket(raw, server_hostname=host) as tls:
            certificate = tls.getpeercert()
            tls.sendall((method + ' ' + path + ' HTTP/1.1\r\nHost: ' + host
                         + '\r\n' + preview_header + 'Accept-Encoding: identity\r\nConnection: close\r\n\r\n').encode('ascii'))
            response = http.client.HTTPResponse(tls, method=method)
            response.begin()
            body = response.read(limit + 1)
            if len(body) > limit:
                raise CheckError('HTTP-Pruefantwort ist unerwartet gross.')
            return response.status, dict((k.lower(), v) for k, v in response.getheaders()), body, certificate


def preflight(ips, request=origin_request, require_www=True):
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
            message = 'www-Verzeichniszuordnung zu immocheck-web noch offen (API HTTP ' + str(status) + ').'
            if require_www:
                raise CheckError(message + ' Aktivierung gesperrt. Fuer den ersten Umzug zuerst prepare ohne DNS-Aenderung ausfuehren, danach www intern zuordnen und activate pruefen.')
            lines.append(message + ' Nur Vorbereitung moeglich; keine Freigabe fuer den oeffentlichen www-Betrieb.')
    return lines


def load_release(sftp, root, release, contents=None):
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
        if contents is not None:
            contents[name] = payload
    config = json.loads(read_regular(sftp, target + '/backend-config.json', 4096))
    if config.get('enabled') is not True or config.get('apiUrl') != 'https://' + APEX + '/api/index.php':
        raise CheckError('Release verwendet eine abweichende API-Konfiguration.')
    return manifest


def fingerprinted(name):
    return bool(re.fullmatch(r'[A-Za-z0-9_-][A-Za-z0-9_.-]*\.[a-f0-9]{16}\.(?:js|css)', name))


def retained_assets(*collections):
    result = set()
    for names in collections:
        for name in names:
            validate_file(name)
            if not name.endswith('.html') and not fingerprinted(name):
                result.add(name)
    return sorted(result)


def direct_version(payload):
    match = re.search(rb'^# NIC-DIRECT-FILES: v([12])$', payload, re.M)
    return int(match[1]) if match else 0


def stored_assets(payload):
    names = [x.decode('ascii') for x in re.findall(rb'^# NIC-RETAIN-ASSET: (.+)$', payload, re.M)]
    if len(names) > 1000 or retained_assets(names) != names:
        raise CheckError('Ungueltige gespeicherte Frontend-Assetliste.')
    return names


def render_rules(manifest, backup, direct=False, version=1, retained=()):
    release = validate_release(manifest['release'])
    operation_id(backup)
    if version not in {1, 2}:
        raise CheckError('Unbekannte Auslieferungsversion.')
    assets = retained_assets(retained) if direct and version == 2 else []
    redirect = '301' if direct and version == 2 else '302'
    files = set(manifest['files']) | set(assets)
    rules = ['# NIC-RELEASE: ' + release, '# NIC-ROLLBACK: ' + backup,
             'Options -Indexes', 'DirectoryIndex index.html', 'RewriteEngine On',
             # STRATO maps a domain to an internal webspace subdirectory.
             # Keep relative release substitutions rooted at the public URL /.
             'RewriteBase /',
             'RewriteRule ^api(?:/|$) - [L]',
             'RewriteRule ^\\.well-known(?:/|$) - [L]',
             # Apache matches decoded paths, including encoded dot characters.
             'RewriteRule (^|/)\\. - [F,END]',
             # A diagnostic header allows exact content checks on the already
             # mapped apex before www DNS/webspace changes. No auth bypass:
             # API exclusions and hidden-path blocks above always apply first.
             'RewriteCond %{HTTP_HOST} ^neustart-immocheck\\.de$ [NC]',
             'RewriteCond %{HTTPS} =on',
             'RewriteCond %{HTTP:X-NIC-Origin-Release} ^' + re.escape(release) + '$',
             'RewriteRule ^ - [E=NIC_ORIGIN_PREVIEW:1]',
             '<IfModule mod_headers.c>',
             'Header always merge Vary X-NIC-Origin-Release',
             'Header always set Cache-Control "no-store" "expr=req(\'X-NIC-Origin-Release\') == \'' + release + '\'"',
             'Header always set X-Robots-Tag "noindex, nofollow" "expr=req(\'X-NIC-Origin-Release\') == \'' + release + '\'"',
             '</IfModule>',
             'RewriteCond %{HTTP_HOST} !^www\\.neustart-immocheck\\.de$ [NC]',
             'RewriteCond %{ENV:NIC_ORIGIN_PREVIEW} !=1',
             'RewriteRule ^(.*)$ https://' + WWW + '/$1 [R=' + redirect + ',L]',
             'RewriteCond %{HTTPS} !=on',
             'RewriteRule ^(.*)$ https://' + WWW + '/$1 [R=' + redirect + ',L]']
    if direct:
        rules.insert(2, '# NIC-DIRECT-FILES: v' + str(version))
        if version == 2:
            rules[3:3] = ['# NIC-RETAIN-ASSET: ' + name for name in assets]
            # Immutable, content-hashed assets are installed before entry pages.
            # Keep both old and new hashes addressable during deploy/rollback.
            rules.append(r'RewriteRule ^[A-Za-z0-9_-][A-Za-z0-9_.-]*\.[a-f0-9]{16}\.(?:js|css)$ - [L]')
    server_gate = direct and 'content-gate.php' in files
    if server_gate:
        # Keep PHP endpoint directly executable and route every public HTML
        # document through it so disabled sections are removed before delivery.
        rules.append(r'RewriteRule ^content-gate\.php$ - [L]')
    for name in sorted(files):
        validate_file(name)
        if name.endswith('/index.html'):
            directory = name[:-len('/index.html')]
            target = ('/content-gate.php?path=' + name + ' [END,QSA]'
                      if server_gate else ('- [L]' if direct else STORE + '/' + release + '/' + name + ' [END]'))
            rules += ['RewriteRule ^' + re.escape(directory) + '$ /' + directory + '/ [R=' + redirect + ',L]',
                      'RewriteRule ^' + re.escape(directory) + '/$ ' + target]
        pattern = '(?:index\\.html)?' if name == 'index.html' else re.escape(name)
        if server_gate and name.endswith('.html'):
            target = '/content-gate.php?path=' + name + ' [END,QSA]'
        else:
            target = '- [L]' if direct else STORE + '/' + release + '/' + name + ' [END]'
        rules.append('RewriteRule ^' + pattern + '$ ' + target)
    rules.append('RewriteRule ^ - [R=404,END]')
    return ('\n'.join(rules) + '\n').encode()


def managed_header(payload):
    match = re.match(rb'# NIC-RELEASE: ([a-f0-9]{40}-[1-9][0-9]*-[1-9][0-9]*)\n# NIC-ROLLBACK: ([1-9][0-9]*-[1-9][0-9]*)\n', payload)
    return (match[1].decode(), match[2].decode()) if match else None


def direct_delivery(payload):
    return bool(direct_version(payload))


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
    if render_rules(manifest, header[1], direct=direct_delivery(payload), version=direct_version(payload) or 1, retained=stored_assets(payload)) != payload:
        raise CheckError('Verwaltete Root-.htaccess wurde ausserhalb des Workflows geaendert.')
    return manifest


def atomic_replace(sftp, path, payload, token):
    operation_id(token)
    temporary = path + '.next-' + token
    write_new(sftp, temporary, payload)
    if read_regular(sftp, temporary, len(payload)) != payload:
        raise CheckError('Vorbereiteter Dateitausch konnte nicht verifiziert werden.')
    # No delete+rename fallback. A failure must leave the old file in place.
    sftp.posix_rename(temporary, path)


def path_parents(sftp, base, name):
    validate_file(name)
    current = base
    for part in name.split('/')[:-1]:
        current += '/' + part
        ensure_directory(sftp, current)


def backup_direct_files(sftp, root, manifest, token):
    """Save every overwritten public file BEFORE any replacement."""
    operation_id(token)
    snapshot = {'operation': token, 'changes': {}}
    backup_base = root + '/' + STORE + '/.backups/' + token + '.files'
    for name, meta in manifest['files'].items():
        validate_file(name)
        path_parents(sftp, root, name)
        live = root + '/' + name
        entry = existing(sftp, live)
        previous_hash = None
        if entry is not None:
            previous = read_regular(sftp, live, 12_000_000)
            previous_hash = hashlib.sha256(previous).hexdigest()
            if previous_hash == meta['sha256']:
                continue
            ensure_directory(sftp, backup_base)
            path_parents(sftp, backup_base, name)
            write_new(sftp, backup_base + '/' + name, previous)
            if read_regular(sftp, backup_base + '/' + name, len(previous)) != previous:
                raise CheckError('Frontend-Sicherung konnte nicht bestaetigt werden.')
        snapshot['changes'][name] = {'previous': previous_hash, 'installed': meta['sha256']}
    write_new(sftp, root + '/' + STORE + '/.backups/' + token + '.files.json',
              (json.dumps(snapshot, indent=2) + '\n').encode())
    return snapshot


def install_direct_files(sftp, root, snapshot, contents, token, names=None):
    selected = list(snapshot['changes']) if names is None else list(names)
    if not set(selected).issubset(snapshot['changes']):
        raise CheckError('Unerwartete Datei ausserhalb der gesicherten Aenderungsliste.')
    for number, name in enumerate(selected, 1):
        live = root + '/' + name
        entry = snapshot['changes'][name]
        present = existing(sftp, live)
        digest = hashlib.sha256(read_regular(sftp, live, 12_000_000)).hexdigest() if present is not None else None
        if digest != entry['previous']:
            raise CheckError('Frontend-Datei zwischen Sicherung und Uebertragung geaendert; nicht ueberschreiben.')
        atomic_replace(sftp, root + '/' + name, contents[name], token)
        if number % 20 == 0 or number == len(selected):
            print('Frontend-Dateien atomar bereitgestellt: ' + str(number) + '/' + str(len(selected)), flush=True)


def restore_direct_files(sftp, root, token, preserve_assets=False):
    operation_id(token)
    base = root + '/' + STORE + '/.backups/' + token + '.files'
    snapshot = json.loads(read_regular(sftp, base + '.json', 500_000))
    if snapshot.get('operation') != token or len(snapshot.get('changes', {})) > 1000:
        raise CheckError('Ungueltige Frontend-Sicherung.')
    for name, entry in snapshot['changes'].items():
        validate_file(name)
        for value in [entry.get('installed'), entry.get('previous')]:
            if value is not None and not re.fullmatch('[a-f0-9]{64}', value):
                raise CheckError('Ungueltige Sicherungspruefsumme.')
        path_parents(sftp, root, name)
        live = root + '/' + name
        current = existing(sftp, live)
        if current is None and entry['previous'] is None:
            continue
        digest = hashlib.sha256(read_regular(sftp, live, 12_000_000)).hexdigest() if current is not None else None
        if digest == entry['previous']:
            continue
        if digest not in {None, entry['installed']}:
            raise CheckError('Frontend-Datei extern geaendert; nicht automatisch loeschen oder ueberschreiben.')
        if entry['previous'] is None:
            if current is not None and not (preserve_assets and not name.endswith('.html')):
                sftp.remove(live)  # Only an unchanged file created by this operation.
        else:
            real_directory(sftp, base)
            previous = read_regular(sftp, base + '/' + name, 12_000_000)
            if hashlib.sha256(previous).hexdigest() != entry['previous']:
                raise CheckError('Frontend-Sicherung hat eine abweichende Pruefsumme.')
            atomic_replace(sftp, live, previous, token + '0')


def verify_direct_files(sftp, root, manifest):
    for name, meta in manifest['files'].items():
        validate_file(name)
        parent = root
        for part in name.split('/')[:-1]:
            parent += '/' + part
            real_directory(sftp, parent)
        data = read_regular(sftp, root + '/' + name, meta['bytes'])
        if hashlib.sha256(data).hexdigest() != meta['sha256']:
            raise CheckError('Oeffentliche Frontend-Dateien stimmen nicht mit dem Release ueberein.')


def verify_http(ips, manifest, request=origin_request, preparation=False):
    release = manifest['release']
    host = APEX if preparation else WWW
    def frontend(ip, path='/', method='HEAD'):
        if preparation:
            result = request(host, ip, path, method, preview_release=release)
        else:
            result = request(host, ip, path, method)
        print('Origin-Test: ' + host + path + ' -> HTTP ' + str(result[0]), flush=True)
        return result
    for ip in ips:
        status, _, body, _ = frontend(ip, '/', 'GET')
        if status != 200 or hashlib.sha256(body).hexdigest() != manifest['files']['index.html']['sha256']:
            raise CheckError('Startseiten-Test: HTTP ' + str(status) + '; erwarteter Release-Inhalt fehlt.')
        for name in manifest['files']:
            if name.endswith('/index.html'):
                path = '/' + name[:-len('index.html')]
                status, _, _, _ = frontend(ip, path)
                if status != 200:
                    raise CheckError('Direkter Aufruf ' + path + ': HTTP ' + str(status) + '.')
        for path in ['/service-worker.js', '/backend-config.json']:
            if frontend(ip, path)[0] != 200:
                raise CheckError('Zentrales Frontend-Asset nicht erreichbar.')
        for path, expected in [('/nic-unknown-page-test/', 404), ('/.' + 'nic-releases/' + release + '/.ready.json', 403)]:
            if frontend(ip, path)[0] != expected:
                raise CheckError('Unbekannte Pfade oder Release-Schutz funktionieren nicht wie erwartet.')
        status, headers, _, _ = request(APEX, ip, '/budget/?nic=check')
        if status not in {301, 302} or headers.get('location') != 'https://' + WWW + '/budget/?nic=check':
            raise CheckError('Canonical-Weiterleitung bewahrt Pfad und Query nicht korrekt.')
    preflight(ips, request, require_www=not preparation)


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
        previous_manifest = verify_known_rules(sftp, root, previous)
        if legacy_rules(previous) and not dns_restored:
            raise CheckError('Erster Rueckweg fuehrt zu GitHub: zuerst www-DNS zuruecksetzen und original_dns_restored bestaetigen.')
        if read_regular(sftp, live_path, 200_000) != original:
            raise CheckError('Root-Regeln zwischenzeitlich geaendert; Rueckweg gestoppt.')
        if direct_version(original) == 2 and direct_delivery(previous):
            # Restore pages while both asset generations remain addressable.
            restore_direct_files(sftp, root, header[1], preserve_assets=True)
            previous_header = managed_header(previous)
            previous = render_rules(previous_manifest, previous_header[1], direct=True, version=2,
                                    retained=retained_assets(stored_assets(previous), stored_assets(original), previous_manifest['files']))
            atomic_replace(sftp, live_path, previous, token)
        else:
            atomic_replace(sftp, live_path, previous, token)
            if direct_delivery(original) and legacy_rules(previous):
                restore_direct_files(sftp, root, header[1])
        return ['Vorherige Root-Regeln atomar wiederhergestellt.', 'API und DNS unveraendert.']
    known = verify_known_rules(sftp, root, original)
    current_header = managed_header(original)
    if direct_delivery(original):
        if current_header[0] != release:
            raise CheckError('Folge-Deployment: Einen anderen Release mit dem Workflow STRATO automatisch veroeffentlichen aus main bauen und ausliefern.')
    contents = {} if mode == 'prepare' and legacy_rules(original) else None
    manifest = known if known is not None and known['release'] == release and contents is None else load_release(sftp, root, release, contents=contents)
    if direct_delivery(original):
        verify_direct_files(sftp, root, manifest)
    if mode == 'check':
        return ['Release-Dateien vollstaendig per SHA256 geprueft.',
                'Root-Regeln und Zugriffsschutz entsprechen dem erwarteten Stand.',
                'Nur gelesen: keine Dateien oder DNS-Eintraege geaendert.']
    if mode not in {'prepare', 'activate'}:
        raise CheckError('Unbekannter Modus.')
    if mode == 'prepare' and current_header and current_header[0] != release:
        raise CheckError('prepare ist nur fuer den ersten Umzug vorgesehen. Spaetere Releases mit activate umschalten.')
    if managed_header(original) and managed_header(original)[0] == release:
        http_verify(ips, manifest)
        return ['Release ist vorbereitet; Hauptdomain-HTTP-Test erfolgreich. www-Zuordnung und activate stehen noch aus.'] if mode == 'prepare' else ['Release ist bereits aktiv; www-HTTP-Pruefung erfolgreich.']
    ensure_directory(sftp, store + '/.backups')
    backup = store + '/.backups/' + token + '.htaccess'
    write_new(sftp, backup, original)
    if read_regular(sftp, backup, len(original)) != original:
        raise CheckError('Root-Sicherung konnte nicht bestaetigt werden.')
    use_direct = mode == 'prepare' and legacy_rules(original)
    snapshot = backup_direct_files(sftp, root, manifest, token) if use_direct else None
    replacement = render_rules(manifest, token, direct=use_direct)
    if read_regular(sftp, live_path, 200_000) != original:
        raise CheckError('Root-Regeln wurden zwischenzeitlich geaendert; nicht ueberschreiben.')
    # The old root still redirects all storage requests. New root blocks decoded
    # dot paths BEFORE rewriting public URLs, so this guard swap exposes no files.
    try:
        if use_direct:
            install_direct_files(sftp, root, snapshot, contents, token)
            if read_regular(sftp, live_path, 200_000) != original:
                raise CheckError('Root-Regeln waehrend der Erstbereitstellung extern geaendert.')
        elif guard == GUARD:
            atomic_replace(sftp, guard_path, ACTIVE_GUARD, token)
        atomic_replace(sftp, live_path, replacement, token)
        http_verify(ips, manifest)
    except Exception as failure:
        try:
            current = read_regular(sftp, live_path, 200_000)
            if current not in {replacement, original}:
                raise CheckError('Root-Regeln extern geaendert.')
            if current == replacement:
                atomic_replace(sftp, live_path, original, token + '0')
            if snapshot is not None:
                restore_direct_files(sftp, root, token)
        except Exception:
            raise CheckError('Bereitstellung UND vollstaendige automatische Ruecknahme fehlgeschlagen. DNS nicht umstellen; Sicherungen in .nic-releases/.backups pruefen.') from None
        reason = str(failure) if isinstance(failure, CheckError) else type(failure).__name__
        raise CheckError('Bereitstellung fehlgeschlagen (' + reason + '). Vorherige Root-Regeln automatisch atomar wiederhergestellt; Frontend-Dateien zurueckgenommen; DNS unveraendert.') from None
    if mode == 'prepare':
        return ['STRATO-Release vor der DNS-Umstellung bereitgestellt: `' + release + '`.',
                'Startseiten-Hash, direkte Routen, API, Schutz und Canonical ueber die Hauptdomain erfolgreich geprueft.',
                'Normale Hauptdomain-Aufrufe leiten weiterhin nach www; DNS unveraendert.',
                'Root-Sicherung: `.nic-releases/.backups/' + token + '.htaccess`.',
                'Naechster Schritt: www-CNAME auf STRATO-Standard zuruecksetzen und www intern auf /immocheck-web zuordnen. Danach activate ausfuehren.']
    return ['Release auf STRATO aktiviert: `' + release + '`.',
            'Startseiten-Inhalt, direkte Routen, Weiterleitung, Zugriffsschutz und API am STRATO-Ziel erfolgreich geprueft.',
            'Root-Sicherung: `.nic-releases/.backups/' + token + '.htaccess`.',
            'DNS NICHT geaendert. www bleibt bis zur manuellen Umstellung auf GitHub Pages.']


def run():
    mode = os.environ.get('STRATO_MODE', 'check')
    if mode not in {'check', 'prepare', 'activate', 'rollback'}:
        raise CheckError('Unbekannter Modus.')
    root = validate_root(os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/'))
    requested_release = os.environ.get('STRATO_RELEASE_ID', 'current')
    release = None if requested_release == 'current' else validate_release(requested_release)
    token = operation_id(os.environ.get('STRATO_OPERATION_ID', ''))
    ips = origin_ips() if mode != 'rollback' else []
    # A rollback must remain available even if the current frontend/TLS is broken.
    lines = preflight(ips, require_www=mode == 'activate') if mode != 'rollback' else []
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
                if release is None:
                    inspect_target(sftp, root)
                    active = managed_header(read_regular(sftp, root + '/.htaccess', 200_000))
                    if active is None:
                        raise CheckError('Noch kein aktiver Release. Fuer die Erstbereitstellung eine konkrete Release-ID angeben.')
                    release = active[0]
                lines += switch(sftp, root, mode, release, token, ips,
                                os.environ.get('STRATO_ORIGINAL_DNS_RESTORED') == 'true',
                                http_verify=(lambda addresses, manifest: verify_http(addresses, manifest, preparation=True)) if mode == 'prepare' else verify_http)
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
