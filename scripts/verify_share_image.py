"""Check crawler-visible image metadata and regeneration from editable settings."""
from pathlib import Path
import base64
import re
import tempfile
from PIL import Image
from render_share_image import render_share_image

site=Path('_site')
for page in [site/'index.html',*(site/name/'index.html' for name in ['budget','eigennutzung','vermietung','fix-flip','unternehmen','impressum'])]:
    source=page.read_text()
    matches=re.findall(r'<meta property="og:image" content="([^"]+)">',source)
    assert len(matches)==1,page
    assert matches[0].startswith('https://www.neustart-immocheck.de/social-preview-'),page
    image=site/matches[0].rsplit('/',1)[1]
    with Image.open(image) as im:assert im.size==(1200,630)
    assert image.stat().st_size<300000
    assert '<meta name="twitter:card" content="summary_large_image">' in source
with tempfile.TemporaryDirectory() as folder:
    first=render_share_image({'sharing':{'text':'Erster Satz'}},folder)
    second=render_share_image({'sharing':{'text':'Geänderter Satz'}},folder)
    assert first!=second,'Text changes must invalidate the image URL'
    custom='data:image/png;base64,'+base64.b64encode(Path('assets/apple-touch-icon.png').read_bytes()).decode()
    third=render_share_image({'sharing':{'text':'Geänderter Satz','image':custom}},folder)
    assert third!=second,'Uploaded motif must be rendered'
    render_share_image({'sharing':{'text':'W '*80}},folder)
print('Sharing image checks passed: seven static pages, public JPEG URL, dimensions, small payload, editable text and custom image regeneration.')
