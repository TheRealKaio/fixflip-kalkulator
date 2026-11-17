"""Publish an immutable release by one atomic root-rules switch, with HTTP rollback."""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import time
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import quote

from strato_activate import (APEX, WWW, atomic_replace, fingerprinted, load_release,
                             managed_header, operation_id, origin_ips, origin_request,
                             preflight, stored_assets, verify_direct_files, verify_known_rules)
from strato_publish import build_manifest, connection, root_backup
from strato_sftp_check import CheckError, inspect_target, validate_root
from strato_stage import STORE, collect_files, read_regular, stage, validate_file, validate_release, write_new


def router_name(release):
    return 'nic-release-' + validate_release(release) + '.php'


def router_bytes(release, preview_token):
    text = Path('server/release-router.php.template').read_text(encoding='utf-8')
    return text.replace('@@RELEASE@@', validate_release(release)).replace(
        '@@PREVIEW_HASH@@', hashlib.sha256(preview_token.encode()).hexdigest()).encode()


def release_rules(manifest, token, router_hash, retained=(), previous_assets=None):
    release = validate_release(manifest['release'])
    operation_id(token)
    if not re.fullmatch('[a-f0-9]{64}', router_hash):
        raise CheckError('Ungueltige Router-Pruefsumme.')
    retained = sorted(set(retained) - set(manifest['files']))
    previous_assets = {name: router for name, router in (previous_assets or {}).items() if name not in manifest['files']}
    if any(not fingerprinted(x) for x in retained):
        raise CheckError('Nur bekannte versionierte Alt-Assets duerfen direkt bleiben.')
    for name, old_router in previous_assets.items():
        if not fingerprinted(name) or not re.fullmatch(r'nic-release-[a-f0-9]{40}-[1-9][0-9]*-[1-9][0-9]*\.php', old_router):
            raise CheckError('Ungueltiger alter Asset-Router.')
    router = router_name(release)
    lines = ['# NIC-RELEASE: ' + release, '# NIC-ROLLBACK: ' + token,
             '# NIC-ATOMIC-RELEASE: v3', '# NIC-ROUTER-SHA256: ' + router_hash]
    lines += ['# NIC-RETAIN-ASSET: ' + name for name in retained]
    lines += ['# NIC-OLD-ROUTER: ' + name for name in sorted(set(previous_assets.values()))]
    lines += ['# NIC-OLD-ASSET: ' + name + ' ' + previous_assets[name] for name in sorted(previous_assets)]
    lines += ['Options -Indexes', 'DirectoryIndex index.html', 'RewriteEngine On', 'RewriteBase /',
              r'RewriteRule ^api(?:/|$) - [L]', r'RewriteRule ^\.well-known(?:/|$) - [L]',
              r'RewriteRule (^|/)\. - [F,END]',
              r'RewriteCond %{HTTP_HOST} !^www\.neustart-immocheck\.de$ [NC]',
              'RewriteRule ^(.*)$ https://' + WWW + '/$1 [R=301,L]',
              'RewriteCond %{HTTPS} !=on',
              'RewriteRule ^(.*)$ https://' + WWW + '/$1 [R=301,L]',
              'RewriteRule ^' + re.escape(router) + '$ - [L]']
    for name in sorted(manifest['files']):
        validate_file(name)
        if name.endswith('.php'):
            continue  # Gate implementation must never be served as source or invoked directly.
        target = router + '?path=' + name + ' [L]'
        if name.endswith('/index.html'):
            directory = name[:-len('/index.html')]
            lines += ['RewriteRule ^' + re.escape(directory) + '$ /' + directory + '/ [R=301,L]',
                      'RewriteRule ^' + re.escape(directory) + '/$ ' + target]
        pattern = r'(?:index\.html)?' if name == 'index.html' else re.escape(name)
        lines.append('RewriteRule ^' + pattern + '$ ' + target)
    lines += ['RewriteRule ^' + re.escape(name) + '$ - [L]' for name in retained]
    lines += ['RewriteRule ^' + re.escape(name) + '$ ' + previous_assets[name] + '?path=' + name + ' [L]' for name in sorted(previous_assets)]
    lines += ['RewriteRule ^' + re.escape(name) + '$ - [L]' for name in sorted(set(previous_assets.values()))]
    lines.append('RewriteRule ^ - [R=404,END]')
    return ('\n'.join(lines) + '\n').encode()


def old_asset_routes(rules):
    return {name.decode(): router.decode() for name, router in
            re.findall(rb'^# NIC-OLD-ASSET: ([^ \r\n]+) ([^ \r\n]+)$', rules, re.M)}


def release_assets(rules):
    # V3 retains only immutable old assets. The V2 helper deliberately excludes
    # these because its old marker described the opposite set of files.
    names = [name.decode() for name in re.findall(rb'^# NIC-RETAIN-ASSET: (.+)$', rules, re.M)]
    if names != sorted(set(names)) or any(not fingerprinted(name) for name in names):
        raise CheckError('Ungueltige versionierte Alt-Assets.')
    return names


def known_release(sftp, root, rules):
    if b'# NIC-ATOMIC-RELEASE: v3\n' not in rules:
        manifest = verify_known_rules(sftp, root, rules)
        if manifest is None:
            raise CheckError('Kein gepruefter STRATO-Rueckweg vorhanden.')
        verify_direct_files(sftp, root, manifest)
        return manifest
    header = managed_header(rules)
    if header is None:
        raise CheckError('Release-Kopf fehlt.')
    manifest = load_release(sftp, root, header[0])
    match = re.search(rb'^# NIC-ROUTER-SHA256: ([a-f0-9]{64})$', rules, re.M)
    if match is None:
        raise CheckError('Router-Pruefsumme fehlt.')
    digest = match[1].decode()
    if hashlib.sha256(read_regular(sftp, root + '/' + router_name(header[0]), 20000)).hexdigest() != digest:
        raise CheckError('Aktiver Router wurde veraendert.')
    if rules != release_rules(manifest, header[1], digest, release_assets(rules), old_asset_routes(rules)):
        raise CheckError('Aktive Regeln wurden extern geaendert.')
    return manifest


def check_live(ips, manifest=None, request=origin_request):
    paths = ['/', '/budget/', '/finanzierungsrechner/', '/eigennutzung/', '/fix-flip/', '/vermietung/']
    for ip in ips:
        for path in paths:
            status, headers, body, _ = request(WWW, ip, path, 'GET')
            if status != 200 or b'data-calculator=' not in body:
                raise CheckError('Live-Pruefung fehlgeschlagen: ' + path + ' HTTP ' + str(status))
            if manifest is not None:
                name = 'index.html' if path == '/' else path.strip('/') + '/index.html'
                check_source(headers, body, manifest, name)
    preflight(ips, request)


def check_source(headers, body, manifest, name):
    expected = manifest['files'][name]['sha256']
    if headers.get('x-nic-release') != manifest['release'] or headers.get('x-nic-source-sha256') != expected:
        raise CheckError('HTTP-Antwort stammt nicht aus der erwarteten Release-Datei: ' + name)
    if name.endswith('.html'):
        if headers.get('x-nic-filtered') != '1' or b'<html' not in body.lower():
            raise CheckError('Serverseitige HTML-Filterung fehlt oder ist fehlgeschlagen.')
    elif hashlib.sha256(body).hexdigest() != expected:
        raise CheckError('Ausgeliefertes Asset stimmt nicht mit dem Release ueberein.')


def raw_text_blocks(html):
    class RawParser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.blocks, self.tag, self.parts = [], None, []
        def handle_starttag(self, tag, attrs):
            if tag in {'script', 'style'}:
                self.tag, self.parts = tag, []
        def handle_data(self, data):
            if self.tag is not None:
                self.parts.append(data)
        def handle_endtag(self, tag):
            if tag == self.tag:
                self.blocks.append((tag, ''.join(self.parts)))
                self.tag, self.parts = None, []
    parser = RawParser()
    parser.feed(html)
    return Counter(parser.blocks)


def check_raw_text(source, output):
    # Disabled sections may remove complete blocks, but no surviving script or
    # style may be rewritten, decoded or HTML-entity-encoded by the server.
    if not raw_text_blocks(output) <= raw_text_blocks(source):
        raise CheckError('Server hat JavaScript- oder CSS-Inhalt bei der HTML-Filterung veraendert.')


def verify_release(ips, manifest, preview_token=None, request=origin_request, source_files=None):
    names = [name for name in manifest['files'] if name.endswith('.html')]
    names += [name for name in manifest['files'] if name.endswith(('.js', '.css', '.json'))]
    for ip in ips:
        for name in names:
            if preview_token:
                path = '/' + router_name(manifest['release']) + '?path=' + quote(name, safe='/')
                response = request(WWW, ip, path, 'GET', preview_token=preview_token)
            else:
                path = '/' if name == 'index.html' else '/' + name[:-10] if name.endswith('/index.html') else '/' + name
                response = request(WWW, ip, path, 'GET')
            status, headers, body, _ = response
            if status != 200:
                raise CheckError('Release-Pruefung fehlgeschlagen: ' + name + ' HTTP ' + str(status))
            check_source(headers, body, manifest, name)
            if source_files is not None and name.endswith('.html'):
                check_raw_text(source_files[name].read_text(encoding='utf-8'), body.decode('utf-8'))
        for path, expected in [('/nic-unknown-page-test/', 404), ('/.nic-releases/' + manifest['release'] + '/.ready.json', 403)]:
            if request(WWW, ip, path)[0] != expected:
                raise CheckError('Unbekannte Pfade oder Release-Speicher nicht geschuetzt.')
    print(('Geschuetzte Vorschau' if preview_token else 'Oeffentlicher Release') + ': HTML, Filterung, JS, CSS und JSON erfolgreich geprueft.', flush=True)


def keep_sftp_alive(sftp, path, request, clock=time.monotonic):
    """Exercise the SFTP channel during long HTTP checks, without retrying writes."""
    last = clock()
    def checked_request(*args, **kwargs):
        nonlocal last
        response = request(*args, **kwargs)
        now = clock()
        if now - last >= 30:
            sftp.lstat(path)
            last = now
        return response
    return checked_request


def restore_interrupted_preview(sftp, root, rules, token, ips, request):
    """Recover only an exact additive preview left by a verified prior operation."""
    try:
        known_release(sftp, root, rules)
        return rules
    except CheckError as failure:
        # The last additive allow-rule identifies the failed operation's backup.
        tail = re.search(rb'(?m)^RewriteRule \^([^\r\n]+)\$ - \[L\]\nRewriteRule \^ - \[R=404,END\]\n$', rules)
        if tail is None:
            raise failure
        name = re.sub(rb'\\(.)', rb'\1', tail[1]).decode('ascii')
        match = re.fullmatch(r'nic-release-([a-f0-9]{40})-([1-9][0-9]*)-([1-9][0-9]*)\.php', name)
        if match is None:
            raise failure
        previous_token = match[2] + '-' + match[3]
        backup = read_regular(sftp, root + '/' + STORE + '/.backups/' + previous_token + '.htaccess', 200000)
        current = known_release(sftp, root, backup)
        allow = ('RewriteRule ^' + re.escape(name) + '$ - [L]\n').encode()
        expected = backup.replace(b'RewriteRule ^ - [R=404,END]\n', allow + b'RewriteRule ^ - [R=404,END]\n')
        if rules != expected:
            raise CheckError('Unterbrochene Vorschau stimmt nicht exakt mit ihrem gesicherten Rueckweg ueberein.')
        check_live(ips, current, request)
        live = root + '/.htaccess'
        root_backup(sftp, root, rules, token + '9')
        if read_regular(sftp, live, 200000) != rules:
            raise CheckError('Root-Regeln waehrend Wiederherstellung extern geaendert.')
        atomic_replace(sftp, live, backup, token + '8')
        check_live(ips, current, request)
        print('Unterbrochene Vorschau entfernt; exakt gesicherter aktiver Release oeffentlich bestaetigt.', flush=True)
        return backup


def publish(sftp, root, files, release, token, ips, request=origin_request, stage_release=stage):
    validate_root(root)
    validate_release(release)
    operation_id(token)
    inspect_target(sftp, root)
    live = root + '/.htaccess'
    original = read_regular(sftp, live, 200000)
    request = keep_sftp_alive(sftp, live, request)
    check_live(ips, request=request)  # Stop before any mutation if the public site is already broken.
    original = restore_interrupted_preview(sftp, root, original, token, ips, request)
    current = known_release(sftp, root, original)
    check_live(ips, current if b'# NIC-ATOMIC-RELEASE: v3\n' in original else None, request)
    print('Bekannter Rueckweg und laufende Website geprueft.', flush=True)
    stage_release(sftp, root, release, files)
    manifest = json.loads(read_regular(sftp, root + '/' + STORE + '/' + release + '/.ready.json', 500000))
    expected, _ = build_manifest(files, release)
    if manifest != expected:
        raise CheckError('Upload-Markierung stimmt nicht mit dem getesteten Build ueberein.')
    secret = secrets.token_hex(32)
    router = router_name(release)
    code = router_bytes(release, secret)
    write_new(sftp, root + '/' + router, code)
    if read_regular(sftp, root + '/' + router, len(code)) != code:
        raise CheckError('Vorschau-Router nicht vollstaendig uebertragen.')
    root_backup(sftp, root, original, token)
    allow = ('RewriteRule ^' + re.escape(router) + '$ - [L]\n').encode()
    preview = original.replace(b'RewriteRule ^ - [R=404,END]\n', allow + b'RewriteRule ^ - [R=404,END]\n')
    if preview == original:
        raise CheckError('Verwaltete Vorschau-Regel kann nicht sicher eingefuegt werden.')
    atomic_previous = b'# NIC-ATOMIC-RELEASE: v3\n' in original
    retained = release_assets(original) if atomic_previous else [name for name in stored_assets(original) if fingerprinted(name)]
    previous_assets = old_asset_routes(original)
    if atomic_previous:
        previous_assets.update({name: router_name(current['release']) for name in current['files'] if fingerprinted(name)})
    else:
        retained += [name for name in current['files'] if fingerprinted(name)]
    final = release_rules(manifest, token, hashlib.sha256(code).hexdigest(), retained, previous_assets)
    if read_regular(sftp, live, 200000) != original:
        raise CheckError('Root-Regeln waehrend Upload extern geaendert; keine Aktivierung.')
    try:
        atomic_replace(sftp, live, preview, token)
        # A caller without the secret cannot inspect the unactivated release.
        for ip in ips:
            if request(WWW, ip, '/' + router + '?path=index.html', 'GET')[0] != 404:
                raise CheckError('Vorschau ist ohne Schluessel erreichbar.')
        verify_release(ips, manifest, secret, request, source_files=files)
        check_live(ips, request=request)  # Adding preview access must leave old public pages working.
        if read_regular(sftp, live, 200000) != preview:
            raise CheckError('Root-Regeln waehrend Vorschau extern geaendert.')
        atomic_replace(sftp, live, final, token + '1')
        check_live(ips, manifest, request)
        verify_release(ips, manifest, request=request, source_files=files)
    except Exception as failure:
        active = read_regular(sftp, live, 200000)
        if active not in {original, preview, final}:
            raise CheckError('Regeln extern geaendert; automatischer Rueckweg gestoppt.') from failure
        atomic_replace(sftp, live, original, token + '0')
        try:
            check_live(ips, current if b'# NIC-ATOMIC-RELEASE: v3\n' in original else None, request)
        except Exception as rollback_failure:
            raise CheckError('Rueckweg ausgefuehrt, aber Live-Pruefung fehlgeschlagen. Sofort pruefen: ' + str(rollback_failure)) from failure
        raise CheckError('Veroeffentlichung gestoppt; vorheriger Release per HTTP wieder bestaetigt: ' + str(failure)) from failure
    return ['Release `' + release + '` vollstaendig aktiviert und oeffentlich geprueft.',
            'HTML-Quelldatei, serverseitige Filterung und ausgelieferte Assets bestaetigt.',
            'Aktivierung: ein atomarer Regeltausch; keine laufenden Frontend-Dateien ueberschrieben.',
            'Gepruefter Rueckweg: `.nic-releases/.backups/' + token + '.htaccess`.']


def main():
    try:
        token = operation_id(os.environ['STRATO_OPERATION_ID'])
        root = validate_root(os.environ.get('STRATO_SFTP_ROOT', '/immocheck-web').rstrip('/'))
        ips = origin_ips()
        if os.environ.get('STRATO_MODE', 'publish') == 'rollback':
            with connection() as sftp:
                live = root + '/.htaccess'
                original = read_regular(sftp, live, 200000)
                header = managed_header(original)
                if header is None or b'# NIC-ATOMIC-RELEASE: v3\n' not in original:
                    raise CheckError('Kein atomarer Release mit gespeichertem Rueckweg aktiv.')
                previous = read_regular(sftp, root + '/' + STORE + '/.backups/' + header[1] + '.htaccess', 200000)
                manifest = known_release(sftp, root, previous)
                root_backup(sftp, root, original, token)
                if read_regular(sftp, live, 200000) != original:
                    raise CheckError('Regeln extern geaendert; Rueckweg gestoppt.')
                atomic_replace(sftp, live, previous, token)
                check_live(ips, manifest if b'# NIC-ATOMIC-RELEASE: v3\n' in previous else None)
                lines = ['Vorheriger Release atomar wiederhergestellt und per HTTP bestaetigt.']
        else:
            files = collect_files(Path(os.environ.get('STRATO_SITE', '_site')))
            release = validate_release(os.environ['STRATO_RELEASE_ID'])
            preflight(ips)
            with connection() as sftp:
                lines = publish(sftp, root, files, release, token, ips)
        result = 0
    except Exception as error:
        lines, result = [str(error) if isinstance(error, CheckError) else type(error).__name__ + ': ' + str(error)], 1
    report = '## STRATO atomare Veroeffentlichung\n\n' + '\n'.join('- ' + line for line in lines) + '\n'
    print(report, flush=True)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as stream:
            stream.write(report)
    return result


if __name__ == '__main__':
    raise SystemExit(main())
