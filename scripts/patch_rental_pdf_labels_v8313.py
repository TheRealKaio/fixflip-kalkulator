from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

old1="'Nettokaltmiete mtl.: '+money(m.coldRent)"
new1="'Nettokaltmiete Mtl.: '+money(m.coldRent)"
old2="'+\'  ·  Hausgeld gesamt pro Monat: \'+money(housegeld)'"
new2="'+\'  ·  Hausgeld Mtl.: \'+money(housegeld)'"

if old1 not in s:
    raise SystemExit("cold rent subtitle label missing")
if old2 not in s:
    raise SystemExit("housegeld subtitle label missing")

s=s.replace(old1,new1,1)
s=s.replace(old2,new2,1)

s=s.replace("V8.312","V8.314")
s=s.replace("service-worker.js?v=8.312","service-worker.js?v=8.314")

required=[
    "Nettokaltmiete Mtl..:",
    "Hausgeld Mtl.:",
    "Nettokaltmiete pro m²:",
    "Davon nicht umlagefähig:",
    "money(m.coldRent)",
    "money(housegeld)",
    "money(m.nonAlloc)",
    "V8.314",
    "service-worker.js?v=8.314"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.314 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.314 rental PDF subtitle labels updated")
