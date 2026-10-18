from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old = '''  const targetMargin = Math.max(0, pct("targetMargin"));
  const sellBrokerRate = Math.max(0, pct("sellBroker"));

  // Ziel-Marge ist Gewinn / Verkaufspreis.
  // Verkaufspreis = Kosten + Zielgewinn; der Verkaufsmakler selbst ist
  // ebenfalls vom Verkaufspreis abhängig. Deshalb wird die Gleichung direkt gelöst.
  const denominator = 1 - targetMargin - sellBrokerRate;'''

new = '''  // Die automatische Verkaufspreis-Kalkulation bleibt bewusst unabhängig
  // von der persönlichen Ziel-Marge. Die Ziel-Marge steuert ausschließlich
  // die Ampelbewertung unter Projektziele & Steuer.
  const saleCalculationMargin = 0.10;
  const sellBrokerRate = Math.max(0, pct("sellBroker"));

  // Kalkulatorischer Verkaufspreis auf Basis einer stabilen 10-%-Kalkulationsmarge.
  // Dadurch verändert eine Anpassung des Wunschziels weder Verkaufspreis,
  // Gewinn noch den maximal sinnvollen Kaufpreis.
  const denominator = 1 - saleCalculationMargin - sellBrokerRate;'''

if old not in s:
    raise SystemExit("V8.255 calculateFlipTargetSale target-margin anchor missing")
s=s.replace(old,new,1)

# V8.254 darf bei einer reinen Änderung der Ziel-Marge den Verkaufspreis
# nicht mehr neu berechnen.
old_ids='''    "holding","otherSaleCosts","targetMargin","sellBroker"'''
new_ids='''    "holding","otherSaleCosts","sellBroker"'''
if old_ids not in s:
    raise SystemExit("V8.255 formulaIds targetMargin anchor missing")
s=s.replace(old_ids,new_ids,1)

s=s.replace("V8.254","V8.255")
s=s.replace("service-worker.js?v=8.254","service-worker.js?v=8.255")

required=[
  'const saleCalculationMargin = 0.10;',
  'const denominator = 1 - saleCalculationMargin - sellBrokerRate;',
  'die Ampelbewertung unter Projektziele & Steuer',
  '"holding","otherSaleCosts","sellBroker"',
  'const missMargin = !isOwnUse && m.margin < targetMargin;',
  'const numerator = s*(1-pct("sellBroker"))-targetProfit-fixed-renoContribution;',
  'V8.255',
  'service-worker.js?v=8.255'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.255 verification failed: "+", ".join(missing))

# Sicherstellen, dass targetMargin im V8.254-Recalc-Set nicht mehr vorkommt.
if '"holding","otherSaleCosts","targetMargin","sellBroker"' in s:
    raise SystemExit("V8.255 targetMargin still triggers sale recalculation")

path.write_text(s,encoding="utf-8")
print("V8.255 target-margin decoupling applied")
