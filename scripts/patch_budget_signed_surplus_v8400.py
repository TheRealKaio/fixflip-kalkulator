"""V8.400: show the signed remaining monthly surplus in whole euros."""
from pathlib import Path
import sys

path=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
html=path.read_text(encoding='utf-8')
old='if($("budgetReserveResult")) $("budgetReserveResult").textContent=eur(m.remainingMonthlySurplus);'
new='if($("budgetReserveResult")) $("budgetReserveResult").textContent=new Intl.NumberFormat("de-DE",{style:"currency",currency:"EUR",minimumFractionDigits:0,maximumFractionDigits:0}).format(m.remainingMonthlySurplus);'
if html.count(old)!=1:raise SystemExit('Budget surplus display anchor missing or duplicated')
html=html.replace(old,new,1)
path.write_text(html,encoding='utf-8')
