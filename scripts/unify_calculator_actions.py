"""Use the existing calculator action bar and one stylesheet on all five pages."""
from pathlib import Path
import re,sys
from unify_calculator_header import split
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
pattern=re.compile(r'\.(?:bottom(?:-actions|-primary|-pdf|-save)?|save-arrow)(?![\w-])|#recalc(?![\w-])')
root=(site/'index.html').read_text();rules=[]
for css in re.findall(r'<style\b[^>]*>(.*?)</style>',root,re.S|re.I):rules.extend(split(css,pattern)[1])
if len(rules)<8:raise SystemExit('Original calculator button CSS missing')
css='\n'.join(rules).replace('#recalc','.bottom-primary')
# Normalize browser button defaults; financing previously supplied its own padding/line height.
css+='\n.bottom{line-height:normal}\n.bottom-actions>button{min-height:0;padding:2px 6px;line-height:normal;cursor:pointer}\n.bottom-actions>.bottom-primary{padding:0 10px;line-height:1.2}\n.bottom-actions>.bottom-save{padding:0}\n'
(site/'calculator-actions.css').write_text(css)
for asset in site.glob('*.css'):
    if asset.name=='calculator-actions.css':continue
    asset.write_text(split(asset.read_text(),pattern)[0])
for page in site.rglob('*.html'):
    html=page.read_text()
    html=re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',lambda m:m[1]+split(m[2],pattern)[0]+m[3],html,flags=re.S|re.I)
    if 'class="bottom-actions"' in html:
        html=html.replace('</head>','<link rel="stylesheet" href="/calculator-actions.css"></head>',1)
    page.write_text(html)
print('All five calculator action bars use existing bottom classes and calculator-actions.css')
