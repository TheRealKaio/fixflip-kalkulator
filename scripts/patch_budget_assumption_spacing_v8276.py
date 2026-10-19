from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

anchor='#budgetAssumptionsBody .budget-state-field{grid-column:1/-1}'
if anchor not in s:
    raise SystemExit("V8.276 assumptions anchor missing")

rule='#budgetAssumptionsBody .budget-grid.three{row-gap:8px;column-gap:10px}'
if rule not in s:
    s=s.replace(anchor,anchor+'\n'+rule,1)

s=s.replace("V8.275","V8.276")
s=s.replace("service-worker.js?v=8.275","service-worker.js?v=8.276")

required=[
    '#budgetAssumptionsBody .budget-grid.three{row-gap:8px;column-gap:10px}',
    'V8.276',
    'service-worker.js?v=8.276'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.276 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.276 financing assumption row gap reduced to 8px")
