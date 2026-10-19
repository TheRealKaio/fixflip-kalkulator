from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

replace_once(
'''          <label>Verkaufspreis nach Sanierung <span class="hint">deine Markterwartung · editierbar</span></label>''',
'''          <label>Verkaufspreis nach Sanierung <span class="hint">automatisch kalkuliert · editierbar</span></label>''',
"sale field hint"
)

replace_once(
'''            <strong>Hinweis:</strong> Trage hier deine realistische Verkaufserwartung nach der Sanierung ein. Ziel-Gewinn und Ziel-Marge verändern diesen Wert nicht; die Ampel zeigt dir stattdessen, ob deine Ziele mit dieser Verkaufserwartung erreichbar sind.''',
'''            <strong>Hinweis:</strong> Der erwartete Verkaufspreis wird automatisch aus den aktuellen Projekt- und Finanzierungskosten kalkuliert. Änderungen am Eigenkapital, an der Finanzierung oder an den Projektkosten aktualisieren den Wert automatisch. Du kannst ihn weiterhin manuell überschreiben.''',
"sale field note"
)

old_save='''  function saveValue(){
    const el=field();
    if(!el) return;
    localStorage.setItem(STORAGE_KEY,String(el.value||"0"));
  }'''
new_save='''  function saveValue(){
    const el=field();
    if(!el) return;
    const value=String(el.value||"0");
    localStorage.setItem(STORAGE_KEY,value);
    localStorage.setItem("ff_flipSaleTarget",value);
  }'''
replace_once(old_save,new_save,"sale persistence")

old_queue='''  function queueFormulaRefresh(target){
    if(currentDealType()!=="flip" || !isFormulaChange(target)) return;
    // Der erwartete Verkaufspreis ist eine Nutzereinschätzung und bleibt bestehen.
    // Änderungen der Kosten/Ziele aktualisieren nur Break-even, Zielpreis und Ampel.
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      try{ render(); }catch(_err){}
    },0);
  }'''
new_queue='''  function queueFormulaRefresh(target){
    if(currentDealType()!=="flip" || !isFormulaChange(target)) return;
    // Automatische Verkaufserwartung: nach allen kosten- und finanzierungsrelevanten
    // Änderungen neu berechnen, ins Feld schreiben und persistent speichern.
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      if(recalcAndStore()){
        try{ render(); }catch(_err){}
      }
    },0);
  }'''
replace_once(old_queue,new_queue,"automatic sale recalculation")

old_mode='''        if(currentDealType()==="flip"){
          if(!loadValue()) recalcAndStore();
          try{ render(); }catch(_err){}
        }'''
new_mode='''        if(currentDealType()==="flip"){
          loadValue();
          recalcAndStore();
          try{ render(); }catch(_err){}
        }'''
replace_once(old_mode,new_mode,"mode switch sale refresh")

old_initial='''  // Initial: gespeicherten Marktwert laden. Nur ohne gespeicherten Wert
  // wird einmalig der kostendeckende Break-even als Startwert vorbelegt.
  if(currentDealType()==="flip"){
    const hadSavedValue=loadValue();
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      if(!hadSavedValue) recalcAndStore();
      try{ render(); }catch(_err){}
    },0);
  }'''
new_initial='''  // Initial: gespeicherten Wert kurz laden und anschließend immer mit den
  // aktuell gültigen Projekt- und Finanzierungsdaten neu berechnen und speichern.
  if(currentDealType()==="flip"){
    loadValue();
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      recalcAndStore();
      try{ render(); }catch(_err){}
    },0);
  }'''
replace_once(old_initial,new_initial,"initial automatic sale refresh")

# Programmatic renovation changes must also recalculate the expected sale.
programmatic_marker='''  // Programmgesteuerte Änderungen der Sanierung ebenfalls synchronisieren.
  ["applyTradeSuggestions","saveTrades","resetTrades"].forEach(function(id){'''
pos=s.find(programmatic_marker)
if pos<0:
    raise SystemExit("programmatic renovation sale marker missing")
old_body='''        if(currentDealType()!=="flip") return;
        try{ render(); }catch(_err){}'''
idx=s.find(old_body,pos)
if idx<0:
    raise SystemExit("programmatic renovation refresh body missing")
new_body='''        if(currentDealType()!=="flip") return;
        recalcAndStore();
        try{ render(); }catch(_err){}'''
s=s[:idx]+new_body+s[idx+len(old_body):]

s=s.replace("V8.290","V8.291")
s=s.replace("service-worker.js?v=8.290","service-worker.js?v=8.291")

required=[
    'automatisch kalkuliert · editierbar',
    'Änderungen am Eigenkapital, an der Finanzierung oder an den Projektkosten aktualisieren den Wert automatisch.',
    'localStorage.setItem("ff_flipSaleTarget",value);',
    'if(recalcAndStore()){',
    '"financeAcquisition","ltv","ownEquityInput","maxEquity","interest","repayment"',
    'loadValue();\n          recalcAndStore();',
    'recacz',
    'V8.291',
    'service-worker.js?v=8.291'
]
# custom checks except intentional dummy
required=[x for x in required if x!='recacz']
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.291 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.291 expected sale now recalculates and persists with financing/equity changes")
