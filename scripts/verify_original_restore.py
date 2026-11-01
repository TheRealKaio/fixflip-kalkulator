"""Verify original backup structure with branding only; do not alter calculator behavior."""
from pathlib import Path
from PIL import Image
import subprocess
root=Path('_site')
backup='0ef48e3faf53704bcdd52b8440da0777d81cbcbd'
# This comparison runs when Git history is available; CI uses a full checkout.
for name in [*map(str,Path('source').glob('*')),'assets/financing.html','assets/pdf-reports.js','assets/user-access.js']:
    expected=subprocess.check_output(['git','show',backup+':'+name])
    assert Path(name).read_bytes()==expected, 'Backup source changed: '+name
for name in ['header-logo.png','apple-touch-icon.png','favicon-64.png','share-logo.png']:
    with Image.open(root/name) as im:im.load()
for slug in ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']:
    html=(root/slug/'index.html').read_text()
    assert '/header-logo.png' in html,slug
    assert 'immocheck-brand-theme' in html,slug
    assert 'immocheck-ui-steps' not in html and 'immocheck-ui-refresh' not in html,slug
assert (root/'immocheck-hero.jpg').read_bytes()==Path('assets/immocheck-hero.jpg').read_bytes()
print('Original backup sources, five original calculator routes and retained brand assets verified.')
