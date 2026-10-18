from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old="Deine harte Liquiditätsgrenze für Finanzierung und Projektlaufzeit."
new="Harte Liquiditätsgrenze für die Projektlaufzeit."
if old in s:
    s=s.replace(old,new,1)

if new not in s:
    raise SystemExit("V8.260 liquidity hint text missing")

s=s.replace("V8.259","V8.260")
s=s.replace("service-worker.js?v=8.259","service-worker.js?v=8.260")

required=[
    "Harte Liquiditätsgrenze für die Projektlaufzeit.",
    "V8.260",
    "service-worker.js?v=8.260"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.260 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.260 liquidity hint updated")
