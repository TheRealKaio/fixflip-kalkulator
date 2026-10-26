from pathlib import Path
import json,re,sys
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
finance.write_text(html,encoding='utf-8')
print('Financing uses shared responsive header measurements:',len(variants),'variants')
