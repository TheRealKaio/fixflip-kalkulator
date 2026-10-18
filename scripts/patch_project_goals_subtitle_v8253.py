from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

base="Trage hier die Bedingungen deiner Finanzziele ein."
extra=" Sie steuern auch die Farbampel der Ergebnisse."
new=base+extra

# Idempotent normalisieren: der Zusatz darf genau einmal vorkommen.
while new+extra in s:
    s=s.replace(new+extra,new)
if new not in s:
    s=s.replace(base,new)

s=s.replace("V8.252","V8.253")
s=s.replace("service-worker.js?v=8.252","service-worker.js?v=8.253")

required=[
  new,
  "V8.253",
  "service-worker.js?v=8.253"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.253 verification failed: "+", ".join(missing))
if new+extra in s:
    raise SystemExit("V8.253 duplicate project-goals subtitle remains")

path.write_text(s,encoding="utf-8")
print("V8.253 project goals subtitle normalized")
