from pathlib import Path
import sys
import re

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

pattern=r'(  function clearRent\(\)\{)(.*?)(\n  \}\n\n  function initState\(\)\{)'
m=re.search(pattern,s,re.S)
if not m:
    raise SystemExit("rental clearRent function missing")

body=m.group(2)
if 'localStorage.removeItem("ff_rent_interest_manual");' not in body:
    anchor='''    localStorage.setItem(PREFIX+"active","1");
    renderRent();'''
    replacement='''    localStorage.removeItem("ff_rent_interest_manual");
    localStorage.setItem(PREFIX+"active","1");
    renderRent();

    // Nach einem Reset den aktuellen Referenzzins erneut laden.
    // Der feste Defaultwert 4,00 % dient nur bis die Referenz geladen ist.
    Promise.resolve(initializeReferenceInterest()).then(function(){
      saveRent();
      renderRent();
    }).catch(function(){
      saveRent();
      renderRent();
    });'''
    if anchor not in body:
        raise SystemExit("rental clearRent reset anchor missing")
    body=body.replace(anchor,replacement,1)

s=s[:m.start()]+m.group(1)+body+m.group(3)+s[m.end():]

s=s.replace("V8.306","V8.307")
s=s.replace("service-worker.js?v=8.306","service-worker.js?v=8.307")

required=[
  'localStorage.removeItem("ff_rent_interest_manual");',
  'Promise.resolve(initializeReferenceInterest())',
  'saveRent();',
  'renderRent();',
  "V8.307",
  "service-worker.js?v=8.307"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.307 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.307 rental reset reloads reference interest")
