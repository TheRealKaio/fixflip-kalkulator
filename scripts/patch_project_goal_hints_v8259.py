from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

replace_once(
'''          <div class="field"><label>Ziel-Gewinn <span class="hint">vor Steuer</span> <button class="info-btn inline-info" type="button" data-info="targetProfitInfo">i</button></label><div class="input-wrap"><input id="targetProfit" inputmode="decimal" value="40000"><span class="unit">€</span></div></div>''',
'''          <div class="field"><label>Ziel-Gewinn <button class="info-btn inline-info" type="button" data-info="targetProfitInfo">i</button></label><div class="input-wrap"><input id="targetProfit" inputmode="decimal" value="40000"><span class="unit">€</span></div><div class="mini">vor Steuer</div></div>''',
"target profit hint below input"
)

replace_once(
'''          <div class="field"><label>Verfügbares Eigenkapital <span class="hint">für das Projekt</span> <button class="info-btn inline-info" type="button" data-info="maxEquityInfo">i</button></label><div class="input-wrap"><input id="maxEquity" inputmode="decimal" value="0"><span class="unit">€</span></div><div class="mini">Deine harte Liquiditätsgrenze für Finanzierung und Projektlaufzeit.</div></div>''',
'''          <div class="field"><label>Verfügbares Eigenkapital <button class="info-btn inline-info" type="button" data-info="maxEquityInfo">i</button></label><div class="input-wrap"><input id="maxEquity" inputmode="decimal" value="0"><span class="unit">€</span></div><div class="mini">Harte Liquiditätsgrenze für die Projektlaufzeit.</div></div>''',
"remove available equity inline hint"
)

replace_once(
'''          <div class="field"><label>Mindest-Rendite <span class="hint">auf eigenes Geld</span> <button class="info-btn inline-info" type="button" data-info="targetRoiInfo">i</button></label><div class="input-wrap"><input id="targetRoi" inputmode="decimal" value="25"><span class="unit">%</span></div></div>''',
'''          <div class="field"><label>Mindest-Rendite <button class="info-btn inline-info" type="button" data-info="targetRoiInfo">i</button></label><div class="input-wrap"><input id="targetRoi" inputmode="decimal" value="25"><span class="unit">%</span></div><div class="mini">auf eigenes Geld</div></div>''',
"ROI hint below input"
)

replace_once(
'''          <div class="field"><label>Persönlicher Steuersatz <span class="hint">auf positiven Projektgewinn</span></label><div class="input-wrap"><input id="personalTax" inputmode="decimal" value="42"><span class="unit">%</span></div></div>''',
'''          <div class="field"><label>Persönlicher Steuersatz</label><div class="input-wrap"><input id="personalTax" inputmode="decimal" value="42"><span class="unit">%</span></div><div class="mini">auf positiven Projektgewinn</div></div>''',
"tax hint below input"
)

# Version bump.
s=s.replace("V8.258","V8.259")
s=s.replace("service-worker.js?v=8.258","service-worker.js?v=8.259")

required=[
    '<label>Ziel-Gewinn <button class="info-btn inline-info"',
    '<div class="mini">vor Steuer</div>',
    '<label>Verfügbares Eigenkapital <button class="info-btn inline-info"',
    'für das Projekt</span>' not in s,
    '<label>Mindest-Rendite <button class="info-btn inline-info"',
    '<div class="mini">auf eigenes Geld</div>',
    '<label>Persönlicher Steuersatz</label>',
    '<div class="mini">auf positiven Projektgewinn</div>',
    'V8.259',
    'service-worker.js?v=8.259'
]
# Boolean token handled separately.
missing=[x for x in required if isinstance(x,str) and x not in s]
if missing:
    raise SystemExit("V8.259 verification failed: "+", ".join(missing))
if 'Verfügbares Eigenkapital <span class="hint">für das Projekt</span>' in s:
    raise SystemExit("V8.259 inline available-equity hint still present")

path.write_text(s,encoding="utf-8")
print("V8.259 project-goal hint layout applied")
