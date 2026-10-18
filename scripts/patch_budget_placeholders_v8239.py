from pathlib import Path
import re

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

# Feste monatliche Ausgaben: Vorschlaege im Eingabefeld statt eigener Spalte.
s = s.replace(
    'display:grid;grid-template-columns:minmax(0,1.4fr) minmax(88px,.7fr) minmax(110px,.8fr);',
    'display:grid;grid-template-columns:minmax(0,1.4fr) minmax(110px,.8fr);',
    1
)
s = s.replace(
    '.budget-suggestion{font-size:12px;color:#64748b;text-align:right}',
    '.budget-suggestion{display:none}.budget-expense-row input::placeholder{color:#a6aebb;font-weight:400;opacity:1;text-align:left}',
    1
)
s = s.replace(
    '.budget-expense-row{grid-template-columns:minmax(0,1fr) 92px}',
    '.budget-expense-row{grid-template-columns:minmax(0,1fr) 92px}',
    1
)

old_render = '''function renderBudgetSuggestions(){
  const s=getBudgetSuggestions();
  const map={
    budgetFood:"budgetFoodSuggestion",
    budgetMobility:"budgetMobilitySuggestion",
    budgetInsurance:"budgetInsuranceSuggestion",
    budgetTelecom:"budgetTelecomSuggestion",
    budgetLeisure:"budgetLeisureSuggestion",
    budgetChildCosts:"budgetChildCostsSuggestion",
    budgetOther:"budgetOtherSuggestion"
  };
  Object.entries(map).forEach(([key,id])=>{
    if(!$(id)) return;
    const suggested=eur(s[key]);
    $(id).textContent = budgetExpenseManual[key]
      ? "individuell · Vorschlag " + suggested
      : "Vorschlag " + suggested;
  });
}'''

new_render = '''function renderBudgetSuggestions(){
  const suggestions=getBudgetSuggestions();
  const map={
    budgetFood:"budgetFoodSuggestion",
    budgetMobility:"budgetMobilitySuggestion",
    budgetInsurance:"budgetInsuranceSuggestion",
    budgetTelecom:"budgetTelecomSuggestion",
    budgetLeisure:"budgetLeisureSuggestion",
    budgetChildCosts:"budgetChildCostsSuggestion",
    budgetOther:"budgetOtherSuggestion"
  };
  Object.entries(map).forEach(([key,id])=>{
    const input=$(key);
    if(input){
      const amount=Math.max(0,Math.round(Number(suggestions[key])||0));
      input.placeholder=amount>0 ? String(amount) : "0";
    }
    if($(id)) $(id).textContent="";
  });
}'''

if old_render not in s:
    raise SystemExit("V8.239 budget suggestion render anchor not found")
s = s.replace(old_render, new_render, 1)

# Individuelle Kreditraten-Zeile hat bewusst keinen Vorschlag.
existing_loans = re.compile(
    r'(<input id="budgetExistingLoans"[^>]*)(>)'
)
s, count = existing_loans.subn(r'\1 placeholder="0"\2', s, count=1)
if count != 1:
    raise SystemExit("V8.239 existing loans placeholder anchor not found")

# Version durchgaengig im Kalkulator, in PDF-Footern und in der SW-Registrierung anheben.
s = s.replace("V8.236", "V8.239")
s = s.replace("service-worker.js?v=8.236", "service-worker.js?v=8.239")

required = [
    'input.placeholder=amount>0 ? String(amount) : "0";',
    '.budget-suggestion{display:none}',
    'budget-expense-row input::placeholder{color:#a6aebb;font-weight:400;',
    'id="budgetExistingLoans" inputmode="decimal" value="0" placeholder="0"',
    'V8.239',
    'service-worker.js?v=8.239'
]
missing = [token for token in required if token not in s]
if missing:
    raise SystemExit("V8.239 verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.239 budget placeholders and version patch applied")
