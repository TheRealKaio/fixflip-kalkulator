"""Render explicit calculator destinations in their final mode before initialization."""
from pathlib import Path
import html as markup,json,re,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
indices={'budget':1,'own':2,'flip':3,'rent':4}
for page in site.rglob('*.html'):
 s=page.read_text()
 if 'id="nic-header-variants"' not in s:continue
 # Apply configuration synchronously in the head, after its inline bootstrap data.
 # The file is already shared/cached when arriving from financing.
 s=re.sub(r'<script\b(?=[^>]*\bsrc="/?site-settings\.js")[^>]*>\s*</script>','',s)
 s=re.sub(r'<script\b(?=[^>]*\bsrc="/?calculator-navigation\.js")[^>]*>\s*</script>','',s)
 s=s.replace('</head>','<script src="/site-settings.js"></script><script src="/calculator-navigation.js"></script></head>',1)
 s=re.sub(r'<script\b(?=[^>]*\bsrc="/?stable-header\.js")[^>]*>\s*</script>','',s)
 s=s.replace('</head>','<script src="/stable-header.js"></script></head>',1)
 s=s.replace('</header>','</header><script>window.NICInitializeHeader();</script>',1)
 if 'function buildBudgetPdf(){' in s:
  old='const savedDealType = localStorage.getItem("ff_dealType") || "budget";'
  new='const requestedDealType=document.documentElement.dataset.nicPage;\nconst savedDealType = ["budget","own","flip"].includes(requestedDealType)?requestedDealType:(localStorage.getItem("ff_dealType") || "budget");'
  if old not in s:raise SystemExit('Initial deal-type anchor missing')
  s=s.replace(old,new,1)
  old='if(localStorage.getItem(PREFIX+"active")==="1" && !["budget","own","flip"].includes(document.documentElement.dataset.nicPage)){'
  if old not in s:raise SystemExit('Rental initialization anchor missing')
  s=s.replace(old,'if(document.documentElement.dataset.nicPage==="rent"){\n    setRentMode(true);\n  }else '+old,1)
  mode=re.search(r'data-nic-page="([^"]+)"',s)
  if mode and mode[1] in indices:
   mode=mode[1];variants=json.loads(re.search(r'id="nic-header-variants">(.*?)</script>',s,re.S)[1]);title,subtitle=variants[indices[mode]]
   s=re.sub(r'(<h1\b[^>]*id="heroTitle"[^>]*>).*?(</h1>)',lambda m:m[1]+title+m[2],s,count=1,flags=re.S)
   s=re.sub(r'(<p\b[^>]*id="heroText"[^>]*>).*?(</p>)',lambda m:m[1]+markup.escape(subtitle)+m[2],s,count=1,flags=re.S)
   visible={'budgetSection':mode=='budget','rentSection':mode=='rent','dealCalculatorContent':mode in ['own','flip']}
   def visibility(m):
    tag=m[0];id=re.search(r'\bid="([^"]+)"',tag)[1];c=re.search(r'\bclass="([^"]*)"',tag);classes=c[1].split() if c else []
    classes=[x for x in classes if x!='mode-hidden']
    if not visible[id]:classes.append('mode-hidden')
    return re.sub(r'\bclass="[^"]*"','class="'+' '.join(classes)+'"',tag,count=1) if c else tag[:-1]+' class="'+' '.join(classes)+'">'
   s=re.sub(r'<(?:div|section)\b(?=[^>]*\bid="(?:budgetSection|rentSection|dealCalculatorContent)")[^>]*>',visibility,s)
   def radio(m):
    tag=re.sub(r'\schecked(?:="[^"]*")?','',m[0]);value=re.search(r'\bvalue="([^"]+)"',tag)
    if value and value[1]==mode:tag=tag[:-1]+' checked>'
    return tag
   s=re.sub(r'<input\b(?=[^>]*\bname="dealType")[^>]*>',radio,s)
 page.write_text(s)
print('Explicit calculator routes render their requested mode and layout before deferred initialization')
