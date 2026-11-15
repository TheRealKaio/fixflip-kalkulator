"""Install the Immobilien ABC into the unified, generated ImmoCheck shell.

Runs after build_unified_navigation and before fingerprinting/verification.
All edits target the generated site; maintained sources remain under assets/.
"""
from pathlib import Path
import json
import html
import re
import shutil
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
items=json.loads(Path('assets/immobilien-abc.json').read_text(encoding='utf-8'))
assert len(items)==120 and len({entry['id'] for entry in items})==120
assert all(all(entry.get(k) for k in ('term','category','explanation','example','id')) for entry in items)
for name in ('immobilien-abc.json','immobilien-abc.js','immobilien-abc.css'):
    shutil.copyfile(Path('assets')/name,site/name)

navigation=site/'calculator-navigation.js'
nav=navigation.read_text(encoding='utf-8')
def replace_once(old,new):
    global nav
    if nav.count(old)!=1:
        raise SystemExit(f'Glossary integration anchor changed, found {nav.count(old)}: {old[:90]}')
    nav=nav.replace(old,new,1)

replace_once("why:'/warum-immocheck/'}", "why:'/warum-immocheck/','immobilien-abc':'/immobilien-abc/'}")
replace_once(" if(!values)return;\n const title=document.getElementById('heroTitle')",
""" if(!values&&key==='immobilien-abc'){
   const title=document.getElementById('heroTitle'),text=document.getElementById('heroText');
   if(title)title.textContent='Immobilien ABC';
   if(text)text.textContent='Immobilienwissen einfach erklärt – mit Beispielen aus der Praxis.';
   window.NICHeader?.refresh();return;
 }
 if(!values)return;
 const title=document.getElementById('heroTitle')""")
replace_once(" const settings=window.NICSettings.current,c=settings.content[key];",
""" if(key==='immobilien-abc'){
  active=key;document.documentElement.dataset.calculator=key;document.body.dataset.calculator=key;
  if(!refresh)setPage(key);
  applyHeader(key);window.NICABC?.render(panel);return;
 }
 const settings=window.NICSettings.current,c=settings.content[key];""")
replace_once("const links=[['/nebenkostenabrechnung/','Mieterabrechnung'],['/preise/','Preise'],['/warum-immocheck/','Warum ImmoCheck?']];",
"const links=[['/preise/','Preise'],['/warum-immocheck/','Warum ImmoCheck?'],['/immobilien-abc/','Immobilien ABC']];")
navigation.write_text(nav,encoding='utf-8')

# Add the glossary as an ordinary content route in the same shared document.
# The price page already carries static calculator controls for direct URLs.
source=site/'preise'/'index.html'
if not source.exists():raise SystemExit('Unified prices route is missing')
page=source.read_text(encoding='utf-8')
static_terms=''.join(
    '<details class="nic-abc-entry" id="begriff-'+html.escape(entry['id'])+'">'
    '<summary class="nic-abc-summary"><span class="nic-abc-title-stack"><strong>'+html.escape(entry['term'])+'</strong><small class="nic-abc-subtext">'+html.escape(entry['category'])+'</small></span></summary>'
    '<div class="nic-abc-detail"><p>'+html.escape(entry['explanation'])+'</p>'
    '<div class="nic-abc-example"><strong>Beispiel</strong><p>'+html.escape(entry['example'])+'</p></div></div></details>'
    for entry in sorted(items,key=lambda e:e['term'].casefold()))
static_content='<section class="nic-abc"><p class="nic-abc-lead">120 Immobilienbegriffe rund um Kauf, Finanzierung, Notar und Vermietung – einfach erklärt mit Beispielen.</p><div class="nic-abc-toolbar"><label class="nic-abc-search-label">Begriff suchen<input class="nic-abc-search" style="display:block!important;width:100%!important;max-width:100%!important;min-width:0!important;box-sizing:border-box" type="search" placeholder="Begriff suchen, z. B. Grundschuld …" aria-label="Immobilienbegriff suchen"></label></div><div class="nic-abc-heading-row"><h2 class="nic-abc-heading">Begriffe von A bis Z</h2><p class="nic-abc-count">120 Begriffe von 120 Begriffen</p></div><div class="nic-abc-list">'+static_terms+'</div></section>'
page=re.sub(r'<article id="nicContentView"[^>]*>.*?</article>',
    lambda _: '<article id="nicContentView" class="nic-content-card">'+static_content+'</article>',
    page,count=1,flags=re.S)
page=page.replace('data-nic-page="prices"','data-nic-page="immobilien-abc"')
page=page.replace('data-calculator="prices"','data-calculator="immobilien-abc"')
page=page.replace('data-calculator="preise"','data-calculator="immobilien-abc"')
page=re.sub(r'(<h1\b[^>]*id="heroTitle"[^>]*>).*?(</h1>)',r'\g<1>Immobilien ABC\2',page,count=1,flags=re.S)
page=re.sub(r'(<p\b[^>]*id="heroText"[^>]*>).*?(</p>)',r'\g<1>Immobilienwissen einfach erklärt – mit Beispielen aus der Praxis.\2',page,count=1,flags=re.S)
page=re.sub(r'<title>.*?</title>','<title>Immobilien ABC – Immobilienbegriffe einfach erklärt | Neustart ImmoCheck</title>',page,count=1,flags=re.S)
page=re.sub(r'(<meta\s+name="description"\s+content=")[^"]*(")',r'\g<1>120 Immobilienbegriffe rund um Kauf, Notar, Finanzierung, Vermietung und Rechner verständlich erklärt – mit Beispielen.\2',page,count=1)
page=re.sub(r'(<link\s+rel="canonical"\s+href=")[^"]*(")',r'\g<1>https://www.neustart-immocheck.de/immobilien-abc/\2',page,count=1)
folder=site/'immobilien-abc';folder.mkdir(exist_ok=True)
(folder/'index.html').write_text(page,encoding='utf-8')

# Every document uses the same stylesheet and renderer, loaded after the
# central calculator routing script. Relative JS/CSS assets are re-fingerprinted.
for path in site.rglob('*.html'):
    html=path.read_text(encoding='utf-8')
    if 'calculator-navigation.js' not in html:continue
    if 'immobilien-abc.css' not in html:
        html=html.replace('</head>','<link rel="stylesheet" href="/immobilien-abc.css"></head>',1)
    if 'immobilien-abc.js' not in html:
        html=html.replace('</body>','<script src="/immobilien-abc.js"></script></body>',1)
    if path==folder/'index.html':
        # Do not show the inherited price page hero on the initial paint.
        html=html.replace('data-nic-page="prices"','data-nic-page="immobilien-abc"')
    path.write_text(html,encoding='utf-8')

# Include the glossary header in responsive height measurements.
for path in site.rglob('*.html'):
    html=path.read_text(encoding='utf-8')
    pattern=r'(<script type="application/json" id="nic-header-variants">)(.*?)(</script>)'
    def add(match):
        variants=json.loads(match.group(2))
        pair=['Immobilien ABC','Immobilienwissen einfach erklärt – mit Beispielen aus der Praxis.']
        if pair not in variants:variants.append(pair)
        return match.group(1)+json.dumps(variants,ensure_ascii=False)+match.group(3)
    html=re.sub(pattern,add,html,flags=re.S)
    path.write_text(html,encoding='utf-8')
print('Immobilien ABC: 120 entries, shared route and assets installed')
