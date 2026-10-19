from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Haushaltsinformationen eindeutig adressierbar machen.
replace_once(
'''    <div id="budgetSection" class="mode-hidden">
      <section class="card">
        <h2>1. Haushaltsinformationen</h2>''',
'''    <div id="budgetSection" class="mode-hidden">
      <section class="card" id="budgetHouseholdSection">
        <h2>1. Haushaltsinformationen</h2>''',
"budget household section id"
)

# Zusatzabstand vor Eigenkapital entfernen.
replace_once(
'.budget-equity-row{display:grid;grid-template-columns:1fr;margin-top:12px;width:100%}',
'.budget-equity-row{display:grid;grid-template-columns:1fr;margin-top:0;width:100%}',
"budget equity row margin"
)

# Wie in "1. Deine Immobilie": .quick-grid .field = 8px 0.
css_anchor='#budgetAssumptionsBody .budget-grid.three{row-gap:8px;column-gap:10px}'
if css_anchor not in s:
    raise SystemExit("V8.277 assumptions spacing anchor missing")

compact_css='''#budgetHouseholdSection .budget-grid>.field,#budgetHouseholdSection .budget-equity-row .field{margin:8px 0}
#budgetAssumptionsBody .budget-grid>.field{margin:8px 0}'''
if compact_css not in s:
    s=s.replace(css_anchor,css_anchor+'\n'+compact_css,1)

# Version bump.
s=s.replace("V8.276","V8.277")
s=s.replace("service-worker.js?v=8.276","service-worker.js?v=8.277")

required=[
    'id="budgetHouseholdSection"',
    '.budget-equity-row{display:grid;grid-template-columns:1fr;margin-top:0;width:100%}',
    '#budgetHouseholdSection .budget-grid>.field,#budgetHouseholdSection .budget-equity-row .field{margin:8px 0}',
    '#budgetAssumptionsBody .budget-grid>.field{margin:8px 0}',
    'V8.277',
    'service-worker.js?v=8.277'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.277 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.277 household and financing field margins aligned to 8px")
