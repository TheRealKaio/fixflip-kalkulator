from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

anchor='''.reno-inline-panel .trade-amount,
  .reno-inline-panel .trade-area-input input,
  .reno-inline-panel .trade-money-input input{width:100%;min-width:0;max-width:100%;box-sizing:border-box}
}'''
if anchor not in s:
    raise SystemExit("V8.288 mobile renovation CSS anchor missing")

replacement='''.reno-inline-panel .trade-amount,
  .reno-inline-panel .trade-area-input input,
  .reno-inline-panel .trade-money-input input{width:100%;min-width:0;max-width:100%;box-sizing:border-box}

  /* V8.288: mobile renovation inputs get their own full-width rows. */
  .reno-inline-panel .trade-inputs-inline{
    flex-direction:column;
    align-items:stretch;
    gap:8px;
  }
  .reno-inline-panel .trade-inputs-inline>.input-wrap,
  .reno-inline-panel .trade-area-input,
  .reno-inline-panel .trade-money-input{
    flex:0 0 auto;
    width:100%;
    min-width:0;
    max-width:100%;
  }
}'''
s=s.replace(anchor,replacement,1)

s=s.replace("V8.287","V8.288")
s=s.replace("service-worker.js?v=8.287","service-worker.js?v=8.288")

required=[
    '.reno-inline-panel .trade-inputs-inline{\n    flex-direction:column;',
    'align-items:stretch;',
    '.reno-inline-panel .trade-area-input,\n  .reno-inline-panel .trade-money-input{\n    flex:0 0 auto;\n    width:100%;',
    'V8.288',
    'service-worker.js?v=8.288'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.288 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.288 mobile renovation calculated inputs moved to full-width rows")
