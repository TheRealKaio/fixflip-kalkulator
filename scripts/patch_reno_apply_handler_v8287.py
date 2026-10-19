from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old_legacy='''$("saveTrades").addEventListener("click",()=>{
  trades.forEach(t=>{
    localStorage.setItem("ff_trade_"+t.key, String(tradeValues[t.key]||0));
    localStorage.setItem("ff_trade_manual_"+t.key, manualTrades.has(t.key) ? "1":"0");
  });
  syncRenoTotal(); render(); renoBackdrop.classList.remove("show");
  $("openReno").textContent="+";
  $("openReno").setAttribute("aria-expanded","false");
  $("openReno").setAttribute("aria-label","Sanierungsgewerke öffnen");
});
'''
if old_legacy not in s:
    raise SystemExit("V8.287 legacy saveTrades handler missing")
s=s.replace(old_legacy,"",1)

old_state='''  const saveButton=document.getElementById("saveTrades");
  if(saveButton){
    saveButton.addEventListener("click",function(){
      storeCurrentRenoState();
    },true);
  }
'''
new_state='''  const saveButton=document.getElementById("saveTrades");
  if(saveButton){
    saveButton.addEventListener("click",function(event){
      event.preventDefault();
      event.stopImmediatePropagation();

      // Einen eindeutigen Übernehmen-Workflow verwenden:
      // aktuellen Rechnerzustand speichern, Summe aktualisieren und Panel schließen.
      storeCurrentRenoState();
      trades.forEach(function(t){
        localStorage.setItem("ff_trade_"+t.key,String(Number(tradeValues[t.key])||0));
        localStorage.setItem("ff_trade_manual_"+t.key,manualTrades.has(t.key)?"1":"0");
      });
      syncRenoTotal();
      try{render();}catch(_err){}

      const panel=document.getElementById("renoBackdrop");
      const toggle=document.getElementById("openReno");
      if(panel) panel.classList.remove("show");
      if(toggle){
        toggle.textContent="+";
        toggle.setAttribute("aria-expanded","false");
        toggle.setAttribute("aria-label","Sanierungsgewerke öffnen");
      }
    },true);
  }
'''
if old_state not in s:
    raise SystemExit("V8.287 namespace save handler missing")
s=s.replace(old_state,new_state,1)

s=s.replace("V8.286","V8.287")
s=s.replace("service-worker.js?v=8.286","service-worker.js?v=8.287")

required=[
    'event.stopImmediatePropagation();',
    'storeCurrentRenoState();',
    'panel.classList.remove("show");',
    'toggle.setAttribute("aria-expanded","false");',
    'localStorage.setItem("ff_trade_"+t.key,String(Number(tradeValues[t.key])||0));',
    'V8.287',
    'service-worker.js?v=8.287'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.287 verification failed: "+", ".join(missing))

if '$("saveTrades").addEventListener("click",()=>{' in s:
    raise SystemExit("V8.287 duplicate legacy save handler still present")

path.write_text(s,encoding="utf-8")
print("V8.287 renovation apply button uses one reliable save-and-close handler")
