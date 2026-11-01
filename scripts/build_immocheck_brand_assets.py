"""Render unified Neustart brand images for web, Apple and social sharing.
Only generated brand assets are changed; no calculator code is touched.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def font(size,bold=False):
    path='/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if bold else '')+'.ttf'
    return ImageFont.truetype(path,size)

def mark(size):
    image=Image.new('RGBA',(size,size),'#ddece8')
    d=ImageDraw.Draw(image)
    s=size/180
    pts=lambda xy: [(round(x*s),round(y*s)) for x,y in xy]
    d.rounded_rectangle((round(9*s),round(9*s),round(171*s),round(171*s)),radius=round(34*s),fill='#DDECE8')
    d.line(pts([(33,88),(90,36),(147,88)]),fill='#075C55',width=round(13*s),joint='curve')
    d.line(pts([(45,85),(45,147),(135,147),(135,85)]),fill='#075C55',width=round(12*s),joint='curve')
    d.rounded_rectangle((round(77*s),round(109*s),round(103*s),round(147*s)),radius=round(4*s),fill='#16867A')
    return image

def run(site):
    site=Path(site)
    site.mkdir(parents=True,exist_ok=True)
    apple=mark(180)
    apple.save(site/'apple-touch-icon.png')
    mark(64).save(site/'favicon-64.png')
    mark(256).save(site/'brand-icon.png')
    logo=Image.new('RGBA',(800,300),'#ffffff')
    icon=mark(240)
    logo.alpha_composite(icon,(18,30))
    draw=ImageDraw.Draw(logo)
    draw.text((285,66),'NEUSTART',font=font(62,True),fill='#075C55')
    draw.text((285,157),'Immo',font=font(55),fill='#075C55')
    draw.text((455,157),'Check',font=font(55,True),fill='#16867A')
    logo.save(site/'share-logo.png')
    (site/'icon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 180"><rect width="180" height="180" rx="34" fill="#ddece8"/><path d="M33 88 90 36 147 88 M45 85V147H135V85" fill="none" stroke="#075c55" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/><rect x="77" y="109" width="26" height="38" rx="4" fill="#16867a"/></svg>''',encoding='utf-8')
    print('Generated brand logo, favicon and Apple icon into',site)

if __name__=='__main__':
    import sys
    run(sys.argv[1] if len(sys.argv)>1 else '_site')
