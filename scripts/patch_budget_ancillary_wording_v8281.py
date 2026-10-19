from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='Notar, Grundbuch, Makler.'
new='Notar, Grund-, Eintragung, Makler.'

if old in s:
    s=s.replace(old,new)
if new not in s:
    raise SystemExit("V8.281 ancillary wording not present")

s=s.replace("V8.280","V8.281")
s=s.replace("service-worker.js?v=8.280","service-worker.js?v=8.281")

required=[
    'Notar, Grund-, Eintragung, Makler.',
    'V8.281',
    'service-worker.js?v=8.281'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.281 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.281 ancillary wording updated")
