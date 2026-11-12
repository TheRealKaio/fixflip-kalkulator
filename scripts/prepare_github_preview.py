"""Create a separate, backend-free project Pages preview of the tested build."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import urlsplit

PREFIX = '/fixflip-kalkulator/'


def prepare(source, target):
    if source.resolve() == target.resolve() or source.resolve() in target.resolve().parents:
        raise ValueError('Preview must use a separate output directory')
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
        if path.suffix == '.html':
            text = re.sub(r'<meta\b[^>]*name=["\']robots["\'][^>]*>', '', text, flags=re.I)
            text = re.sub(r'<head\b[^>]*>', lambda m: m[0] + '<meta name="robots" content="noindex,nofollow">', text, count=1, flags=re.I)
        path.write_text(text)
    for hashed in old_assets.values():
        (target / hashed).unlink(missing_ok=True)
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
    args = parser.parse_args()
    prepare(args.source, args.target)
