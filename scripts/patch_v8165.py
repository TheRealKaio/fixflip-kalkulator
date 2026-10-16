from pathlib import Path
import sys
import re

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
s = path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f"{label} target not found")
    s = s.replace(old, new, 1)

replace_once(
    '.market-check-card.collapsed .market-check-body{display:none}',
    '.market-check-card.collapsed .market-check-body{display:none}\n'
    '.budget-assumptions-body{display:block}\n'
    '.budget-assumptions-card.collapsed .budget-assumptions-body{display:none}\n'
    '.budget-assumptions-card .market-check-head h2{margin:0}\n'
    '.budget-rate-ratio{font-size:11px;font-weight:700;color:#365b96;margin-left:4px}\n'
    '.budget-rate-guidance{margin-top:8px;padding:9px 10px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;color:#52627a;font-size:11px;line-height:1.45}\n.budget-result-card.budget-loan-highlight{background:#fff7cc;border-color:#f1cf55;box-shadow:0 0 0 1px rgba(241,207,85,.18) inset}\n.budget-summary-row.rate-status-green{background:#eaf8ef;border-color:#8fd3a5}\n.budget-summary-row.rate-status-yellow{background:#fff7cc;border-color:#f1cf55}\n.budget-summary-row.rate-status-red{background:#fdecec;border-color:#e8a0a0}\n.budget-summary-row.rate-status-green .budget-rate-ratio,.budget-summary-row.rate-status-yellow .budget-rate-ratio,.budget-summary-row.rate-status-red .budget-rate-ratio{color:inherit}',
    "assumptions CSS"
)

# V8.172: All budget note boxes use the same neutral style as the orientation box.
old_budget_note_css = '.budget-note{margin-top:12px;padding:11px 12px;border-radius:13px;background:#fef3c7;border:1px solid #facc15;color:#475569;font-size:11px;line-height:1.45}'
new_budget_note_css = '.budget-note{margin-top:12px;padding:11px 12px;border-radius:13px;background:#f8fafc;border:1px solid #e2e8f0;color:#52627a;font-size:11px;line-height:1.45}'
if old_budget_note_css in s:
    s = s.replace(old_budget_note_css, new_budget_note_css, 1)

# Apply neutral styling to the residual-debt note if the old markup is still present.
# The source HTML may already contain the neutral-note class after earlier patches, so
# this step must be idempotent and must not abort the entire Pages build.
old_residual_note = (
    '        <div class="budget-note">\\n'
    '          Restschulden werden hier als Annuitätendarlehen mit konstanter Monatsrate und konstantem Zinssatz modelliert. Tatsächliche Konditionen, Zinsbindungen und Anschlussfinanzierungen können abweichen.\\n'
    '        </div>'
)
new_residual_note = (
    '        <div class="budget-note neutral-note">\\n'
    '          Restschulden werden hier als Annuitätendarlehen mit konstanter Monatsrate und konstantem Zinssatz modelliert. Tatsächliche Konditionen, Zinsbindungen und Anschlussfinanzierungen können abweichen.\\n'
    '        </div>'
)
if old_residual_note in s:
    s = s.replace(old_residual_note, new_residual_note, 1)


old_head = '''      <section class="card">
        <h2>3. Weitere Annahmen</h2>
        <div class="budget-grid three">'''
new_head = '''      <section class="card budget-assumptions-card collapsed" id="budgetAssumptionsSection">
        <div class="market-check-head">
          <h2>3. Weitere Annahmen</h2>
          <button type="button" class="plus-btn" id="budgetAssumptionsToggle" aria-expanded="false" aria-controls="budgetAssumptionsBody" aria-label="Weitere Annahmen öffnen">+</button>
        </div>
        <div class="budget-assumptions-body" id="budgetAssumptionsBody">
        <div class="budget-grid three">'''
replace_once(old_head, new_head, "assumptions header")

old_note = '''        <div class="budget-note">
          <strong>Hinweis:</strong> Der Budgetanteil bestimmt, welcher Anteil deines frei verfügbaren Monatsbudgets maximal für die Kreditrate eingesetzt wird. Der verbleibende Anteil bleibt als zusätzlicher monatlicher Puffer. Die Berechnung ist eine Orientierung und keine Finanzierungszusage einer Bank.
        </div>
      </section>'''
new_note = '''        <div class="budget-note">
          <strong>Hinweis:</strong> Der Budgetanteil bestimmt, welcher Anteil deines frei verfügbaren Monatsbudgets maximal für die Kreditrate eingesetzt wird. Der verbleibende Anteil bleibt als zusätzlicher monatlicher Puffer. Die Berechnung ist eine Orientierung und keine Finanzierungszusage einer Bank.
        </div>
        </div>
      </section>'''
if old_note in s:
    s = s.replace(old_note, new_note, 1)

replace_once(
    '          <div class="budget-summary-row highlight"><span>Maximal tragbare Kreditrate</span><strong id="budgetRate">–</strong></div>',
    '          <div class="budget-summary-row highlight" id="budgetRateRow"><span>Maximal tragbare Kreditrate <span class="budget-rate-ratio" id="budgetRateRatio"></span></span><strong id="budgetRate">–</strong></div>\n'
    '          <div class="budget-rate-guidance" id="budgetRateGuidance">Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten. Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung.</div>',
    "rate display"
)

old_render = '  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);'
new_render = '''  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);
  const budgetRatePct = m.net > 0 ? (m.monthlyRate / m.net) * 100 : 0;
  if($("budgetRateRatio")){
    $("budgetRateRatio").textContent = m.net > 0
      ? "(ca. " + new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(budgetRatePct) + " % vom Haushaltsnetto)"
      : "";
  }
  if($("budgetRateGuidance")){
    let budgetRateStatus = "";
    if(m.net > 0){
      budgetRateStatus = budgetRatePct <= 30 ? "komfortabel" : (budgetRatePct <= 35 ? "solide" : "erhöhte Belastung");
    }
    $("budgetRateGuidance").textContent = "Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten. Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung." + (budgetRateStatus ? " Aktuelle Einordnung: " + budgetRateStatus + "." : "");
  }
  if($("budgetRateRow")){
    const row = $("budgetRateRow");
    row.classList.remove("rate-status-green","rate-status-yellow","rate-status-red");
    if(m.net > 0){
      row.classList.add(budgetRatePct <= 30 ? "rate-status-green" : (budgetRatePct <= 35 ? "rate-status-yellow" : "rate-status-red"));
    }
  }'''
replace_once(old_render, new_render, "rate render")

marker = 'if($("budgetApplySuggestions")){'
toggle_js = '''if($("budgetAssumptionsToggle") && $("budgetAssumptionsSection")){
  $("budgetAssumptionsToggle").addEventListener("click",()=>{
    const section=$("budgetAssumptionsSection");
    const collapsed=!section.classList.contains("collapsed");
    section.classList.toggle("collapsed",collapsed);
    $("budgetAssumptionsToggle").textContent=collapsed ? "+" : "−";
    $("budgetAssumptionsToggle").setAttribute("aria-expanded",collapsed ? "false" : "true");
    $("budgetAssumptionsToggle").setAttribute("aria-label",collapsed ? "Weitere Annahmen öffnen" : "Weitere Annahmen schließen");
  });
}

'''
replace_once(marker, toggle_js + marker, "assumptions toggle JS")



# V8.172: Single-buffer logic.
old_burden_field = '''          <div class="field">
            <label>Budgetanteil für Kreditrate</label>
            <div class="input-wrap"><input id="budgetMaxBurdenPct" inputmode="decimal" value="75"><span class="unit">%</span></div>
            <div class="mini">Anteil des frei verfügbaren Monatsbudgets</div>
          </div>
'''
if old_burden_field in s:
    s = s.replace(old_burden_field, '', 1)

old_assumption_note = '''        <div class="budget-note">
          <strong>Hinweis:</strong> Der Budgetanteil bestimmt, welcher Anteil deines frei verfügbaren Monatsbudgets maximal für die Kreditrate eingesetzt wird. Der verbleibende Anteil bleibt als zusätzlicher monatlicher Puffer. Die Berechnung ist eine Orientierung und keine Finanzierungszusage einer Bank.
        </div>'''
new_assumption_note = '''        <div class="budget-note">
          <strong>Hinweis:</strong> Der Mindest-Sicherheitspuffer wird automatisch aus dem frei verfügbaren Budget vor Kreditrate berechnet: 10 % von Einnahmen minus Ausgaben, mindestens jedoch 300 € monatlich. Der aktuelle Puffer ergibt sich anschließend aus Einnahmen minus Ausgaben minus Kreditrate.
        </div>'''
if old_assumption_note in s:
    s = s.replace(old_assumption_note, new_assumption_note, 1)

s = s.replace(
    '<div class="field"><label>Sicherheitsreserve</label><div class="input-wrap"><input id="budgetSafetyReserve" inputmode="decimal" value="300"><span class="unit">€</span></div><div class="mini">monatlich</div></div>',
    '<div class="field"><label>Mindest-Sicherheitspuffer</label><div class="input-wrap"><input id="budgetSafetyReserve" inputmode="decimal" value="300" readonly aria-readonly="true"><span class="unit">€</span></div><div class="mini">10 % von Einnahmen − Ausgaben · mindestens 300 €</div></div>',
    1
)

s = s.replace(
    '  "budgetSafetyReserve","budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct","budgetMaxBurdenPct"',
    '  "budgetSafetyReserve","budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"',
    1
)

old_model = '''  const reserve=Math.max(0,budgetVal("budgetSafetyReserve"));
  const available=Math.max(0,income-expenses-reserve);
  const burdenPct=Math.min(1,Math.max(0,budgetVal("budgetMaxBurdenPct")/100));
  const rateCap=Math.max(0,available*burdenPct);
  const monthlyRate=rateCap;'''
new_model = '''  const reserve=Math.max(0,budgetVal("budgetSafetyReserve"));
  const available=Math.max(0,income-expenses-reserve);
  const rateCap=available;
  const monthlyRate=available;'''
if old_model in s:
    s = s.replace(old_model, new_model, 1)

# There is no second hidden buffer anymore.
s = s.replace(
    '          <div class="budget-summary-row"><span>Verbleibender zusätzlicher Puffer</span><strong id="budgetAdditionalBuffer">–</strong></div>\n',
    '',
    1
)

# Remove legacy PDF line for the 75% budget-share input.
s = s.replace('  line("Budgetanteil fuer Kreditrate",pdfPercent(budgetVal("budgetMaxBurdenPct")));\n','',1)

# Automatic reserve suggestion: 10% of net income, minimum 300 EUR, until manually edited.
s = s.replace(
    'let budgetChildBenefitManual = false;\nlet budgetIncomeAutoUpdating = false;',
    'let budgetChildBenefitManual = false;\nlet budgetSafetyReserveManual = false;\nlet budgetIncomeAutoUpdating = false;',
    1
)

reserve_helper = '''function syncBudgetSafetyReserve(){
  if(!$("budgetSafetyReserve")) return;
  const net=Math.max(0,budgetVal("budgetNetIncome"));
  const childBenefit=Math.max(0,budgetVal("budgetChildBenefit"));
  const income=net+childBenefit;
  const expenses=budgetExpenseIds.reduce((sum,id)=>sum+Math.max(0,budgetVal(id)),0);
  const freeBudget=income-expenses;
  const minimumReserve=Math.max(300,freeBudget*0.10);
  budgetAutoUpdating=true;
  $("budgetSafetyReserve").value=String(Math.round(minimumReserve));
  budgetAutoUpdating=false;
}

'''
helper_anchor='function budgetVal(id){'
if reserve_helper not in s and helper_anchor in s:
    s=s.replace(helper_anchor,reserve_helper+helper_anchor,1)

s = s.replace(
    '  localStorage.setItem("ff_budget_childBenefitManual",budgetChildBenefitManual ? "1":"0");',
    '  localStorage.setItem("ff_budget_childBenefitManual",budgetChildBenefitManual ? "1":"0");\n  localStorage.setItem("ff_budget_safetyReserveManual",budgetSafetyReserveManual ? "1":"0");',
    1
)

s = s.replace(
    '  budgetChildBenefitManual=localStorage.getItem("ff_budget_childBenefitManual")==="1";',
    '  budgetChildBenefitManual=localStorage.getItem("ff_budget_childBenefitManual")==="1";\n  budgetSafetyReserveManual=localStorage.getItem("ff_budget_safetyReserveManual")==="1";',
    1
)

s = s.replace(
    '  syncBudgetSuggestions();\n}',
    '  syncBudgetSuggestions();\n  syncBudgetSafetyReserve();\n}',
    1
)

s = s.replace(
    '  if(el.id==="budgetNetIncome" && !budgetIncomeAutoUpdating){\n    syncBudgetEmploymentFromNetIncome();\n  }',
    '  if(el.id==="budgetNetIncome" && !budgetIncomeAutoUpdating){\n    syncBudgetEmploymentFromNetIncome();\n    syncBudgetSafetyReserve();\n  }\n\n  if(el.id==="budgetSafetyReserve" && !budgetAutoUpdating){\n    budgetSafetyReserveManual=true;\n    localStorage.setItem("ff_budget_safetyReserveManual","1");\n  }',
    1
)


# Ensure the residual-debt explanatory note is neutral in the final HTML.
residual_text = "Restschulden werden hier als Annuitätendarlehen mit konstanter Monatsrate und konstantem Zinssatz modelliert. Tatsächliche Konditionen, Zinsbindungen und Anschlussfinanzierungen können abweichen."
residual_plain = '<div class="budget-note">\n          ' + residual_text
residual_neutral = '<div class="budget-note neutral-note">\n          ' + residual_text
if residual_plain in s:
    s = s.replace(residual_plain, residual_neutral, 1)

# V8.172: Budget UI refinements.
replace_once(
    '<h2>3. Weitere Annahmen</h2>',
    '<h2>3. Annahme zur möglichen Finanzierung</h2>',
    "assumptions title"
)

replace_once(
    '<div class="budget-result-card"><div class="name">Max. Darlehen</div><div class="value" id="budgetLoan">–</div><div class="note">aus maximal tragbarer Rate, Zins und Tilgung</div></div>',
    '<div class="budget-result-card budget-loan-highlight"><div class="name">Max. Darlehen</div><div class="value" id="budgetLoan">–</div><div class="note">aus maximal tragbarer Rate, Zins und Tilgung</div></div>',
    "max loan highlight"
)

# V8.234: Kaufpreis-Check in Budget und Eigennutzung standardmaessig geschlossen.
# The first two matching market-check cards are collapsed; toggle behavior stays unchanged.
for _ in range(2):
    if 'class="card market-check-card"' in s:
        s = s.replace('class="card market-check-card"', 'class="card market-check-card collapsed"', 1)

replace_once(
    '.reno-input-row{display:grid;grid-template-columns:1fr 56px;gap:9px}',
    '.reno-input-row{display:grid;grid-template-columns:minmax(0,1fr) 50px;gap:8px;width:100%}\\n'
    '.reno-input-row .input-wrap{min-width:0;width:100%}\\n'
    '@media(max-width:520px){.reno-input-row{grid-template-columns:minmax(0,1fr) 45px;gap:8px;width:100%}}',
    "mobile plus-row width"
)

# V8.172: Default location for Fix & Flip and Eigennutzung.
replace_once(
    'stateEl.value="Schleswig-Holstein";',
    'stateEl.value="Hamburg";',
    "default state Hamburg"
)
replace_once(
    '<input id="marketLocation" inputmode="text" placeholder="z. B. 22850 Norderstedt">',
    '<input id="marketLocation" inputmode="text" value="20095 Hamburg" placeholder="z. B. 20095 Hamburg">',
    "default market location Hamburg"
)


# V8.186: Consistent interest / repayment logic.
# Standard initial repayment is 1.5% in both financing calculators.
s = s.replace(
    '<input id="repayment" inputmode="decimal" value="2">',
    '<input id="repayment" inputmode="decimal" value="1.50">',
    1
)
s = s.replace(
    '<input id="budgetRepayment" inputmode="decimal" value="2">',
    '<input id="budgetRepayment" inputmode="decimal" value="1.50">',
    1
)

# Shared annuity projection: the monthly payment is fixed at the initial
# interest + repayment rate, while interest is charged on the remaining debt.
annuity_helper = '''function annuityProjection(debt, annualInterestRate, initialRepaymentRate, months){
  const principal=Math.max(0,Number(debt)||0);
  const annualInterest=Math.max(0,Number(annualInterestRate)||0);
  const annualRepayment=Math.max(0,Number(initialRepaymentRate)||0);
  const monthCount=Math.max(0,Math.round(Number(months)||0));
  const monthlyRate=annualInterest/12;
  const monthlyAnnuity=principal*(annualInterest+annualRepayment)/12;
  let balance=principal;
  let totalInterest=0;
  let totalRepayment=0;
  for(let i=0;i<monthCount && balance>0.005;i++){
    const interestMonth=balance*monthlyRate;
    const repaymentMonth=Math.min(balance,Math.max(0,monthlyAnnuity-interestMonth));
    totalInterest+=interestMonth;
    totalRepayment+=repaymentMonth;
    balance=Math.max(0,balance-repaymentMonth);
  }
  return {
    monthlyAnnuity,
    initialInterest:principal*monthlyRate,
    initialRepayment:principal*annualRepayment/12,
    totalInterest,
    totalRepayment,
    remainingDebt:balance
  };
}

'''
annuity_anchor='function calculateFlipTargetSale(){'
if annuity_helper not in s:
    if annuity_anchor not in s:
        raise SystemExit("V8.186 annuity helper anchor not found")
    s=s.replace(annuity_anchor,annuity_helper+annuity_anchor,1)

old_target_interest = '''  const monthlyInterest = debt * Math.max(0, pct("interest")) / 12;
  const interest = monthlyInterest * months;'''
new_target_interest = '''  const financingProjection = annuityProjection(
    debt,
    Math.max(0,pct("interest")),
    Math.max(0,pct("repayment")),
    months
  );
  const interest = financingProjection.totalInterest;'''
if old_target_interest not in s:
    raise SystemExit("V8.186 target interest block not found")
s=s.replace(old_target_interest,new_target_interest,1)

old_model_finance = '''  const monthlyInterestRate = Math.max(0, pct("interest") / 12);
  const monthlyPayment = debt * monthlyInterestRate;
  const interest = monthlyPayment * Math.max(0, months);
  const monthlyRepayment = debt * Math.max(0, pct("repayment")) / 12;
  const repayment = Math.min(debt, monthlyRepayment * Math.max(0, months));'''
new_model_finance = '''  const financingProjection = annuityProjection(
    debt,
    Math.max(0,pct("interest")),
    Math.max(0,pct("repayment")),
    months
  );
  const monthlyPayment = financingProjection.initialInterest;
  const monthlyRepayment = financingProjection.initialRepayment;
  const interest = financingProjection.totalInterest;
  const repayment = financingProjection.totalRepayment;'''
if old_model_finance not in s:
    raise SystemExit("V8.186 model finance block not found")
s=s.replace(old_model_finance,new_model_finance,1)

old_int_factor = '  const intFactor = pct("interest")*(months/12);'
new_int_factor = '  const intFactor = annuityProjection(1,Math.max(0,pct("interest")),Math.max(0,pct("repayment")),months).totalInterest;'
if old_int_factor not in s:
    raise SystemExit("V8.186 max-buy interest factor not found")
s=s.replace(old_int_factor,new_int_factor,1)

# Update explanatory texts to match the annuity calculation.
s=s.replace(
    'Im Rechner gilt vereinfacht: Monatliche Zinsbelastung = Kreditsumme × Zins p.a. ÷ 12. Beispiel: 200.000 EUR Kredit bei 6 % Zins ergeben 1.000 EUR Zinsen pro Monat.',
    'Die anfängliche Monatsrate ergibt sich aus Zins plus anfänglicher Tilgung. Der Zinsanteil wird danach monatlich auf die verbleibende Restschuld berechnet und sinkt mit fortschreitender Tilgung.',
    1
)
s=s.replace(
    'Der Rechner arbeitet mit einer vereinfachten konstanten Zinsbelastung auf Basis der angesetzten Kreditsumme. Ein echter Darlehensverlauf kann durch sinkende Restschuld, Zinsbindung, Sondertilgungen oder bankindividuelle Bedingungen abweichen.',
    'Der Rechner modelliert eine Annuität mit konstantem Zinssatz und konstanter Monatsrate. Sondertilgungen, Zinswechsel und bankindividuelle Bedingungen sind nicht enthalten.',
    1
)
s=s.replace(
    'Im Rechner gilt vereinfacht: Monatliche Tilgung = Kreditsumme × Tilgung p.a. ÷ 12. Beispiel: 200.000 EUR Kredit bei 2 % Tilgung ergeben rund 333 EUR Tilgung pro Monat.',
    'Die eingestellte Tilgung ist die anfängliche Tilgung. Mit sinkender Restschuld fällt der Zinsanteil der konstanten Rate, sodass der Tilgungsanteil im Zeitverlauf steigt.',
    1
)
s=s.replace(
    'Die Tilgung wird im Rechner linear auf Basis der angesetzten Kreditsumme berechnet. Bei einer echten Annuitätenfinanzierung verändert sich das Verhältnis von Zins und Tilgung im Zeitverlauf, weil die Restschuld sinkt.',
    'Die Berechnung folgt einer Annuitätenlogik: konstante Monatsrate bei konstantem Zinssatz, mit sinkendem Zinsanteil und steigendem Tilgungsanteil.',
    1
)

# Fresh-session interest reference from Deutsche Bundesbank, with an offline fallback.
# V8.186 migration: old saved values are not treated as intentional manual overrides.
# Only values changed by the user from this version onward are protected.
reference_interest_js = '''const REFERENCE_INTEREST_FALLBACK = 4.0;
const REFERENCE_INTEREST_URL = "https://api.statistiken.bundesbank.de/rest/data/BBIM1/M.DE.B.A2C.A.R.A.2250.EUR.N?format=csv&lang=de";
const DEFAULT_REPAYMENT_RATE = 1.5;

function parseBundesbankInterestCsv(csvText){
  const lines=String(csvText||"").split(/\\\\r?\\\\n/).filter(Boolean);
  for(let i=lines.length-1;i>=0;i--){
    const cells=lines[i].split(";").map(v=>v.replace(/^"|"$/g,"").trim());
    for(let j=cells.length-1;j>=0;j--){
      const value=Number(cells[j].replace(",","."));
      if(Number.isFinite(value) && value>0 && value<20) return value;
    }
  }
  throw new Error("Kein gueltiger Zinswert in der Bundesbank-Antwort");
}

async function fetchReferenceInterest(){
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),4500);
  try{
    const response=await fetch(REFERENCE_INTEREST_URL,{
      signal:controller.signal,
      cache:"no-store",
      headers:{"Accept":"text/csv"}
    });
    if(!response.ok) throw new Error("Bundesbank HTTP "+response.status);
    return parseBundesbankInterestCsv(await response.text());
  }finally{
    clearTimeout(timer);
  }
}

function installFinancingManualOverrideTracking(){
  const bindings=[
    ["interest","ff_interest_manual"],
    ["budgetInterest","ff_budget_interest_manual"],
    ["repayment","ff_repayment_manual"],
    ["budgetRepayment","ff_budget_repayment_manual"]
  ];
  bindings.forEach(([id,key])=>{
    const el=$(id);
    if(!el || el.dataset.manualOverrideTracking==="1") return;
    const markManual=()=>localStorage.setItem(key,"1");
    el.addEventListener("input",markManual);
    el.addEventListener("change",markManual);
    el.dataset.manualOverrideTracking="1";
  });
}

function initializeRepaymentDefaults(){
  if(localStorage.getItem("ff_repayment_manual")!=="1" && $("repayment")){
    $("repayment").value=Number(DEFAULT_REPAYMENT_RATE).toFixed(2);
  }
  if(localStorage.getItem("ff_budget_repayment_manual")!=="1" && $("budgetRepayment")){
    $("budgetRepayment").value=Number(DEFAULT_REPAYMENT_RATE).toFixed(2);
  }
}

async function initializeReferenceInterest(){
  const mainManual=localStorage.getItem("ff_interest_manual")==="1";
  const budgetManual=localStorage.getItem("ff_budget_interest_manual")==="1";
  let rate=REFERENCE_INTEREST_FALLBACK;
  try{
    rate=await fetchReferenceInterest();
    localStorage.setItem("ff_reference_interest_source","Bundesbank");
    localStorage.setItem("ff_reference_interest_updated",new Date().toISOString());
  }catch(err){
    localStorage.setItem("ff_reference_interest_source","Fallback");
  }
  const value=(Math.round(rate*100)/100).toFixed(2);
  if(!mainManual && $("interest")) $("interest").value=value;
  if(!budgetManual && $("budgetInterest")) $("budgetInterest").value=value;
  initializeRepaymentDefaults();
  installFinancingManualOverrideTracking();
  render();
}

'''
reference_anchor='function saveBudget(){'
if reference_interest_js not in s:
    if reference_anchor not in s:
        raise SystemExit("V8.186 reference interest anchor not found")
    s=s.replace(reference_anchor,reference_interest_js+reference_anchor,1)

init_anchor='setDealType(savedDealType, false);'
if init_anchor not in s:
    raise SystemExit("V8.186 init anchor not found")
s=s.replace(init_anchor,init_anchor+chr(10)+'initializeReferenceInterest();',1)

# V8.186: Sanierungsfeld 5 px breiter; Plus-Button rechts bündig.
reno_css_old = '.reno-input-row{display:grid;grid-template-columns:minmax(0,1fr) 50px;gap:8px;width:100%}\\n.reno-input-row .input-wrap{min-width:0;width:100%}\\n@media(max-width:520px){.reno-input-row{grid-template-columns:minmax(0,1fr) 45px;gap:8px;width:100%}}'
reno_css_new = '.reno-input-row{display:grid;grid-template-columns:minmax(0,1fr) 45px;gap:8px;width:100%}\\n.reno-input-row .input-wrap{min-width:0;width:100%}\\n.reno-input-row .plus-btn{justify-self:end}\\n@media(max-width:520px){.reno-input-row{grid-template-columns:minmax(0,1fr) 45px;gap:8px;width:100%}}'
if reno_css_old not in s:
    raise SystemExit("V8.186 renovation layout anchor not found")
s=s.replace(reno_css_old, reno_css_new, 1)


# V8.186: Budget PDF runtime fix and financing/sale-cost layout.
if 'const recommendationLines = doc.splitTextToSize(pdfSafeText(recommendation),contentW-10);' in s and 'const contentW=right-left;' not in s:
    s=s.replace(
        '  drawPdfBrandHeader(doc,"Budget - Immobilien-Report","Wie viel Immobilie kann ich mir leisten?",new Date().toLocaleDateString("de-DE"));\n\n  const budgetPdfNorm',
        '  drawPdfBrandHeader(doc,"Budget - Immobilien-Report","Wie viel Immobilie kann ich mir leisten?",new Date().toLocaleDateString("de-DE"));\n  const contentW=right-left;\n\n  const budgetPdfNorm',
        1
    )

old_sale_layout = '''        <div class="sale-cost-grid">
          <div class="field"><label>Makler beim Verkauf</label><div class="input-wrap"><input id="sellBroker" inputmode="decimal" value="3.57"><span class="unit">%</span></div></div>
          <div class="field"><label>Weitere Kosten bei Verkauf</label><div class="input-wrap"><input id="otherSaleCosts" inputmode="decimal" value="0"><span class="unit">€</span></div></div>
          <div class="field"><label>Sanierungs-Puffer</label><div class="input-wrap"><input id="buffer" inputmode="decimal" value="15"><span class="unit">%</span></div></div>
        </div>

        <div class="field"><label>Laufende Kosten pro Monat <span class="hint">WEG, Energie, Versicherung etc.</span></label><div class="input-wrap"><input id="holding" inputmode="decimal" value="740"><span class="unit">€</span></div></div>'''
new_sale_layout = '''        <div class="field"><label>Sanierungs-Puffer</label><div class="input-wrap"><input id="buffer" inputmode="decimal" value="15"><span class="unit">%</span></div></div>

        <div class="field"><label>Laufende Kosten pro Monat</label><div class="input-wrap"><input id="holding" inputmode="decimal" value="740"><span class="unit">€</span></div><div class="mini">WEG, Energie, Versicherung etc.</div></div>

        <div class="sale-cost-grid">
          <div class="field"><label>Makler beim Verkauf</label><div class="input-wrap"><input id="sellBroker" inputmode="decimal" value="3.57"><span class="unit">%</span></div></div>
          <div class="field"><label>Weitere Kosten bei Verkauf</label><div class="input-wrap"><input id="otherSaleCosts" inputmode="decimal" value="0"><span class="unit">€</span></div></div>
        </div>'''
if old_sale_layout in s:
    s=s.replace(old_sale_layout,new_sale_layout,1)

s=s.replace(
    '.sale-cost-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}',
    '.sale-cost-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}',
    1
)

s=s.replace(
    'Das PDF konnte nicht direkt geteilt werden. Bitte pruefe deine Internetverbindung oder versuche es erneut.',
    'Das PDF konnte nicht erstellt oder geteilt werden. Bitte versuche es erneut.'
)
s=s.replace(
    'Das PDF konnte nicht gespeichert werden. Bitte pruefe deine Internetverbindung oder versuche es erneut.',
    'Das PDF konnte nicht erstellt oder gespeichert werden. Bitte versuche es erneut.'
)

# V8.186: PDF wording, recommendation box, and Budget summary values.
s=s.replace('doc.text("Handlungsempfehlung | Kurzfazit",left,y); y+=6;', 'doc.text("Handlungsempfehlung",left,y); y+=6;', 1)
s=s.replace('drawInfoBox("Kurzfazit", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, minHeight:18});',
            'drawInfoBox("", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, minHeight:18});')

old_recommendation_box = '''  const recommendationLines = doc.splitTextToSize(pdfSafeText(recommendation),contentW-10);
  const recommendationH = Math.max(34, 10 + recommendationLines.length * 4);
  doc.setFillColor(246,248,251); doc.setDrawColor(216,222,231);
  doc.roundedRect(left,y,contentW,recommendationH,3,3,"FD");
  doc.setFont("helvetica","normal"); doc.setFontSize(8.2); doc.setTextColor(55,65,81);
  doc.text(recommendationLines,left+5,y+7);
  y += recommendationH + 9;'''
new_recommendation_box = '''  const recommendationPadding=4;
  const recommendationH=29;
  const recommendationInnerW=contentW-(recommendationPadding*2);
  let recommendationFontSize=8.2;
  let recommendationLines=[];
  let recommendationLineH=3.7;
  while(recommendationFontSize>=6.6){
    doc.setFont("helvetica","normal");
    doc.setFontSize(recommendationFontSize);
    recommendationLines=doc.splitTextToSize(pdfSafeText(recommendation),recommendationInnerW);
    recommendationLineH=recommendationFontSize*0.46;
    if(recommendationLines.length*recommendationLineH <= recommendationH-(recommendationPadding*2)-1) break;
    recommendationFontSize-=0.2;
  }
  doc.setTextColor(55,65,81);
  doc.setFillColor(239,246,255); doc.setDrawColor(191,219,254);
  doc.roundedRect(left,y,contentW,recommendationH,3,3,"FD");
  doc.text(recommendationLines,left+recommendationPadding,y+recommendationPadding+1.7);
  y += recommendationH + 5;'''
if old_recommendation_box in s:
    s=s.replace(old_recommendation_box,new_recommendation_box,1)

old_budget_values = '''  const maxLoan = budgetPdfResultValue("Max. Darlehen") !== "-" ? budgetPdfResultValue("Max. Darlehen") : budgetPdfResultValue("Darlehen");
  const freeBudget = budgetPdfResultValue("Frei verfügbares Monatsbudget") !== "-" ? budgetPdfResultValue("Frei verfügbares Monatsbudget") : budgetPdfResultValue("Monatsbudget");
  const equity = budgetPdfEuro(budgetPdfInputNumber("budgetEquity"));
  const interest = budgetPdfPct("budgetInterest");
  const repayment = budgetPdfPct("budgetRepayment");'''
new_budget_values = '''  const maxLoan = pdfMoney(m.loan);
  const freeBudget = pdfMoney(m.available);
  const equity = pdfMoney(m.equity);
  const interest = new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:2}).format(m.interestPct*100) + " %";
  const repayment = new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.repaymentPct*100) + " %";'''
if old_budget_values in s:
    s=s.replace(old_budget_values,new_budget_values,1)

# Remove any remaining separator immediately before Kurzfazit and any standalone PDF title.
s=s.replace(' | Kurzfazit','')
s=s.replace('"Kurzfazit", recommendationText','"", recommendationText')

# V8.186: Compact Budget summary cards and keep Haushalt + expense details on page 1.
s=s.replace(
    'budgetPdfCard(left,y,cardW,24,"Maximales Darlehen",maxLoan);\n'
    '  budgetPdfCard(left+cardW+gap,y,cardW,24,"Zinssatz",interest);\n'
    '  budgetPdfCard(left+(cardW+gap)*2,y,cardW,24,"Tilgung",repayment);\n'
    '  y += 28;\n'
    '  const wideW=(contentW-gap)/2;\n'
    '  budgetPdfCard(left,y,wideW,24,"Eigenkapital",equity);\n'
    '  budgetPdfCard(left+wideW+gap,y,wideW,24,"Frei verfügbares Monatsbudget",freeBudget);\n\n'
    '  doc.addPage();\n'
    '  drawPdfBrandHeader(doc,"Budget - Immobilien-Report","Finanzierungsdetails",new Date().toLocaleDateString("de-DE"));\n'
    '  y=43;',
    'budgetPdfCard(left,y,cardW,18,"Maximales Darlehen",maxLoan);\n'
    '  budgetPdfCard(left+cardW+gap,y,cardW,18,"Zinssatz",interest);\n'
    '  budgetPdfCard(left+(cardW+gap)*2,y,cardW,18,"Tilgung",repayment);\n'
    '  y += 22;\n'
    '  const wideW=(contentW-gap)/2;\n'
    '  budgetPdfCard(left,y,wideW,18,"Eigenkapital",equity);\n'
    '  budgetPdfCard(left+wideW+gap,y,wideW,18,"Frei verfügbares Monatsbudget",freeBudget);\n'
    '  y += 22;',
    1
)

# V8.186: Budget PDF separator cleanup.
s=s.replace('  |  Erwachsene: ', '  ·  Erwachsene: ', 1)
s=s.replace('  |  Kinder: ', '  ·  Kinder: ', 1)

# V8.234: Two-decimal interest/repayment display and compact 5-line Budget recommendation box.
s=s.replace(
    'function pdfPercent(n){\n  return new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(n) + " %";\n}',
    'function pdfPercent(n){\n  return new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(n) + " %";\n}',
    1
)

s=s.replace(
    'const interest = new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:2}).format(m.interestPct*100) + " %";',
    'const interest = new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.interestPct*100) + " %";',
    1
)

# Normalize every percentage input in every calculator to exactly two decimals.
interest_format_js = '''function formatPercentInputField(el){
  if(!el) return;
  const n=parseLocalizedNumber(el.value,true);
  if(Number.isFinite(n)) el.value=n.toFixed(2);
}
function initTwoDecimalPercentFields(){
  document.querySelectorAll(".input-wrap").forEach(wrap=>{
    const unit=wrap.querySelector(".unit");
    const el=wrap.querySelector("input");
    if(!unit || !el || String(unit.textContent||"").trim()!=="%") return;
    if(el.dataset.twoDecimalPercent!=="1"){
      el.dataset.twoDecimalPercent="1";
      el.addEventListener("blur",()=>formatPercentInputField(el));
      el.addEventListener("change",()=>formatPercentInputField(el));
    }
    formatPercentInputField(el);
  });
}
initTwoDecimalPercentFields();

'''
interest_anchor='function saveBudget(){'
if interest_format_js not in s:
    if interest_anchor not in s:
        raise SystemExit("V8.186 interest formatting anchor not found")
    s=s.replace(interest_anchor,interest_format_js+interest_anchor,1)

# Shared recommendation box: fixed height for ~7 lines, text starts at the top and shrinks responsively only if needed.
old_info_box = '''  const drawInfoBox = (title, text, options={}) => {
    const fill = options.fill || [248,250,252];
    const stroke = options.stroke || [226,232,240];
    const titleColor = options.titleColor || [15,23,42];
    const textColor = options.textColor || [71,85,105];
    const titleSize = options.titleSize || 10;
    const bodySize = options.bodySize || 8.7;
    const boxWidth = options.width || 178;
    const lines = wrap(text, boxWidth-8, bodySize);
    const boxHeight = Math.max(options.minHeight || 18, 10 + lines.length*4.2 + 6);
    ensureSpace(boxHeight + 3);
    doc.setFillColor(fill[0], fill[1], fill[2]);
    doc.setDrawColor(stroke[0], stroke[1], stroke[2]);
    doc.roundedRect(left, y, boxWidth, boxHeight, 3, 3, 'FD');
    doc.setTextColor(titleColor[0], titleColor[1], titleColor[2]);
    doc.setFont('helvetica','bold');
    doc.setFontSize(titleSize);
    doc.text(pdfSafeText(title), left+4, y+6);
    doc.setTextColor(textColor[0], textColor[1], textColor[2]);
    doc.setFont('helvetica','normal');
    doc.setFontSize(bodySize);
    doc.text(lines, left+4, y+11);
    doc.setTextColor(23,32,51);
    y += boxHeight + 4;
  };'''
new_info_box = '''  const drawInfoBox = (title, text, options={}) => {
    const fill = options.fill || [248,250,252];
    const stroke = options.stroke || [226,232,240];
    const titleColor = options.titleColor || [15,23,42];
    const textColor = options.textColor || [71,85,105];
    const titleSize = options.titleSize || 10;
    const boxWidth = options.width || 178;
    const padding = options.padding || 4;
    const fixedHeight = options.fixedHeight || null;
    let bodySize = options.bodySize || 8.7;
    let lines = [];
    let lineH = bodySize*0.46;
    const bodyTop = title ? 10 : 5;
    if(fixedHeight){
      while(bodySize>=6.8){
        doc.setFont("helvetica","normal");
        doc.setFontSize(bodySize);
        lines=doc.splitTextToSize(pdfSafeText(text),boxWidth-padding*2);
        lineH=bodySize*0.46;
        if(lines.length*lineH <= fixedHeight-bodyTop-padding) break;
        bodySize-=0.2;
      }
    }else{
      lines=wrap(text,boxWidth-padding*2,bodySize);
    }
    const boxHeight = fixedHeight || Math.max(options.minHeight || 18, bodyTop + lines.length*4.2 + padding);
    ensureSpace(boxHeight + 3);
    doc.setFillColor(fill[0], fill[1], fill[2]);
    doc.setDrawColor(stroke[0], stroke[1], stroke[2]);
    doc.roundedRect(left, y, boxWidth, boxHeight, 3, 3, 'FD');
    if(title){
      doc.setTextColor(titleColor[0], titleColor[1], titleColor[2]);
      doc.setFont('helvetica','bold');
      doc.setFontSize(titleSize);
      doc.text(pdfSafeText(title), left+padding, y+6);
    }
    doc.setTextColor(textColor[0], textColor[1], textColor[2]);
    doc.setFont('helvetica','normal');
    doc.setFontSize(bodySize);
    doc.text(lines, left+padding, y+bodyTop);
    doc.setTextColor(23,32,51);
    y += boxHeight + 4;
  };'''
if old_info_box in s:
    s=s.replace(old_info_box,new_info_box,1)

s=s.replace(
    'drawInfoBox("", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, minHeight:18});',
    'drawInfoBox("", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, fixedHeight:34, padding:4});',
    1
)

# Budget recommendation box: compact ~5-line height; freed space is available to the following content.
s=s.replace('  const recommendationH=29;','  const recommendationH=26;',1)
s=s.replace('  y += recommendationH + 5;','  y += recommendationH + 10;',1)

# V8.234: Budget-PDF Abschnittsueberschriften wie in den anderen Berichten:
# dunkler Hintergrund, weisse Schrift. Vor "Haushalt" zusaetzlich ca. 5 px Abstand.
section_start = s.find("  function section(")
if section_start < 0:
    section_start = s.find("function section(")
if section_start < 0:
    raise SystemExit("Budget section function not found")

brace_start = s.find("{", section_start)
if brace_start < 0:
    raise SystemExit("Budget section function brace not found")

depth = 0
section_end = -1
for i in range(brace_start, len(s)):
    ch = s[i]
    if ch == "{":
        depth += 1
    elif ch == "}":
        depth -= 1
        if depth == 0:
            section_end = i + 1
            break
if section_end < 0:
    raise SystemExit("Budget section function end not found")

new_budget_section = '''  function section(t){
    // 5 px entsprechen bei jsPDF (mm) rund 1,3 mm.
    if(t==="Haushalt") y+=1.3;
    const sectionH=8;
    doc.setFillColor(15,23,42);
    doc.setDrawColor(15,23,42);
    doc.roundedRect(left,y,contentW,sectionH,2,2,"FD");
    doc.setFont("helvetica","bold");
    doc.setFontSize(9.2);
    doc.setTextColor(255,255,255);
    doc.text(pdfSafeText(t),left+4,y+5.4);
    y+=sectionH+4;
    doc.setTextColor(23,32,51);
  }'''
s = s[:section_start] + new_budget_section + s[section_end:]

# V8.186: Budget household labels and expanded two-page Budget PDF.
replace_once(
    '<p class="sub">Grundlage ist dein tatsächlich verfügbares Haushaltsnettoeinkommen. Steuerklasse ist deshalb nicht erforderlich.</p>',
    '<p class="sub">Grundlage ist dein tatsächlich verfügbares monatliches Haushaltsnettoeinkommen. Steuerklasse ist deshalb nicht erforderlich.</p>',
    "budget household info text"
)
replace_once(
    '<label>Haushaltsnettoeinkommen <span class="hint">monatlich</span></label>',
    '<label>Haushaltsnettoeinkommen</label>',
    "budget net income monthly hint"
)
replace_once(
    '<label>Kindergeld <span class="hint">gesamt / Monat</span></label>',
    '<label>Kindergeld</label>',
    "budget child benefit monthly hint"
)

old_budget_pdf_flow = '''  section("Haushalt");
  line("Haushaltsnettoeinkommen",pdfMoney(m.net),true);
  line("  Gehalt / Lohn netto",pdfMoney(Math.max(0,budgetVal("budgetIncomeEmployment"))));
  line("  Rente / Pension",pdfMoney(Math.max(0,budgetVal("budgetIncomePension"))));
  line("  Unterhalt",pdfMoney(Math.max(0,budgetVal("budgetIncomeSupport"))));
  line("  Nebentaetigkeit",pdfMoney(Math.max(0,budgetVal("budgetIncomeSide"))));
  line("  Mieteinnahmen",pdfMoney(Math.max(0,budgetVal("budgetIncomeRent"))));
  line("  Sonstige Einnahmen",pdfMoney(Math.max(0,budgetVal("budgetIncomeOther"))));
  line("Kindergeld",pdfMoney(m.childBenefit));
  line("Gesamte Einnahmen",pdfMoney(m.income),true);
  line("Feste Ausgaben",pdfMoney(m.expenses));
  line("Sicherheitsreserve",pdfMoney(m.reserve));
  line("Frei verfuegbares Monatsbudget",pdfMoney(m.available),true);
  line("Zusaetzlicher Monats-Puffer",pdfMoney(m.additionalBuffer));
  line("Maximal tragbare Kreditrate",pdfMoney(m.monthlyRate),true);

  section("Finanzierung");'''

new_budget_pdf_flow = '''
  section("Haushalt");
  y+=1.2;
  line("Haushaltsnettoeinkommen",pdfMoney(m.net),true);
  line("  Gehalt / Lohn netto",pdfMoney(Math.max(0,budgetVal("budgetIncomeEmployment"))));
  line("  Rente / Pension",pdfMoney(Math.max(0,budgetVal("budgetIncomePension"))));
  line("  Unterhalt",pdfMoney(Math.max(0,budgetVal("budgetIncomeSupport"))));
  line("  Nebentaetigkeit",pdfMoney(Math.max(0,budgetVal("budgetIncomeSide"))));
  line("  Mieteinnahmen",pdfMoney(Math.max(0,budgetVal("budgetIncomeRent"))));
  line("  Sonstige Einnahmen",pdfMoney(Math.max(0,budgetVal("budgetIncomeOther"))));
  y+=1.6;
  line("Kindergeld",pdfMoney(m.childBenefit));
  line("Gesamte Einnahmen",pdfMoney(m.income),true);
  y+=1.6;
  line("Feste Ausgaben",pdfMoney(m.expenses));
  line("Mindest-Sicherheitspuffer",pdfMoney(m.minimumReserve));
  y+=1.6;
  line("Frei verfuegbares Monatsbudget",pdfMoney(m.available),true);
  line("Zusaetzlicher Monats-Puffer",pdfMoney(m.additionalBuffer));
  line("Maximal tragbare Kreditrate",pdfMoney(m.monthlyRate),true);

  // V8.234: Neuer Seitenumbruch direkt vor der Einzelaufstellung der festen Ausgaben.
  doc.addPage();
  drawPdfBrandHeader(
    doc,
    "Budget - Immobilien-Report",
    "Ausgaben und Finanzierungsdetails",
    new Date().toLocaleDateString("de-DE")
  );
  y=43;

  section("Übersicht der Festen Ausgaben als Einzelposition");
  line("Lebensmittel / Haushalt",pdfMoney(Math.max(0,budgetVal("budgetFood"))));
  line("Mobilitaet",pdfMoney(Math.max(0,budgetVal("budgetMobility"))));
  line("Versicherungen",pdfMoney(Math.max(0,budgetVal("budgetInsurance"))));
  line("Telekommunikation",pdfMoney(Math.max(0,budgetVal("budgetTelecom"))));
  line("Freizeit, Kultur, Kleidung",pdfMoney(Math.max(0,budgetVal("budgetLeisure"))));
  line("Kinderkosten",pdfMoney(Math.max(0,budgetVal("budgetChildCosts"))));
  line("Bestehende Kreditraten",pdfMoney(Math.max(0,budgetVal("budgetExistingLoans"))));
  line("Sonstige Ausgaben",pdfMoney(Math.max(0,budgetVal("budgetOther"))));
  line("Gesamte feste Ausgaben",pdfMoney(m.expenses),true);

  y+=2.0;
  section("Finanzierung");'''

replace_once(old_budget_pdf_flow, new_budget_pdf_flow, "budget PDF expense page")

# V8.234 Layout-Ziel: Seite 1 Überblick/Haushalt, Seite 2 Ausgaben+Finanzierung, Seite 3 Empfehlungen; maximal 3 Seiten.

old_budget_pdf_footer = '''  drawPdfBrandLogo(doc);
  drawPdfFooter(doc,1,1,"V8.234");
  return doc;'''
new_budget_pdf_footer = '''  // Abschlussseite: Unsere wichtigsten Empfehlungen.
  doc.addPage();
  drawPdfBrandHeader(
    doc,
    "Unsere wichtigsten Empfehlungen",
    "Checkliste für den Immobilienkauf",
    new Date().toLocaleDateString("de-DE")
  );
  y=43;

  const budgetChecklistItem = (number, heading, paragraphs=[], bullets=[]) => {
    doc.setFont("helvetica","bold");
    doc.setFontSize(9.2);
    doc.setTextColor(23,32,51);
    doc.text(pdfSafeText(number + ". " + heading),left,y);
    y+=4.5;

    doc.setFont("helvetica","normal");
    doc.setFontSize(7.4);
    doc.setTextColor(55,65,81);
    for(const paragraph of paragraphs){
      const lines=doc.splitTextToSize(pdfSafeText(paragraph),contentW);
      doc.text(lines,left,y);
      y+=lines.length*3.35+1.8;
    }

    for(const bullet of bullets){
      const lines=doc.splitTextToSize(pdfSafeText(bullet),contentW-7);
      doc.text("•",left+1.5,y);
      doc.text(lines,left+6,y);
      y+=lines.length*3.25+0.9;
    }
    y+=2.2;
  };

  budgetChecklistItem(1,"Eigenkapital gezielt einsetzen",[
    "Ideal sind etwa 20–30 % des Kaufpreises als Eigenkapital, zusätzlich zu den Kaufnebenkosten. Das ist auch die Orientierung der Verbraucherzentrale.",
    "Wichtig ist aber, nicht die gesamten Ersparnisse einzusetzen. Ein finanzieller Notgroschen sollte erhalten bleiben."
  ]);

  budgetChecklistItem(2,"Die monatliche Belastung konservativ kalkulieren",[
    "Als grobe Orientierung würde ich die Kreditrate möglichst auf 30–35 % des monatlichen Haushaltsnettoeinkommens begrenzen. Je nach Einkommen und Lebenshaltungskosten kann auch weniger sinnvoll sein.",
    "Zusätzlich fallen Hausgeld oder Betriebskosten, Versicherungen, Grundsteuer und Instandhaltung an."
  ]);

  budgetChecklistItem(3,"Nicht nur den Zinssatz vergleichen",[
    "Ein niedriger Sollzins allein macht noch keine gute Finanzierung aus. Entscheidend sind auch:"
  ],[
    "Effektiver Jahreszins",
    "Zinsbindung von beispielsweise 10, 15 oder 20 Jahren",
    "Anfängliche Tilgung, möglichst 2–3 % oder mehr",
    "Kostenlose Sondertilgungsmöglichkeiten",
    "Möglichkeit zum Tilgungssatzwechsel",
    "Restschuld nach Ablauf der Zinsbindung"
  ]);

  doc.setFont("helvetica","normal");
  doc.setFontSize(7.4);
  doc.setTextColor(55,65,81);
  const annuityText=doc.splitTextToSize(pdfSafeText("Für viele Käufer ist ein klassisches Annuitätendarlehen die verständlichste und sinnvollste Lösung."),contentW);
  doc.text(annuityText,left,y);
  y+=annuityText.length*3.35+4.2;

  budgetChecklistItem(4,"Die Anschlussfinanzierung von Anfang an mitdenken",[
    "Wenn nach 10 oder 15 Jahren noch 200.000 € Restschuld bestehen, können höhere Zinsen die monatliche Belastung deutlich erhöhen.",
    "Ich würde deshalb immer ein Szenario mit 2 Prozentpunkten höheren Anschlusszinsen durchrechnen."
  ]);

  budgetChecklistItem(5,"Die Immobilie unabhängig prüfen lassen",[
    "Eine günstige Finanzierung rettet keinen schlechten Immobilienkauf. Vor allem bei Bestandsimmobilien würde ich Bausubstanz, Energieeffizienz, Heizung, Dach und möglichen Sanierungsbedarf prüfen lassen."
  ]);

  budgetChecklistItem(6,"Mehrere Banken vergleichen",[
    "Mindestens drei Angebote einholen, beispielsweise über Hausbank, Sparkasse oder Volksbank und einen unabhängigen Finanzierungsvermittler. Wichtig ist, wirklich identische Kreditbedingungen gegenüberzustellen."
  ]);

  budgetChecklistItem(7,"Fördermöglichkeiten vor Vertragsabschluss prüfen",[
    "Für selbst genutzte Immobilien kommt beispielsweise das KfW-Wohneigentumsprogramm 124 infrage. Für bestimmte Familien und energetische Sanierungen existieren weitere Förderprogramme."
  ]);

  const budgetPdfPages=doc.getNumberOfPages();
  for(let pageNo=1; pageNo<=budgetPdfPages; pageNo++){
    doc.setPage(pageNo);
    drawPdfBrandLogo(doc);
    drawPdfFooter(doc,pageNo,budgetPdfPages,"V8.234");
  }
  return doc;'''
replace_once(old_budget_pdf_footer, new_budget_pdf_footer, "budget PDF two-page footer")


# V8.234: Eigennutzung-Kaufpreis-Check initial geschlossen und Recalc-Buttons als bestaetigte Reset-Buttons.
s=s.replace(
    '<section class="card market-check-card mode-hidden" id="ownMarketCheckSection">',
    '<section class="card market-check-card mode-hidden collapsed" id="ownMarketCheckSection">',
    1
)
s=s.replace(
    '<button class="market-check-toggle" id="marketCheckToggle" type="button" aria-expanded="true" aria-label="Kaufpreis-Check ein- oder ausklappen">−</button>',
    '<button class="market-check-toggle" id="marketCheckToggle" type="button" aria-expanded="false" aria-label="Kaufpreis-Check ein- oder ausklappen">+</button>',
    1
)

s=s.replace(
    '.bottom-primary{background:#93C572;color:#ffffff;box-shadow:0 8px 20px rgba(147,197,114,.28)}',
    '.bottom-primary{background:#dc2626;color:#ffffff;box-shadow:0 8px 20px rgba(220,38,38,.28)}',
    1
)

old_recalc_handler = '''$("recalc").addEventListener("click",()=>{
  if(currentDealType()==="budget"){
    renderBudget();
    return;
  }
  if(currentDealType()==="flip" && $("flipSaleTarget")){
    const targetSale = calculateFlipTargetSale();
    $("flipSaleTarget").value = targetSale > 0 ? String(Math.round(targetSale)) : "";
    flipSaleManualOverride = false;
    localStorage.setItem(FLIP_SALE_OVERRIDE_KEY, "0");
    setSaleRecalculatedState(true);
  }
  render();
});'''

new_recalc_handler = '''function resetControlToMarkupDefault(el){
  if(!el) return;
  if(el.tagName==="SELECT"){
    const options=Array.from(el.options || []);
    const idx=options.findIndex(o=>o.defaultSelected);
    el.selectedIndex=idx>=0 ? idx : 0;
    return;
  }
  if(el.type==="checkbox" || el.type==="radio"){
    el.checked=el.defaultChecked;
    return;
  }
  el.value=el.defaultValue;
}

function collapseOwnMarketCheck(){
  if($("ownMarketCheckSection")) $("ownMarketCheckSection").classList.add("collapsed");
  if($("marketCheckToggle")){
    $("marketCheckToggle").textContent="+";
    $("marketCheckToggle").setAttribute("aria-expanded","false");
  }
}

function resetBudgetCalculatorToDefaults(){
  Object.keys(localStorage).forEach(key=>{
    if(key.startsWith("ff_budget_")) localStorage.removeItem(key);
  });

  if($("budgetSection")){
    $("budgetSection").querySelectorAll("input,select,textarea").forEach(resetControlToMarkupDefault);
  }

  budgetChildBenefitManual=false;
  budgetSafetyReserveManual=false;
  budgetIncomeAutoUpdating=false;
  budgetAutoUpdating=false;
  Object.keys(budgetExpenseManual).forEach(key=>delete budgetExpenseManual[key]);

  loadBudget();

  // Verbindliche Budget-Standardwerte.
  if($("budgetNetIncome")) $("budgetNetIncome").value="0";
  if($("budgetFamilyStatus")) $("budgetFamilyStatus").value="single";
  if($("budgetAdults")) $("budgetAdults").value="1";
  if($("budgetChildren")) $("budgetChildren").value="0";
  if($("budgetEquity")) $("budgetEquity").value="0";
  if($("budgetAncillaryPct")) $("budgetAncillaryPct").value="12.00";
  if($("budgetExtraCostsPct")) $("budgetExtraCostsPct").value="5.00";
  if($("budgetIncomeEmployment")) $("budgetIncomeEmployment").value="0";
  if($("budgetChildBenefit")) $("budgetChildBenefit").value="0";

  // Nach einem echten Reset wird die erste Kreditrate erst nach der ersten
  // abgeschlossenen Einkommenseingabe gesetzt. Danach gilt wieder die normale Logik.
  budgetRateNeedsInitialValue=true;
  budgetRateManualSelection=false;
  localStorage.setItem("ff_budget_rateNeedsInitialValue","1");
  localStorage.setItem("ff_budget_rateManualSelection","0");
  localStorage.removeItem("ff_budget_rateSliderPct");

  initTwoDecimalPercentFields();
  initializeRepaymentDefaults();
  renderBudget();
  initializeReferenceInterest();
}

function resetDealCalculatorToDefaults(){
  const mode=currentDealType();
  const dealStorageIds=[
    "purchase","sale","area","buildYear","plotArea","energyClass","energyDemand","months",
    "interest","repayment","ltv","notary","buyBroker","sellBroker","otherSaleCosts","buffer",
    "holding","targetProfit","targetMargin","maxEquity","targetRoi","personalTax",
    "stressSalePct","stressRenoPct","marketLocation","marketPropertyType","marketCondition",
    "comp1Price","comp1Area","comp2Price","comp2Area","comp3Price","comp3Area","flipSaleTarget"
  ];
  dealStorageIds.forEach(id=>localStorage.removeItem("ff_"+id));
  [
    "ff_state","ff_financeAcquisition","ff_interest_manual","ff_repayment_manual",
    COMP1_OVERRIDE_KEY,PROPERTY_TYPE_SET_KEY,FLIP_SALE_OVERRIDE_KEY
  ].forEach(key=>localStorage.removeItem(key));

  if(mode==="own"){
    localStorage.removeItem("ff_own_months");
    localStorage.removeItem("ff_own_equity_input");
  }else{
    localStorage.removeItem("ff_flip_months");
    localStorage.removeItem("ff_flip_equity_input");
    dealGoalIds.forEach(id=>localStorage.removeItem("ff_flip_"+id));
  }

  trades.forEach(t=>{
    localStorage.removeItem("ff_trade_"+t.key);
    localStorage.removeItem("ff_trade_manual_"+t.key);
  });
  Object.keys(fixedTradeHints).forEach(name=>{
    const hint=fixedTradeHints[name];
    if(hint && hint.areaKey) localStorage.removeItem("ff_trade_area_"+hint.areaKey);
  });

  if($("dealCalculatorContent")){
    $("dealCalculatorContent").querySelectorAll('input:not([name="dealType"]),select,textarea').forEach(resetControlToMarkupDefault);
  }
  stateEl.value="Hamburg";
  comp1ManualOverride=false;
  flipSaleManualOverride=false;
  initializeTrades(true);
  setSaleRecalculatedState(false);
  collapseOwnMarketCheck();
  setDealType(mode,false);
  initTwoDecimalPercentFields();
  initializeRepaymentDefaults();
  render();
  initializeReferenceInterest();
}

$("recalc").addEventListener("click",()=>{
  const mode=currentDealType();
  const label = mode==="budget"
    ? "Budget-Rechner"
    : (mode==="own" ? "Eigennutzungs-Rechner" : "Fix-&-Flip-Rechner");
  const ok=confirm("Möchtest du wirklich alle Eingaben im " + label + " auf die initialen Standardwerte zurücksetzen?");
  if(!ok) return;

  if(mode==="budget"){
    resetBudgetCalculatorToDefaults();
  }else{
    resetDealCalculatorToDefaults();
  }
});'''

replace_once(old_recalc_handler, new_recalc_handler, "V8.234 recalc reset handler")


# V8.234: Eigennutzung - feste Initial-/Reset-Standardwerte.
own_defaults_helper = '''function applyOwnUseStandardValues(){
  const ownDefaults={
    purchase:"0",
    area:"0",
    months:"60",
    ltv:"100.00",
    ownEquityInput:"0",
    buyBroker:"0",
    buffer:"5",
    holding:"0",
    sellBroker:"0",
    otherSaleCosts:"0"
  };

  Object.entries(ownDefaults).forEach(([id,value])=>{
    const el=$(id);
    if(el) el.value=value;
  });
  if($("financeAcquisition")) $("financeAcquisition").checked=true;

  ["purchase","area","ltv","buyBroker","buffer","holding","sellBroker","otherSaleCosts"].forEach(id=>{
    localStorage.setItem("ff_"+id,ownDefaults[id]);
  });
  localStorage.setItem("ff_own_months","60");
  localStorage.setItem("ff_own_equity_input","0");
  localStorage.setItem("ff_financeAcquisition","1");
}'''

if own_defaults_helper not in s:
    target = 'function resetDealCalculatorToDefaults(){'
    if target not in s:
        raise SystemExit("V8.234 own defaults reset anchor not found")
    s = s.replace(target, own_defaults_helper + '\n\n' + target, 1)

own_switch_old = '''      zeroOwnUseGoals();
      restoreModeMonths(true);
      restoreModeEquity(true);'''
own_switch_new = '''      zeroOwnUseGoals();
      restoreModeMonths(true);
      restoreModeEquity(true);
      if(localStorage.getItem("ff_own_defaults_v8197")!=="1"){
        applyOwnUseStandardValues();
        localStorage.setItem("ff_own_defaults_v8197","1");
      }'''
if own_switch_old not in s:
    raise SystemExit("V8.234 own setDealType anchor not found")
s = s.replace(own_switch_old, own_switch_new, 1)

own_reset_old = '''  stateEl.value="Hamburg";
  comp1ManualOverride=false;'''
own_reset_new = '''  if(mode==="own"){
    applyOwnUseStandardValues();
    localStorage.setItem("ff_own_defaults_v8197","1");
  }

  stateEl.value="Hamburg";
  comp1ManualOverride=false;'''
if own_reset_old not in s:
    raise SystemExit("V8.234 own reset injection anchor not found")
s = s.replace(own_reset_old, own_reset_new, 1)


# V8.234: Fix & Flip - feste Initial-/Reset-Standardwerte und Reset-Pruefung.
flip_defaults_helper = '''function applyFlipStandardValues(){
  const flipDefaults={
    purchase:"0",
    area:"0",
    months:"6",
    ltv:"100.00",
    flipEquityInput:"0",
    buyBroker:"0",
    buffer:"5",
    holding:"0",
    sellBroker:"0",
    otherSaleCosts:"0",
    personalTax:"42"
  };

  Object.entries(flipDefaults).forEach(([id,value])=>{
    const el=$(id);
    if(el) el.value=value;
  });
  if($("financeAcquisition")) $("financeAcquisition").checked=true;

  ["purchase","area","ltv","buyBroker","buffer","holding","sellBroker","otherSaleCosts","personalTax"].forEach(id=>{
    localStorage.setItem("ff_"+id,flipDefaults[id]);
  });
  localStorage.setItem("ff_flip_months","6");
  localStorage.setItem("ff_flip_equity_input","0");
  localStorage.setItem("ff_financeAcquisition","1");
}'''

if flip_defaults_helper not in s:
    target = 'function resetDealCalculatorToDefaults(){'
    if target not in s:
        raise SystemExit("V8.234 flip defaults reset anchor not found")
    s = s.replace(target, flip_defaults_helper + '\n\n' + target, 1)

flip_switch_old = '''    } else {
      restoreFlipGoals();
      restoreModeMonths(false);
      restoreModeEquity(false);
    }'''
flip_switch_new = '''    } else {
      restoreFlipGoals();
      restoreModeMonths(false);
      restoreModeEquity(false);
      if(localStorage.getItem("ff_flip_defaults_v8198")!=="1"){
        applyFlipStandardValues();
        localStorage.setItem("ff_flip_defaults_v8198","1");
      }
    }'''
if flip_switch_old not in s:
    raise SystemExit("V8.234 flip setDealType anchor not found")
s = s.replace(flip_switch_old, flip_switch_new, 1)

flip_reset_old = '''  if(mode==="own"){
    applyOwnUseStandardValues();
    localStorage.setItem("ff_own_defaults_v8197","1");
  }

  stateEl.value="Hamburg";'''
flip_reset_new = '''  if(mode==="own"){
    applyOwnUseStandardValues();
    localStorage.setItem("ff_own_defaults_v8197","1");
  }else{
    applyFlipStandardValues();
    localStorage.setItem("ff_flip_defaults_v8198","1");
  }

  stateEl.value="Hamburg";'''
if flip_reset_old not in s:
    raise SystemExit("V8.234 flip reset injection anchor not found")
s = s.replace(flip_reset_old, flip_reset_new, 1)

# Build-time guards: fail deployment if the requested Fix-&-Flip reset values are missing.
required_flip_reset_tokens = [
    'function applyFlipStandardValues(){',
    'purchase:"0"',
    'area:"0"',
    'months:"6"',
    'ltv:"100.00"',
    'flipEquityInput:"0"',
    'buyBroker:"0"',
    'buffer:"5"',
    'holding:"0"',
    'sellBroker:"0"',
    'otherSaleCosts:"0"',
    'if($("financeAcquisition")) $("financeAcquisition").checked=true',
    'localStorage.setItem("ff_flip_months","6")',
    'localStorage.setItem("ff_flip_equity_input","0")',
    'localStorage.setItem("ff_financeAcquisition","1")'
]
missing_flip_reset_tokens = [token for token in required_flip_reset_tokens if token not in s]
if missing_flip_reset_tokens:
    raise SystemExit("V8.234 Fix-&-Flip reset verification failed: " + ", ".join(missing_flip_reset_tokens))


# V8.234: Dynamischer Kreditraten-Regler.
# Der Regler arbeitet prozentual zum Netto-Haushaltseinkommen.
# Links endet er bei 0 EUR Kreditrate. Rechts endet er dort, wo zuerst
# entweder 45 % vom Netto oder 300 EUR Mindest-Sicherheitspuffer erreicht sind.
slider_css = '''
.budget-rate-slider-wrap{margin-top:10px;padding:11px 12px;border:1px solid #e2e8f0;border-radius:13px;background:#f8fafc}
.budget-rate-slider-head{display:flex;justify-content:space-between;gap:10px;align-items:baseline;margin-bottom:7px;font-size:11px;color:#52627a}
.budget-rate-slider-head strong{font-size:12px;color:#172033}
#budgetRateSlider{width:100%;height:24px;min-height:24px;padding:0;border:0;background:transparent;accent-color:var(--rate-slider-color,#22c55e);cursor:pointer}
#budgetRateSlider::-webkit-slider-runnable-track{height:7px;border-radius:999px;background:linear-gradient(to right,var(--rate-slider-color,#22c55e) 0 var(--rate-slider-fill,0%),#dbe3ec var(--rate-slider-fill,0%) 100%)}
#budgetRateSlider::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:20px;height:20px;border-radius:50%;background:var(--rate-slider-color,#22c55e);border:3px solid #fff;box-shadow:0 1px 5px rgba(15,23,42,.22);margin-top:-6.5px}
#budgetRateSlider::-moz-range-track{height:7px;border-radius:999px;background:#dbe3ec}
#budgetRateSlider::-moz-range-progress{height:7px;border-radius:999px;background:var(--rate-slider-color,#22c55e)}
#budgetRateSlider::-moz-range-thumb{width:16px;height:16px;border-radius:50%;background:var(--rate-slider-color,#22c55e);border:3px solid #fff;box-shadow:0 1px 5px rgba(15,23,42,.22)}
.budget-rate-slider-note{margin-top:6px;font-size:10.5px;line-height:1.4;color:#64748b}
.budget-rate-slider-warning{margin-top:7px;padding:8px 10px;border-radius:9px;background:#fef2f2;border:1px solid #fecaca;color:#b91c1c;font-size:10.5px;font-weight:700;line-height:1.4}
.budget-rate-slider-warning[hidden]{display:none}
'''
css_anchor = '.budget-rate-guidance{margin-top:8px;padding:9px 10px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;color:#52627a;font-size:11px;line-height:1.45}'
if slider_css.strip() not in s:
    if css_anchor not in s:
        raise SystemExit("V8.234 slider CSS anchor not found")
    s=s.replace(css_anchor,css_anchor+slider_css,1)

slider_markup = '''          <div class="budget-rate-slider-wrap">
            <div class="budget-rate-slider-head">
              <span>Maximal tragbare Kreditrate</span>
              <strong id="budgetRateSliderValue">–</strong>
            </div>
            <input id="budgetRateSlider" type="range" min="0" max="45" step="0.1" value="0" aria-label="Maximal tragbare Kreditrate in Prozent vom Netto-Haushaltseinkommen">
            <div class="budget-rate-slider-note" id="budgetRateSliderNote">Nach links sinkt die Kreditrate und der Sicherheitspuffer steigt. Nach rechts umgekehrt.</div>
            <div class="budget-rate-slider-warning" id="budgetRateSliderWarning" hidden>Mindestpuffer unterschritten. Bitte Einnahmen oder Ausgaben prüfen.</div>
          </div>
'''
guidance_anchor = '          <div class="budget-rate-guidance" id="budgetRateGuidance">Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten. Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung.</div>'
if slider_markup.strip() not in s:
    if guidance_anchor not in s:
        raise SystemExit("V8.234 slider markup anchor not found")
    s=s.replace(guidance_anchor,slider_markup+guidance_anchor,1)

state_anchor='let budgetIncomeAutoUpdating = false;'
toast_state_block='''let budgetRateSliderSyncing = false;
let budgetRateBeforeRecalc=null;
let budgetInputValueBeforeRecalc=null;
let budgetRateNeedsInitialValue=localStorage.getItem("ff_budget_rateNeedsInitialValue")==="1";
let budgetRateManualSelection=localStorage.getItem("ff_budget_rateManualSelection")==="1";'''
if toast_state_block not in s:
    if state_anchor not in s:
        raise SystemExit("V8.234 slider state anchor not found")
    s=s.replace(state_anchor,state_anchor+'\n'+toast_state_block,1)

old_budget_model='''  const reserve=Math.max(0,budgetVal("budgetSafetyReserve"));
  const available=Math.max(0,income-expenses-reserve);
  const rateCap=available;
  const monthlyRate=available;'''
new_budget_model='''  const freeBudget=income-expenses;
  const ratePool=Math.max(0,freeBudget);
  const minimumReserve=Math.max(300,freeBudget*0.10);
  const maxRateByReserve=Math.max(0,ratePool-minimumReserve);
  const maxRateByPct=Math.max(0,net*0.45);
  const rateCap=Math.max(0,Math.min(maxRateByReserve,maxRateByPct));
  const maxRatePct=net>0 ? (rateCap/net)*100 : 0;
  const defaultRate=Math.max(0,ratePool-minimumReserve);
  const defaultRatePct=net>0 ? (defaultRate/net)*100 : 0;
  const storedRatePctRaw=localStorage.getItem("ff_budget_rateSliderPct");
  const hasStoredRatePct=storedRatePctRaw!==null && Number.isFinite(Number(storedRatePctRaw));
  const requestedRatePct=hasStoredRatePct ? Number(storedRatePctRaw) : defaultRatePct;
  const requestedMonthlyRate=net>0 ? net*(Math.max(0,requestedRatePct)/100) : 0;
  const monthlyRate=Math.max(0,Math.min(Math.max(0,freeBudget),requestedMonthlyRate));
  const selectedRatePct=net>0 ? (monthlyRate/net)*100 : 0;
  const rawReserve=freeBudget-monthlyRate;
  const reserve=Math.max(0,rawReserve);
  // Anzeige "Frei verfügbares Monatsbudget": Einnahmen minus Ausgaben minus Mindest-Sicherheitspuffer.
  // Die Kreditraten-/Pufferlogik oben bleibt unverändert; der Puffer wird nicht doppelt abgezogen.
  const available=freeBudget-minimumReserve;'''
if old_budget_model not in s:
    raise SystemExit("V8.234 budget model anchor not found")
s=s.replace(old_budget_model,new_budget_model,1)

old_return='''    net,childBenefit,income,expenses,reserve,available,rateCap,monthlyRate,
    additionalBuffer:Math.max(0,available-monthlyRate),'''
new_return='''    net,childBenefit,income,expenses,reserve,rawReserve,minimumReserve,ratePool,available,rateCap,monthlyRate,
    maxMonthlyRate:rateCap,maxRatePct,selectedRatePct,
    additionalBuffer:reserve,'''
if old_return not in s:
    raise SystemExit("V8.234 budget model return anchor not found")
s=s.replace(old_return,new_return,1)

old_rate_line='  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);'
new_rate_line='''  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);
  if($("budgetRateSlider")){
    const slider=$("budgetRateSlider");
    const selectedPct=Math.max(0,m.selectedRatePct||0);
    const safeMaxPct=Math.max(0,m.maxRatePct||0);
    const sliderMaxPct=Math.max(safeMaxPct,selectedPct);
    slider.max=String(sliderMaxPct);
    slider.value=String(selectedPct);
    const fillPct=sliderMaxPct>0 ? Math.max(0,Math.min(100,(selectedPct/sliderMaxPct)*100)) : 0;
    const sliderColor=selectedPct>=40 ? "#dc2626" : (selectedPct>=35 ? "#eab308" : "#16a34a");
    slider.style.setProperty("--rate-slider-color",sliderColor);
    slider.style.setProperty("--rate-slider-fill",fillPct+"%");
    slider.setAttribute("aria-valuetext",eur(m.monthlyRate)+" · "+new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(selectedPct)+" % vom Netto-Haushaltseinkommen");
    if($("budgetRateSliderValue")){
      $("budgetRateSliderValue").textContent=eur(m.monthlyRate)+" · "+new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(selectedPct)+" %";
    }
    if($("budgetRateSliderNote")){
      const limitingReserve=m.rateCap<=Math.max(0,m.ratePool-m.minimumReserve)+0.01 && Math.max(0,m.ratePool-m.minimumReserve)<=Math.max(0,m.net*0.45)+0.01;
      const limitText=limitingReserve ? "Mindest-Sicherheitspuffer" : "45 % vom Netto-Haushaltseinkommen";
      $("budgetRateSliderNote").textContent="Aktueller Sicherheitspuffer: "+eur(m.rawReserve)+" · Mindest-Sicherheitspuffer: "+eur(m.minimumReserve);
      if($("budgetRateSliderWarning")){
        const currentBuffer=Number.isFinite(Number(m.rawReserve)) ? Number(m.rawReserve) : 0;
        const minimumReserve=Math.max(300,Number(m.minimumReserve)||300);
        const bufferDeviation=currentBuffer-minimumReserve;
        const minimumBufferBelow=bufferDeviation<-0.005;
        const minimumBufferReached=Math.abs(bufferDeviation)<=0.005;
        const minimumBufferAbove=bufferDeviation>0.005;
        $("budgetRateSliderWarning").hidden=minimumBufferAbove;
        if(minimumBufferBelow){
          $("budgetRateSliderWarning").textContent="Mindestpuffer unterschritten · Abweichung: "+eur(bufferDeviation)+" · Mindestpuffer: "+eur(minimumReserve)+" · Aktueller Puffer: "+eur(currentBuffer)+" · Bitte Einnahmen oder Ausgaben prüfen.";
        }else if(minimumBufferReached){
          $("budgetRateSliderWarning").textContent="Mindestpuffer erreicht: "+eur(minimumReserve)+". Bitte Einnahmen oder Ausgaben prüfen.";
        }else{
          $("budgetRateSliderWarning").textContent="";
        }

      }
    }
    if($("budgetSafetyReserve") && localStorage.getItem("ff_budget_rateSliderPct")!==null){
      budgetRateSliderSyncing=true;
      $("budgetSafetyReserve").value=String(Math.round(m.minimumReserve));
      budgetRateSliderSyncing=false;
      localStorage.setItem("ff_budget_rateSliderPct",String(selectedPct));
    }
  }'''
if old_rate_line not in s:
    raise SystemExit("V8.234 rate render anchor not found")
s=s.replace(old_rate_line,new_rate_line,1)

# Der Status neben der Rate folgt der aktuell gewählten, dynamischen Kreditrate.
old_ratio='const budgetRatePct = m.net > 0 ? (m.monthlyRate / m.net) * 100 : 0;'
if old_ratio not in s:
    raise SystemExit("V8.234 rate ratio anchor not found")

# Manuelle Änderung des Sicherheitspuffers setzt die Regler-Auswahl auf den daraus
# neu berechneten Startwert zurück.
old_reserve_listener='''  if(el.id==="budgetSafetyReserve" && !budgetAutoUpdating){
    budgetSafetyReserveManual=true;
    localStorage.setItem("ff_budget_safetyReserveManual","1");
  }'''
new_reserve_listener='''  if(el.id==="budgetSafetyReserve" && !budgetAutoUpdating && !budgetRateSliderSyncing){
    budgetSafetyReserveManual=true;
    localStorage.setItem("ff_budget_safetyReserveManual","1");
    localStorage.removeItem("ff_budget_rateSliderPct");
  }'''
if old_reserve_listener not in s:
    raise SystemExit("V8.234 reserve listener anchor not found")
s=s.replace(old_reserve_listener,new_reserve_listener,1)

slider_handler = '''if($("budgetRateSlider")){
  $("budgetRateSlider").addEventListener("input",()=>{
    budgetRateNeedsInitialValue=false;
    budgetRateManualSelection=true;
    localStorage.setItem("ff_budget_rateNeedsInitialValue","0");
    localStorage.setItem("ff_budget_rateManualSelection","1");
    const current=budgetModel();
    const safeMaxPct=Math.max(0,current.maxRatePct||0);
    const currentPct=Math.max(0,current.selectedRatePct||0);
    const sliderMaxPct=Math.max(safeMaxPct,currentPct);
    const selectedPct=Math.max(0,Math.min(sliderMaxPct,Number($("budgetRateSlider").value)||0));
    const selectedRate=current.net>0 ? current.net*(selectedPct/100) : 0;
    const totalReserve=Math.max(0,(current.ratePool||0)-selectedRate);

    budgetRateSliderSyncing=true;
    budgetSafetyReserveManual=true;
    if($("budgetSafetyReserve")) $("budgetSafetyReserve").value=String(Math.round(current.minimumReserve));
    localStorage.setItem("ff_budget_rateSliderPct",String(selectedPct));
    localStorage.setItem("ff_budget_safetyReserveManual","1");
    saveBudget();
    budgetRateSliderSyncing=false;
    renderBudget();
  });
}

'''
handler_anchor='if($("budgetAssumptionsToggle") && $("budgetAssumptionsSection")){'
if slider_handler not in s:
    if handler_anchor not in s:
        raise SystemExit("V8.234 slider handler anchor not found")
    s=s.replace(handler_anchor,slider_handler+handler_anchor,1)

# Alte V8.200-Speicherung nicht weiter verwenden.
s=s.replace('localStorage.removeItem("ff_budget_rateSliderExtra");','localStorage.removeItem("ff_budget_rateSliderPct");',1)

# V8.234: Einnahmen, Ausgaben und Finanzierungsannahmen nach den bestehenden
# Feld-Synchronisierungen neu bewerten. Die bestehende Berechnungslogik bleibt unveraendert.
budget_recalc_listener = '''const budgetRateIncomeIds=new Set([
  "budgetNetIncome",
  "budgetIncomeEmployment","budgetIncomePension","budgetIncomeSupport","budgetIncomeSide","budgetIncomeRent","budgetIncomeOther",
  "budgetChildBenefit"
]);
const budgetRateExpenseIds=new Set([
  "budgetFood","budgetMobility","budgetInsurance","budgetTelecom","budgetLeisure","budgetChildCosts","budgetExistingLoans","budgetOther"
]);
const budgetFinancingAssumptionIds=new Set([
  "budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"
]);
const budgetRateRecalcIds=new Set([...budgetRateIncomeIds,...budgetRateExpenseIds,...budgetFinancingAssumptionIds]);

document.addEventListener("beforeinput",(event)=>{
  const el=event.target;
  if(!el || !budgetRateRecalcIds.has(el.id)) return;
  const beforeChange=budgetModel();
  budgetRateBeforeRecalc=Math.max(0,Number(beforeChange.monthlyRate)||0);
  budgetInputValueBeforeRecalc=Math.max(0,Number(String(el.value||"0").replace(",", "."))||0);
},true);

document.addEventListener("focusin",(event)=>{
  const el=event.target;
  if(!el || !budgetRateRecalcIds.has(el.id)) return;
  const beforeChange=budgetModel();
  budgetRateBeforeRecalc=Math.max(0,Number(beforeChange.monthlyRate)||0);
  budgetInputValueBeforeRecalc=Math.max(0,Number(String(el.value||"0").replace(",", "."))||0);
},true);

document.addEventListener("input",(event)=>{
  const el=event.target;
  if(!el || !budgetRateRecalcIds.has(el.id)) return;

  const newInput=Math.max(0,Number(String(el.value||"0").replace(",", "."))||0);
  const previousRate=Math.max(0,Number(budgetRateBeforeRecalc)||0);

  // Solange der Regler nicht manuell bewegt wurde, bleibt 35 % vom Haushaltsnetto
  // der automatische Zielwert. Die sichere Budgetgrenze kann diesen Wert nur nach unten begrenzen.
  // Nach einer manuellen Reglerbewegung bleibt die gewählte absolute Rate erhalten,
  // wird bei Änderungen aber weiterhin auf die aktuell sichere Maximalrate begrenzt.
  localStorage.removeItem("ff_budget_rateSliderPct");
  const recalculated=budgetModel();
  const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));
  const adjustedRate=budgetRateManualSelection
    ? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))
    : automaticRate;
  const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;
  localStorage.setItem("ff_budget_rateSliderPct",String(preservedRatePct));

  budgetRateSliderSyncing=true;
  if($("budgetSafetyReserve")) $("budgetSafetyReserve").value=String(Math.round(recalculated.minimumReserve));
  budgetRateSliderSyncing=false;

  renderBudget();
  budgetRateBeforeRecalc=null;
  budgetInputValueBeforeRecalc=newInput;
});

// V8.234: Nur nach einem bestätigten Budget-Reset wird beim ersten abgeschlossenen
// Einkommenseintrag einmalig eine sinnvolle Start-Kreditrate gesetzt.
// Während des Tippens bleibt die Rate 0; so wird z. B. "4000" nicht schon bei "4"
// oder "40" initialisiert. Danach bleibt die bestehende V8.234-Logik unverändert.
document.addEventListener("focusout",(event)=>{
  const el=event.target;
  if(!el || !budgetRateNeedsInitialValue || !budgetRateIncomeIds.has(el.id)) return;

  const m=budgetModel();
  if(!(m.net>0)) return;

  const initialRatePct=Math.min(35,Math.max(0,m.maxRatePct||0));
  localStorage.setItem("ff_budget_rateSliderPct",String(initialRatePct));
  budgetRateNeedsInitialValue=false;
  budgetRateManualSelection=false;
  localStorage.setItem("ff_budget_rateNeedsInitialValue","0");
  localStorage.setItem("ff_budget_rateManualSelection","0");
  budgetRateBeforeRecalc=null;
  renderBudget();
},true);
'''
recalc_anchor='if($("budgetAssumptionsToggle") && $("budgetAssumptionsSection")){'
if budget_recalc_listener not in s:
    if recalc_anchor not in s:
        raise SystemExit("V8.234 budget recalc listener anchor not found")
    s=s.replace(recalc_anchor,budget_recalc_listener+"\n"+recalc_anchor,1)

# V8.234: Den Kreditraten-Regler aus dem globalen Input-Listener ausschliessen.
# Sonst rendert der globale Listener zuerst und setzt den Slider zurueck,
# bevor sein eigener input-Handler den neuen Wert lesen kann.
generic_input_selector = "document.querySelectorAll('input:not(.trade-amount):not([name=\"dealType\"]),select')"
generic_input_selector_fixed = "document.querySelectorAll('input:not(.trade-amount):not([name=\"dealType\"]):not(#budgetRateSlider),select')"
if generic_input_selector not in s:
    raise SystemExit("V8.234 global input selector anchor not found")
s=s.replace(generic_input_selector,generic_input_selector_fixed,1)

required_v8203_tokens = [
    'id="budgetRateSlider"',
    'ff_budget_rateSliderPct',
    'ff_budget_rateNeedsInitialValue',
    'budgetRateNeedsInitialValue=true;',
    'document.addEventListener("focusout",(event)=>',
    'if(!el || !budgetRateNeedsInitialValue || !budgetRateIncomeIds.has(el.id)) return;',
    'const initialRatePct=Math.min(35,Math.max(0,m.maxRatePct||0));',
    'localStorage.setItem("ff_budget_rateSliderPct",String(initialRatePct));',
    'budgetRateNeedsInitialValue=false;',
    'const requestedMonthlyRate=net>0 ? net*(Math.max(0,requestedRatePct)/100) : 0;',
    'const monthlyRate=Math.max(0,Math.min(Math.max(0,freeBudget),requestedMonthlyRate));',
    'const selectedRatePct=net>0 ? (monthlyRate/net)*100 : 0;',

    'const sliderMaxPct=Math.max(safeMaxPct,selectedPct);',
    'slider.max=String(sliderMaxPct)',
    'slider.value=String(selectedPct)',
    'budgetRateBeforeRecalc=Math.max(0,Number(beforeChange.monthlyRate)||0);',
    'const previousRate=Math.max(0,Number(budgetRateBeforeRecalc)||0);',
    'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    'const adjustedRate=budgetRateManualSelection',
    '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    ': automaticRate;',
    'const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;',
    'const minimumReserve=Math.max(300,freeBudget*0.10);',
    'const rawReserve=freeBudget-monthlyRate;',
    'const currentBuffer=Number.isFinite(Number(m.rawReserve)) ? Number(m.rawReserve) : 0;',
    'const bufferDeviation=currentBuffer-minimumReserve;',
    'const minimumBufferBelow=bufferDeviation<-0.005;',
    'const minimumBufferAbove=bufferDeviation>0.005;',
    '$("budgetRateSliderWarning").hidden=minimumBufferAbove;',
    'Mindestpuffer unterschritten · Abweichung: "+eur(bufferDeviation)',
    'Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten.',
    'const maxRateByReserve=Math.max(0,ratePool-minimumReserve);',
    'const maxRateByPct=Math.max(0,net*0.45);',
    'Sicherheitspuffer: "+eur(m.rawReserve)',
    ':not(#budgetRateSlider),select\')',
    'const budgetRateIncomeIds=new Set([',
    'const budgetRateExpenseIds=new Set([',
    'const budgetFinancingAssumptionIds=new Set([',
    '"budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"',
    'const budgetRateRecalcIds=new Set([...budgetRateIncomeIds,...budgetRateExpenseIds,...budgetFinancingAssumptionIds]);',
    'budgetInputValueBeforeRecalc=Math.max(0,Number(String(el.value||"0").replace(",", "."))||0);',
    'localStorage.removeItem("ff_budget_rateSliderPct");',
    'document.addEventListener("input",(event)=>',
    'id="budgetSafetyReserve" inputmode="decimal" value="300" readonly aria-readonly="true"',
    '10 % von Einnahmen − Ausgaben · mindestens 300 €',
    'Mindest-Sicherheitspuffer',
    '"Mindestpuffer erreicht: "+eur(minimumReserve)+". Bitte Einnahmen oder Ausgaben prüfen."',
    'document.addEventListener("input",(event)=>',
    '},true);',
    'renderBudget();'
]
missing_v8203_tokens=[token for token in required_v8203_tokens if token not in s]
if missing_v8203_tokens:
    raise SystemExit("V8.234 slider verification failed: "+", ".join(missing_v8203_tokens))


# V8.234: Monatliche Belastung & Restschuld strukturell vom Tragfaehigkeits-Slider entkoppeln.
# Grundlage ist ausschließlich das bereits berechnete Max. Darlehen sowie Zins + Tilgung.
old_budget_loan_burden = '''  const interestPart=loan*interestPct/12;
  const repaymentPart=Math.max(0,monthlyRate-interestPart);

  function remainingDebt(years){
    const n=Math.max(0,Math.round(years*12));
    const r=interestPct/12;
    if(loan<=0) return 0;
    if(r<=0) return Math.max(0,loan-monthlyRate*n);
    const factor=Math.pow(1+r,n);
    return Math.max(0,loan*factor-monthlyRate*((factor-1)/r));
  }'''
new_budget_loan_burden = '''  const loanMonthlyRate=loan*debtServicePct/12;
  const interestPart=loan*interestPct/12;
  const repaymentPart=loan*repaymentPct/12;

  function remainingDebt(years){
    const n=Math.max(0,Math.round(years*12));
    const r=interestPct/12;
    if(loan<=0) return 0;
    if(r<=0) return Math.max(0,loan-loanMonthlyRate*n);
    const factor=Math.pow(1+r,n);
    return Math.max(0,loan*factor-loanMonthlyRate*((factor-1)/r));
  }'''
if old_budget_loan_burden not in s:
    raise SystemExit("V8.234 loan burden calculation anchor not found")
s=s.replace(old_budget_loan_burden,new_budget_loan_burden,1)

old_budget_return_tail='''    interestPct,repaymentPct,loan,equity,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,
    interestPart,repaymentPart,debt10:remainingDebt(10),debt20:remainingDebt(20),debt30:remainingDebt(30)'''
new_budget_return_tail='''    interestPct,repaymentPct,loan,loanMonthlyRate,equity,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,
    interestPart,repaymentPart,debt10:remainingDebt(10),debt20:remainingDebt(20),debt30:remainingDebt(30)'''
if old_budget_return_tail not in s:
    raise SystemExit("V8.234 budget return tail anchor not found")
s=s.replace(old_budget_return_tail,new_budget_return_tail,1)

if '<div class="budget-summary-row total"><span>Monatliche Rate</span><strong id="budgetMonthlyRateResult">–</strong></div>' not in s:
    raise SystemExit("V8.234 monthly rate label anchor not found")
s=s.replace(
    '<div class="budget-summary-row total"><span>Monatliche Rate</span><strong id="budgetMonthlyRateResult">–</strong></div>',
    '<div class="budget-summary-row total"><span>Monatliche Rate (Max. Darlehen)</span><strong id="budgetMonthlyRateResult">–</strong></div>',
    1
)

if 'if($("budgetMonthlyRateResult")) $("budgetMonthlyRateResult").textContent=eur(m.monthlyRate);' not in s:
    raise SystemExit("V8.234 monthly rate render anchor not found")
s=s.replace(
    'if($("budgetMonthlyRateResult")) $("budgetMonthlyRateResult").textContent=eur(m.monthlyRate);',
    'if($("budgetMonthlyRateResult")) $("budgetMonthlyRateResult").textContent=eur(m.loanMonthlyRate);',
    1
)

if 'line("Monatliche Rate",pdfMoney(m.monthlyRate),true);' not in s:
    raise SystemExit("V8.234 budget PDF monthly rate anchor not found")
s=s.replace(
    'line("Monatliche Rate",pdfMoney(m.monthlyRate),true);',
    'line("Monatliche Rate (Max. Darlehen)",pdfMoney(m.loanMonthlyRate),true);',
    1
)

# V8.234: Freies Budget darf negativ sein; Kreditrate bleibt bei Defizit 0.
required_v8223_tokens = [
    'const freeBudget=income-expenses;',
    'const ratePool=Math.max(0,freeBudget);',
    'const minimumReserve=Math.max(300,freeBudget*0.10);',
    'const requestedMonthlyRate=net>0 ? net*(Math.max(0,requestedRatePct)/100) : 0;',
    'const monthlyRate=Math.max(0,Math.min(Math.max(0,freeBudget),requestedMonthlyRate));',
    'const selectedRatePct=net>0 ? (monthlyRate/net)*100 : 0;',
    'const rawReserve=freeBudget-monthlyRate;',
    'const available=freeBudget-minimumReserve;',
    'Mindest-Sicherheitspuffer',
    'eur(m.minimumReserve)'
]
missing_v8223_tokens=[token for token in required_v8223_tokens if token not in s]
if missing_v8223_tokens:
    raise SystemExit("V8.234 free-budget verification failed: "+", ".join(missing_v8223_tokens))

# V8.234: Kreditrate ist immer zwischen 0 und freiem Monatsbudget gedeckelt.
required_v8224_tokens = [
    'const requestedMonthlyRate=net>0 ? net*(Math.max(0,requestedRatePct)/100) : 0;',
    'const monthlyRate=Math.max(0,Math.min(Math.max(0,freeBudget),requestedMonthlyRate));',
    'const selectedRatePct=net>0 ? (monthlyRate/net)*100 : 0;'
]
missing_v8224_tokens=[token for token in required_v8224_tokens if token not in s]
if missing_v8224_tokens:
    raise SystemExit("V8.234 credit-rate cap verification failed: "+", ".join(missing_v8224_tokens))

# V8.234: Jede nachtraegliche Ausgabenaenderung setzt die Rate auf die neu sichere Maximalrate.
required_v8225_tokens = [
    'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    'const adjustedRate=budgetRateManualSelection',
    '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    ': automaticRate;',
    'const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;'
]
missing_v8225_tokens=[token for token in required_v8225_tokens if token not in s]
if missing_v8225_tokens:
    raise SystemExit("V8.234 expense recalculation verification failed: "+", ".join(missing_v8225_tokens))

# V8.234: Jede nachtraegliche Ausgabenaenderung setzt die Rate auf die neu sichere Maximalrate.
required_v8226_tokens = [
    'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    'const adjustedRate=budgetRateManualSelection',
    '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    ': automaticRate;',
    'const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;'
]
missing_v8226_tokens=[token for token in required_v8226_tokens if token not in s]
if missing_v8226_tokens:
    raise SystemExit("V8.234 expense full recalculation verification failed: "+", ".join(missing_v8226_tokens))

# V8.234: Warnung wird nur fuer < oder = Mindestpuffer angezeigt.
required_v8227_tokens = [
    'const minimumBufferAbove=bufferDeviation>0.005;',
    '$("budgetRateSliderWarning").hidden=minimumBufferAbove;',
    'if(minimumBufferBelow){',
    '}else if(minimumBufferReached){',
    '$("budgetRateSliderWarning").textContent="";'
]
missing_v8227_tokens=[token for token in required_v8227_tokens if token not in s]
if missing_v8227_tokens:
    raise SystemExit("V8.234 warning display verification failed: "+", ".join(missing_v8227_tokens))

# V8.234: Automatik startet bei 35 %, manuelle Reglerwahl uebernimmt danach.
required_v8228_tokens = [
    'let budgetRateManualSelection=localStorage.getItem("ff_budget_rateManualSelection")==="1";',
    'budgetRateManualSelection=true;',
    'localStorage.setItem("ff_budget_rateManualSelection","1");',
    'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    'const adjustedRate=budgetRateManualSelection',
    '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    ': automaticRate;',
    'const initialRatePct=Math.min(35,Math.max(0,m.maxRatePct||0));'
]
missing_v8228_tokens=[token for token in required_v8228_tokens if token not in s]
if missing_v8228_tokens:
    raise SystemExit("V8.234 35-percent initialization verification failed: "+", ".join(missing_v8228_tokens))

# V8.234: Alle Budget-Eingabekategorien loesen dieselbe Neuberechnung aus.
required_v8229_tokens = [
    'const budgetFinancingAssumptionIds=new Set([',
    '"budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"',
    'const budgetRateRecalcIds=new Set([...budgetRateIncomeIds,...budgetRateExpenseIds,...budgetFinancingAssumptionIds]);'
]
missing_v8229_tokens=[token for token in required_v8229_tokens if token not in s]
if missing_v8229_tokens:
    raise SystemExit("V8.234 full-input recalculation verification failed: "+", ".join(missing_v8229_tokens))

# V8.234: Frei verfuegbares Monatsbudget wird nach Mindestpuffer angezeigt.
required_v8230_tokens = [
    'const freeBudget=income-expenses;',
    'const minimumReserve=Math.max(300,freeBudget*0.10);',
    'const maxRateByReserve=Math.max(0,ratePool-minimumReserve);',
    'const available=freeBudget-minimumReserve;',
    'const rawReserve=freeBudget-monthlyRate;'
]
missing_v8230_tokens=[token for token in required_v8230_tokens if token not in s]
if missing_v8230_tokens:
    raise SystemExit("V8.234 available-budget verification failed: "+", ".join(missing_v8230_tokens))

# V8.234: Begriffe klar trennen:
# - Finanzierungsreserve = vorgesehene Mindestreserve
# - Aktueller Sicherheitspuffer = tatsaechlich verbleibender Betrag nach Kreditrate
s=s.replace("Mindest-Sicherheitspuffer","Finanzierungsreserve")
s=s.replace("Mindestpuffer unterschritten","Finanzierungsreserve unterschritten")
s=s.replace("Mindestpuffer erreicht","Finanzierungsreserve erreicht")
s=s.replace("Mindestpuffer:","Finanzierungsreserve:")
s=s.replace("Sicherheitsreserve","Aktueller Sicherheitspuffer")

required_v8231_tokens = [
    "Finanzierungsreserve",
    "Aktueller Sicherheitspuffer",
    "Finanzierungsreserve unterschritten",
    "Finanzierungsreserve erreicht"
]
missing_v8231_tokens=[token for token in required_v8231_tokens if token not in s]
if missing_v8231_tokens:
    raise SystemExit("V8.234 terminology verification failed: "+", ".join(missing_v8231_tokens))
if "Mindest-Sicherheitspuffer" in s or "Mindestpuffer unterschritten" in s or "Mindestpuffer erreicht" in s:
    raise SystemExit("V8.234 terminology verification failed: legacy minimum-buffer wording remains")

# V8.234: Finanzierungsreserve im monatlich verfuegbaren Budget direkt unter Feste Ausgaben ausweisen.
budget_summary_expenses_row = '<div class="budget-summary-row"><span>- Feste Ausgaben</span><strong id="budgetExpensesResult">–</strong></div>'
budget_summary_financing_reserve_row = budget_summary_expenses_row + '\n          <div class="budget-summary-row"><span>- Finanzierungsreserve</span><strong id="budgetFinancingReserveResult">–</strong></div>'
if budget_summary_expenses_row not in s:
    raise SystemExit("V8.234 budget summary expenses row anchor not found")
s=s.replace(budget_summary_expenses_row,budget_summary_financing_reserve_row,1)

budget_summary_render_anchor = 'if($("budgetExpensesResult")) $("budgetExpensesResult").textContent=eur(m.expenses);'
budget_summary_render_new = budget_summary_render_anchor + '\n  if($("budgetFinancingReserveResult")) $("budgetFinancingReserveResult").textContent=eur(m.minimumReserve);'
if budget_summary_render_anchor not in s:
    raise SystemExit("V8.234 budget summary render anchor not found")
s=s.replace(budget_summary_render_anchor,budget_summary_render_new,1)

required_v8232_tokens = [
    '<span>- Finanzierungsreserve</span><strong id="budgetFinancingReserveResult">–</strong>',
    'if($("budgetFinancingReserveResult")) $("budgetFinancingReserveResult").textContent=eur(m.minimumReserve);',
    '<span>- Aktueller Sicherheitspuffer</span><strong id="budgetReserveResult">–</strong>'
]
missing_v8232_tokens=[token for token in required_v8232_tokens if token not in s]
if missing_v8232_tokens:
    raise SystemExit("V8.234 financing-reserve summary verification failed: "+", ".join(missing_v8232_tokens))

# V8.234: Budget startet mit 0 EUR Ausgaben und 0 EUR Finanzierungsreserve.
# Vorschlaege werden nur noch angezeigt und erst ueber "Vorschlaege uebernehmen" in die Felder geschrieben.
expense_zero_ids = [
    "budgetFood","budgetMobility","budgetInsurance","budgetTelecom",
    "budgetLeisure","budgetChildCosts","budgetExistingLoans","budgetOther"
]
for expense_id in expense_zero_ids:
    pattern = re.compile(r'(<input[^>]*id="' + re.escape(expense_id) + r'"[^>]*value=")[^"]*(")')
    s, count = pattern.subn(r'\g<1>0\2', s, count=1)
    if count != 1:
        raise SystemExit("V8.234 expense default anchor not found: " + expense_id)

reserve_pattern = re.compile(r'(<input[^>]*id="budgetSafetyReserve"[^>]*value=")[^"]*(")')
s, reserve_count = reserve_pattern.subn(r'\g<1>0\2', s, count=1)
if reserve_count != 1:
    raise SystemExit("V8.234 financing reserve default anchor not found")

old_sync_suggestions = '''function syncBudgetSuggestions(){
  const s=getBudgetSuggestions();
  budgetAutoUpdating=true;
  budgetSuggestedExpenseIds.forEach(id=>{
    if(!budgetExpenseManual[id] && $(id)){
      $(id).value=String(Math.round(s[id]));
    }
  });
  budgetAutoUpdating=false;
  renderBudgetSuggestions();
}'''
new_sync_suggestions = '''function syncBudgetSuggestions(){
  // Vorschlaege nur aktualisieren; die Eingabefelder bleiben unveraendert,
  // bis der Nutzer "Vorschlaege uebernehmen" auswaehlt.
  renderBudgetSuggestions();
}'''
if old_sync_suggestions not in s:
    raise SystemExit("V8.234 suggestion sync anchor not found")
s=s.replace(old_sync_suggestions,new_sync_suggestions,1)

# Finanzierungsreserve erst berechnen, sobald ein positives Haushaltsnettoeinkommen vorliegt.
old_sync_reserve = '''  const freeBudget=income-expenses;
  const minimumReserve=Math.max(300,freeBudget*0.10);
  budgetAutoUpdating=true;'''
new_sync_reserve = '''  const freeBudget=income-expenses;
  const minimumReserve=net>0 ? Math.max(300,freeBudget*0.10) : 0;
  budgetAutoUpdating=true;'''
if old_sync_reserve not in s:
    raise SystemExit("V8.234 reserve sync anchor not found")
s=s.replace(old_sync_reserve,new_sync_reserve,1)

old_model_reserve = '  const minimumReserve=Math.max(300,freeBudget*0.10);'
new_model_reserve = '  const minimumReserve=net>0 ? Math.max(300,freeBudget*0.10) : 0;'
if old_model_reserve not in s:
    raise SystemExit("V8.234 budget model reserve anchor not found")
s=s.replace(old_model_reserve,new_model_reserve,1)

# Reset erzwingt 0 EUR fuer alle festen Ausgaben und fuer die Finanzierungsreserve.
reset_anchor = '''  if($("budgetIncomeEmployment")) $("budgetIncomeEmployment").value="0";
  if($("budgetChildBenefit")) $("budgetChildBenefit").value="0";'''
reset_new = reset_anchor + '''
  budgetExpenseIds.forEach(id=>{
    if($(id)) $(id).value="0";
  });
  if($("budgetSafetyReserve")) $("budgetSafetyReserve").value="0";'''
if reset_anchor not in s:
    raise SystemExit("V8.234 budget reset anchor not found")
s=s.replace(reset_anchor,reset_new,1)

required_v8233_tokens = [
    'function syncBudgetSuggestions(){',
    'Vorschlaege nur aktualisieren; die Eingabefelder bleiben unveraendert',
    'const minimumReserve=net>0 ? Math.max(300,freeBudget*0.10) : 0;',
    'budgetExpenseIds.forEach(id=>{',
    'if($("budgetSafetyReserve")) $("budgetSafetyReserve").value="0";',
    'function applyBudgetSuggestions(){'
]
missing_v8233_tokens=[token for token in required_v8233_tokens if token not in s]
if missing_v8233_tokens:
    raise SystemExit("V8.234 zero-default verification failed: "+", ".join(missing_v8233_tokens))

for expense_id in expense_zero_ids:
    if not re.search(r'<input[^>]*id="' + re.escape(expense_id) + r'"[^>]*value="0"', s):
        raise SystemExit("V8.234 expense zero default verification failed: " + expense_id)
if not re.search(r'<input[^>]*id="budgetSafetyReserve"[^>]*value="0"', s):
    raise SystemExit("V8.234 reserve zero default verification failed")

# V8.234: "Aktueller Sicherheitspuffer" wird zum verbleibenden Monatsueberschuss
# nach separatem Abzug der Finanzierungsreserve.
model_anchor = '''  const rawReserve=freeBudget-monthlyRate;
  const reserve=Math.max(0,rawReserve);'''
model_new = '''  const rawReserve=freeBudget-monthlyRate;
  const reserve=Math.max(0,rawReserve);
  const remainingMonthlySurplus=rawReserve-minimumReserve;'''
if model_anchor not in s:
    raise SystemExit("V8.234 remaining surplus model anchor not found")
s=s.replace(model_anchor,model_new,1)

return_anchor = 'net,childBenefit,income,expenses,reserve,rawReserve,minimumReserve,ratePool,available,rateCap,monthlyRate,'
return_new = 'net,childBenefit,income,expenses,reserve,rawReserve,remainingMonthlySurplus,minimumReserve,ratePool,available,rateCap,monthlyRate,'
if return_anchor not in s:
    raise SystemExit("V8.234 remaining surplus return anchor not found")
s=s.replace(return_anchor,return_new,1)

if 'additionalBuffer:reserve,' not in s:
    raise SystemExit("V8.234 PDF surplus value anchor not found")
s=s.replace('additionalBuffer:reserve,','additionalBuffer:remainingMonthlySurplus,',1)

s=s.replace(
    '<span>- Aktueller Sicherheitspuffer</span><strong id="budgetReserveResult">–</strong>',
    '<span>- Verbleibender Monatsüberschuss</span><strong id="budgetReserveResult">–</strong>',
    1
)
s=s.replace(
    'if($("budgetReserveResult")) $("budgetReserveResult").textContent=eur(m.reserve);',
    'if($("budgetReserveResult")) $("budgetReserveResult").textContent=eur(m.remainingMonthlySurplus);',
    1
)
s=s.replace(
    'Aktueller Sicherheitspuffer: "+eur(m.rawReserve)+" · Finanzierungsreserve: "+eur(m.minimumReserve)',
    'Verbleibender Monatsüberschuss: "+eur(m.remainingMonthlySurplus)+" · Finanzierungsreserve: "+eur(m.minimumReserve)',
    1
)
s=s.replace(
    'Nach links sinkt die Kreditrate und der Sicherheitspuffer steigt. Nach rechts umgekehrt.',
    'Nach links sinkt die Kreditrate und der verbleibende Monatsüberschuss steigt. Nach rechts umgekehrt.',
    1
)
s=s.replace(
    'line("Zusaetzlicher Monats-Puffer",pdfMoney(m.additionalBuffer));',
    'line("Verbleibender Monatsueberschuss",pdfMoney(m.additionalBuffer));',
    1
)

required_v8234_tokens = [
    'const remainingMonthlySurplus=rawReserve-minimumReserve;',
    '<span>- Verbleibender Monatsüberschuss</span><strong id="budgetReserveResult">–</strong>',
    'if($("budgetReserveResult")) $("budgetReserveResult").textContent=eur(m.remainingMonthlySurplus);',
    'Verbleibender Monatsüberschuss: "+eur(m.remainingMonthlySurplus)+" · Finanzierungsreserve: "+eur(m.minimumReserve)',
    'additionalBuffer:remainingMonthlySurplus,',
    'line("Verbleibender Monatsueberschuss",pdfMoney(m.additionalBuffer));'
]
missing_v8234_tokens=[token for token in required_v8234_tokens if token not in s]
if missing_v8234_tokens:
    raise SystemExit("V8.234 remaining surplus verification failed: "+", ".join(missing_v8234_tokens))
if '<span>- Aktueller Sicherheitspuffer</span><strong id="budgetReserveResult">–</strong>' in s:
    raise SystemExit("V8.234 legacy current safety buffer label remains")

path.write_text(s, encoding="utf-8")
print("V8.234 interest and repayment patch applied")
