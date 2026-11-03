"""Mount financing in the same document as the four existing calculators."""
from pathlib import Path
import json,re,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
finance=(site/'finanzierungsrechner/index.html').read_text()
source=Path('assets/financing.html').read_text()
body=re.search(r'(<section\b[^>]*><h2>1\. Finanzierung einstellen</h2>.*?)</main>',finance,re.S)
if not body:raise SystemExit('Finance content missing')
markup=body[1]
style=re.search(r'<style>(.*?)</style>',source,re.S)[1]
style=style.replace(':root',':host').replace('body',':host')
style+=':host{display:block;font:inherit;color:inherit}.card{margin:17px 0}.bottom{display:none}'
actions=re.search(r'<div class="bottom">(.*?)</footer>',source,re.S)[0].split('<footer')[0]
script=re.search(r'<script>\s*\(function\(\)\{\'use strict\';(.*?)window.addEventListener\(\'DOMContentLoaded\'',source,re.S)[1]
script=script[:script.rfind('})();')]
script=re.sub(r"document.querySelectorAll\('\.menu.*?\n",'',script,count=1)
script=script.replace('document.getElementById(id)','root.getElementById(id)')
factory='function createFinance(host){const root=host.attachShadow({mode:"open"});root.innerHTML='+json.dumps('<style>'+style+'</style>'+markup+actions)+';\n'+script+'\nreturn root;}\n'
nav=Path('assets/unified-calculator-navigation.js').read_text().replace('/* FINANCE_MODULE */',factory)
(site/'calculator-navigation.js').write_text(nav)
# Direct finance URLs boot the identical application, with finance selected.
base=(site/'index.html').read_text()
base=re.sub(r'data-nic-page="[^"]+"','data-nic-page="finance"',base,count=1)
for pattern in [r'<title>.*?</title>',r'<link rel="canonical"[^>]*>',r'<meta (?:name="description"|property="og:[^"]+"|name="twitter:[^"]+")[^>]*>']:
 old=re.findall(pattern,finance,re.S)
 if old:
  base=re.sub(pattern,'',base,flags=re.S)
  base=base.replace('</head>',''.join(old)+'</head>',1)
base=base.replace('!["budget","own","flip"].includes(document.documentElement.dataset.nicPage)', '!["budget","own","flip","finance"].includes(document.documentElement.dataset.nicPage)')
(site/'finanzierungsrechner/index.html').write_text(base)
print('Unified five-calculator document and financing module built')
for page in site.rglob('*.html'):
 s=page.read_text()
 s=re.sub(r'calculator-navigation\.[a-f0-9]{16}\.js','calculator-navigation.js',s)
 page.write_text(s)
