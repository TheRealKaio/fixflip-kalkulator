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
from render_share_image import render_share_image

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
config=json.loads((site/'site-settings.json').read_text())
if config.get('version')!=1:
    raise SystemExit('Unsupported site settings version')
base='https://www.neustart-immocheck.de/'
share_name=render_share_image(config,site)
share_url=base+share_name
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
    share_alt=html.escape(str(config.get('imageAlts',{}).get('sharing','Neustart ImmoCheck – Immobilien verstehen. Sicherer entscheiden.')),quote=True)
    return f'<title>{title}</title>\n<meta name="description" content="{description}">\n<link rel="canonical" href="{url}">\n<meta property="og:title" content="{title}">\n<meta property="og:description" content="{description}">\n<meta property="og:url" content="{url}">\n<meta property="og:type" content="website">\n<meta property="og:site_name" content="Neustart ImmoCheck">\n<meta property="og:image" content="{share_url}">\n<meta property="og:image:type" content="image/jpeg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="{share_alt}">\n<meta name="twitter:image:alt" content="{share_alt}">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{share_url}">\n<meta name="twitter:title" content="{title}">\n<meta name="twitter:description" content="{description}">'

def customize(s,key,path):
    s=re.sub(r'<html lang="de"([^>]*)>',lambda m:f'<html lang="de"{m[1]} data-nic-page="{key}">',s,count=1)
    s=re.sub(r'<title>.*?</title>',metadata(key,path),s,count=1,flags=re.S)
    icon=config.get('favicon','')
    if isinstance(icon,str) and len(icon)<=400000 and re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+',icon):
        s=s.replace('</head>',f'<link rel="icon" href="{html.escape(icon,quote=True)}"></head>',1)
    logo=config.get('websiteLogo','')
    if isinstance(logo,str) and len(logo)<=400000 and re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+',logo):
        s=re.sub(r'(<div class="brand-logo-wrap">).*?</svg>',lambda m:m[1]+'<img class="brand-logo" alt="'+html.escape(str(config.get('imageAlts',{}).get('websiteLogo','Neustart ImmoCheck – Immobilien-Kalkulatoren')),quote=True)+'" style="max-height:72px;object-fit:contain" src="'+html.escape(logo,quote=True)+'">',s,count=1,flags=re.S)
    website=str(config.get('company',{}).get('website','')).strip()
    if website and not urlparse(website).scheme:
        website='https://'+website
    parsed=urlparse(website)
    target=website if parsed.scheme in ('http','https') and parsed.hostname and not parsed.username and not parsed.password else base
    s=re.sub(r'(<div class="brand-logo-wrap">)(.*?)(</div>)',lambda m:m[1]+'<a class="nic-logo-link" href="'+html.escape(target,quote=True)+'">'+m[2]+'</a>'+m[3],s,count=1,flags=re.S)
    s=re.sub(r'<link\b(?=[^>]*\brel=[\"\']apple-touch-icon[\"\'])[^>]*>', '', s, flags=re.I)
    s=s.replace('</head>','<link rel="apple-touch-icon" sizes="180x180" type="image/png" href="/apple-touch-icon.png"></head>',1)
    return s
(site/'index.html').write_text(customize(root,'website',''))
for key in ['budget','own','rent','flip']:
    path=pages[key];folder=site/path;folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(customize(root,key,path))

company=config.get('company',{})
groups=[('Anbieter',['name','legalForm']),('Vertreten durch',['representative']),('Anschrift',['street','postalCode','city','country']),('Kontakt',['email','website','phone','fax']),('Register',['registerType','registerCourt','registerNumber']),('Umsatzsteuer-ID',['vatId']),('Wirtschafts-ID',['businessId']),('Aufsichtsbehörde',['authority']),('Berufsrechtliche Angaben',['profession','professionalCountry','chamber','professionalRules']),('Kapitalangaben',['capital']),('Abwicklung / Liquidation',['liquidation']),('Audiovisuelle Mediendienste',['mediaState','mediaAuthority']),('Redaktionell verantwortlich',['editorialResponsible','editorialAddress']),('Verbraucherstreitbeilegung',['disputeResolution']),('Weitere Angaben',['additional'])]
parts=[]
for label,keys in groups:
    raw_values=([company.get('street'), ' '.join(' '.join(str(company.get(k,'')).split()) for k in ['postalCode','city'] if company.get(k)), company.get('country')] if label=='Anschrift' else [company.get(k) for k in keys])
    values=[html.escape(str(value)) for value in raw_values if value]
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


# Bundle verified Bundesbank monthly data on this same origin as a fallback for browsers
# that disallow cross-origin reads from the Bundesbank API.
def write_mortgage_rates():
    import urllib.request
    import csv
    import io
    from datetime import date
    try:
        values={}
        for name,code in [('five','I'),('ten','O')]:
            url=('https://api.statistiken.bundesbank.de/rest/data/BBIM1/'
                 'M.DE.B.A2C.'+code+'.R.A.2250.EUR.N?format=sdmx_csv&startPeriod='+str(date.today().year-11)+'-01')
            req=urllib.request.Request(url,headers={'Accept':'text/csv','User-Agent':'Neustart-ImmoCheck/1.0'})
            with urllib.request.urlopen(req,timeout=15) as response:
                raw=response.read().decode('utf-8-sig')
            lines=raw.splitlines()
            i=next((i for i,line in enumerate(lines) if 'TIME_PERIOD' in line and 'OBS_VALUE' in line),None)
            if i is None:
                raise ValueError('No SDMX CSV header for '+name+': '+raw[:250].replace('\\n',' '))
            reader=csv.DictReader(io.StringIO('\n'.join(lines[i:])))
            rows={}
            for row in reader:
                month=row.get('TIME_PERIOD','')
                value=row.get('OBS_VALUE','')
                if len(month)==7 and month[4]=='-' and value:
                    try:rows[month]=float(value)
                    except ValueError:pass
            if not rows:raise ValueError('No data for '+name)
            values[name]=rows
        keys=sorted(set(values['five'])|set(values['ten']))
        points=[{'month':k,'five':values['five'].get(k),'ten':values['ten'].get(k)} for k in keys[-121:]]
        (site/'mortgage-rates.json').write_text(json.dumps({'source':'Deutsche Bundesbank BBIM1 SUD117 SUD118','series':points,'latest':keys[-1]},ensure_ascii=False))
        print('Bundesbank rate data bundled:',keys[-1],len(points))
    except Exception as err:
        print('Bundesbank bundled data unavailable; client falls back to live API:',err)

write_mortgage_rates()

# Finance standalone page shares the same release number as the four calculators.
finance=site/'finanzierungsrechner'/'index.html'
if finance.exists():
    release=(site/'.release-version').read_text(encoding='utf-8').strip()
    finance.write_text(finance.read_text(encoding='utf-8').replace('VERSION_PLACEHOLDER',release),encoding='utf-8')
