from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Rote Fehlbetragsmeldung direkt unter der gelben Eigenkapitalbox.
replace_once(
'''          <div class="equity-capital-note" id="equityCapitalNote">
            Dein Eigenkapital deckt zuerst den Liquiditätsbedarf des Projekts. Nur der danach verbleibende Betrag reduziert die Kreditsumme.
            <span id="equityCapitalNeed"></span>
          </div>''',
'''          <div class="equity-capital-note" id="equityCapitalNote">
            Dein Eigenkapital deckt zuerst den Liquiditätsbedarf des Projekts. Nur der danach verbleibende Betrag reduziert die Kreditsumme.
            <span id="equityCapitalNeed"></span>
          </div>
          <div class="equity-shortfall-warning" id="equityShortfallWarning" hidden></div>''',
"equity shortfall warning markup"
)

css_anchor='.equity-capital-note strong{color:var(--ink)}'
if css_anchor not in s:
    raise SystemExit("equity warning CSS anchor missing")
s=s.replace(
    css_anchor,
    css_anchor+'''
.equity-shortfall-warning{margin:8px 0 0;padding:9px 11px;border-radius:10px;background:#fdecec;border:1px solid #e8a0a0;color:#b91c1c;font-size:12px;font-weight:800;line-height:1.4}
.equity-shortfall-warning[hidden]{display:none}''',
    1
)

# Dynamisch nur bei nicht mitfinanzierten NK oder Finanzierung < 100 % und echtem Fehlbetrag.
render_anchor='''  if($("equityNeedNote") && currentDealType()==="flip"){
    $("equityNeedNote").textContent = m.equityShortfall>0
      ? "Eigenkapital im Projekt · Fehlbetrag "+eur(m.equityShortfall)
      : (m.fullFinanceMode ? "vollständig fremdfinanziert" : "100 % des verfügbaren Eigenkapitals eingesetzt");
  }'''
render_new=render_anchor+'''
  if($("equityShortfallWarning")){
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
replace_once(render_anchor,render_new,"equity shortfall warning render")

s=s.replace("V8.267","V8.268")
s=s.replace("service-worker.js?v=8.267","service-worker.js?v=8.268")

required=[
    'id="equityShortfallWarning"',
    'class="equity-shortfall-warning"',
    'const financingBelowFull = Math.max(0,pct("ltv")) < 0.999999;',
    '(!financeAcquisitionChecked || financingBelowFull)',
    '"Eigenkapital erhöhen – Fehlbetrag: "+eur(m.equityShortfall)+"."',
    'V8.268',
    'service-worker.js?v=8.268'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.268 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.268 financing shortfall warning applied")
