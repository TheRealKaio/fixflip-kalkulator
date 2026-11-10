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
nav=nav.replace("''/* OWN_INTRO_MARKUP */",json.dumps(Path("assets/own-intro.html").read_text()))
import shutil
shutil.copyfile('assets/homepage.css',site/'homepage.css')
shutil.copyfile('assets/initial-layout.js',site/'initial-layout.js')
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

# Direct information URLs boot the complete shared application as well.
# Retain their static SEO metadata and rendered article for direct visits/crawlers.
shared=base
for content_key,slug in [('settlement','nebenkostenabrechnung'),('prices','preise'),('why','warum-immocheck')]:
 destination=site/slug/'index.html'
 old=destination.read_text()
 article=re.search(r'<article class="nic-content-card">(.*?)</article>',old,re.S)
 if not article:raise SystemExit('Content article missing: '+slug)
 document=shared
 document=re.sub(r'data-nic-page="[^"]+"','data-nic-page="'+content_key+'"',document,count=1)
 document=re.sub(r'<body\b([^>]*)>',lambda m:'<body'+m[1]+' class="nic-content-active nic-standard-header-page">' if 'class=' not in m[1] else '<body'+re.sub(r'class="([^"]*)"',lambda c:'class="'+c[1]+' nic-content-active nic-standard-header-page"',m[1])+'>',document,count=1)
 document=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+'<article id="nicContentView" class="nic-content-card">'+article[1]+'</article>',document,count=1)
 for pattern in [r'<title>.*?</title>',r'<link rel="canonical"[^>]*>',r'<meta (?:name="description"|property="og:[^"]+"|name="twitter:[^"]+")[^>]*>']:
  metadata=re.findall(pattern,old,re.S)
  document=re.sub(pattern,'',document,flags=re.S)
  document=document.replace('</head>',''.join(metadata)+'</head>',1)
 for tag,identifier in [('h1','heroTitle'),('p','heroText')]:
  pattern=r'(<'+tag+r'\b[^>]*id="'+identifier+r'"[^>]*>).*?(</'+tag+'>)'
  heading=re.search(pattern,old,re.S)
  if heading:document=re.sub(pattern,lambda m:heading[0],document,count=1,flags=re.S)
 destination.write_text(document)

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
 if 'nic-published-settings' in s and re.search(r'class="[^"]*\bapp\b',s) and 'initial-layout.js' not in s:
  s=s.replace('<head>','<head><script src="/initial-layout.js"></script>',1)
 s=re.sub(r'<script\b[^>]*src="[^"]*calculator-finance(?:\.[a-f0-9]{16})?\.js"[^>]*>\s*</script>','',s)
 # Shared calculator initialization may warm hidden controls on the homepage,
 # but only the route controller owns its header. Avoid the old title/restore race.
 if 'function updateDealTypeUI(){' in s:
  for target in ['heroTitle','heroText']:
   old='if($("'+target+'")){'
   new='if($("'+target+'")&&!document.body.matches(".nic-home-active,.nic-content-active")){'
   if s.count(old)!=1:raise SystemExit('Header ownership guard missing: '+str(page)+' '+target)
   s=s.replace(old,new,1)
  s=s.replace('if(heroTitle) heroTitle.innerHTML=', 'if(heroTitle&&!document.body.matches(".nic-home-active,.nic-content-active")) heroTitle.innerHTML=')
  s=s.replace('if(heroText) heroText.textContent=', 'if(heroText&&!document.body.matches(".nic-home-active,.nic-content-active")) heroText.textContent=')
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
  config=json.loads((site/'site-settings.json').read_text())
  home=config.get('meta',{}).get('website',{})
  headers=[finance_header,[home.get('homeTitle','Deine Immobilie. Dein Plan. Dein Überblick.'),home.get('homeDescription','')]]
  for content_key in ['settlement','prices','why']:
   content=config.get('content',{}).get(content_key,{})
   headers.append([content.get('title',''),content.get('metaDescription','')])
  for header in headers:
   if header[0] and header not in items:items.append(header)
  return match[1]+json.dumps(items,ensure_ascii=False).replace('<','\\u003c')+match[3]
 s=re.sub(r'(<script type="application/json" id="nic-header-variants">)(.*?)(</script>)',variants,s,flags=re.S)
 if page==site/'finanzierungsrechner/index.html':
  s=re.sub(r'(<h1\b[^>]*id="heroTitle"[^>]*>).*?(</h1>)',lambda m:m[1]+finance_header[0]+m[2],s,count=1,flags=re.S)
  s=re.sub(r'(<p\b[^>]*id="heroText"[^>]*>).*?(</p>)',lambda m:m[1]+html.escape(finance_header[1])+m[2],s,count=1,flags=re.S)
 if 'homepage.css' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/homepage.css"></head>',1)
 key=next((item['id'] for item in calculators if page==site/item['path'].strip('/')/'index.html'),'home' if page==site/'index.html' else next((key for key,slug in [('settlement','nebenkostenabrechnung'),('prices','preise'),('why','warum-immocheck')] if page==site/slug/'index.html'),'budget'))
 s=re.sub(r'<html\b', '<html data-calculator="'+key+'"',s,count=1)
 s=re.sub(r'calculator-navigation\.[a-f0-9]{16}\.js','calculator-navigation.js',s)
 # Keep inactive calculator form copy out of information pages' initial HTML.
 # Restore the shared controls synchronously before legacy inline initialization,
 # preserving IDs, event handlers and same-document navigation to calculators.
 if page.parent.name in {'nebenkostenabrechnung','preise','warum-immocheck'}:
  main=re.search(r'(<main\b[^>]*>)(.*?)(</main>)',s,re.S)
  article=re.search(r'<article id="nicContentView"[^>]*>.*?</article>',main[2],re.S)
  if not article:raise SystemExit('Missing static content article: '+str(page))
  controls=main[2][:article.start()]+main[2][article.end():]
  bundle='content-calculator-controls.js'
  payload='document.currentScript.insertAdjacentHTML("beforebegin",'+json.dumps(controls).replace('<','\\u003c')+');\n'
  target=site/bundle
  if target.exists() and target.read_text()!=payload:raise SystemExit('Information routes must share identical calculator controls')
  target.write_text(payload)
  s=s[:main.start()]+main[1]+article[0]+'<script src="/'+bundle+'"></script>'+main[3]+s[main.end():]
 if page.parent.name in {'ueber-uns','kontakt','anmelden'}:
  s=re.sub(r'<h1\b([^>]*id="heroTitle"[^>]*)>.*?</h1>',r'<h1\1></h1>',s,count=1,flags=re.S)
  s=re.sub(r'(<p\b[^>]*id="heroText"[^>]*>).*?(</p>)',r'\1\2',s,count=1,flags=re.S)
 if page==site/'eigennutzung/index.html':
  s=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+Path('assets/own-intro.html').read_text(),s,count=1)
 page.write_text(s)
