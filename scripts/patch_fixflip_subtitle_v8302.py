from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

old="Kauf, Sanierung und Verkauf"
new="Kauf, Sanierung und Verkauf prüfen"

if new not in s:
    if old not in s:
        raise SystemExit("Fix & Flip subtitle anchor missing")
    s=s.replace(old,new,1)

s=s.replace("V8.301","V8.302")
s=s.replace("service-worker.js?v=8.301","service-worker.js?v=8.302")

required=[
  new,
  "V8.302",
  "service-worker.js?v=8.302"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.302 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.302 Fix & Flip subtitle applied")
