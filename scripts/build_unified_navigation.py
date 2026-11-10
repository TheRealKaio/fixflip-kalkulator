"""Mount financing in the same document as the four existing calculators."""
from pathlib import Path
import json,re,sys,html
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
finance=(site/'finanzierungsrechner/index.html').read_text()
source=Path('assets/financing.html').read_text()
finance_header=[re.search(r'<h1\b[^>]*>(.*?)</h1>',finance,re.S)[1], html.unescape(re.sub('<[^>]+>','',re.search(r'<p\b[^>]*id="heroText"[^>]*>(.*?)</p>',finance,re.S)[1]))]

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
# Financing consumes the existing shared reference, not its historical chart series.
script=script.replace('interest:4.01','interest:(window.NICReferenceInterest?.rate??4.0)')
script=script.replace('let currentRate=4.01','let currentRate=window.NICReferenceInterest?.rate??4.0')
script=script.replace("if(latest[key]){$('interest').value=", "if(latest[key]){localStorage.setItem('nic_financing_interest_manual_v1','1');$('interest').value=")
script+="""
function applyReferenceRate(rate){
 if(!Number.isFinite(rate))return;
 currentRate=rate;
 if(localStorage.getItem('nic_financing_interest_manual_v1')!=='1'){
  $('interest').value=rate;calculate();
 }
}
window.addEventListener('nic-reference-interest',event=>applyReferenceRate(event.detail.rate));
applyReferenceRate(window.NICReferenceInterest?.rate??4.0);
"""
factory='const financeHeader='+json.dumps(finance_header)+';\nfunction createFinance(host){const root=host.attachShadow({mode:"open"});root.innerHTML='+json.dumps('<style>'+style+'</style>'+markup+actions)+';\n'+script+'\nreturn root;}\n'
registry=json.loads(Path('assets/calculators.json').read_text())
calculators=registry['calculators']
if len(calculators)!=5 or len({item['id'] for item in calculators})!=5 or len({item['path'] for item in calculators})!=5:
 raise SystemExit('Expected five unique calculator IDs and routes')
nav=Path('assets/unified-calculator-navigation.js').read_text().replace('/* FINANCE_MODULE */',factory)
nav=nav.replace("''/* HOME_MARKUP */",json.dumps(Path('assets/homepage.html').read_text()))
import shutil
shutil.copyfile('assets/homepage.css',site/'homepage.css')
nav=nav.replace('/* CALCULATOR_REGISTRY */','const calculators='+json.dumps(calculators)+';')
(site/'calculators.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n')
# Finance shares the same loaded controller and initialization scope as all modes.
(site/'calculator-navigation.js').write_text(nav)
# Remove obsolete split bundles if rebuilding an existing output directory.
for obsolete in site.glob('calculator-finance*.js'):obsolete.unlink()
# Direct finance URLs boot the identical application, with finance selected.
base=(site/'index.html').read_text().replace(' nic-home-active','').replace('class="nic-home-active"','class=""')
# The homepage contains nested sections; remove its complete balanced element.
from unify_finance_footer_markup import FooterParser
class HomeParser(FooterParser):
 def handle_starttag(self,tag,attrs):
  home=any(k=='id' and v=='nic-home-intro' for k,v in attrs)
  attrs=[(k,v) for k,v in attrs if not(home and k=='class')]
  if home:attrs.append(('class','footer-note'))
  elif any(k=='class' and v and 'footer-note' in v.split() for k,v in attrs):
   attrs=[(k,'' if k=='class' else v) for k,v in attrs]
  super().handle_starttag(tag,attrs)
home=HomeParser(base);home.feed(base)
if home.start is not None and home.end is not None:base=base[:home.start]+base[home.end:]

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
 s=re.sub(r'<script\b[^>]*src="[^"]*calculator-finance(?:\.[a-f0-9]{16})?\.js"[^>]*>\s*</script>','',s)
 if 'async function initializeReferenceInterest()' in s:
  anchor='const value=(Math.round(rate*100)/100).toFixed(2);'
  if s.count(anchor)!=1:raise SystemExit('Shared interest initializer must occur once: '+str(page))
  snapshot_anchor='if(!restored) initializeModeDefaults(mode);'
  if s.count(snapshot_anchor)!=1:raise SystemExit('Mode snapshot initializer missing: '+str(page))
  s=s.replace(snapshot_anchor,snapshot_anchor+'\n    if(window.NICReferenceInterest&&localStorage.getItem("ff_interest_manual")!=="1")document.getElementById("interest").value=window.NICReferenceInterest.rate.toFixed(2);',1)
  s=s.replace('async function initializeReferenceInterest(){','async function initializeReferenceInterest(){\n  installFinancingManualOverrideTracking();',1)
  # Read the manual flags after the request, including edits made while it loads.
  for flag,key in [('mainManual','ff_interest_manual'),('budgetManual','ff_budget_interest_manual'),('rentalManual','ff_rent_interest_manual')]:
   s=s.replace('if(!'+flag+' &&', 'if(localStorage.getItem("'+key+'")!=="1" &&')
  s=s.replace('  initializeRepaymentDefaults();\n  installFinancingManualOverrideTracking();', '  window.NICReferenceInterest={rate:Number(value),source:localStorage.getItem("ff_reference_interest_source")};\n  window.dispatchEvent(new CustomEvent("nic-reference-interest",{detail:window.NICReferenceInterest}));\n  initializeRepaymentDefaults();\n  installFinancingManualOverrideTracking();',1)
 def variants(match):
  items=json.loads(match[2])
  if finance_header not in items:items.append(finance_header)
  return match[1]+json.dumps(items,ensure_ascii=False).replace('<','\\u003c')+match[3]
 s=re.sub(r'(<script type="application/json" id="nic-header-variants">)(.*?)(</script>)',variants,s,flags=re.S)
 if page==site/'finanzierungsrechner/index.html':
  s=re.sub(r'(<h1\b[^>]*id="heroTitle"[^>]*>).*?(</h1>)',lambda m:m[1]+finance_header[0]+m[2],s,count=1,flags=re.S)
  s=re.sub(r'(<p\b[^>]*id="heroText"[^>]*>).*?(</p>)',lambda m:m[1]+html.escape(finance_header[1])+m[2],s,count=1,flags=re.S)
 key=next((item['id'] for item in calculators if page==site/item['path'].strip('/')/'index.html'),'budget')
 s=re.sub(r'<html\b', '<html data-calculator="'+key+'"',s,count=1)
 s=re.sub(r'calculator-navigation\.[a-f0-9]{16}\.js','calculator-navigation.js',s)
 page.write_text(s)
