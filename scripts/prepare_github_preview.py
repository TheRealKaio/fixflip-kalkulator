"""Create a separate, backend-free project Pages preview of the tested build."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit
from urllib.request import urlopen

PREFIX = '/fixflip-kalkulator/'
PUBLIC_SETTINGS = 'https://neustart-immocheck.de/api/index.php?r=settings'


def public_layout(defaults, opener=urlopen):
    # Public GET only, during build; never authenticate or enable the browser API.
    with opener(PUBLIC_SETTINGS, timeout=25) as response:
        payload = response.read(2_000_001)
    if len(payload) > 2_000_000:
        raise ValueError('Public settings response too large')
    layout = json.loads(payload)['settings']['layout']
    result = {}
    for key, default in defaults.items():
        value = layout[key]
        if key == 'font':
            valid = value in {'system','arial','verdana','georgia','trebuchet'}
        elif isinstance(default, (int, float)):
            valid = type(value) in {int,float} and (0 if key == 'cornerRadius' else 10) <= value <= (40 if key == 'cornerRadius' else 72)
        else:
            valid = isinstance(value,str) and (bool(re.fullmatch(r'#[0-9a-fA-F]{6}',value)) or (key.endswith('Text') and value == 'AUTO'))
        if not valid:
            raise ValueError('Invalid public layout field: ' + key)
        result[key] = value
    return result


def prepare(source, target, live_layout=False):
    if source.resolve() == target.resolve() or source.resolve() in target.resolve().parents:
        raise ValueError('Preview must use a separate output directory')
    layout = None
    if live_layout:
        bundled = json.loads((source / 'site-settings.json').read_text())
        layout = public_layout(bundled['layout'])
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('CNAME', '_checks'))

    old_assets = json.loads((source / ".asset-manifest.json").read_text())

    def local(value):
        if not value.startswith('/') or value.startswith('//') or value.startswith(PREFIX):
            return False
        path = urlsplit(value.rstrip('\\')).path
        return path != '/' and (source / path.lstrip('/')).exists()

    def rewrite(text):
        # Restrict rewriting to paths that really belong to this static build.
        # Do not change URL schemes, external URLs, regexes or split('/') calls.
        text = re.sub(r'''(["'`])(/[^\s"'`<>]*)''',
                      lambda m: m[1] + PREFIX.rstrip('/') + m[2] if local(m[2]) or (m[2].startswith('/#')) else m[0], text)
        text = re.sub(r'''(url\(\s*)(/[^)\s]+)''',
                      lambda m: m[1] + PREFIX.rstrip('/') + m[2] if local(m[2]) else m[0], text)
        text = re.sub(r'''(<base\s+href=["'])/(["'])''', r'\g<1>' + PREFIX + r'\2', text)
        text = re.sub(r'''(new URL\(\s*["'])/(["']\s*,)''', r'\g<1>' + PREFIX + r'\2', text)
        text = text.replace("routes['/']", "routes['" + PREFIX + "']")
        return text

    for path in target.rglob('*'):
        if path.suffix.lower() not in {'.html', '.js', '.css', '.json', '.webmanifest'}:
            continue
        text = path.read_text()
        for original, hashed in old_assets.items():
            text = text.replace(hashed, original)
        text = rewrite(text)
        # The brand link must stay inside this preview, including after settings apply.
        if path.name == 'site-settings.js':
            needle = 'link.href=websiteUrl(website)||ROOT.href'
            if text.count(needle) != 2:
                raise ValueError('Preview logo hook changed; review brand navigation')
            text = text.replace(needle, 'link.href=ROOT.href')
        if path.suffix == '.html':
            if layout is not None:
                def bootstrap(match):
                    settings = json.loads(match[2])
                    settings['layout'] = layout
                    return match[1] + json.dumps(settings, ensure_ascii=True).replace('<', r'\u003c') + match[3]
                text = re.sub(r'(<script\b[^>]*id="nic-published-settings"[^>]*>)(.*?)(</script>)', bootstrap, text, flags=re.S)
            text = re.sub(r'(<a\b[^>]*class="nic-logo-link"[^>]*href=")[^"]*(")', r'\g<1>' + PREFIX + r'\2', text)
            text = re.sub(r'<meta\b[^>]*name=["\']robots["\'][^>]*>', '', text, flags=re.I)
            text = re.sub(r'<head\b[^>]*>', lambda m: m[0] + '<meta name="robots" content="noindex,nofollow">', text, count=1, flags=re.I)
        path.write_text(text)
    for hashed in old_assets.values():
        (target / hashed).unlink(missing_ok=True)
    if layout is not None:
        settings_path = target / 'site-settings.json'
        settings = json.loads(settings_path.read_text())
        settings['layout'] = layout
        settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + '\n')
        print('Public layout snapshot: body=' + str(layout['bodySize']) + 'px, h1=' + str(layout['h1']) + 'px; preview content preserved.')
    (target / 'backend-config.json').write_text(json.dumps({'enabled': False, 'apiUrl': ''}) + '\n')
    (target / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    (target / 'sitemap.xml').unlink(missing_ok=True)
    # Project-scope worker never clears caches belonging to other GitHub projects.
    (target / 'service-worker.js').write_text('self.addEventListener("install",()=>self.skipWaiting());\nself.addEventListener("activate",e=>e.waitUntil(self.registration.unregister()));\n')
    subprocess.run([sys.executable, str(Path(__file__).with_name('fingerprint_assets.py')), str(target)], check=True)
    print('GitHub preview prepared at ' + str(target) + PREFIX + '; production backend disabled.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('_site'))
    parser.add_argument('--target', type=Path, default=Path('_preview'))
    parser.add_argument('--live-layout', action='store_true', help='Snapshot only public layout values at build time')
    args = parser.parse_args()
    prepare(args.source, args.target, live_layout=args.live_layout)
