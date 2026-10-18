from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Fix & Flip: das eingegebene verfügbare Eigenkapital wird vollständig dem
# Projekt zugeordnet. Der Wasserfall entscheidet nur über seine Verwendung:
# Projektreserve zuerst, danach Darlehensreduzierung.
replace_once(
'''  const equity = currentDealType()==="own"
    ? Math.max(0, initialOwnUseCosts - debt)
    : financePlan.projectEquityNeed;''',
'''  const equity = currentDealType()==="own"
    ? Math.max(0, initialOwnUseCosts - debt)
    : Math.max(0, ownEquityInput);''',
"ROI/equity base"
)

# Die interne Restliquidität wird für Fix & Flip nicht mehr als Ergebnis geführt.
# Das verfügbare EK gilt als vollständig eingesetzt; ein Fehlbetrag bleibt separat.
replace_once(
'''    equityRemaining:isFlipFinancing ? financePlan.equityRemaining : 0,
    equityShortfall:isFlipFinancing ? financePlan.equityShortfall : 0,''',
'''    equityRemaining:0,
    equityShortfall:isFlipFinancing ? financePlan.equityShortfall : 0,''',
"remove remaining liquidity from model"
)

# ROI explizit auf das vollständig eingesetzte eigene Geld beziehen.
old_roi='''  const roi = equity ? profit/equity : 0;'''
new_roi='''  const roi = equity ? profit/equity : 0;'''
if old_roi not in s:
    # tolerate whitespace variants but require the current formula to exist
    if 'profit/equity' not in s:
        raise SystemExit("ROI formula anchor missing")

# Ergebnisdetail ohne Restliquidität.
old_breakdown='''      const available=Math.max(0,m.ownEquityInput||0);
      const reserveNeed=Math.max(0,m.projectReserveNeed||0);
      const toFinance=Math.max(0,m.equityForFinancing||0);
      const remaining=Math.max(0,m.equityRemaining||0);
      const shortfall=Math.max(0,m.equityShortfall||0);
      $("equityCapitalNeed").textContent = showEquityCapitalNote
        ? " Verfügbar: "+eur(available)+" · Projektreserve: "+eur(reserveNeed)+" · davon laufende Kosten: "+eur(m.projectReserveHolding||0)+" · Zinsen: "+eur(m.projectReserveInterest||0)+" · zur Kreditreduzierung: "+eur(toFinance)+" · "+(shortfall>0 ? "Fehlbetrag: "+eur(shortfall) : "Restliquidität: "+eur(remaining))
        : "";'''
new_breakdown='''      const available=Math.max(0,m.ownEquityInput||0);
      const reserveNeed=Math.max(0,m.projectReserveNeed||0);
      const toFinance=Math.max(0,m.equityForFinancing||0);
      const shortfall=Math.max(0,m.equityShortfall||0);
      $("equityCapitalNeed").textContent = showEquityCapitalNote
        ? " Eigenkapital im Projekt: "+eur(available)+" · Projektreserve: "+eur(reserveNeed)+" · davon laufende Kosten: "+eur(m.projectReserveHolding||0)+" · Zinsen: "+eur(m.projectReserveInterest||0)+" · zur Kreditreduzierung: "+eur(toFinance)+(shortfall>0 ? " · Fehlbetrag: "+eur(shortfall) : "")
        : "";'''
replace_once(old_breakdown,new_breakdown,"equity breakdown")

replace_once(
'''  if($("equityNeedNote") && currentDealType()==="flip"){
    $("equityNeedNote").textContent = m.equityShortfall>0
      ? "Eigenkapitalbedarf · Fehlbetrag "+eur(m.equityShortfall)
      : (m.fullFinanceMode ? "vollständig fremdfinanziert" : "Eigenkapitalbedarf · Restliquidität "+eur(m.equityRemaining));
  }''',
'''  if($("equityNeedNote") && currentDealType()==="flip"){
    $("equityNeedNote").textContent = m.equityShortfall>0
      ? "Eigenkapital im Projekt · Fehlbetrag "+eur(m.equityShortfall)
      : (m.fullFinanceMode ? "vollständig fremdfinanziert" : "100 % des verfügbaren Eigenkapitals eingesetzt");
  }''',
"equity KPI note"
)

# ROI-Infotext präzisieren.
s=s.replace(
    'Gewinn geteilt durch dein eingesetztes eigenes Geld.',
    'Gewinn vor Steuer geteilt durch dein tatsächlich im Projekt eingesetztes eigenes Geld.'
)
s=s.replace(
    'Gewinn geteilt durch das im Projekt gebundene eigene Geld.',
    'Gewinn vor Steuer geteilt durch dein tatsächlich im Projekt eingesetztes eigenes Geld.'
)

# PDF: keine Restliquidität mehr; vollständigen EK-Einsatz ausweisen.
s=s.replace(
    'page2Line("Verbleibende Liquiditätsreserve", pdfMoney(m.equityRemaining));',
    'page2Line("Eigenkapital im Projekt", pdfMoney(m.ownEquityInput));'
)

# Version bump.
s=s.replace("V8.261","V8.262")
s=s.replace("service-worker.js?v=8.261","service-worker.js?v=8.262")

required=[
    ': Math.max(0, ownEquityInput);',
    'equityRemaining:0,',
    'Eigenkapital im Projekt: "+eur(available)',
    '100 % des verfügbaren Eigenkapitals eingesetzt',
    'Gewinn vor Steuer geteilt durch dein tatsächlich im Projekt eingesetztes eigenes Geld.',
    'page2Line("Eigenkapital im Projekt", pdfMoney(m.ownEquityInput));',
    'const roi = equity ? profit/equity : 0;',
    'V8.262',
    'service-worker.js?v=8.262'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.262 verification failed: "+", ".join(missing))
if "Restliquidität" in s:
    raise SystemExit("V8.262 stale Restliquidität text still present")

path.write_text(s,encoding="utf-8")
print("V8.262 full-equity ROI model applied")
