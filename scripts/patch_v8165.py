from pathlib import Path
import sys

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
    '          <div class="budget-rate-guidance" id="budgetRateGuidance">Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung.</div>',
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
    $("budgetRateGuidance").textContent = "Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung." + (budgetRateStatus ? " Aktuelle Einordnung: " + budgetRateStatus + "." : "");
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
          <strong>Hinweis:</strong> Der Sicherheitspuffer wird mit 10 % des Haushaltsnettoeinkommens vorgeschlagen, mindestens jedoch mit 300 € monatlich. Du kannst den Betrag individuell anpassen. Nach Lebenshaltungskosten, festen Verpflichtungen und diesem Sicherheitspuffer bildet der verbleibende Betrag die maximal tragbare Kreditrate. Die 30–35-%-Regel dient nur als zusätzliche Orientierung und begrenzt die Rate nicht erneut.
        </div>'''
if old_assumption_note in s:
    s = s.replace(old_assumption_note, new_assumption_note, 1)

s = s.replace(
    '<div class="field"><label>Sicherheitsreserve</label><div class="input-wrap"><input id="budgetSafetyReserve" inputmode="decimal" value="300"><span class="unit">€</span></div><div class="mini">monatlich</div></div>',
    '<div class="field"><label>Sicherheitspuffer</label><div class="input-wrap"><input id="budgetSafetyReserve" inputmode="decimal" value="300"><span class="unit">€</span></div><div class="mini">Vorschlag: 10 % vom Haushaltsnetto, mindestens 300 € · editierbar</div></div>',
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
  if(!$("budgetSafetyReserve") || budgetSafetyReserveManual) return;
  const net=Math.max(0,budgetVal("budgetNetIncome"));
  const suggested=Math.max(300,Math.round(net*0.10));
  budgetAutoUpdating=true;
  $("budgetSafetyReserve").value=String(suggested);
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

# V8.173: Kaufpreis-Check im Budget standardmaessig geschlossen.
# Only the first matching market-check card is changed; toggle behavior stays unchanged.
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


# V8.174: Consistent interest / repayment logic.
# Standard initial repayment is 1.5% in both financing calculators.
s = s.replace(
    '<input id="repayment" inputmode="decimal" value="2">',
    '<input id="repayment" inputmode="decimal" value="1.5">',
    1
)
s = s.replace(
    '<input id="budgetRepayment" inputmode="decimal" value="2">',
    '<input id="budgetRepayment" inputmode="decimal" value="1.5">',
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
        raise SystemExit("V8.174 annuity helper anchor not found")
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
    raise SystemExit("V8.174 target interest block not found")
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
    raise SystemExit("V8.174 model finance block not found")
s=s.replace(old_model_finance,new_model_finance,1)

old_int_factor = '  const intFactor = pct("interest")*(months/12);'
new_int_factor = '  const intFactor = annuityProjection(1,Math.max(0,pct("interest")),Math.max(0,pct("repayment")),months).totalInterest;'
if old_int_factor not in s:
    raise SystemExit("V8.174 max-buy interest factor not found")
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
reference_interest_js = '''const REFERENCE_INTEREST_FALLBACK = 4.0;
const REFERENCE_INTEREST_URL = "https://api.statistiken.bundesbank.de/rest/data/BBIM1/M.DE.B.A2C.A.R.A.2250.EUR.N?format=csv&lang=de";

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

async function initializeReferenceInterest(){
  const mainSaved=localStorage.getItem("ff_interest")!==null;
  const budgetSaved=localStorage.getItem("ff_budget_budgetInterest")!==null;
  if(mainSaved && budgetSaved) return;
  let rate=REFERENCE_INTEREST_FALLBACK;
  try{
    rate=await fetchReferenceInterest();
    localStorage.setItem("ff_reference_interest_source","Bundesbank");
    localStorage.setItem("ff_reference_interest_updated",new Date().toISOString());
  }catch(err){
    localStorage.setItem("ff_reference_interest_source","Fallback");
  }
  const value=(Math.round(rate*100)/100).toFixed(2);
  if(!mainSaved && $("interest")) $("interest").value=value;
  if(!budgetSaved && $("budgetInterest")) $("budgetInterest").value=value;
  render();
}

'''
reference_anchor='function save(){'
if reference_interest_js not in s:
    if reference_anchor not in s:
        raise SystemExit("V8.174 reference interest anchor not found")
    s=s.replace(reference_anchor,reference_interest_js+reference_anchor,1)

init_anchor='setDealType(savedDealType, false);'
if init_anchor not in s:
    raise SystemExit("V8.174 init anchor not found")
s=s.replace(init_anchor,init_anchor+'\\ninitializeReferenceInterest();',1)

path.write_text(s, encoding="utf-8")
print("V8.174 interest and repayment patch applied")
