from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

old_markup='''          <div class="field budget-calculated-field">
            <div class="budget-calculated-card">
              <div class="budget-calculated-title">Finanzierungsreserve</div>
              <div class="budget-calculated-subtitle">Automatisch berechnet</div>
              <div class="budget-calculated-value" id="budgetSafetyReserveDisplay">0 €</div>
              <div class="input-wrap budget-calculated-storage" aria-hidden="true"><input id="budgetSafetyReserve" inputmode="decimal" value="0" readonly aria-readonly="true" tabindex="-1"><span class="unit">€</span></div>
            </div>
          </div>'''
new_markup='''          <div class="field budget-calculated-field">
            <label class="budget-calculated-title">Finanzierungsreserve</label>
            <div class="budget-calculated-card">
              <div class="budget-calculated-value" id="budgetSafetyReserveDisplay">0 €</div>
              <div class="input-wrap budget-calculated-storage" aria-hidden="true"><input id="budgetSafetyReserve" inputmode="decimal" value="0" readonly aria-readonly="true" tabindex="-1"><span class="unit">€</span></div>
            </div>
            <div class="mini budget-calculated-subtitle">Automatisch berechnet</div>
          </div>'''
replace_once(old_markup,new_markup,"financial reserve layout")

old_css='''#budgetAssumptionsBody .budget-calculated-field{margin:8px 0}
#budgetAssumptionsBody .budget-calculated-card{background:#eef6ff;border:1px solid #cfe2f7;border-radius:14px;padding:12px 14px;min-height:50px;box-sizing:border-box}
#budgetAssumptionsBody .budget-calculated-title{font-size:13px;font-weight:800;color:#244a73;line-height:1.2}
#budgetAssumptionsBody .budget-calculated-subtitle{font-size:11px;color:#6c8197;line-height:1.3;margin-top:2px}
#budgetAssumptionsBody .budget-calculated-value{font-size:21px;font-weight:800;color:#17395c;line-height:1.15;margin-top:7px}
#budgetAssumptionsBody .budget-calculated-storage{display:none}'''
new_css='''#budgetAssumptionsBody .budget-calculated-field{margin:8px 0}
#budgetAssumptionsBody .budget-calculated-title{display:block}
#budgetAssumptionsBody .budget-calculated-card{display:flex;align-items:center;width:100%;height:50px;min-height:50px;background:#eef6ff;border:1.5px solid #cfe2f7;border-radius:14px;padding:0 14px;box-sizing:border-box}
#budgetAssumptionsBody .budget-calculated-value{font-size:17px;font-weight:650;color:var(--ink);line-height:1}
#budgetAssumptionsBody .budget-calculated-subtitle{margin-top:6px}
#budgetAssumptionsBody .budget-calculated-storage{display:none}'''
replace_once(old_css,new_css,"financial reserve display sizing")

s=s.replace("V8.279","V8.280")
s=s.replace("service-worker.js?v=8.279","service-worker.js?v=8.280")

required=[
    '<label class="budget-calculated-title">Finanzierungsreserve</label>',
    '<div class="mini budget-calculated-subtitle">Automatisch berechnet</div>',
    '.budget-calculated-card{display:flex;align-items:center;width:100%;height:50px;min-height:50px;',
    '.budget-calculated-value{font-size:17px;font-weight:650;',
    'V8.280',
    'service-worker.js?v=8.280'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.280 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.280 financing reserve layout aligned to input fields")
