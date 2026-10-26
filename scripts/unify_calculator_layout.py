"""Share original app, section and white card layout across all calculators."""
from pathlib import Path
import re,sys
from unify_calculator_header import split
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
pattern=re.compile(r'\.(?:app|section|card|deal-type-card)(?![\w-])')
root=(site/'index.html').read_text();rules=[]
for css in re.findall(r'<style\b[^>]*>(.*?)</style>',root,re.S|re.I):rules.extend(split(css,pattern)[1])
# Preserve matching layout rules from the standard external stylesheets too.
for href in re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="([^"]+)"',root):
 asset=site/Path(href).name
 if asset.is_file():rules.extend(split(asset.read_text(),pattern)[1])
if not rules:raise SystemExit('Original card layout rules missing')
(site/'calculator-layout.css').write_text('/* Original shared calculator shell and card layout. */\n'+'\n'.join(rules)+'\n')
for asset in site.glob('*.css'):
 if asset.name=='calculator-layout.css':continue
 asset.write_text(split(asset.read_text(),pattern)[0])
for page in site.rglob('*.html'):
 html=page.read_text()
 html=re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',lambda m:m[1]+split(m[2],pattern)[0]+m[3],html,flags=re.S|re.I)
 if 'class="bottom-actions"' in html:html=html.replace('</head>','<link rel="stylesheet" href="/calculator-layout.css"></head>',1)
 page.write_text(html)
print('All five calculators use the original white-card/app/section rules in calculator-layout.css')
