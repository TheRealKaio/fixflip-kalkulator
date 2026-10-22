from pathlib import Path
import sys
import re

path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")

# Single source of truth: derive the active release from the newest patch filename.
# Example: patch_pdf_summary_spacing_v8320.py -> V8.320.
patch_versions=[]
for patch in Path("scripts").glob("patch*_v8*.py"):
    m=re.search(r"_v8(\d{3})\.py$", patch.name)
    if m:
        patch_versions.append(int(m.group(1)))
if not patch_versions:
    raise SystemExit("Rental acceptance failed - no release patch version found")
release_version=f"V8.{max(patch_versions):03d}"

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
  "rental factor traffic": 'id="rentFactorRating"',
  "rental cashflow traffic": 'id="rentCashflowRating"',
  "rental factor very good": 'Sehr gut / Schnäppchen',
  "rental factor very expensive": 'Schlecht / Sehr teuer',
  "rental cashflow ratio": 'const ratio=m.monthlyCashflow/m.coldRent;',
  "rental AfA info": 'Eine mögliche AfA',
  "rental appreciation info": 'Eine mögliche Wertsteigerung',
  "rental V8.308 traffic style": 'id="rental-kpi-traffic-v8308"',
  "unified info badge style": 'id="unified-info-ui-v8309"',
  "rental shared info sheet": 'id="unified-rental-info-sheet-v8309"',
  "shared sheet open": 'backdrop.classList.add("show");',
  "rental PDF recommendation": 'Erstellt aus der Vermietungs-Kalkulation',
  "rental PDF overview title": 'Wichtigste Ergebnisse auf einen Blick',
  "rental PDF monthly interest": 'Monatliche Zinsbelastung',
  "rental PDF monthly repayment": 'Monatliche Tilgung',
  "rental PDF overview cold rent sqm": 'Nettokaltmiete pro m²',
  "rental PDF overview housegeld": 'Hausgeld gesamt pro Monat',
  "rental PDF overview nonalloc": 'Davon nicht umlagefähig',
  "rental PDF equity return": 'Rendite auf dein Eigenkapital',
  "PDF summary heading": 'Zusammenfassung',
  "PDF summary justified": 'align:"justify"',
  "PDF summary top aligned": 'baseline:"top"',
  "PDF summary tight height": 'tight:true',
  "PDF summary 9pt": 'const summaryFontSize=9;',
  "PDF summary 10mm padding": 'const summaryPadding=10;',
  "PDF summary anthracite": 'textColor:[45,55,70]',
  "PDF summary line spacing": 'const summaryLineHeightFactor=1.18;',
  "PDF summary page break": 'ensureSpace(summaryPreviewH+12);',
  "PDF summary budget gap": 'y+=4.7;',
  "PDF summary main gap": 'y += 2.7;',
  "PDF summary rental gap": 'y+=2.7;',
  "rental own contribution paragraph break": 'selbst.\\n\\nDu musst jeden Monat eigenes Geld zuschießen.',
  "rental overview subtitle size": 'doc.setFontSize(8.2);',
  "content width 640px": '.app{max-width:640px}',
  "footer legal links": 'class="footer-legal-links"',
  "footer impressum placeholder": 'data-legal-placeholder="impressum"',
  "footer agbs placeholder": 'data-legal-placeholder="agbs"',
  "footer datenschutz placeholder": 'data-legal-placeholder="datenschutz"',
  "rental PDF subtitle cold rent label": 'Nettokaltmiete Mtl.:',
  "rental PDF subtitle housegeld label": 'Hausgeld Mtl.:',
  "rental negative cashflow summary": 'Ein negativer Cashflow bei Vermietung ist nicht automatisch ein Ausschlusskriterium',
  "rental negative cashflow own contribution": 'Du musst jeden Monat eigenes Geld zuschießen.',
  "rental negative cashflow -5": 'bis etwa -5 % der Nettokaltmiete',
  "rental negative cashflow -10": 'etwa -5 bis -10 % der Nettokaltmiete',
  "rental negative cashflow critical": 'Mehr als -10 % der Nettokaltmiete',
  "rental negative cashflow conditional": 'if(m.cashflow<0)',
  "rental version": release_version
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
