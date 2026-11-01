"""Validate built brand assets and routes without changing calculator logic."""
from pathlib import Path
from PIL import Image
import re
site=Path('_site')
for name in ['header-logo.png','brand-icon.png','apple-touch-icon.png','favicon-64.png','share-logo.png']:
    with Image.open(site/name) as im: im.load()
for name,size in [('apple-touch-icon.png',(180,180)),('favicon-64.png',(64,64)),('share-logo.png',(800,300))]:
    with Image.open(site/name) as im:
        assert im.size==size,(name,im.size)
        rgb=im.convert('RGB')
        assert rgb.getpixel((0,0))==(255,255,255),name
        assert any(r>170 and g>100 and b<90 for r,g,b in rgb.getdata()),'Yellow wave missing: '+name
for slug in ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']:
    html=(site/slug/'index.html').read_text()
    assert 'src="/header-logo.png"' in html,slug
    assert 'href="/icon.svg"' in html and 'apple-touch-icon' in html,slug
    assert 'user-scalable=no' not in html,slug
    assert 'immocheck-ui-refresh' in html,slug
    meta=re.search(r'<meta property="og:image" content="([^"]+)"',html)
    assert meta,slug
    with Image.open(site/meta[1].rsplit('/',1)[-1]) as im:assert im.size==(1200,630)
print('Approved logo, yellow wave, white background, favicon, Apple, social and five routes passed.')
