from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='<input id="interest" inputmode="decimal" value="7.5">'
new='<input id="interest" inputmode="decimal" value="4.00">'

if old not in s:
    raise SystemExit("V8.285 legacy 7.5 interest default anchor missing")
s=s.replace(old,new,1)

s=s.replace("V8.284","V8.285")
s=s.replace("service-worker.js?v=8.284","service-worker.js?v=8.285")

required=[
    '<input id="interest" inputmode="decimal" value="4.00">',
    'const REFERENCE_INTEREST_FALLBACK = 4.0;',
    'V8.285',
    'service-worker.js?v=8.285'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.285 verification failed: "+", ".join(missing))

if '<input id="interest" inputmode="decimal" value="7.5">' in s:
    raise SystemExit("V8.285 legacy 7.5 Fix-&-Flip interest default still present")

path.write_text(s,encoding="utf-8")
print("V8.285 Fix-&-Flip interest markup default changed from 7.5 to 4.00")
