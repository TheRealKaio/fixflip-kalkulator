from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Eigennutzung: rote Fehlbetragsmeldung direkt unter dem Eingabefeld Eigenkapital.
replace_once(
'''          <div class="input-wrap">
            <input id="ownEquityInput" inputmode="decimal" value="0" placeholder="z. B. 75000">
            <span class="unit">€</span>
          </div>
          <div class="equity-capital-note" id="equityCapitalNote">''',
'''          <div class="input-wrap">
            <input id="ownEquityInput" inputmode="decimal" value="0" placeholder="z. B. 75000">
            <span class="unit">€</span>
          </div>
          <div class="equity-shortfall-warning" id="ownEquityShortfallWarning" hidden></div>
          <div class="equity-capital-note" id="equityCapitalNote">''',
"own equity warning markup"
)

# Eigennutzung: notwendiges Eigenkapital = nicht durch die eingestellte Finanzierung
# gedeckter Anteil von Kaufpreis + Kaufnebenkosten + Sanierung.
render_anchor='''  if($("equityShortfallWarning")){
    const financeAcquisitionChecked = $("financeAcquisition") ? $("financeAcquisition").checked : false;
    const financingBelowFull = Math.max(0,pct("ltv")) < 0.999999;
    const equityIncreaseRequired = currentDealType()==="flip"
      && (!financeAcquisitionChecked || financingBelowFull)
      && Math.max(0,m.equityShortfall||0) > 1;
    $("equityShortfallWarning").hidden = !equityIncreaseRequired;
    $("equityShortfallWarning").textContent = equityIncreaseRequired
      ? "Eigenkapital erhöhen – Fehlbetrag: "+eur(m.equityShortfall)+"."
      : "";
  }'''

render_new=render_anchor+'''
  if($("ownEquityShortfallWarning")){
    const ownFinanceAcquisitionChecked = $("financeAcquisition") ? $("financeAcquisition").checked : false;
    const ownFinancingBelowFull = Math.max(0,pct("ltv")) < 0.999999;
    const ownRequiredEquity = Math.max(0,(m.initialOwnUseCosts||0)-(m.grossDebt||0));
    const ownEquityShortfall = Math.max(0,ownRequiredEquity-Math.max(0,m.ownEquityInput||0));
    const ownEquityIncreaseRequired = currentDealType()==="own"
      && (!ownFinanceAcquisitionChecked || ownFinancingBelowFull)
      && ownEquityShortfall > 1;
    $("ownEquityShortfallWarning").hidden = !ownEquityIncreaseRequired;
    $("ownEquityShortfallWarning").textContent = ownEquityIncreaseRequired
      ? "Eigenkapital erhöhen – Fehlbetrag: "+eur(ownEquityShortfall)+"."
      : "";
  }'''

replace_once(render_anchor,render_new,"own equity shortfall render")

s=s.replace("V8.268","V8.269")
s=s.replace("service-worker.js?v=8.268","service-worker.js?v=8.269")

required=[
    'id="ownEquityShortfallWarning"',
    'const ownRequiredEquity = Math.max(0,(m.initialOwnUseCosts||0)-(m.grossDebt||0));',
    'const ownEquityShortfall = Math.max(0,ownRequiredEquity-Math.max(0,m.ownEquityInput||0));',
    '(!ownFinanceAcquisitionChecked || ownFinancingBelowFull)',
    '"Eigenkapital erhöhen – Fehlbetrag: "+eur(ownEquityShortfall)+"."',
    'V8.269',
    'service-worker.js?v=8.269'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.269 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.269 own-use equity shortfall warning applied")
