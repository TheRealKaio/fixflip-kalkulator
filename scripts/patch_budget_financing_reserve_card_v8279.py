from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

old_markup='''          <div class="field"><label>Finanzierungsreserve</label><div class="input-wrap"><input id="budgetSafetyReserve" inputmode="decimal" value="0" readonly aria-readonly="true"><span class="unit">€</span></div><div class="mini">10 % von Einnahmen − Ausgaben · mindestens 300 €</div></div>'''
new_markup='''          <div class="field budget-calculated-field">
            <div class="budget-calculated-card">
              <div class="budget-calculated-title">Finanzierungsreserve</div>
              <div class="budget-calculated-subtitle">Automatisch berechnet</div>
              <div class="budget-calculated-value" id="budgetSafetyReserveDisplay">0 €</div>
              <div class="input-wrap budget-calculated-storage" aria-hidden="true"><input id="budgetSafetyReserve" inputmode="decimal" value="0" readonly aria-readonly="true" tabindex="-1"><span class="unit">€</span></div>
            </div>
          </div>'''
replace_once(old_markup,new_markup,"financial reserve display card")

css_anchor='#budgetAssumptionsBody .budget-grid>.field{margin:8px 0}'
if css_anchor not in s:
    raise SystemExit("V8.279 CSS anchor missing")

css='''#budgetAssumptionsBody .budget-calculated-field{margin:8px 0}
#budgetAssumptionsBody .budget-calculated-card{background:#eef6ff;border:1px solid #cfe2f7;border-radius:14px;padding:12px 14px;min-height:50px;box-sizing:border-box}
#budgetAssumptionsBody .budget-calculated-title{font-size:13px;font-weight:800;color:#244a73;line-height:1.2}
#budgetAssumptionsBody .budget-calculated-subtitle{font-size:11px;color:#6c8197;line-height:1.3;margin-top:2px}
#budgetAssumptionsBody .budget-calculated-value{font-size:21px;font-weight:800;color:#17395c;line-height:1.15;margin-top:7px}
#budgetAssumptionsBody .budget-calculated-storage{display:none}'''
if css not in s:
    s=s.replace(css_anchor,css_anchor+'\n'+css,1)

render_anchor='''  if($("budgetFinancingReserveResult")) $("budgetFinancingReserveResult").textContent=eur(m.minimumReserve);'''
if render_anchor not in s:
    raise SystemExit("V8.279 reserve render anchor missing")
render_new=render_anchor+'''\n  if($("budgetSafetyReserveDisplay")) $("budgetSafetyReserveDisplay").textContent=eur(m.minimumReserve);'''
s=s.replace(render_anchor,render_new,1)

s=s.replace("V8.278","V8.279")
s=s.replace("service-worker.js?v=8.278","service-worker.js?v=8.279")

required=[
    'class="field budget-calculated-field"',
    '<div class="budget-calculated-title">Finanzierungsreserve</div>',
    '<div class="budget-calculated-subtitle">Automatisch berechnet</div>',
    'id="budgetSafetyReserveDisplay"',
    '.budget-calculated-card{background:#eef6ff;',
    '$("budgetSafetyReserveDisplay").textContent=eur(m.minimumReserve);',
    'V8.279',
    'service-worker.js?v=8.279'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.279 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.279 financing reserve converted to calculated display card")
