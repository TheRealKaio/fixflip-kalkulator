"""Build brand variants from the approved house/four-window/yellow-wave logo."""
from pathlib import Path
import base64
from PIL import Image, ImageOps
ASSETS = Path(__file__).resolve().parent.parent / 'assets'
def run(site):
    site = Path(site)
    site.mkdir(parents=True, exist_ok=True)
    with Image.open(ASSETS / 'brand-logo-source.png') as original:
        logo = original.convert('RGB')
    mark = logo.crop((105, 55, 790, 610))
    for name, size in [('apple-touch-icon.png',180), ('favicon-64.png',64), ('brand-icon.png',256)]:
        ImageOps.pad(mark, (size,size), color='white').save(site/name)
    ImageOps.pad(logo,(800,300),color='white').save(site/'share-logo.png')
    logo.thumbnail((920,307),Image.Resampling.LANCZOS)
    logo.save(site/'header-logo.png',optimize=True)
    raw=base64.b64encode((site/'brand-icon.png').read_bytes()).decode()
    (site/'icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><image width="256" height="256" href="data:image/png;base64,'+raw+'"/></svg>')
    (site/'immocheck-hero.jpg').write_bytes((ASSETS/'immocheck-hero.jpg').read_bytes())
    print('Approved brand assets generated:',site)
if __name__ == '__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else '_site')
