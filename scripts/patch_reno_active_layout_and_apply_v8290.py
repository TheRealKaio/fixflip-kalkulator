from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

marker='// V8.289 separated renovation state, automatic proposal tracking and buffer sync'
idx=s.find(marker)
if idx<0:
    raise SystemExit("V8.290 active renovation-state marker missing")

head=s[:idx]
tail=s[idx:]

# Active renderTrades: give the two groups explicit classes.
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

s=head+tail

# Remove the original value-changing proposal listener from the older renovation script.
legacy_original='''    btn.textContent="Vorschlag übernehmen";
    btn.addEventListener("click",applyTradeSuggestions);

    right.appendChild(btn);'''
legacy_original_new='''    btn.textContent="Vorschlag übernehmen";

    right.appendChild(btn);'''
if legacy_original not in s:
    raise SystemExit("V8.290 original proposal listener anchor missing")
s=s.replace(legacy_original,legacy_original_new,1)

# Remove the old signature-only click listener as well. The authoritative state script
# below already writes the current proposal signature.
legacy_signature='''  ensureRenoSuggestionUi();
  const renoButton=document.getElementById("applyTradeSuggestions");
  if(renoButton){
    renoButton.addEventListener("click",function(){
      const data=renoSuggestionData();
      localStorage.setItem(renoSignatureKey(),data.signature);
      setTimeout(updateRenoSuggestionTotal,0);
    });
  }
'''
if legacy_signature not in s:
    raise SystemExit("V8.290 legacy proposal signature listener anchor missing")
s=s.replace(legacy_signature,'''  ensureRenoSuggestionUi();
''',1)

# A deliberate proposal takeover must replace reset/manual zero values too.
old_apply_logic='''  function applyCurrentSuggestions(){
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
  }'''
new_apply_logic='''  function applyCurrentSuggestions(){
    const mode=renoMode();
    if(!mode) return;
    setSuggestionsActive(true,mode);
    trades.forEach(function(t){
      // "Vorschlag übernehmen" ersetzt die aktuellen Positionswerte bewusst.
      // Danach gelten sie wieder als automatisch, bis der Nutzer sie manuell ändert.
      manualTrades.delete(t.key);
      tradeValues[t.key]=suggestionForTradeV8241(t);
      storeTrade(t);
    });
    localStorage.setItem("ff_"+mode+"_reno_suggestions_applied_signature",suggestionSignature());
    storeCurrentRenoState(mode);
    renderTrades();
    syncRenoTotal();
    try{render();}catch(_err){}
  }'''
if old_apply_logic not in s:
    raise SystemExit("V8.290 active proposal logic anchor missing")
s=s.replace(old_apply_logic,new_apply_logic,1)

# Keep one authoritative apply handler, but allow later dependent UI handlers to run.
old_handler='''  const applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      event.stopImmediatePropagation();
      applyCurrentSuggestions();
    },true);
  }'''
new_handler='''  const applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      applyCurrentSuggestions();
    });
  }'''
if old_handler not in s:
    raise SystemExit("V8.290 authoritative proposal handler anchor missing")
s=s.replace(old_handler,new_handler,1)

s=s.replace("V8.289","V8.290")
s=s.replace("service-worker.js?v=8.289","service-worker.js?v=8.290")

required=[
    'class="trade-row trade-row-sqm"',
    'class="trade-row trade-row-fixed"',
    'manualTrades.delete(t.key);',
    'applyButton.addEventListener("click",function(event){',
    'event.preventDefault();\n      applyCurrentSuggestions();',
    'V8.290',
    'service-worker.js?v=8.290'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.290 verification failed: "+", ".join(missing))

if 'btn.addEventListener("click",applyTradeSuggestions);' in s:
    raise SystemExit("V8.290 old value-changing proposal listener still present")
if 'event.stopImmediatePropagation();\n      applyCurrentSuggestions();' in s:
    raise SystemExit("V8.290 proposal handler still blocks dependent updates")

path.write_text(s,encoding="utf-8")
print("V8.290 active renovation layout and proposal takeover corrected")
