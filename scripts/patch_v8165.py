Warning: truncated output (original token count: 29504)
Total output lines: 2446

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

# V8.236: Kaufpreis-Check in Budget und Eigennutzung standardmaessig geschlossen.
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

# V8.236: Two-decimal interest/repayment display and compact 5-line Budget recommendation box.
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

# V8.236: Budget-PDF Abschnittsueberschriften wie in den anderen Berichten:
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
  line("  Rente / Pension",pdfMone…9504 tokens truncated…ptionIds]);',
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
    raise SystemExit("V8.236 slider verification failed: "+", ".join(missing_v8203_tokens))


# V8.236: Monatliche Belastung & Restschuld strukturell vom Tragfaehigkeits-Slider entkoppeln.
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
    raise SystemExit("V8.236 loan burden calculation anchor not found")
s=s.replace(old_budget_loan_burden,new_budget_loan_burden,1)

old_budget_return_tail='''    interestPct,repaymentPct,loan,equity,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,
    interestPart,repaymentPart,debt10:remainingDebt(10),debt20:remainingDebt(20),debt30:remainingDebt(30)'''
new_budget_return_tail='''    interestPct,repaymentPct,loan,loanMonthlyRate,equity,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,
    interestPart,repaymentPart,debt10:remainingDebt(10),debt20:remainingDebt(20),debt30:remainingDebt(30)'''
if old_budget_return_tail not in s:
    raise SystemExit("V8.236 budget return tail anchor not found")
s=s.replace(old_budget_return_tail,new_budget_return_tail,1)

if '<div class="budget-summary-row total"><span>Monatliche Rate</span><strong id="budgetMonthlyRateResult">–</strong></div>' not in s:
    raise SystemExit("V8.236 monthly rate label anchor not found")
s=s.replace(
    '<div class="budget-summary-row total"><span>Monatliche Rate</span><strong id="budgetMonthlyRateResult">–</strong></div>',
    '<div class="budget-summary-row total"><span>Monatliche Rate (Max. Darlehen)</span><strong id="budgetMonthlyRateResult">–</strong></div>',
    1
)

if 'if($("budgetMonthlyRateResult")) $("budgetMonthlyRateResult").textContent=eur(m.monthlyRate);' not in s:
    raise SystemExit("V8.236 monthly rate render anchor not found")
s=s.replace(
    'if($("budgetMonthlyRateResult")) $("budgetMonthlyRateResult").textContent=eur(m.monthlyRate);',
    'if($("budgetMonthlyRateResult")) $("budgetMonthlyRateResult").textContent=eur(m.loanMonthlyRate);',
    1
)

if 'line("Monatliche Rate",pdfMoney(m.monthlyRate),true);' not in s:
    raise SystemExit("V8.236 budget PDF monthly rate anchor not found")
s=s.replace(
    'line("Monatliche Rate",pdfMoney(m.monthlyRate),true);',
    'line("Monatliche Rate (Max. Darlehen)",pdfMoney(m.loanMonthlyRate),true);',
    1
)

# V8.236: Freies Budget darf negativ sein; Kreditrate bleibt bei Defizit 0.
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
    raise SystemExit("V8.236 free-budget verification failed: "+", ".join(missing_v8223_tokens))

# V8.236: Kreditrate ist immer zwischen 0 und freiem Monatsbudget gedeckelt.
required_v8224_tokens = [
    'const requestedMonthlyRate=net>0 ? net*(Math.max(0,requestedRatePct)/100) : 0;',
    'const monthlyRate=Math.max(0,Math.min(Math.max(0,freeBudget),requestedMonthlyRate));',
    'const selectedRatePct=net>0 ? (monthlyRate/net)*100 : 0;'
]
missing_v8224_tokens=[token for token in required_v8224_tokens if token not in s]
if missing_v8224_tokens:
    raise SystemExit("V8.236 credit-rate cap verification failed: "+", ".join(missing_v8224_tokens))

# V8.236: Jede nachtraegliche Ausgabenaenderung setzt die Rate auf die neu sichere Maximalrate.
required_v8225_tokens = [
    'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    'const adjustedRate=budgetRateManualSelection',
    '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    ': automaticRate;',
    'const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;'
]
missing_v8225_tokens=[token for token in required_v8225_tokens if token not in s]
if missing_v8225_tokens:
    raise SystemExit("V8.236 expense recalculation verification failed: "+", ".join(missing_v8225_tokens))

# V8.236: Jede nachtraegliche Ausgabenaenderung setzt die Rate auf die neu sichere Maximalrate.
required_v8226_tokens = [
    'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    'const adjustedRate=budgetRateManualSelection',
    '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    ': automaticRate;',
    'const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;'
]
missing_v8226_tokens=[token for token in required_v8226_tokens if token not in s]
if missing_v8226_tokens:
    raise SystemExit("V8.236 expense full recalculation verification failed: "+", ".join(missing_v8226_tokens))

# V8.236: Warnung wird nur fuer < oder = Mindestpuffer angezeigt.
required_v8227_tokens = [
    'const minimumBufferAbove=bufferDeviation>0.005;',
    '$("budgetRateSliderWarning").hidden=minimumBufferAbove;',
    'if(minimumBufferBelow){',
    '}else if(minimumBufferReached){',
    '$("budgetRateSliderWarning").textContent="";'
]
missing_v8227_tokens=[token for token in required_v8227_tokens if token not in s]
if missing_v8227_tokens:
    raise SystemExit("V8.236 warning display verification failed: "+", ".join(missing_v8227_tokens))

# V8.236: Automatik startet bei 35 %, manuelle Reglerwahl uebernimmt danach.
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
    raise SystemExit("V8.236 35-percent initialization verification failed: "+", ".join(missing_v8228_tokens))

# V8.236: Alle Budget-Eingabekategorien loesen dieselbe Neuberechnung aus.
required_v8229_tokens = [
    'const budgetFinancingAssumptionIds=new Set([',
    '"budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"',
    'const budgetRateRecalcIds=new Set([...budgetRateIncomeIds,...budgetRateExpenseIds,...budgetFinancingAssumptionIds]);'
]
missing_v8229_tokens=[token for token in required_v8229_tokens if token not in s]
if missing_v8229_tokens:
    raise SystemExit("V8.236 full-input recalculation verification failed: "+", ".join(missing_v8229_tokens))

# V8.236: Frei verfuegbares Monatsbudget wird nach Mindestpuffer angezeigt.
required_v8230_tokens = [
    'const freeBudget=income-expenses;',
    'const minimumReserve=Math.max(300,freeBudget*0.10);',
    'const maxRateByReserve=Math.max(0,ratePool-minimumReserve);',
    'const available=freeBudget-minimumReserve;',
    'const rawReserve=freeBudget-monthlyRate;'
]
missing_v8230_tokens=[token for token in required_v8230_tokens if token not in s]
if missing_v8230_tokens:
    raise SystemExit("V8.236 available-budget verification failed: "+", ".join(missing_v8230_tokens))

# V8.236: Begriffe klar trennen:
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
    raise SystemExit("V8.236 terminology verification failed: "+", ".join(missing_v8231_tokens))
if "Mindest-Sicherheitspuffer" in s or "Mindestpuffer unterschritten" in s or "Mindestpuffer erreicht" in s:
    raise SystemExit("V8.236 terminology verification failed: legacy minimum-buffer wording remains")

# V8.236: Finanzierungsreserve im monatlich verfuegbaren Budget direkt unter Feste Ausgaben ausweisen.
budget_summary_expenses_row = '<div class="budget-summary-row"><span>- Feste Ausgaben</span><strong id="budgetExpensesResult">–</strong></div>'
budget_summary_financing_reserve_row = budget_summary_expenses_row + '\n          <div class="budget-summary-row"><span>- Finanzierungsreserve</span><strong id="budgetFinancingReserveResult">–</strong></div>'
if budget_summary_expenses_row not in s:
    raise SystemExit("V8.236 budget summary expenses row anchor not found")
s=s.replace(budget_summary_expenses_row,budget_summary_financing_reserve_row,1)

budget_summary_render_anchor = 'if($("budgetExpensesResult")) $("budgetExpensesResult").textContent=eur(m.expenses);'
budget_summary_render_new = budget_summary_render_anchor + '\n  if($("budgetFinancingReserveResult")) $("budgetFinancingReserveResult").textContent=eur(m.minimumReserve);'
if budget_summary_render_anchor not in s:
    raise SystemExit("V8.236 budget summary render anchor not found")
s=s.replace(budget_summary_render_anchor,budget_summary_render_new,1)

required_v8232_tokens = [
    '<span>- Finanzierungsreserve</span><strong id="budgetFinancingReserveResult">–</strong>',
    'if($("budgetFinancingReserveResult")) $("budgetFinancingReserveResult").textContent=eur(m.minimumReserve);',
    '<span>- Aktueller Sicherheitspuffer</span><strong id="budgetReserveResult">–</strong>'
]
missing_v8232_tokens=[token for token in required_v8232_tokens if token not in s]
if missing_v8232_tokens:
    raise SystemExit("V8.236 financing-reserve summary verification failed: "+", ".join(missing_v8232_tokens))

# V8.236: Budget startet mit 0 EUR Ausgaben und 0 EUR Finanzierungsreserve.
# Vorschlaege werden nur noch angezeigt und erst ueber "Vorschlaege uebernehmen" in die Felder geschrieben.
expense_zero_ids = [
    "budgetFood","budgetMobility","budgetInsurance","budgetTelecom",
    "budgetLeisure","budgetChildCosts","budgetExistingLoans","budgetOther"
]
for expense_id in expense_zero_ids:
    pattern = re.compile(r'(<input[^>]*id="' + re.escape(expense_id) + r'"[^>]*value=")[^"]*(")')
    s, count = pattern.subn(r'\g<1>0\2', s, count=1)
    if count != 1:
        raise SystemExit("V8.236 expense default anchor not found: " + expense_id)

reserve_pattern = re.compile(r'(<input[^>]*id="budgetSafetyReserve"[^>]*value=")[^"]*(")')
s, reserve_count = reserve_pattern.subn(r'\g<1>0\2', s, count=1)
if reserve_count != 1:
    raise SystemExit("V8.236 financing reserve default anchor not found")

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
    raise SystemExit("V8.236 suggestion sync anchor not found")
s=s.replace(old_sync_suggestions,new_sync_suggestions,1)

# Finanzierungsreserve erst berechnen, sobald ein positives Haushaltsnettoeinkommen vorliegt.
old_sync_reserve = '''  const freeBudget=income-expenses;
  const minimumReserve=Math.max(300,freeBudget*0.10);
  budgetAutoUpdating=true;'''
new_sync_reserve = '''  const freeBudget=income-expenses;
  const minimumReserve=net>0 ? Math.max(300,freeBudget*0.10) : 0;
  budgetAutoUpdating=true;'''
if old_sync_reserve not in s:
    raise SystemExit("V8.236 reserve sync anchor not found")
s=s.replace(old_sync_reserve,new_sync_reserve,1)

old_model_reserve = '  const minimumReserve=Math.max(300,freeBudget*0.10);'
new_model_reserve = '  const minimumReserve=net>0 ? Math.max(300,freeBudget*0.10) : 0;'
if old_model_reserve not in s:
    raise SystemExit("V8.236 budget model reserve anchor not found")
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
    raise SystemExit("V8.236 budget reset anchor not found")
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
    raise SystemExit("V8.236 zero-default verification failed: "+", ".join(missing_v8233_tokens))

for expense_id in expense_zero_ids:
    if not re.search(r'<input[^>]*id="' + re.escape(expense_id) + r'"[^>]*value="0"', s):
        raise SystemExit("V8.236 expense zero default verification failed: " + expense_id)
if not re.search(r'<input[^>]*id="budgetSafetyReserve"[^>]*value="0"', s):
    raise SystemExit("V8.236 reserve zero default verification failed")

# V8.236: "Aktueller Sicherheitspuffer" wird zum verbleibenden Monatsueberschuss
# nach separatem Abzug der Finanzierungsreserve.
model_anchor = '''  const rawReserve=freeBudget-monthlyRate;
  const reserve=Math.max(0,rawReserve);'''
model_new = '''  const rawReserve=freeBudget-monthlyRate;
  const reserve=Math.max(0,rawReserve);
  const remainingMonthlySurplus=rawReserve-minimumReserve;'''
if model_anchor not in s:
    raise SystemExit("V8.236 remaining surplus model anchor not found")
s=s.replace(model_anchor,model_new,1)

return_anchor = 'net,childBenefit,income,expenses,reserve,rawReserve,minimumReserve,ratePool,available,rateCap,monthlyRate,'
return_new = 'net,childBenefit,income,expenses,reserve,rawReserve,remainingMonthlySurplus,minimumReserve,ratePool,available,rateCap,monthlyRate,'
if return_anchor not in s:
    raise SystemExit("V8.236 remaining surplus return anchor not found")
s=s.replace(return_anchor,return_new,1)

if 'additionalBuffer:reserve,' not in s:
    raise SystemExit("V8.236 PDF surplus value anchor not found")
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
    raise SystemExit("V8.236 remaining surplus verification failed: "+", ".join(missing_v8234_tokens))
if '<span>- Aktueller Sicherheitspuffer</span><strong id="budgetReserveResult">–</strong>' in s:
    raise SystemExit("V8.236 legacy current safety buffer label remains")

# V8.236: Budgetwerte aus dem Budget-Rechner in Eigennutzung uebernehmen.
own_budget_css = '''
.own-budget-transfer{grid-column:1/-1;background:#f8fafc;border-color:#cbd5e1}
.own-budget-transfer-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap}
.own-budget-transfer-copy{min-width:220px;flex:1}
.own-budget-transfer-btn{border:0;border-radius:10px;padding:10px 14px;background:#0b5cab;color:#fff;font-weight:800;font-size:12px;cursor:pointer;box-shadow:0 2px 8px rgba(15,23,42,.12)}
.own-budget-transfer-btn:hover{filter:brightness(.97)}
.own-budget-household-grid{margin-top:12px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.own-budget-household-row{display:flex;justify-content:space-between;gap:12px;padding:9px 10px;border:1px solid #e2e8f0;border-radius:10px;background:#fff;font-size:11px;color:#52627a}
.own-budget-household-row strong{color:#172033;white-space:nowrap}
.own-budget-household-row.total{grid-column:1/-1;background:#eef6ff;border-color:#bfdbfe;font-weight:800;color:#17324d}
.own-budget-household-row.total strong{font-size:15px}
@media(max-width:620px){.own-budget-household-grid{grid-template-columns:1fr}.own-budget-household-row.total{grid-column:auto}.own-budget-transfer-btn{width:100%}}
'''
if '.own-budget-transfer{' not in s:
    if '</style>' not in s:
        raise SystemExit("V8.236 style anchor not found")
    s=s.replace('</style>',own_budget_css+'\n</style>',1)

own_monthly_kpi = '''        <div class="kpi">
          <div class="name">Monatliche Gesamtbelastung</div>
          <div class="value" id="ownKpiMonthlyTotal">–</div>
          <div class="note">Kreditrate + laufende Kosten</div>
        </div>'''
own_budget_card = own_monthly_kpi + '''
        <div class="kpi wide own-budget-transfer" id="ownBudgetTransferCard">
          <div class="own-budget-transfer-head">
            <div class="own-budget-transfer-copy">
              <div class="name">Haushaltsbudget einbeziehen</div>
              <div class="note">Übernimmt Gesamte Einnahmen und feste Ausgaben aus dem Budget-Rechner. Die Finanzierungsreserve wird hier nicht erneut abgezogen.</div>
            </div>
            <button type="button" class="own-budget-transfer-btn" id="ownImportBudgetValues">Budgetwerte übernehmen</button>
          </div>
          <div class="own-budget-household-grid">
            <div class="own-budget-household-row"><span>Haushaltseinnahmen</span><strong id="ownHouseholdIncome">–</strong></div>
            <div class="own-budget-household-row"><span>Feste Haushaltsausgaben</span><strong id="ownHouseholdExpenses">–</strong></div>
            <div class="own-budget-household-row"><span>Monatliche Immobilienbelastung</span><strong id="ownHouseholdPropertyCost">–</strong></div>
            <div class="own-budget-household-row total"><span>Verbleibender Monatsüberschuss</span><strong id="ownHouseholdRemaining">–</strong></div>
          </div>
        </div>'''
if own_monthly_kpi not in s:
    raise SystemExit("V8.236 own monthly KPI anchor not found")
s=s.replace(own_monthly_kpi,own_budget_card,1)

own_render_anchor = '  if($("ownKpiMonthlyTotal")) $("ownKpiMonthlyTotal").textContent = eur(m.monthlyPayment + m.monthlyRepayment + val("holding"));'
own_render_new = own_render_anchor + '\n  renderOwnHouseholdBudget(m);'
if own_render_anchor not in s:
    raise SystemExit("V8.236 own render anchor not found")
s=s.replace(own_render_anchor,own_render_new,1)

own_budget_js = '''const OWN_BUDGET_INCOME_KEY="ff_own_budget_income";
const OWN_BUDGET_EXPENSES_KEY="ff_own_budget_expenses";

function ownImportedBudgetValues(){
  const incomeRaw=localStorage.getItem(OWN_BUDGET_INCOME_KEY);
  const expensesRaw=localStorage.getItem(OWN_BUDGET_EXPENSES_KEY);
  const income=incomeRaw===null ? null : Math.max(0,Number(incomeRaw)||0);
  const expenses=expensesRaw===null ? null : Math.max(0,Number(expensesRaw)||0);
  return {income,expenses,hasValues:income!==null && expenses!==null};
}

function renderOwnHouseholdBudget(m=model()){
  if(!$("ownHouseholdIncome")) return;
  const imported=ownImportedBudgetValues();
  const propertyCost=Math.max(0,(Number(m.monthlyPayment)||0)+(Number(m.monthlyRepayment)||0)+Math.max(0,val("holding")));
  const remaining=imported.hasValues ? imported.income-imported.expenses-propertyCost : null;
  $("ownHouseholdIncome").textContent=imported.hasValues ? eur(imported.income) : "–";
  $("ownHouseholdExpenses").textContent=imported.hasValues ? eur(imported.expenses) : "–";
  $("ownHouseholdPropertyCost").textContent=eur(propertyCost);
  $("ownHouseholdRemaining").textContent=remaining===null ? "–" : eur(remaining);
  if($("ownHouseholdRemaining")){
    $("ownHouseholdRemaining").style.color=remaining!==null && remaining<0 ? "#b91c1c" : "";
  }
}

function importBudgetValuesToOwnUse(){
  const budget=budgetModel();
  localStorage.setItem(OWN_BUDGET_INCOME_KEY,String(Math.max(0,budget.income||0)));
  localStorage.setItem(OWN_BUDGET_EXPENSES_KEY,String(Math.max(0,budget.expenses||0)));
  renderOwnHouseholdBudget(model());
}

if($("ownImportBudgetValues")){
  $("ownImportBudgetValues").addEventListener("click",importBudgetValuesToOwnUse);
}

'''
reset_fn_anchor='function resetControlToMarkupDefault(el){'
if reset_fn_anchor not in s:
    raise SystemExit("V8.236 reset function anchor not found")
s=s.replace(reset_fn_anchor,own_budget_js+reset_fn_anchor,1)

own_reset_anchor='''  if(mode==="own"){
    localStorage.removeItem("ff_own_months");
    localStorage.removeItem("ff_own_equity_input");
  }else{'''
own_reset_new='''  if(mode==="own"){
    localStorage.removeItem("ff_own_months");
    localStorage.removeItem("ff_own_equity_input");
    localStorage.removeItem("ff_own_budget_income");
    localStorage.removeItem("ff_own_budget_expenses");
    localStorage.removeItem("ff_own_budget_imported_at");
  }else{'''
if own_reset_anchor not in s:
    raise SystemExit("V8.236 own reset storage anchor not found")
s=s.replace(own_reset_anchor,own_reset_new,1)

required_v8235_tokens = [
    'id="ownImportBudgetValues">Budgetwerte übernehmen</button>',
    'id="ownHouseholdIncome"',
    'id="ownHouseholdExpenses"',
    'id="ownHouseholdPropertyCost"',
    'id="ownHouseholdRemaining"',
    'const remaining=imported.hasValues ? imported.income-imported.expenses-propertyCost : null;',
    'const budget=budgetModel();',
    'String(Math.max(0,budget.income||0))',
    'String(Math.max(0,budget.expenses||0))',
    'renderOwnHouseholdBudget(m);',
    'localStorage.removeItem("ff_own_budget_income");',
    'localStorage.removeItem("ff_own_budget_expenses");',
    'localStorage.removeItem("ff_own_budget_imported_at");'
]
missing_v8235_tokens=[token for token in required_v8235_tokens if token not in s]
if missing_v8235_tokens:
    raise SystemExit("V8.236 own budget transfer verification failed: "+", ".join(missing_v8235_tokens))
if "LOKALTEST" in s:
    raise SystemExit("V8.236 local-test marker must not be deployed")

# V8.236: Header fuer "Deine mögliche Finanzierung" analog zum Eigennutzungs-Header.
old_budget_financing_header = '''      <section class="card">
        <h2>Deine mögliche Finanzierung</h2>
        <div class="budget-result-grid">'''
new_budget_financing_header = '''      <section class="card">
        <div class="decision go budget-financing-decision">
          <div class="light" aria-hidden="true">💶</div>
          <div>
            <h2>Deine mögliche Finanzierung</h2>
            <p>Aus deinem Budget, Eigenkapital und den Finanzierungsannahmen ergibt sich hier deine mögliche Finanzierung.</p>
          </div>
        </div>
        <div class="budget-result-grid">'''
if old_budget_financing_header not in s:
    raise SystemExit("V8.236 budget financing header anchor not found")
s=s.replace(old_budget_financing_header,new_budget_financing_header,1)

# Etwas Abstand zwischen Header und Ergebnis-Kacheln, analog zum Eigennutzungs-Ergebnisbereich.
if '.budget-financing-decision{' not in s:
    if '</style>' not in s:
        raise SystemExit("V8.236 style anchor not found")
    s=s.replace(
        '</style>',
        '.budget-financing-decision{margin-bottom:14px}\n</style>',
        1
    )

required_v8236_tokens = [
    'class="decision go budget-financing-decision"',
    '<div class="light" aria-hidden="true">💶</div>',
    '<h2>Deine mögliche Finanzierung</h2>',
    'Aus deinem Budget, Eigenkapital und den Finanzierungsannahmen ergibt sich hier deine mögliche Finanzierung.',
    '.budget-financing-decision{margin-bottom:14px}'
]
missing_v8236_tokens=[token for token in required_v8236_tokens if token not in s]
if missing_v8236_tokens:
    raise SystemExit("V8.236 financing header verification failed: "+", ".join(missing_v8236_tokens))

# V8.236: Layout Finanzierungsfelder - Laufzeit vor Sanierungs-Puffer, laufende Kosten an Laufzeit-Position.
def _field_block_at_label(html, label, label_pos):
    start = html.rfind('<div class="field">', 0, label_pos)
    if start < 0:
        raise SystemExit("V8.236 layout field start not found: " + label)
    pos = start
    depth = 0
    while True:
        next_open = html.find("<div", pos)
        next_close = html.find("</div>", pos)
        if next_close < 0:
            raise SystemExit("V8.236 layout field end not found: " + label)
        if next_open >= 0 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + len("</div>")
            if depth == 0:
                block = html[start:pos]
                if not (start <= label_pos < pos) or label not in block:
                    raise SystemExit("V8.236 label occurrence is not inside selected field: " + label)
                return start, pos, block

def _label_positions(html, label, start=0, end=None):
    if end is None:
        end = len(html)
    positions = []
    pos = start
    while True:
        pos = html.find(label, pos, end)
        if pos < 0:
            return positions
        positions.append(pos)
        pos += len(label)

def _target_financing_section(html):
    menu_pos = html.find("Finanzierung & Nebenkosten anpassen")
    if menu_pos < 0:
        raise SystemExit("V8.236 layout section heading not found")
    section_start = html.rfind("<section", 0, menu_pos)
    section_end = html.find("</section>", menu_pos)
    if section_start < 0 or section_end < 0:
        raise SystemExit("V8.236 layout section bounds not found")
    return menu_pos, section_start, section_end + len("</section>")

menu_pos, section_start, section_end = _target_financing_section(s)

# Ziel-Felder im geöffneten Bereich eindeutig auswählen.
holding_positions = _label_positions(s, "Laufende Kosten pro Monat", section_start, section_end)
buffer_positions = _label_positions(s, "Sanierungs-Puffer", section_start, section_end)
if len(holding_positions) != 1 or len(buffer_positions) != 1:
    raise SystemExit(
        "V8.236 layout target fields not unique in financing section: holding="
        + str(holding_positions) + ", buffer=" + str(buffer_positions)
    )
holding_start, holding_end, holding_block = _field_block_at_label(
    s, "Laufende Kosten pro Monat", holding_positions[0]
)
buffer_start, buffer_end, buffer_block = _field_block_at_label(
    s, "Sanierungs-Puffer", buffer_positions[0]
)

# Das gemeinsame Laufzeit-Feld wird im Eigennutzungsmodus per JavaScript von
# "Sanierungsdauer" auf "Laufzeit Finanzierung" umbenannt. Deshalb stabil über
# die eindeutige DOM-ID des Labels auswählen.
term_marker = 'id="monthsLabel"'
term_positions = _label_positions(s, term_marker)
if len(term_positions) != 1:
    raise SystemExit("V8.236 layout monthsLabel not unique: " + repr(term_positions))
term_start, term_end, term_block = _field_block_at_label(
    s, term_marker, term_positions[0]
)

# Laufende Kosten aus dem Anpassungsbereich entfernen.
s = s[:holding_start] + s[holding_end:]

# Am bisherigen Laufzeit-Platz die laufenden Kosten einsetzen.
term_now = s.find(term_block)
if term_now < 0:
    raise SystemExit("V8.236 layout term block disappeared before replacement")
s = s[:term_now] + holding_block + s[term_now + len(term_block):]

# Laufzeit Finanzierung im Anpassungsbereich direkt vor den Sanierungs-Puffer setzen.
_, section_start, section_end = _target_financing_section(s)
buffer_positions = _label_positions(s, "Sanierungs-Puffer", section_start, section_end)
if len(buffer_positions) != 1:
    raise SystemExit("V8.236 layout buffer field not unique after replacement")
buffer_start, _, _ = _field_block_at_label(s, "Sanierungs-Puffer", buffer_positions[0])
s = s[:buffer_start] + term_block + "\n\n        " + s[buffer_start:]

# Abnahmekontrolle nur im gemeinten Formularbereich.
_, section_start, section_end = _target_financing_section(s)
section_html = s[section_start:section_end]
term_in_section = section_html.find('id="monthsLabel"')
buffer_in_section = section_html.find("Sanierungs-Puffer")
holding_in_section = section_html.find("Laufende Kosten pro Monat")
if term_in_section < 0 or buffer_in_section < 0 or not (term_in_section < buffer_in_section):
    raise SystemExit(
        "V8.236 layout verification failed in financing section: term/buffer="
        + str((term_in_section, buffer_in_section))
    )
if holding_in_section < 0:
    raise SystemExit("V8.236 layout verification failed: laufende Kosten missing from financing section")
if s.count('id="holding"') != 1:
    raise SystemExit("V8.236 layout verification failed: holding input duplicated or missing")
if s.count('id="monthsLabel"') != 1 or s.count('id="months"') != 1:
    raise SystemExit("V8.236 layout verification failed: duration field duplicated or missing")


# V8.236: Eigennutzung und Fix & Flip erhalten vollständig getrennte Eingabestände.
# Die Berechnungslogik bleibt unverändert; nur die Persistenz beim Moduswechsel wird getrennt.
deal_mode_storage_js = r'''
<script>
(function(){
  const SNAPSHOT_VERSION="v8237";
  const SNAPSHOT_PREFIX="ff_mode_snapshot_"+SNAPSHOT_VERSION+"_";

  function modeNow(){
    try{
      const mode=typeof currentDealType==="function" ? currentDealType() : "";
      return mode==="own" || mode==="flip" ? mode : null;
    }catch(_err){
      return null;
    }
  }

  function snapshotKey(mode){
    return SNAPSHOT_PREFIX+mode;
  }

  function dealControls(){
    const root=document.getElementById("dealCalculatorContent");
    if(!root) return [];
    return Array.from(root.querySelectorAll("input,select,textarea"))
      .filter(el=>!(el.name==="dealType"));
  }

  function serializeControl(el,index){
    return {
      index,
      id:el.id || "",
      value:el.value,
      checked:!!el.checked,
      selectedIndex:typeof el.selectedIndex==="number" ? el.selectedIndex : null,
      type:(el.type || "").toLowerCase(),
      tag:el.tagName
    };
  }

  function saveModeSnapshot(mode){
    if(mode!=="own" && mode!=="flip") return;
    const controls=dealControls();
    const payload={
      version:SNAPSHOT_VERSION,
      mode,
      savedAt:Date.now(),
      controls:controls.map(serializeControl)
    };
    localStorage.setItem(snapshotKey(mode),JSON.stringify(payload));
  }

  function readModeSnapshot(mode){
    try{
      const raw=localStorage.getItem(snapshotKey(mode));
      if(!raw) return null;
      const parsed=JSON.parse(raw);
      return parsed && Array.isArray(parsed.controls) ? parsed : null;
    }catch(_err){
      return null;
    }
  }

  function restoreControl(el,item){
    if(!el || !item) return;
    const type=(el.type || "").toLowerCase();
    if(type==="checkbox" || type==="radio"){
      el.checked=!!item.checked;
      return;
    }
    if(el.tagName==="SELECT" && Number.isInteger(item.selectedIndex) && item.selectedIndex>=0){
      el.selectedIndex=item.selectedIndex;
      return;
    }
    el.value=item.value == null ? "" : String(item.value);
  }

  function restoreModeSnapshot(mode){
    const snap=readModeSnapshot(mode);
    if(!snap) return false;
    const controls=dealControls();
    const byId=new Map(controls.filter(el=>el.id).map(el=>[el.id,el]));
    snap.controls.forEach(item=>{
      const el=(item.id && byId.get(item.id)) || controls[item.index];
      restoreControl(el,item);
    });
    return true;
  }

  function initializeModeDefaults(mode){
    const root=document.getElementById("dealCalculatorContent");
    if(root && typeof resetControlToMarkupDefault==="function"){
      root.querySelectorAll('input:not([name="dealType"]),select,textarea')
        .forEach(resetControlToMarkupDefault);
    }
    if(typeof stateEl!=="undefined" && stateEl) stateEl.value="Hamburg";
    if(typeof initializeTrades==="function") initializeTrades(true);

    if(mode==="own"){
      if(typeof applyOwnUseStandardValues==="function") applyOwnUseStandardValues();
      if(typeof zeroOwnUseGoals==="function") zeroOwnUseGoals();
    }else{
      if(typeof applyFlipStandardValues==="function") applyFlipStandardValues();
    }
  }

  function syncCurrentDomToExistingStorageAndRender(){
    try{
      if(typeof save==="function") save();
    }catch(_err){}
    try{
      if(typeof initTwoDecimalPercentFields==="function") initTwoDecimalPercentFields();
    }catch(_err){}
    try{
      if(typeof render==="function") render();
    }catch(_err){}
  }

  let activeMode=modeNow();

  function activateMode(mode){
    if(mode!=="own" && mode!=="flip") return;
    const restored=restoreModeSnapshot(mode);
    if(!restored) initializeModeDefaults(mode);
    syncCurrentDomToExistingStorageAndRender();
    saveModeSnapshot(mode);
    activeMode=mode;
  }

  // Beim initialen Laden wird ein bereits getrennter Stand bevorzugt.
  // Fehlt er (Migration von älteren Versionen), gehört der aktuell geladene
  // gemeinsame Altbestand ausschließlich zum gerade aktiven Modus.
  if(activeMode){
    if(readModeSnapshot(activeMode)){
      setTimeout(()=>activateMode(activeMode),0);
    }else{
      saveModeSnapshot(activeMode);
    }
  }

  // Capture-Phase: alten Modus sichern, bevor die bestehende setDealType-Logik
  // die gemeinsamen DOM-Felder für den neuen Modus anpasst.
  document.addEventListener("change",event=>{
    const el=event.target;
    if(!el || el.name!=="dealType") return;
    if(activeMode) saveModeSnapshot(activeMode);
    const requested=el.value==="own" || el.value==="flip" ? el.value : modeNow();
    setTimeout(()=>{
      const target=requested || modeNow();
      if(target) activateMode(target);
    },0);
  },true);

  function queueSnapshot(){
    const mode=activeMode || modeNow();
    if(!mode) return;
    queueMicrotask(()=>saveModeSnapshot(mode));
  }

  // Jede Benutzereingabe aktualisiert nur den Snapshot des aktiven Modus.
  document.addEventListener("input",event=>{
    const root=document.getElementById("dealCalculatorContent");
    if(!root || !root.contains(event.target) || event.target.name==="dealType") return;
    queueSnapshot();
  });
  document.addEventListener("change",event=>{
    const root=document.getElementById("dealCalculatorContent");
    if(!root || !root.contains(event.target) || event.target.name==="dealType") return;
    queueSnapshot();
  });

  // Auch programmatische Änderungen über Plus-/Aktionsbuttons und ein bestätigter
  // Reset werden nach Abschluss in den aktuell aktiven Modus zurückgeschrieben.
  document.addEventListener("click",event=>{
    const root=document.getElementById("dealCalculatorContent");
    if(!root || !root.contains(event.target)) return;
    setTimeout(()=>{
      const mode=activeMode || modeNow();
      if(mode) saveModeSnapshot(mode);
    },0);
  });
})();
</script>
'''

if 'ff_mode_snapshot_"+SNAPSHOT_VERSION+"_' not in s:
    if "</body>" not in s:
        raise SystemExit("V8.236 body anchor not found")
    s=s.replace("</body>",deal_mode_storage_js+"\n</body>",1)

required_v8237_tokens = [
    'ff_mode_snapshot_"+SNAPSHOT_VERSION+"_',
    'function saveModeSnapshot(mode)',
    'function restoreModeSnapshot(mode)',
    'function initializeModeDefaults(mode)',
    'if(typeof applyOwnUseStandardValues==="function") applyOwnUseStandardValues();',
    'if(typeof applyFlipStandardValues==="function") applyFlipStandardValues();',
    'document.addEventListener("change",event=>{',
    'if(activeMode) saveModeSnapshot(activeMode);',
    'setTimeout(()=>{',
    'activateMode(target);',
    'if(typeof save==="function") save();',
    'if(typeof render==="function") render();'
]
missing_v8237_tokens=[token for token in required_v8237_tokens if token not in s]
if missing_v8237_tokens:
    raise SystemExit("V8.236 separated mode storage verification failed: "+", ".join(missing_v8237_tokens))


path.write_text(s, encoding="utf-8")
print("V8.236 interest and repayment patch applied")
