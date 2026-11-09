"""Build crawlable metadata and stable URLs from the published configuration."""
from pathlib import Path
import base64
import struct
import shutil
import html
import json
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse
from render_share_image import render_share_image
from unify_finance_footer_markup import extract_footer

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
config=json.loads((site/'site-settings.json').read_text())
if config.get('version')!=1:
    raise SystemExit('Unsupported site settings version')
base='https://www.neustart-immocheck.de/'
ASSET_VERSION='8.364'
share_name=render_share_image(config,site)
share_url=base+share_name
pages={'website':'','company':'unternehmen/','budget':'budget/','own':'eigennutzung/','rent':'vermietung/','flip':'fix-flip/','finance':'finanzierungsrechner/'}
content_routes={'settlement':'nebenkostenabrechnung/','prices':'preise/','why':'warum-immocheck/','about':'ueber-uns/','contact':'kontakt/','login':'anmelden/'}
content_nav=[('settlement','Nebenkostenabrechnung'),('prices','Preise'),('why','Warum Immo-Kalkulator')]

class ContentSanitizer(HTMLParser):
    allowed={'p','br','strong','b','em','i','u','s','ul','ol','li','a','blockquote','hr','div','span','h2','h3','h4'}
    void={'br','hr'}
    def __init__(self):
        super().__init__(convert_charrefs=True);self.out=[]
    def handle_starttag(self,tag,attrs):
        if tag not in self.allowed:return
        if tag=='a':
            href=next((v for k,v in attrs if k=='href'), '') or ''
            href=href.strip()
            if '{{company.email}}' in href: href='mailto:{{company.email}}'
            if re.match(r'^(https?://|mailto:|tel:)',href):
                self.out.append('<a href="'+html.escape(href,quote=True)+'" rel="noopener noreferrer">');return
        self.out.append('<'+tag+'>')
    def handle_endtag(self,tag):
        if tag in self.allowed and tag not in self.void:self.out.append('</'+tag+'>')
    def handle_data(self,data):self.out.append(html.escape(data))
    def fragment(self,value):
        self.feed(str(value or ''));result=''.join(self.out)
        for key,value in config.get('company',{}).items():
            result=result.replace('{{company.'+key+'}}',html.escape(str(value or '')))
        return result
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
root_calculators=root
def metadata(key,path):
    c=config.get('content',{}).get(key,{})
    m=config.get('meta',{}).get(key,{})
    fallback=config.get('meta',{}).get('website',{})
    title=html.escape(str(c.get('seoTitle') or m.get('title') or fallback.get('title') or 'Neustart ImmoCheck'),quote=True)
    description=html.escape(str(c.get('metaDescription') or m.get('description') or fallback.get('description') or ''),quote=True)
    url=html.escape(base+path,quote=True)
    share_alt=html.escape(str(config.get('imageAlts',{}).get('sharing','Neustart ImmoCheck – Immobilien verstehen. Sicherer entscheiden.')),quote=True)
    robots='<meta name="robots" content="noindex,follow">' if c.get('noindex') or key=='login' else ''
    return f'<title>{title}</title>\n{robots}<meta name="description" content="{description}">\n<link rel="canonical" href="{url}">\n<meta property="og:title" content="{title}">\n<meta property="og:description" content="{description}">\n<meta property="og:url" content="{url}">\n<meta property="og:type" content="website">\n<meta property="og:site_name" content="Neustart ImmoCheck">\n<meta property="og:image" content="{share_url}">\n<meta property="og:image:type" content="image/jpeg">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n<meta property="og:image:alt" content="{share_alt}">\n<meta name="twitter:image:alt" content="{share_alt}">\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{share_url}">\n<meta name="twitter:title" content="{title}">\n<meta name="twitter:description" content="{description}">'

def customize(s,key,path):
    s=re.sub(r'<html lang="de"([^>]*)>',lambda m:f'<html lang="de"{m[1]} data-nic-page="{key}">',s,count=1)
    s=re.sub(r'<title>.*?</title>',metadata(key,path),s,count=1,flags=re.S)
    icon=config.get('favicon','')
    if not (isinstance(icon,str) and len(icon)<=400000 and re.fullmatch(r'data:image/(?:png|jpeg|webp);base64,[A-Za-z0-9+/=]+',icon)):
        icon=f'/favicon-64.png?v={ASSET_VERSION}'
        icon_type='image/png'
    else:
        icon_type=icon[5:icon.find(';')]
    s=re.sub(r'<link[^>]*rel="(?:icon|shortcut icon)"[^>]*>', '', s, flags=re.I)
    s=s.replace('</head>',f'<link rel="icon" type="{icon_type}" href="{html.escape(icon,quote=True)}"></head>',1)
    outer=config.get('layout',{}).get('outerBackground','#F6F1E9')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',str(outer)):
        outer='#F6F1E9'
    critical=f'<style id="nic-critical-background">html,body{{min-height:100%;background:{outer}!important}}body:not(.nic-admin):not(.nic-embed){{background:{outer}!important}}</style>'
    s=s.replace('</head>',critical+'</head>',1)
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
    s=s.replace('</head>',f'<link rel="apple-touch-icon" sizes="180x180" type="image/png" href="/apple-touch-icon.png?v={ASSET_VERSION}"></head>',1)
    return s
home_content=config.get('content',{}).get('welcome',{})
home_title=html.escape(str(home_content.get('title') or 'Deine Immobilien. Klar gerechnet.'))
home_body=ContentSanitizer().fragment(home_content.get('description',''))
intro='''<section id="nic-home-intro" class="nic-home-intro"><div class="nic-home-copy"><p class="nic-eyebrow">IMMOBILIEN EINFACH IM BLICK</p><h2>__TITLE__</h2><div class="nic-home-description">__BODY__</div><div class="nic-home-actions"><button type="button" data-nic-show-calculators>Immobilie berechnen</button><a href="/nebenkostenabrechnung/">Nebenkosten abrechnen</a></div></div></section>'''
intro=intro.replace('__TITLE__',home_title).replace('__BODY__',home_body)
style='''<style>.nic-home-intro{margin:24px 0;padding:28px 30px;border:1px solid #e2e9e5;border-radius:12px;background:#f6f1e9;color:#263b3a}.nic-home-copy{max-width:900px;margin:auto}.nic-home-intro h2{margin:0;color:#075c55;font-size:26px}.nic-home-description{margin-top:10px;max-width:780px;line-height:1.55}.nic-eyebrow{margin:0 0 7px;color:#16867a;font-size:12px;font-weight:700;letter-spacing:.07em}.nic-home-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.nic-home-actions a,.nic-home-actions button{display:inline-flex;min-height:44px;align-items:center;padding:10px 18px;border:1px solid #075c55;border-radius:12px;background:linear-gradient(135deg,#16867a,#075c55);color:#fff;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}.nic-home-actions a{background:#fff;color:#075c55}@media(max-width:600px){.nic-home-intro{padding:22px 18px}.nic-home-intro h2{font-size:22px}.nic-home-actions{flex-direction:column}.nic-home-actions>*{justify-content:center}}</style>'''
root=root.replace('</head>',style+'</head>',1)
header_end=root.find('</header>')
if header_end>=0 and 'id="nic-home-intro"' not in root:
    header_end+=len('</header>')
    root=root[:header_end]+intro+root[header_end:]
elif 'id="nic-home-intro"' not in root:
    root=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+intro,root,count=1)
(site/'index.html').write_text(customize(root,'website',''))
for key in ['budget','own','rent','flip']:
    path=pages[key];folder=site/path;folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(customize(root_calculators,key,path))

# Crawlable information pages reuse the existing app shell, header, and footer.
content_style='''<style>
html,body{min-height:100%}
body{min-height:100vh}
body.nic-content-page>.app>.hero{display:none!important}
body.nic-content-page>.app{min-height:100vh;display:flex;flex-direction:column;background:var(--nic-design-warm,#F6F1E9)!important}
body.nic-content-page>.app>main.nic-content-main{display:flex;flex-direction:column;flex:1;width:100%;max-width:1180px;box-sizing:border-box;margin:0 auto;padding:32px 20px 16px}
body.nic-content-page>.app>.bottom{display:none!important}
body.nic-content-page .nic-actions-above-footer{display:none!important}
.nic-content-card{flex:1;width:100%;max-width:980px;box-sizing:border-box;margin:0 auto;padding:32px;border:1px solid #e2e9e5;border-radius:16px;background:#fff}
.nic-content-card h1{margin:0 0 18px;color:#075c55;font-size:clamp(28px,4vw,42px);line-height:1.15}
.nic-content-card p{margin:12px 0}
@media(max-width:760px){body.nic-content-page>.app>main.nic-content-main{padding:24px 16px 16px}.nic-content-card{padding:24px 18px}}
</style>'''
login_activation='''<script>
window.addEventListener('DOMContentLoaded',function(){
 if(document.documentElement.dataset.nicPage!=='login')return;
 if(!window.NICAccess)return;
 window.NICAccess.init().then(function(){return window.NICAccess.login();}).catch(console.error);
});
</script>'''
footer_markup,_,_=extract_footer(root_calculators)
for key,path in content_routes.items():
    content=config.get('content',{}).get(key,{})
    title=html.escape(str(content.get('title') or key))
    body=ContentSanitizer().fragment(content.get('description',''))
    article='<article class="nic-content-card"><h1>'+title+'</h1><div>'+body+'</div></article>'
    def replace_existing_content_container(match):
        return '<main class="section nic-content-main">'+article+footer_markup+'</main>'
    page,count=re.subn(r'<main\b[^>]*>[\s\S]*?</main>',replace_existing_content_container,root_calculators,count=1)
    if count!=1:
        raise SystemExit('Could not replace the existing content container for '+key)
    page=page.replace('</head>',content_style+'</head>',1)
    def mark_content_page(match):
        attrs=match.group(1)
        class_match=re.search(r'\bclass\s*=\s*(["\'])(.*?)\1',attrs)
        if class_match:
            classes=class_match.group(2).split()
            if 'nic-content-page' not in classes:classes.append('nic-content-page')
            attrs=attrs[:class_match.start()]+'class="'+ ' '.join(classes)+'"'+attrs[class_match.end():]
        else:
            attrs+=' class="nic-content-page"'
        return '<body'+attrs+'>'
    page=re.sub(r'<body\b([^>]*)>',mark_content_page,page,count=1)
    if key=='login':page=page.replace('</body>',login_activation+'</body>',1)
    folder=site/path;folder.mkdir(exist_ok=True)
    (folder/'index.html').write_text(customize(page,key,path))

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
urls=[base+p for p in pages.values()]+[base+p for k,p in content_routes.items() if k!='login']
(site/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in urls)+'</urlset>')
print('Settings metadata pages built: website, company, four calculators and six content pages')

for name in ('admin.css','admin.js','legal-drafts.js'):
    shutil.copyfile(Path('assets')/name,site/name)
docs_dir=site/'docs'
docs_dir.mkdir(exist_ok=True)
shutil.copyfile('docs/README-Projektdokumentation.pdf',docs_dir/'README-Projektdokumentation.pdf')
admin=site/'admin.html'
admin_html=re.sub(r'<link\b(?=[^>]*\brel=[\"\']apple-touch-icon[\"\'])[^>]*>', '', admin.read_text(), flags=re.I)
admin_html=admin_html.replace('</head>','<link rel="apple-touch-icon" sizes="180x180" type="image/png" href="/apple-touch-icon.png"></head>',1)
download_href='/docs/README-Projektdokumentation.pdf'
if download_href not in admin_html:
    layout_start=admin_html.find('<section id="panel-layout"')
    social_start=admin_html.find('<section id="panel-social"',layout_start)
    layout_end=admin_html.rfind('</section>',layout_start,social_start)
    if layout_start<0 or social_start<0 or layout_end<0:
        raise SystemExit('Admin Layout insertion point missing')
    readme_card='<div class="form-card"><h3>Projektdokumentation</h3><p class="helper">Formeln, Berechnungsregeln, Standardwerte und der aktuelle Projektstand als PDF.</p><a class="button primary" href="/docs/README-Projektdokumentation.pdf" download="README-Projektdokumentation.pdf">README als PDF herunterladen</a></div>'
    admin_html=admin_html[:layout_end]+readme_card+admin_html[layout_end:]
admin.write_text(admin_html)


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
                raise ValueError('No SDMX CSV header for '+name+': '+raw[:250].replace('\n',' '))
            sample=lines[i]
            delimiter=';' if sample.count(';')>sample.count(',') else ','
            reader=csv.DictReader(io.StringIO('\n'.join(lines[i:])),delimiter=delimiter)
            rows={}
            for row in reader:
                month=str(row.get('TIME_PERIOD','')).strip().strip('"')
                value=str(row.get('OBS_VALUE','')).strip().strip('"')
                import re
                match=re.search(r'(20[0-9]{2}|19[0-9]{2})[-/]([01][0-9])',month)
                if match and value and value not in ('-','.'):
                    try:rows[match[1]+'-'+match[2]]=float(value.replace(',','.'))
                    except ValueError:pass
            if not rows:raise ValueError('No data for '+name+'; headers='+str(reader.fieldnames)+'; sample='+str(lines[i+1:i+4])[:350])
            values[name]=rows
        keys=sorted(set(values['five'])|set(values['ten']))
        points=[{'month':k,'five':values['five'].get(k),'ten':values['ten'].get(k)} for k in keys[-121:]]
        (site/'mortgage-rates.json').write_text(json.dumps({'source':'Deutsche Bundesbank BBIM1 SUD117 SUD118','series':points,'latest':keys[-1]},ensure_ascii=False))
        print('Bundesbank rate data bundled:',keys[-1],len(points))
    except Exception as err:
        raise SystemExit('Bundesbank-Daten konnten nicht eingelesen werden: '+str(err))

write_mortgage_rates()

