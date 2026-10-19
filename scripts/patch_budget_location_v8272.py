from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Ort des Objekts als erstes Feld in den Budget-Finanzierungsannahmen.
grid_anchor='''        <div class="budget-grid three">
          <div class="field"><label>Finanzierungsreserve</label>'''
grid_new='''        <div class="budget-grid three">
          <div class="field">
            <label>Ort des Objekts</label>
            <div class="input-wrap">
              <select id="budgetState"></select>
            </div>
            <div class="mini" id="budgetStateTaxNote">Grunderwerbsteuer wird zu den Kaufnebenkosten addiert.</div>
          </div>
          <div class="field"><label>Finanzierungsreserve</label>'''
replace_once(grid_anchor,grid_new,"budget state field")

# Kaufnebenkosten-Hinweis präzisieren.
replace_once(
'''            <div class="mini">inkl. Steuer, Notar, Makler</div>''',
'''            <div class="mini" id="budgetAncillaryNote">zzgl. Grunderwerbsteuer gemäß Ort des Objekts</div>''',
"budget ancillary note"
)

# 2) Eigene ID persistieren.
replace_once(
'''  "budgetSafetyReserve","budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"
];''',
'''  "budgetSafetyReserve","budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetAncillaryPct","budgetExtraCostsPct"
];''',
"budget persist state"
)

# 3) Bundesland-Dropdown aus derselben states-Tabelle wie Eigennutzung befüllen.
state_init_anchor='''const budgetExpenseManual = {};
let budgetAutoUpdating = false;

function syncBudgetSafetyReserve(){'''
state_init_new='''const budgetExpenseManual = {};
let budgetAutoUpdating = false;

function initBudgetState(){
  const el=$("budgetState");
  if(!el) return;
  if(el.options.length===0){
    Object.keys(states).forEach(name=>{
      const option=document.createElement("option");
      option.value=name;
      option.textContent=name+" · "+states[name].toFixed(1).replace(".",",")+" %";
      el.appendChild(option);
    });
  }
  const saved=localStorage.getItem("ff_budget_budgetState");
  el.value=(saved && states[saved]!==undefined) ? saved : "Hamburg";
  if(!el.value) el.value="Hamburg";
}

function syncBudgetSafetyReserve(){'''
replace_once(state_init_anchor,state_init_new,"budget state init")

# 4) Kaufnebenkosten = eingegebener Satz + Grunderwerbsteuer des ausgewählten Bundeslands.
model_old='''  const equity=Math.max(0,budgetVal("budgetEquity"));
  const ancillaryPct=Math.max(0,budgetVal("budgetAncillaryPct")/100);
  const extraCostsPct=Math.max(0,budgetVal("budgetExtraCostsPct")/100);
  const allIn=loan+equity;'''
model_new='''  const equity=Math.max(0,budgetVal("budgetEquity"));
  const ancillaryBasePct=Math.max(0,budgetVal("budgetAncillaryPct")/100);
  const budgetStateName=$("budgetState") && states[$("budgetState").value]!==undefined ? $("budgetState").value : "Hamburg";
  const transferTaxPct=Math.max(0,(states[budgetStateName]||0)/100);
  const ancillaryPct=ancillaryBasePct+transferTaxPct;
  const extraCostsPct=Math.max(0,budgetVal("budgetExtraCostsPct")/100);
  const allIn=loan+equity;'''
replace_once(model_old,model_new,"budget ancillary state tax")

return_old='''    interestPct,repaymentPct,loan,loanMonthlyRate,equity,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,'''
return_new='''    interestPct,repaymentPct,loan,loanMonthlyRate,equity,ancillaryBasePct,transferTaxPct,budgetStateName,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,'''
replace_once(return_old,return_new,"budget state return")

# 5) Hinweise dynamisch mit Basis + GrESt + Gesamt anzeigen.
render_anchor='''  if($("budgetAdditionalBuffer")) $("budgetAdditionalBuffer").textContent=eur(m.additionalBuffer);
  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);'''
render_new='''  if($("budgetAdditionalBuffer")) $("budgetAdditionalBuffer").textContent=eur(m.additionalBuffer);
  if($("budgetStateTaxNote")){
    $("budgetStateTaxNote").textContent="Grunderwerbsteuer "+new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)+" % wird zu den Kaufnebenkosten addiert.";
  }
  if($("budgetAncillaryNote")){
    $("budgetAncillaryNote").textContent=
      new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryBasePct*100)
      +" % + "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)
      +" % GrESt = "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)
      +" % gesamt";
  }
  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);'''
replace_once(render_anchor,render_new,"budget state render notes")

# 6) Initialisierung vor dem Laden gespeicherter Budgetwerte.
load_call='''load();
loadBudget();
initializeTrades(false);'''
load_new='''load();
initBudgetState();
loadBudget();
initializeTrades(false);'''
replace_once(load_call,load_new,"budget init call")

# Sicherstellen, dass loadBudget ohne gespeicherten Wert Hamburg behält.
load_end='''  syncBudgetSuggestions();
  syncBudgetSafetyReserve();
}'''
load_end_new='''  if($("budgetState") && (!localStorage.getItem("ff_budget_budgetState") || states[$("budgetState").value]===undefined)){
    $("budgetState").value="Hamburg";
  }
  syncBudgetSuggestions();
  syncBudgetSafetyReserve();
}'''
replace_once(load_end,load_end_new,"budget state load default")

# 7) Reset setzt Ort auf Hamburg und speichert keinen Altwert.
reset_anchor='''  if($("budgetEquity")) $("budgetEquity").value="0";
  if($("budgetAncillaryPct")) $("budgetAncillaryPct").value="12.00";'''
reset_new='''  if($("budgetEquity")) $("budgetEquity").value="0";
  initBudgetState();
  if($("budgetState")) $("budgetState").value="Hamburg";
  if($("budgetAncillaryPct")) $("budgetAncillaryPct").value="12.00";'''
replace_once(reset_anchor,reset_new,"budget reset Hamburg")

# 8) PDF zeigt Ort, Grunderwerbsteuer und Gesamt-Kaufnebenkosten.
pdf_old='''  line("Zins p.a.",pdfPercent(budgetVal("budgetInterest")));
  line("Tilgung p.a.",pdfPercent(budgetVal("budgetRepayment")));
  line("Kaufnebenkosten",pdfPercent(budgetVal("budgetAncillaryPct")));
  line("Sonstige Kosten",pdfPercent(budgetVal("budgetExtraCostsPct")));'''
pdf_new='''  line("Ort des Objekts",m.budgetStateName);
  line("Grunderwerbsteuer",new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)+" %");
  line("Zins p.a.",pdfPercent(budgetVal("budgetInterest")));
  line("Tilgung p.a.",pdfPercent(budgetVal("budgetRepayment")));
  line("Kaufnebenkosten gesamt",new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)+" %");
  line("Sonstige Kosten",pdfPercent(budgetVal("budgetExtraCostsPct")));'''
replace_once(pdf_old,pdf_new,"budget PDF location and ancillary")

# Version bump.
s=s.replace("V8.271","V8.272")
s=s.replace("service-worker.js?v=8.271","service-worker.js?v=8.272")

required=[
    'id="budgetState"',
    '"budgetState","budgetAncillaryPct"',
    'function initBudgetState(){',
    'el.value=(saved && states[saved]!==undefined) ? saved : "Hamburg";',
    'const transferTaxPct=Math.max(0,(states[budgetStateName]||0)/100);',
    'const ancillaryPct=ancillaryBasePct+transferTaxPct;',
    'if($("budgetState")) $("budgetState").value="Hamburg";',
    'line("Ort des Objekts",m.budgetStateName);',
    'Kaufnebenkosten gesamt',
    'V8.272',
    'service-worker.js?v=8.272'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.272 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.272 budget location and transfer tax applied")
