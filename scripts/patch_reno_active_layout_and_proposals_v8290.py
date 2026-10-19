from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

marker='// V8.289 separated renovation state, automatic proposal tracking and buffer sync'
idx=s.find(marker)
if idx<0:
    raise SystemExit("V8.290 active renovation-state script marker missing")

head=s[:idx]
tail=s[idx:]

# 1) Apply the mobile row classes to the ACTUALLY ACTIVE renderTrades implementation.
old_sqm="""      out+='<div class="trade-row"><div class="trade-top"><div>'+"""
new_sqm="""      out+='<div class="trade-row trade-row-sqm"><div class="trade-top"><div>'+"""
if old_sqm not in tail:
    raise SystemExit("V8.290 active sqm row anchor missing")
tail=tail.replace(old_sqm,new_sqm,1)

old_fixed="""      out+='<div class="trade-row"><div class="trade-top">'+
        '<div class="trade-copy">"""
new_fixed="""      out+='<div class="trade-row trade-row-fixed"><div class="trade-top">'+
        '<div class="trade-copy">"""
if old_fixed not in tail:
    raise SystemExit("V8.290 active fixed row anchor missing")
tail=tail.replace(old_fixed,new_fixed,1)

# 2) "Vorschlag übernehmen" means exactly that: overwrite the current renovation
# rows with the current proposal and clear manual flags. This also fixes the reset
# state where all zero values had deliberately been marked manual.
old_apply='''  function applyCurrentSuggestions(){
    const mode=renoMode();
    if(!mode) return;
    setSuggestionsActive(true,mode);
    trades.forEach(function(t){
      // Bewusste manuelle Eingaben haben Vorrang.
      if(manualTrades.has(t.key)) return;
      tradeValues[t.key]=suggestionForTradeV8241(t);
      storeTrade(t);
    });
    localStorage.setItem("ff_"+mode+"_reno_suggestions_applied_signature",suggestionSignature());
    storeCurrentRenoState(mode);
    renderTrades();
    syncRenoTotal();
    try{render();}catch(_err){}
  }

  const applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      event.stopImmediatePropagation();
      applyCurrentSuggestions();
    },true);
  }
'''
new_apply='''  function applyCurrentSuggestions(){
    const mode=renoMode();
    if(!mode) return;
    setSuggestionsActive(true,mode);
    trades.forEach(function(t){
      // Eine bewusste Vorschlagübernahme ersetzt die aktuellen Positionswerte.
      // Danach gelten die Werte wieder als automatisch, bis der Nutzer sie ändert.
      manualTrades.delete(t.key);
      tradeValues[t.key]=suggestionForTradeV8241(t);
      storeTrade(t);
    });
    localStorage.setItem("ff_"+mode+"_reno_suggestions_applied_signature",suggestionSignature());
    storeCurrentRenoState(mode);
    renderTrades();
    syncRenoTotal();
    try{render();}catch(_err){}
  }

  // Frühere Skripte haben dem Button bereits Listener gegeben. Durch Klonen werden
  // diese alten Listener entfernt; anschließend gibt es genau einen Übernahme-Handler.
  let applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    const cleanApplyButton=applyButton.cloneNode(true);
    applyButton.replaceWith(cleanApplyButton);
    applyButton=cleanApplyButton;
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      applyCurrentSuggestions();
    });
  }
'''
if old_apply not in tail:
    raise SystemExit("V8.290 active proposal handler anchor missing")
tail=tail.replace(old_apply,new_apply,1)

s=head+tail

s=s.replace("V8.289","V8.290")
s=s.replace("service-worker.js?v=8.289","service-worker.js?v=8.290")

required=[
    'class="trade-row trade-row-sqm"',
    'class="trade-row trade-row-fixed"',
    'manualTrades.delete(t.key);',
    'const cleanApplyButton=applyButton.cloneNode(true);',
    'applyButton.replaceWith(cleanApplyButton);',
    'applyCurrentSuggestions();',
    'V8.290',
    'service-worker.js?v=8.290'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.290 verification failed: "+", ".join(missing))

# Active handler must no longer suppress later dependent update handlers.
active=s[s.find(marker):]
if 'event.stopImmediatePropagation();\n      applyCurrentSuggestions();' in active:
    raise SystemExit("V8.290 active proposal handler still blocks dependent listeners")

path.write_text(s,encoding="utf-8")
print("V8.290 active renovation layout and proposal takeover corrected")
