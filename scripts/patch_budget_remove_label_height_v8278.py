from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

old='''#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field){display:flex;flex-direction:column;min-width:0}
#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{display:flex;align-items:flex-end;min-height:34px;line-height:1.25}
#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>.input-wrap{width:100%;min-width:0}
@media(max-width:520px){#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{min-height:0}}'''

new='''#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field){min-width:0}
#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{line-height:1.25}
#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>.input-wrap{width:100%;min-width:0}'''

replace_once(old,new,"remove artificial financing label height")

s=s.replace("V8.277","V8.278")
s=s.replace("service-worker.js?v=8.277","service-worker.js?v=8.278")

required=[
    '#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{line-height:1.25}',
    '#budgetAssumptionsBody .budget-grid>.field{margin:8px 0}',
    'V8.278',
    'service-worker.js?v=8.278'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.278 verification failed: "+", ".join(missing))

if '#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{display:flex;align-items:flex-end;min-height:34px;line-height:1.25}' in s:
    raise SystemExit("V8.278 artificial financing label height still present")

path.write_text(s,encoding="utf-8")
print("V8.278 removed artificial label height from financing assumptions")
