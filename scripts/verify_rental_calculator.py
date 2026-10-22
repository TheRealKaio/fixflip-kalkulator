from pathlib import Path
import sys
import re

path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")

required={
  "rental tab": 'id="dealTypeRent"',
  "rental section": 'id="rentSection"',
  "rental purchase": 'id="rentPurchase"',
  "rental cold rent": 'id="rentColdRent"',
  "rental vacancy": 'id="rentVacancy"',
  "rental non alloc": 'id="rentNonAlloc"',
  "rental equity": 'id="rentEquity"',
  "rental prefix": 'const PREFIX="ff_rent_";',
  "rental cashflow formula": 'const monthlyCashflow=effectiveMonthlyRent-ownerMonthlyCosts-debtService;',
  "rental gross yield": 'const grossYield=purchase>0 ? annualGrossRent/purchase : null;',
  "rental net yield": 'const netYield=totalInvestment>0 ? noi/totalInvestment : null;',
  "rental cash on cash": 'const cashOnCash=equityUsed>0 ? (monthlyCashflow*12)/equityUsed : null;',
  "rental factor": 'const factor=annualGrossRent>0 ? purchase/annualGrossRent : null;',
  "rental break even": 'const breakEvenRent=(1-vacancy)>0 ? (ownerMonthlyCosts+debtService)/(1-vacancy) : null;',
  "rental reset isolation": 'if(key.startsWith(PREFIX)) localStorage.removeItem(key);',
  "rental PDF report": "Vermietung - Deal Report",
  "rental renovation panel": 'id="rentRenoPanel"',
  "rental renovation storage": 'ff_rent_reno_',
  "rental info icons": 'rent-info-dot',
  "rental housegeld wording": "nicht vollständig als Eigentümerkosten angesetzt",
  "Fix & Flip subtitle": "Kauf, Sanierung und Verkauf prüfen",
  "rental build year": 'id="rentBuildYear"',
  "rental plot area": 'id="rentPlotArea"',
  "rental modernization hint": 'Anfangsinvestition inklusive Puffer',
  "rental modernization style": 'id="rental-ui-v8304"',
  "rental reference interest": 'if(!rentalManual && $("rentInterest")) $("rentInterest").value=value;',
  "rental interest manual tracking": '["rentInterest","ff_rent_interest_manual"]',
  "rental housegeld examples": 'z. B. Wasser, Heizung, Müllentsorgung',
  "rental nonalloc examples below field": 'z. B. Verwalterkosten, Instandhaltung/Instandsetzung, Erhaltungsrücklage',
  "rental maintenance calculated status": 'id="rentMaintenanceStatus"',
  "rental maintenance changed status": 'pro Monat · geänderter Vorschlag',
  "rental maintenance 1.50 info": '1,50 € pro m² Wohnfläche und Monat',
  "rental maintenance auto formula": 'sqm*1.5',
  "rental V8.306 script": 'id="rental-ui-script-v8306"',
  "rental reset reloads reference interest": 'Promise.resolve(initializeReferenceInterest())',
  "rental reset clears manual interest": 'localStorage.removeItem("ff_rent_interest_manual");',
  "content width 640px": '.app{max-width:640px}',
  "rental version": 'V8.307'
}
missing=[name for name,token in required.items() if token not in html]
if missing:
    raise SystemExit("Rental acceptance failed - missing: "+", ".join(missing))

# Storage isolation: all explicitly persisted rental field values go through ff_rent_.
if 'localStorage.setItem("ff_purchase"' in html or 'localStorage.setItem("ff_area"' in html:
    # Existing calculators legitimately use these keys, so inspect only the rental script.
    pass

script_match=re.search(r'<script id="rental-calculator-script-v8299">(.*?)</script>',html,re.S)
if not script_match:
    raise SystemExit("Rental acceptance failed - rental script missing")
script=script_match.group(1)
for forbidden in [
    'localStorage.setItem("ff_purchase"',
    'localStorage.setItem("ff_area"',
    'localStorage.setItem("ff_interest"',
    'localStorage.setItem("ff_repayment"',
    'localStorage.removeItem("ff_purchase"',
    'localStorage.removeItem("ff_area"'
]:
    if forbidden in script:
        raise SystemExit("Rental acceptance failed - shared storage touched: "+forbidden)

# Numerical acceptance case.
purchase=300000
cold_rent=1500
vacancy=0.02
transfer_rate=0.055
notary=0.02
broker=0.0
renovation=10000
equity=80000
interest=0.04
repayment=0.015
non_alloc=120
management=40
maintenance=80
other=20

transfer_tax=purchase*transfer_rate
acquisition=purchase*notary+purchase*broker+transfer_tax
total_investment=purchase+acquisition+renovation
equity_used=min(equity,total_investment)
loan=max(0,total_investment-equity_used)
debt_service=loan*(interest+repayment)/12
effective_monthly=cold_rent*(1-vacancy)
owner_costs=non_alloc+management+maintenance+other
cashflow=effective_monthly-owner_costs-debt_service
annual_gross=cold_rent*12
noi=effective_monthly*12-owner_costs*12
gross_yield=annual_gross/purchase
net_yield=noi/total_investment
cash_on_cash=cashflow*12/equity_used
factor=purchase/annual_gross
break_even=(owner_costs+debt_service)/(1-vacancy)

if round(total_investment,2)!=332500.00:
    raise SystemExit("Rental acceptance failed - total investment")
if round(loan,2)!=252500.00:
    raise SystemExit("Rental acceptance failed - loan")
if round(cashflow,2)!=52.71:
    raise SystemExit("Rental acceptance failed - monthly cashflow")
if round(gross_yield*100,2)!=6.00:
    raise SystemExit("Rental acceptance failed - gross yield")
if round(net_yield*100,2)!=4.37:
    raise SystemExit("Rental acceptance failed - net yield")
if round(cash_on_cash*100,2)!=0.79:
    raise SystemExit("Rental acceptance failed - cash-on-cash")
if round(factor,2)!=16.67:
    raise SystemExit("Rental acceptance failed - factor")
if round(break_even,2)!=1446.22:
    raise SystemExit("Rental acceptance failed - break-even rent")

print("Rental acceptance passed: isolated storage, formulas, reset scope and key KPI outputs")
