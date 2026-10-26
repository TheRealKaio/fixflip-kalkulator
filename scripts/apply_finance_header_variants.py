from pathlib import Path
import json,re,sys,html as markup
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
original=(site/'index.html').read_text(encoding='utf-8')
finance=site/'finanzierungsrechner'/'index.html'
source=re.search(r'<script type="application/json" id="nic-header-variants">([^<]*)</script>',original)
if not source:raise SystemExit('Original responsive-header variants not found')
variants=json.loads(source.group(1))
finance_variant=['Fi&shy;nan&shy;zie&shy;rungs&shy;rech&shy;ner','Darlehen, Tilgung, Sondertilgung und Restschuld']
if finance_variant not in variants:variants.append(finance_variant)
target='<script type="application/json" id="nic-header-variants">[]</script>'
html=finance.read_text(encoding='utf-8')
if target not in html:raise SystemExit('Finance responsive-header placeholder missing')
html=html.replace(target,'<script type="application/json" id="nic-header-variants">'+json.dumps(variants,ensure_ascii=False).replace('<','\\u003c')+'</script>',1)
# Use the original header DOM, including logo/account controls, on both pages.
header=re.search(r'<header class="hero"[^>]*>.*?</header>',original,re.S)
if not header:raise SystemExit('Original header markup missing')
shared=header.group()
shared=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+finance_variant[0]+m[2],shared,flags=re.S)
shared=re.sub(r'(<p\b[^>]*>).*?(</p>)',lambda m:m[1]+finance_variant[1]+m[2],shared,count=1,flags=re.S)
shared=shared.replace('href="admin.html"','href="/#admin"')
html,count=re.subn(r'<header class="hero"[^>]*>.*?</header>',lambda m:shared,html,count=1,flags=re.S)
if count!=1:raise SystemExit('Finance header markup missing')
config=json.loads((site/'site-settings.json').read_text())
meta=config.get('meta',{}).get('finance',{})
title=markup.escape(meta.get('title') or 'Finanzierungsrechner | Neustart ImmoCheck',quote=True)
description=markup.escape(meta.get('description') or '',quote=True)
# Reuse the root's complete share metadata, with finance-specific title/description/URL.
# Copy individual metadata tags so unrelated styles/scripts cannot enter the page.
tags=re.findall(r'<meta\b[^>]*>|<link\b[^>]*rel="canonical"[^>]*>',original,re.I)
selected=[tag for tag in tags if re.search(r'(?:description|og:|twitter:|canonical)',tag)]
for tag in selected:
 tag=re.sub(r'(content=")[^"]*(")',lambda m:m[1]+(title if re.search(r'(?:og|twitter):title',tag) else description)+m[2],tag) if ('og:title' in tag or 'twitter:title' in tag or 'name="description"' in tag or 'og:description' in tag or 'twitter:description' in tag) else tag
 if 'canonical' in tag or 'og:url' in tag:tag=re.sub(r'(href|content)="[^"]*"',lambda m:m[1]+'="https://www.neustart-immocheck.de/finanzierungsrechner/"',tag)
 html=html.replace('</head>',tag+'</head>',1)
html=re.sub(r'<title>.*?</title>',lambda m:'<title>'+title+'</title>',html,count=1,flags=re.S)
html=html.replace('<html lang="de">','<html lang="de" data-nic-page="finance">',1)
finance.write_text(html,encoding='utf-8')
print('Financing uses shared responsive header measurements:',len(variants),'variants')
