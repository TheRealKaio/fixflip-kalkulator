from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

old='''  function clearRent(){
    Object.keys(localStorage).forEach(function(key){
      if(key.startsWith(PREFIX)) localStorage.removeItem(key);
    });
    fieldIds.forEach(function(id){
      const el=document.getElementById(id);
      if(el) el.value=defaults[id];
    });
    localStorage.setItem(PREFIX+"active","1");
    renderRent();
  }'''

new='''  function clearRent(){
    Object.keys(localStorage).forEach(function(key){
      if(key.startsWith(PREFIX)) localStorage.removeItem(key);
    });
    fieldIds.forEach(function(id){
      const el=document.getElementById(id);
      if(el) el.value=defaults[id];
    });
    localStorage.removeItem("ff_rent_interest_manual");
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
    });
  }'''

if old not in s:
    raise SystemExit("rental clearRent anchor missing")
s=s.replace(old,new,1)

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
