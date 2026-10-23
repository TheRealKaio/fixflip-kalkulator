"""Give local script/style resources a content-specific URL on every page."""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import re
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
manifest={}
for asset in sorted(site.iterdir()):
    if asset.suffix not in {'.js','.css'} or asset.name=='service-worker.js' or re.search(r'\.[a-f0-9]{16}\.(js|css)$',asset.name):
        continue
    payload=asset.read_bytes()
    digest=hashlib.sha256(payload).hexdigest()[:16]
    hashed=f'{asset.stem}.{digest}{asset.suffix}'
    (site/hashed).write_bytes(payload)
    manifest[asset.name]=hashed
pattern=re.compile(r'''\b(src|href)=(['"])([^'"]+)\2''')
for page in site.rglob('*.html'):
    def rewrite(match):
        attr,quote,value=match.groups()
        parts=urlsplit(value)
        name=Path(parts.path).name
        if parts.scheme or parts.netloc or name not in manifest:
            return match.group(0)
        new=parts.path[:-len(name)]+manifest[name]
        if parts.fragment:
            new+='#'+parts.fragment
        return f'{attr}={quote}{new}{quote}'
    page.write_text(pattern.sub(rewrite,page.read_text()))
(site/'.asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Fingerprinting applied to {len(manifest)} assets on all public and admin pages')
