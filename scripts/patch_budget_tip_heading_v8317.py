from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

old='"Unsere wichtigsten Empfehlungen"'
new='"Unser wichtigster Tipp"'

if old not in s:
    raise SystemExit("budget PDF tip heading missing")
s=s.replace(old,new,1)

s=s.replace("V8.316","V8.317")
s=s.replace("service-worker.js?v=8.316","service-worker.js?v=8.317")

required=[
  "Unser wichtigster Tipp",
  "V8.317",
  "service-worker.js?v=8.317"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.317 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.317 budget PDF tip heading updated")
