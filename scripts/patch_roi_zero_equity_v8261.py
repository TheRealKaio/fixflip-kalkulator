from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''  const missRoi = !isOwnUse && m.roi + rateTolerance < targetRoi;'''
new='''  // ROI auf eigenes Geld ist nur bewertbar, wenn tatsächlich eigenes Geld
  // im Projekt gebunden ist. Bei 0 EUR Eigenkapitalbedarf löst die ROI-Ampel
  // deshalb kein Ziel-Miss aus.
  const hasOwnMoneyInProject = !isOwnUse && m.equity > moneyTolerance;
  const missRoi = hasOwnMoneyInProject && m.roi + rateTolerance < targetRoi;'''

if old not in s:
    raise SystemExit("V8.261 ROI status anchor missing")
s=s.replace(old,new,1)

s=s.replace("V8.260","V8.261")
s=s.replace("service-worker.js?v=8.260","service-worker.js?v=8.261")

required=[
  'const hasOwnMoneyInProject = !isOwnUse && m.equity > moneyTolerance;',
  'const missRoi = hasOwnMoneyInProject && m.roi + rateTolerance < targetRoi;',
  'V8.261',
  'service-worker.js?v=8.261'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.261 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.261 ROI light ignores zero-equity projects")
