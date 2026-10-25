"""Build crawlable metadata and stable URLs from the published configuration."""
from pathlib import Path
import base64
import struct
import shutil
import html
import json
import re
import sys
from urllib.parse import urlparse

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
config=json.loads((site/'site-settings.json').read_text())
if config.get('version')!=1:
    raise SystemExit('Unsupported site settings version')
base='https://www.neustart-immocheck.de/'
pages={'website':'','company':'unternehmen/','budget':'budget/','own':'eigennutzung/','rent':'vermietung/','flip':'fix-flip/'}
# Publish a real PNG so Safari can fetch the icon before JavaScript runs.
apple=config.get('appleTouchIcon','')
if apple:
    if not isinstance(apple,str) or len(apple)>400000 or not re.fullmatch(r'data:image/png;base64,[A-Za-z0-9+/=]+',apple):
        raise SystemExit('Apple Touch Icon must be a PNG data URL')
    data=base64.b64decode(apple.split(',',1)[1],validate=True)
    if len(data)<24 or data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR' or struct.unpack('>II',data[16:24])!=(180,180):
        raise SystemExit('Apple Touch Icon must be a 180 x 180 PNG')
    (site/'apple-touch-icon.png').write_bytes(data)
else:
    shutil.copyfile('assets/apple-touch-icon.png',site/'apple-touch-icon.png')
root=(site/'index.html').read_text()
# The base keeps calculator assets and the service worker on the root scope.
root=root.replace('<head>','<head>\n<base href="/">',1)
def metadata(key,path):
    m=config.get('meta',{}).get(key,{})
    fallback=config.get('meta',{}).get('website',{})
    title=html.escape(str(m.get('title') or fallback.get('title') or 'Neustart ImmoCheck'),quote=True)
    description=html.escape(str(m.get('description') or fallback.get('description') or ''),quote=True)
    url=html.escape(base+path,quote=True)
    return f'<title>{title}</title>\n<meta name="description" content="{description}">\n<link rel="canonical" href="{url}">\n<meta property="og:title" content="{title}">\n<meta property="og:description" content="{description}">\n<meta property="og:url" content="{url}">\n<meta name="twitter:card" content="summary">\n<meta name="twitter:title" content="{title}">\n<meta name="twitter:description" content="{description}">'

def customize(s,key,path):
    s=s.replace('<html lang="de">',f'<html lang="de" data-nic-page="{key}">',1)
    s=re.sub(r'<title>.*?</title>',metadata(key,path),s,count=1,flags=re.S)
    icon=config.get('favicon','')
    if isinstance(icon,str) and len(icon)<=400000 and re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+',icon):
        s=s.replace('</head>',f'<link rel="icon" href="{html.escape(icon,quote=True)}"></head>',1)
    logo=config.get('websiteLogo','')
    if isinstance(logo,str) and len(logo)<=400000 and re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+',logo):
        s=re.sub(r'(<div class="brand-logo-wrap">).*?</svg>',lambda m:m[1]+'<img class="brand-logo" alt="Neustart ImmoCheck" style="max-height:72px;object-fit:contain" src="'+html.escape(logo,quote=True)+'">',s,count=1,flags=re.S)
    s=re.sub(r'<link\b(?=[^>]*\brel=[\"\']apple-touch-icon[\"\'])[^>]*>', '', s, flags=re.I)
    s=s.replace('</head>','<link rel="apple-touch-icon" sizes="180x180" type="image/png" href="/apple-touch-icon.png"></head>',1)
    return s
(site/'index.html').write_text(customize(root,'website',''))
for key in ['budget','own','rent','flip']:
    path=pages[key];folder=site/path;folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(customize(root,key,path))

company=config.get('company',{})
groups=[('Anbieter',['name','legalForm']),('Vertreten durch',['representative']),('Anschrift',['street','postalCode','city','country']),('Kontakt',['email','phone','fax']),('Register',['registerType','registerCourt','registerNumber']),('Umsatzsteuer-ID',['vatId']),('Wirtschafts-ID',['businessId']),('Aufsichtsbehörde',['authority']),('Berufsrechtliche Angaben',['profession','professionalCountry','chamber','professionalRules']),('Kapitalangaben',['capital']),('Abwicklung / Liquidation',['liquidation']),('Audiovisuelle Mediendienste',['mediaState','mediaAuthority']),('Redaktionell verantwortlich',['editorialResponsible','editorialAddress']),('Verbraucherstreitbeilegung',['disputeResolution']),('Weitere Angaben',['additional'])]
parts=[]
for label,keys in groups:
    values=[html.escape(str(company.get(k,''))) for k in keys if company.get(k)]
    if values:parts.append('<h2>'+label+'</h2><p>'+'\n'.join(values)+'</p>')
content=''.join(parts) or '<p>Die Anbieterangaben wurden noch nicht hinterlegt.</p>'
public='''<!doctype html><html lang="de"><head><base href="/"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Neustart ImmoCheck</title><link rel="icon" href="icon.svg"><style>body{margin:0;background:#f5f7fb;color:#172033;font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.public-shell{max-width:760px;margin:auto;padding:24px 20px}header{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:35px}a{color:#1d4ed8}article{background:white;border:1px solid #e2e8f0;border-radius:20px;padding:28px}h1{font-size:30px;margin:0 0 24px}h2{font-size:18px;margin-top:26px}p{white-space:pre-line;overflow-wrap:anywhere}.public-footer{padding:24px 0;font-size:13px}.nic-social-links{display:flex;gap:15px;flex-wrap:wrap;margin-top:12px}</style><script src="site-settings.js" defer></script><link rel="stylesheet" href="statistics.css"><script src="statistics-core.js" defer></script><script src="statistics.js" defer></script><script src="site-integration.js" defer></script></head><body><div class="public-shell"><header><strong>Neustart ImmoCheck</strong><a href="./">← Zu den Kalkulatoren</a></header><main><article><h1>__TITLE__</h1><div id="companyContent">__CONTENT__</div></article></main><footer class="public-footer"><a href="unternehmen/">Unternehmen</a> · <a href="impressum/">Impressum</a></footer></div></body></html>'''
for path,title in [('unternehmen/','Unternehmen & Kontakt'),('impressum/','Impressum')]:
    folder=site/path;folder.mkdir(exist_ok=True)
    s=public.replace('__TITLE__',title).replace('__CONTENT__',content)
    s=customize(s,'company',path)
    if path=='impressum/':s=s.replace('</head>','<meta name="robots" content="noindex,follow"></head>',1)
    (folder/'index.html').write_text(s)
urls=[base+p for p in pages.values()]
(site/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in urls)+'</urlset>')
print('Settings metadata pages built: website, company and four calculators')

admin=site/'admin.html'
admin.write_text(re.sub(r'<link\b(?=[^>]*\brel=[\"\']apple-touch-icon[\"\'])[^>]*>', '', admin.read_text(), flags=re.I).replace('</head>','<link rel="apple-touch-icon" sizes="180x180" type="image/png" href="/apple-touch-icon.png"></head>',1))
