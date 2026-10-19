from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''@media(max-width:520px){
  .budget-grid,.budget-grid.three,.budget-result-grid{grid-template-columns:1fr}
  .budget-expense-row{grid-template-columns:minmax(0,1fr) 92px}
  .budget-expense-name{grid-column:1/-1}
}'''

new='''@media(max-width:520px){
  .budget-grid,.budget-grid.three,.budget-result-grid{grid-template-columns:1fr}
  .budget-expense-row{grid-template-columns:1fr;gap:7px}
  .budget-expense-name{grid-column:1}
  .budget-expense-row .input-wrap{grid-column:1;width:100%;min-width:0}
  .budget-expense-row .input-wrap input{width:100%;min-width:0}
}'''

if old not in s:
    raise SystemExit("V8.270 mobile budget expense CSS anchor missing")
s=s.replace(old,new,1)

s=s.replace("V8.269","V8.270")
s=s.replace("service-worker.js?v=8.269","service-worker.js?v=8.270")

required=[
    '.budget-expense-row{grid-template-columns:1fr;gap:7px}',
    '.budget-expense-row .input-wrap{grid-column:1;width:100%;min-width:0}',
    '.budget-expense-row .input-wrap input{width:100%;min-width:0}',
    'V8.270',
    'service-worker.js?v=8.270'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.270 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.270 mobile budget expense fields use full width")
