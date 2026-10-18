from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Begrifflich sauber trennen: verfügbare Liquidität vs. direkt eingesetztes EK.
replace_once(
    '<div class="field"><label>Max. eigenes Geld <span class="hint">im Projekt</span> <button class="info-btn inline-info" type="button" data-info="maxEquityInfo">i</button></label><div class="input-wrap"><input id="maxEquity" inputmode="decimal" value="100000"><span class="unit">€</span></div></div>',
    '<div class="field"><label>Verfügbares Eigenkapital <span class="hint">für das Projekt</span> <button class="info-btn inline-info" type="button" data-info="maxEquityInfo">i</button></label><div class="input-wrap"><input id="maxEquity" inputmode="decimal" value="100000"><span class="unit">€</span></div><div class="mini">Deine harte Liquiditätsgrenze für Finanzierung und Projektlaufzeit.</div></div>',
    "available equity field"
)

s=s.replace(
    'Prüfe unter <strong>„Projektziele &amp; Steuer“ → „Max. eigenes Geld“</strong>, ob dein persönliches Kapital-Limit zum Projekt passt.',
    'Das eingesetzte Eigenkapital reduziert direkt die Kreditsumme. Nicht eingesetztes verfügbares Eigenkapital bleibt als Liquiditätsreserve für den Projektverlauf.',
    1
)

replace_once(
'''maxEquityInfo:{
 title:"Was bedeutet Max. eigenes Geld?",
 body:"Dieser Wert ist deine persönliche Obergrenze dafür, wie viel eigenes Geld insgesamt im Projekt gebunden sein darf. Er ist nicht dasselbe wie das Eingabefeld „Eigenkapital eingesetzt“.",
 plain:"„Eigenkapital eingesetzt“ reduziert aktiv die Kreditsumme. „Eigenes Geld im Projekt“ zeigt den tatsächlich benötigten Kapitalbedarf. „Max. eigenes Geld“ prüft nur, ob dieser Kapitalbedarf innerhalb deiner persönlichen Grenze liegt.",
''',
'''maxEquityInfo:{
 title:"Was bedeutet verfügbares Eigenkapital?",
 body:"Dieser Wert ist deine harte Liquiditätsgrenze für das gesamte Projekt. Ein Teil kann direkt als Eigenkapital in die Finanzierung fließen; der verbleibende Teil steht als Reserve für nicht finanzierte Kosten, Zinsen und laufende Belastungen zur Verfügung.",
 plain:"„Eigenkapital eingesetzt“ ist nur der Teil, der direkt die Kreditsumme reduziert. „Dein Geld im Projekt“ zeigt den gesamten rechnerischen Eigenkapitalbedarf. Übersteigt dieser Bedarf dein verfügbares Eigenkapital, ist das Projekt mit den aktuellen Annahmen nicht aus eigener Liquidität darstellbar.",
''',
    "max equity info"
)

s=s.replace(
    'Wichtig: Der Wert „Max. eigenes Geld“ unter „Projektziele & Steuer“ ist nur deine persönliche Obergrenze. Er verändert die Berechnung nicht. Wenn du z. B. maximal 50.000 € einsetzen möchtest, der Deal aber 72.000 € eigenes Geld benötigt, zeigt die App weiterhin 72.000 € an und markiert das Ziel als nicht erreicht.',
    'Wichtig: „Verfügbares Eigenkapital“ ist deine harte Liquiditätsgrenze. „Eigenkapital eingesetzt“ ist der Teil davon, der direkt die Kreditsumme reduziert. Der übrige Betrag bleibt als Reserve. Benötigt das Projekt insgesamt mehr eigenes Geld als verfügbar ist, wird das Kapitalziel rot markiert.',
    1
)

# Dynamische Ergebnisnotiz.
replace_once(
    '<div class="name">Dein Geld im Projekt</div><div class="value" id="equity">–</div><div class="note">Eigenkapitalbedarf</div>',
    '<div class="name">Dein Geld im Projekt</div><div class="value" id="equity">–</div><div class="note" id="equityNeedNote">gesamter Eigenkapitalbedarf</div>',
    "equity KPI note"
)

old_note = '''  if($("equityCapitalNote")){
    const showEquityCapitalNote = currentDealType()==="flip" && val("ownEquityInput") > 0;
    $("equityCapitalNote").classList.toggle("show", showEquityCapitalNote);
    if($("equityCapitalNeed")){
      $("equityCapitalNeed").textContent = showEquityCapitalNote
        ? " Der Kalkulator ermittelt aktuell rund " + eur(m.equity) + " eigenes Geld, das während der Projektlaufzeit insgesamt im Projekt gebunden bzw. benötigt wird."
        : "";
    }
  }'''
new_note = '''  if($("equityCapitalNote")){
    const showEquityCapitalNote = currentDealType()==="flip";
    $("equityCapitalNote").classList.toggle("show", showEquityCapitalNote);
    if($("equityCapitalNeed")){
      const available=Math.max(0,val("maxEquity"));
      const deployed=Math.max(0,m.ownEquityInput||0);
      const additional=Math.max(0,m.equity-deployed);
      const reserve=available-m.equity;
      $("equityCapitalNeed").textContent = showEquityCapitalNote
        ? " Verfügbar: "+eur(available)+" · davon Finanzierung: "+eur(deployed)+" · weiterer Projektbedarf: "+eur(additional)+" · "+(reserve>=0 ? "verbleibende Reserve: "+eur(reserve) : "Fehlbetrag: "+eur(Math.abs(reserve)))
        : "";
    }
  }
  if($("equityNeedNote") && currentDealType()==="flip"){
    const reserve=Math.max(0,val("maxEquity"))-m.equity;
    $("equityNeedNote").textContent = reserve>=0
      ? "Eigenkapitalbedarf · Reserve "+eur(reserve)
      : "Eigenkapitalbedarf · Fehlbetrag "+eur(Math.abs(reserve));
  }'''
replace_once(old_note,new_note,"equity capital note render")

# 2) Eigenkapital eingesetzt ist eine Teilmenge des verfügbaren Eigenkapitals.
equity_guard = r'''
function syncEquityAllocationToAvailable(){
  if(currentDealType()!=="flip" || !$("ownEquityInput") || !$("maxEquity")) return false;
  const cap=Math.max(0,val("maxEquity"));
  const input=$("ownEquityInput");
  input.max=String(cap);
  const deployed=Math.max(0,val("ownEquityInput"));
  if(deployed<=cap) return false;
  input.value=String(cap);
  localStorage.setItem("ff_flip_equity_input",String(cap));
  localStorage.setItem("ff_ownEquityInput",String(cap));
  return true;
}

["ownEquityInput","maxEquity"].forEach(function(id){
  const el=$(id);
  if(!el) return;
  el.addEventListener("input",function(){
    if(syncEquityAllocationToAvailable()){
      try{ render(); }catch(_err){}
    }
  });
  el.addEventListener("change",function(){
    if(syncEquityAllocationToAvailable()){
      try{ render(); }catch(_err){}
    }
  });
});
syncEquityAllocationToAvailable();

'''
anchor='function render(){'
if equity_guard not in s:
    if anchor not in s:
        raise SystemExit("equity allocation guard anchor missing")
    s=s.replace(anchor,equity_guard+anchor,1)

# 3) Kapitalgrenze ist eine harte Ampel: grün oder rot, nicht gelb.
css_anchor='.kpi.goal-miss{background:#fff7cc;border-color:#f2c94c;box-shadow:0 0 0 2px rgba(242,201,76,.12)}'
if css_anchor not in s:
    raise SystemExit("goal-miss css anchor missing")
s=s.replace(
    css_anchor,
    css_anchor+'\n.kpi.goal-stop{background:#fdecec;border-color:#e8a0a0;box-shadow:0 0 0 2px rgba(232,160,160,.14)}',
    1
)
value_css='.kpi.goal-miss .value{color:#8a5a00}'
if value_css not in s:
    raise SystemExit("goal-miss value css anchor missing")
s=s.replace(value_css,value_css+'\n.kpi.goal-stop .value{color:#b91c1c}',1)

replace_once(
'''  ["kpiProfit","kpiMargin","kpiEquity","kpiRoi","kpiMaxBuy"].forEach(id=>{
    const el=$(id);
    if(el) el.classList.remove("goal-miss");
  });''',
'''  ["kpiProfit","kpiMargin","kpiEquity","kpiRoi","kpiMaxBuy"].forEach(id=>{
    const el=$(id);
    if(el) el.classList.remove("goal-miss","goal-stop");
  });''',
    "goal class reset"
)

replace_once(
    '  const missEquity = !isOwnUse && maxEquity > 0 && m.equity > maxEquity + moneyTolerance;',
    '  const missEquity = !isOwnUse && m.equity > Math.max(0,maxEquity) + moneyTolerance;',
    "hard equity miss"
)

replace_once(
    '  if(missEquity && $("kpiEquity")) $("kpiEquity").classList.add("goal-miss");',
    '  if(missEquity && $("kpiEquity")) $("kpiEquity").classList.add("goal-stop");',
    "red equity KPI"
)

old_decision='''  let cls="go",emoji="🟢",title="Sieht belastbar aus",text="Deine aktuellen Annahmen lassen ausreichend Abstand zu den Zielwerten.";
  if(m.profit<0 || m.safety<0){cls="stop";emoji="🔴";title="So nicht kaufen";text="Mit diesen Annahmen macht der Deal rechnerisch Verlust."}
  else if(missProfit || missMargin || missRoi || missEquity || missMaxBuy){cls="check";emoji="🟡";title="Noch verhandeln oder prüfen";text="Mindestens eines deiner Projektziele wird noch nicht erreicht."}'''
new_decision='''  let cls="go",emoji="🟢",title="Sieht belastbar aus",text="Deine aktuellen Annahmen lassen ausreichend Abstand zu den Zielwerten.";
  if(m.profit<0 || m.safety<0){cls="stop";emoji="🔴";title="So nicht kaufen";text="Mit diesen Annahmen macht der Deal rechnerisch Verlust."}
  else if(missEquity){cls="stop";emoji="🔴";title="Eigenkapital reicht nicht aus";text="Der errechnete Eigenkapitalbedarf übersteigt dein verfügbares Eigenkapital. Passe Finanzierung, Projektkosten oder Kapitalrahmen an."}
  else if(missProfit || missMargin || missRoi || missMaxBuy){cls="check";emoji="🟡";title="Noch verhandeln oder prüfen";text="Mindestens eines deiner Projektziele wird noch nicht erreicht."}'''
replace_once(old_decision,new_decision,"hard equity decision")

# PDF-Bezeichnungen und Liquiditätsreserve.
s=s.replace('page2Line("Max. eigenes Geld", pdfMoney(val("maxEquity")));',
            'page2Line("Verfügbares Eigenkapital", pdfMoney(val("maxEquity")));\n    page2Line("Verbleibende Liquiditätsreserve", pdfMoney(val("maxEquity")-m.equity));',
            1)

# Sichtbare Hilfetexte konsistent umbenennen.
s=s.replace('„Projektziele & Steuer“ → „Max. eigenes Geld“','„Projektziele & Steuer“ → „Verfügbares Eigenkapital“')

# Version bump.
s=s.replace("V8.256","V8.257")
s=s.replace("service-worker.js?v=8.256","service-worker.js?v=8.257")

required=[
    'Verfügbares Eigenkapital <span class="hint">für das Projekt</span>',
    'Deine harte Liquiditätsgrenze für Finanzierung und Projektlaufzeit.',
    'function syncEquityAllocationToAvailable(){',
    'input.max=String(cap);',
    'const additional=Math.max(0,m.equity-deployed);',
    'Fehlbetrag: "+eur(Math.abs(reserve))',
    '.kpi.goal-stop{',
    'const missEquity = !isOwnUse && m.equity > Math.max(0,maxEquity) + moneyTolerance;',
    '$("kpiEquity").classList.add("goal-stop")',
    'title="Eigenkapital reicht nicht aus"',
    'page2Line("Verfügbare'  # partial to avoid quote issues
]
missing=[token for token in required if token not in s]
if missing:
    raise SystemExit("V8.257 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.257 equity liquidity model applied")
