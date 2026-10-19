from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

anchor='''@media(max-width:520px){.reno-inline-panel .reno-sheet{padding:12px}}'''
if anchor not in s:
    raise SystemExit("V8.283 mobile renovation anchor missing")

mobile_css='''@media(max-width:520px){
  .reno-inline-panel{min-width:0;max-width:100%;overflow:hidden}
  .reno-inline-panel .reno-sheet{width:100%;max-width:100%;min-width:0;padding:12px;box-sizing:border-box}
  .reno-inline-panel .trade-list,.reno-inline-panel .trade-row,.reno-inline-panel .trade-top{min-width:0;max-width:100%;box-sizing:border-box}
  .reno-inline-panel .trade-top{flex-wrap:wrap}
  .reno-inline-panel .trade-copy{flex:1 1 100%;width:100%;min-width:0}
  .reno-inline-panel .trade-inputs-inline{display:flex;flex:1 1 100%;width:100%;min-width:0;max-width:100%;justify-content:stretch}
  .reno-inline-panel .trade-inputs-inline>.input-wrap,
  .reno-inline-panel .trade-row .input-wrap,
  .reno-inline-panel .trade-area-input,
  .reno-inline-panel .trade-money-input{flex:1 1 0;width:auto;min-width:0;max-width:100%}
  .reno-inline-panel .trade-amount,
  .reno-inline-panel .trade-area-input input,
  .reno-inline-panel .trade-money-input input{width:100%;min-width:0;max-width:100%;box-sizing:border-box}
}'''

s=s.replace(anchor,anchor+'\n'+mobile_css,1)

s=s.replace("V8.282","V8.283")
s=s.replace("service-worker.js?v=8.282","service-worker.js?v=8.283")

required=[
    '.reno-inline-panel .reno-sheet{width:100%;max-width:100%;min-width:0;padding:12px;box-sizing:border-box}',
    '.reno-inline-panel .trade-top{flex-wrap:wrap}',
    '.reno-inline-panel .trade-inputs-inline{display:flex;flex:1 1 100%;width:100%;min-width:0;max-width:100%;justify-content:stretch}',
    '.reno-inline-panel .trade-money-input{flex:1 1 0;width:auto;min-width:0;max-width:100%}',
    '.reno-inline-panel .trade-amount,',
    'V8.283',
    'service-worker.js?v=8.283'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.283 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.283 mobile renovation inputs constrained within inline panel")
