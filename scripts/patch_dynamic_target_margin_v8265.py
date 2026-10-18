from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Die Projektziel-Berechnung verwendet ausschließlich die aktuelle Eingabe
# aus dem Feld targetMargin. Kein fixer Kalkulationswert.
replace_once(
'''  const targetProfit = currentDealType()==="own" ? 0 : val("targetProfit");
  const targetMarginForSale = currentDealType()==="own" ? 0 : Math.max(0,pct("targetMargin"));
  const profitSaleDenominator = 1-sellBrokerRate;
  const marginSaleDenominator = 1-sellBrokerRate-targetMarginForSale;''',
'''  const targetProfit = currentDealType()==="own" ? 0 : val("targetProfit");
  const targetMarginInput = currentDealType()==="own" ? 0 : Math.max(0,pct("targetMargin"));
  const targetMarginForSale = targetMarginInput;
  const profitSaleDenominator = 1-sellBrokerRate;
  const marginSaleDenominator = 1-sellBrokerRate-targetMarginInput;''',
"dynamic target margin"
)

# Auch die Ampel liest explizit denselben aktuellen Feldwert.
replace_once(
'''  const targetProfit=val("targetProfit");
  const targetMargin=pct("targetMargin");
  const targetRoi=pct("targetRoi");''',
'''  const targetProfit=val("targetProfit");
  const targetMargin=Math.max(0,pct("targetMargin"));
  const targetRoi=pct("targetRoi");''',
"dynamic target margin ampel"
)

# Version bump.
s=s.replace("V8.264","V8.265")
s=s.replace("service-worker.js?v=8.264","service-worker.js?v=8.265")

required=[
    'const targetMarginInput = currentDealType()==="own" ? 0 : Math.max(0,pct("targetMargin"));',
    'const marginSaleDenominator = 1-sellBrokerRate-targetMarginInput;',
    'const targetMargin=Math.max(0,pct("targetMargin"));',
    'V8.265',
    'service-worker.js?v=8.265'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.265 verification failed: "+", ".join(missing))

# In der finalen Deal-Logik darf keine feste 10-%-Verkaufsmarge mehr existieren.
for forbidden in [
    'const saleCalculationMargin = 0.10;',
    'const saleCalculationMargin=0.10;',
    '1 - 0.10 - sellBrokerRate',
    '1-0.10-sellBrokerRate'
]:
    if forbidden in s:
        raise SystemExit("V8.265 hard-coded target margin still present: "+forbidden)

path.write_text(s,encoding="utf-8")
print("V8.265 target margin uses field input only")
