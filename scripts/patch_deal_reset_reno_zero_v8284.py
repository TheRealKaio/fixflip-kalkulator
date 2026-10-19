from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''  initializeTrades(true);
  setSaleRecalculatedState(false);'''
new='''  initializeTrades(true);

  // "Deal neu berechnen" setzt alle Einzelwerte der Sanierungsaufteilung bewusst auf 0.
  // Die Nullen werden als manuelle Werte gespeichert, damit m²-Positionen beim
  // erneuten Öffnen nicht sofort wieder automatisch aus der Wohnfläche vorbelegt werden.
  trades.forEach(t=>{
    tradeValues[t.key]=0;
    manualTrades.add(t.key);
    localStorage.setItem("ff_trade_"+t.key,"0");
    localStorage.setItem("ff_trade_manual_"+t.key,"1");
  });
  syncRenoTotal();
  if($("tradeList")) renderTrades();

  setSaleRecalculatedState(false);'''

if old not in s:
    raise SystemExit("V8.284 deal reset renovation anchor missing")
s=s.replace(old,new,1)

s=s.replace("V8.283","V8.284")
s=s.replace("service-worker.js?v=8.283","service-worker.js?v=8.284")

required=[
    'tradeValues[t.key]=0;',
    'localStorage.setItem("ff_trade_"+t.key,"0");',
    'localStorage.setItem("ff_trade_manual_"+t.key,"1");',
    'syncRenoTotal();',
    'if($("tradeList")) renderTrades();',
    'V8.284',
    'service-worker.js?v=8.284'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.284 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.284 deal reset now zeros all renovation split values")
