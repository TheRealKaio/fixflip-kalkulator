from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old="Trage hier die Bedingungen deiner Finanzziele ein."
new="Trage hier die Bedingungen deiner Finanzziele ein. Sie steuern auch die Farbampel der Ergebnisse."

# Alte Formulierungen im erzeugten HTML final auf die neue Fassung vereinheitlichen.
s=s.replace(old,new)

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

path.write_text(s,encoding="utf-8")
print("V8.253 project goals subtitle updated")
