from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

# Give both renovation groups explicit row classes so mobile CSS can treat them differently.
old_sqm="""out+='<div class="trade-row"><div class="trade-top"><div>'+"""
new_sqm="""out+='<div class="trade-row trade-row-sqm"><div class="trade-top"><div>'+"""
if old_sqm not in s:
    raise SystemExit("V8.289 sqm row markup anchor missing")
s=s.replace(old_sqm,new_sqm,1)

old_fixed="""out+='<div class="trade-row"><div class="trade-top">'+
        '<div class="trade-copy">"""
new_fixed="""out+='<div class="trade-row trade-row-fixed"><div class="trade-top">'+
        '<div class="trade-copy">"""
if old_fixed not in s:
    raise SystemExit("V8.289 fixed row markup anchor missing")
s=s.replace(old_fixed,new_fixed,1)

# Override the V8.288 generic stacking with group-specific mobile layouts.
anchor='''  .reno-inline-panel .trade-area-input,
  .reno-inline-panel .trade-money-input{
    flex:0 0 auto;
    width:100%;
    min-width:0;
    max-width:100%;
  }
}'''
if anchor not in s:
    raise SystemExit("V8.289 mobile CSS anchor missing")

replacement='''  .reno-inline-panel .trade-area-input,
  .reno-inline-panel .trade-money-input{
    flex:0 0 auto;
    width:100%;
    min-width:0;
    max-width:100%;
  }

  /* Wohnflächen-Vorschläge: Betrag in eigener Zeile über volle Breite. */
  .reno-inline-panel .trade-row-sqm .trade-top>div:first-child{
    flex:1 1 100%;
    width:100%;
    min-width:0;
  }
  .reno-inline-panel .trade-row-sqm .trade-top>.input-wrap{
    flex:1 1 100%;
    width:100%;
    min-width:0;
    max-width:100%;
    margin-top:8px;
  }

  /* Pauschal / Stück: m² links, Betrag rechts – beide in einer Zeile. */
  .reno-inline-panel .trade-row-fixed .trade-inputs-inline{
    flex-direction:row;
    align-items:stretch;
    gap:8px;
  }
  .reno-inline-panel .trade-row-fixed .trade-area-input,
  .reno-inline-panel .trade-row-fixed .trade-money-input{
    flex:1 1 0;
    width:0;
    min-width:0;
    max-width:none;
  }
}'''
s=s.replace(anchor,replacement,1)

s=s.replace("V8.288","V8.289")
s=s.replace("service-worker.js?v=8.288","service-worker.js?v=8.289")

required=[
    'class="trade-row trade-row-sqm"',
    'class="trade-row trade-row-fixed"',
    '.trade-row-sqm .trade-top>.input-wrap{',
    'flex:1 1 100%;',
    '.trade-row-fixed .trade-inputs-inline{',
    'flex-direction:row;',
    '.trade-row-fixed .trade-area-input,',
    'width:0;',
    'V8.289',
    'service-worker.js?v=8.289'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.289 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.289 mobile renovation groups now use distinct layouts")
