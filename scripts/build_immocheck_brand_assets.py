"""Build brand variants from the approved house/four-window/yellow-wave logo."""
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image, ImageOps
ASSETS = Path(__file__).resolve().parent.parent / 'assets'
def save_png(image, path):
    buffer=BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    payload=buffer.getvalue()
    with Image.open(BytesIO(payload)) as check: check.load()
    temporary=path.with_suffix(".png.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)

def run(site):
    site = Path(site)
    site.mkdir(parents=True, exist_ok=True)
    with Image.open(ASSETS / 'brand-logo-source.png') as original:
        logo = original.convert('RGB')
    mark = logo.crop((100, 50, 832, 670))
    for name, size in [('apple-touch-icon.png',180), ('favicon-64.png',64), ('brand-icon.png',256)]:
        save_png(ImageOps.pad(mark, (size,size), color='white'),site/name)
    save_png(ImageOps.pad(logo,(800,300),color='white'),site/'share-logo.png')
    logo.thumbnail((920,307),Image.Resampling.LANCZOS)
    save_png(logo,site/'header-logo.png')
    raw=base64.b64encode((site/'brand-icon.png').read_bytes()).decode()
    (site/'icon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><image width="256" height="256" href="data:image/png;base64,'+raw+'"/></svg>')
    (site/'immocheck-hero.jpg').write_bytes((ASSETS/'immocheck-hero.jpg').read_bytes())
    print('Approved brand assets generated:',site)
if __name__ == '__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else '_site')
