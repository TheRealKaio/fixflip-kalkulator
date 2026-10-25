"""Render a public, cache-versioned social image from the published settings."""
from pathlib import Path
from io import BytesIO
import base64
import hashlib
import re
import warnings
from PIL import Image, ImageDraw, ImageFont

DEFAULT_TEXT='Immobilien verstehen. Sicherer entscheiden.'

def render_share_image(config,site):
    sharing=config.get('sharing',{})
    text=str(sharing.get('text',DEFAULT_TEXT)).strip()[:160]
    source=sharing.get('image') or config.get('websiteLogo')
    if source:
        if not isinstance(source,str) or len(source)>400000 or not re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+',source):
            raise ValueError('Invalid sharing image')
        raw=BytesIO(base64.b64decode(source.split(',',1)[1],validate=True))
    else:
        raw=Path('assets/share-logo.png')
    with warnings.catch_warnings():
        warnings.simplefilter('error',Image.DecompressionBombWarning)
        with Image.open(raw) as original:
            if original.width*original.height>20000000:
                raise ValueError('Sharing image dimensions too large')
            logo=original.convert('RGBA')
    logo.thumbnail((800,300),Image.Resampling.LANCZOS)
    image=Image.new('RGB',(1200,630),'#f5f7fb')
    image.paste(logo,((1200-logo.width)//2,90+(300-logo.height)//2),logo)
    draw=ImageDraw.Draw(image)
    def font(size):
        try:return ImageFont.truetype('DejaVuSans.ttf',size)
        except OSError:return ImageFont.load_default(size=size)
    for size in range(38,13,-1):
        selected=font(size);lines=[];line=''
        for word in text.split():
            next_line=(line+' '+word).strip()
            if line and draw.textlength(next_line,font=selected)>1000:
                lines.append(line);line=word
            else:line=next_line
        if line:lines.append(line)
        if len(lines)<=3 and all(draw.textlength(line,font=selected)<=1000 for line in lines):break
    # A single unbroken string can still exceed the width at the smallest size.
    while lines and max(draw.textlength(line,font=selected) for line in lines)>1000 and size>6:
        size-=1;selected=font(size)
    for i,line in enumerate(lines):
        draw.text((600,450+i*46),line,font=selected,fill='#07345f',anchor='mm')
    output=BytesIO();image.save(output,format='JPEG',quality=88,optimize=True)
    content=output.getvalue()
    name='social-preview-'+hashlib.sha256(content).hexdigest()[:16]+'.jpg'
    (Path(site)/name).write_bytes(content)
    print('Social image rendered:',name,'1200 x 630,',len(content),'bytes')
    return name
