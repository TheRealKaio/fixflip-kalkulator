"""V8.388: synchronize the budget slider immediately with changed cashflow."""
from pathlib import Path
import sys
path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")
anchor='document.addEventListener("beforeinput",(event)=>{\n  const el=event.target;\n  if(!el || !budgetRateRecalcIds.has(el.id)) return;'
if html.count(anchor)!=1:raise SystemExit("Expected one budget capture listener")
html=html.replace(anchor,"function refreshBudgetCashflowRate(){\n  localStorage.removeItem(\"ff_budget_rateSliderPct\");\n  const updated=budgetModel();\n  const updatedPct=updated.net>0 ? Math.max(0,updated.maxRatePct||0) : 0;\n  budgetRateManualSelection=false;\n  budgetRateNeedsInitialValue=false;\n  localStorage.setItem(\"ff_budget_rateManualSelection\",\"0\");\n  localStorage.setItem(\"ff_budget_rateNeedsInitialValue\",\"0\");\n  localStorage.setItem(\"ff_budget_rateSliderPct\",String(updatedPct));\n  budgetRateSliderSyncing=true;\n  if($(\"budgetSafetyReserve\")) $(\"budgetSafetyReserve\").value=String(Math.round(updated.minimumReserve));\n  budgetRateSliderSyncing=false;\n  budgetRateBeforeRecalc=null;\n  renderBudget();\n}\ndocument.addEventListener(\"change\",event=>{\n  if(budgetRateIncomeIds.has(event.target?.id)||budgetRateExpenseIds.has(event.target?.id)){\n    refreshBudgetCashflowRate();\n  }\n});\n"+anchor,1)
old='document.addEventListener("input",(event)=>{\n  const el=event.target;\n  if(!el || !budgetRateRecalcIds.has(el.id)) return;\n'
new=old+'  if(budgetRateIncomeIds.has(el.id)||budgetRateExpenseIds.has(el.id)){\n    refreshBudgetCashflowRate();\n    return;\n  }\n'
if html.count(old)!=1:raise SystemExit("Expected one budget input recalculation listener")
html=html.replace(old,new,1)
path.write_text(html,encoding="utf-8")
print("V8.388 budget cashflow immediately synchronizes rate and slider")
