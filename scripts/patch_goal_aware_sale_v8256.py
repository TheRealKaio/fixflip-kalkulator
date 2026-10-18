from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old = '''  // Die automatische Verkaufspreis-Kalkulation bleibt bewusst unabhängig
  // von der persönlichen Ziel-Marge. Die Ziel-Marge steuert ausschließlich
  // die Ampelbewertung unter Projektziele & Steuer.
  const saleCalculationMargin = 0.10;
  const sellBrokerRate = Math.max(0, pct("sellBroker"));

  // Kalkulatorischer Verkaufspreis auf Basis einer stabilen 10-%-Kalkulationsmarge.
  // Dadurch verändert eine Anpassung des Wunschziels weder Verkaufspreis,
  // Gewinn noch den maximal sinnvollen Kaufpreis.
  const denominator = 1 - saleCalculationMargin - sellBrokerRate;
  if(denominator <= 0) return 0;

  return nonBrokerCosts / denominator;'''

new = '''  const targetMargin = Math.max(0, pct("targetMargin"));
  const targetProfit = Math.max(0, val("targetProfit"));
  const sellBrokerRate = Math.max(0, pct("sellBroker"));

  // Der automatische Verkaufspreis muss beide Projektziele erfüllen:
  // 1) die eingegebene Ziel-Marge und 2) den eingegebenen Ziel-Gewinn.
  // Maßgeblich ist deshalb der höhere der beiden notwendigen Verkaufspreise.
  const marginDenominator = 1 - targetMargin - sellBrokerRate;
  const profitDenominator = 1 - sellBrokerRate;
  if(marginDenominator <= 0 || profitDenominator <= 0) return 0;

  const saleForTargetMargin = nonBrokerCosts / marginDenominator;
  const saleForTargetProfit = (nonBrokerCosts + targetProfit) / profitDenominator;

  return Math.max(saleForTargetMargin, saleForTargetProfit);'''

if old not in s:
    raise SystemExit("V8.256 V8.255 sale calculation block missing")
s=s.replace(old,new,1)

# Ziel-Marge ist wieder Bestandteil der Verkaufspreisformel und muss deshalb
# bei Änderungen den gespeicherten Verkaufspreis aktualisieren.
old_ids='''    "holding","otherSaleCosts","sellBroker"'''
new_ids='''    "holding","otherSaleCosts","targetMargin","targetProfit","sellBroker"'''
if old_ids not in s:
    raise SystemExit("V8.256 formulaIds anchor missing")
s=s.replace(old_ids,new_ids,1)

# Verkaufspreis immer auf den nächsten vollen Euro AUFRUNDEN, damit die
# Zielwerte durch Rundung nicht minimal unterschritten werden.
old_round='''    el.value=value>0 ? String(Math.round(value)) : "0";'''
new_round='''    el.value=value>0 ? String(Math.ceil(value)) : "0";'''
if old_round not in s:
    raise SystemExit("V8.256 sale rounding anchor missing")
s=s.replace(old_round,new_round,1)

# Kleine numerische Toleranz für die Ampelbewertung.
old_status='''  const missProfit = !isOwnUse && m.profit < targetProfit;
  const missMargin = !isOwnUse && m.margin < targetMargin;
  const missRoi = !isOwnUse && m.roi < targetRoi;
  const missEquity = !isOwnUse && maxEquity > 0 && m.equity > maxEquity;
  const missMaxBuy = !isOwnUse && m.p > m.maxBuy;'''
new_status='''  const moneyTolerance = 1;
  const rateTolerance = 0.00005;
  const missProfit = !isOwnUse && m.profit + moneyTolerance < targetProfit;
  const missMargin = !isOwnUse && m.margin + rateTolerance < targetMargin;
  const missRoi = !isOwnUse && m.roi + rateTolerance < targetRoi;
  const missEquity = !isOwnUse && maxEquity > 0 && m.equity > maxEquity + moneyTolerance;
  const missMaxBuy = !isOwnUse && m.p > m.maxBuy + moneyTolerance;'''
if old_status not in s:
    raise SystemExit("V8.256 status tolerance anchor missing")
s=s.replace(old_status,new_status,1)

s=s.replace("V8.255","V8.256")
s=s.replace("service-worker.js?v=8.255","service-worker.js?v=8.256")

required=[
  'const targetMargin = Math.max(0, pct("targetMargin"));',
  'const targetProfit = Math.max(0, val("targetProfit"));',
  'const saleForTargetMargin = nonBrokerCosts / marginDenominator;',
  'const saleForTargetProfit = (nonBrokerCosts + targetProfit) / profitDenominator;',
  'return Math.max(saleForTargetMargin, saleForTargetProfit);',
  '"holding","otherSaleCosts","targetMargin","targetProfit","sellBroker"',
  'String(Math.ceil(value))',
  'const moneyTolerance = 1;',
  'const rateTolerance = 0.00005;',
  'V8.256',
  'service-worker.js?v=8.256'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.256 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.256 goal-aware sale calculation applied")
