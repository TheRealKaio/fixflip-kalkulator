from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 5 px entsprechen im PDF ungefähr 1,3 mm.
# Budget: Abstand Überschrift -> Zusammenfassungsbox 6,0 -> 4,7 mm.
rep(
'''  doc.text("Zusammenfassung",left,y);
  y+=6;

  doc.setFont("helvetica","normal");''',
'''  doc.text("Zusammenfassung",left,y);
  y+=4.7;

  doc.setFont("helvetica","normal");''',
"budget summary gap"
)

# Eigennutzung / Fix & Flip: 4,0 -> 2,7 mm.
rep(
'''  doc.text("Zusammenfassung", left, y);
  y += 4;
  drawInfoBox("", recommendationText, {''',
'''  doc.text("Zusammenfassung", left, y);
  y += 2.7;
  drawInfoBox("", recommendationText, {''',
"main summary gap"
)

# Vermietung: 4,0 -> 2,7 mm.
rep(
'''    doc.text('Zusammenfassung',L,y);
    y+=4;
    drawInfoBox('',recommendation,{''',
'''    doc.text('Zusammenfassung',L,y);
    y+=2.7;
    drawInfoBox('',recommendation,{''',
"rental summary gap"
)

# Vermietung: Leerabsatz vor dem konkreten Eigenzuschuss-Hinweis.
rep(
"""Die Immobilie trägt sich aus der laufenden Vermietung nicht selbst. Du musst jeden Monat eigenes Geld zuschießen. """,
"""Die Immobilie trägt sich aus der laufenden Vermietung nicht selbst.\\n\\nDu musst jeden Monat eigenes Geld zuschießen. """,
"rental own contribution paragraph"
)

s=s.replace("V8.319","V8.320")
s=s.replace("service-worker.js?v=8.319","service-worker.js?v=8.320")

required=[
  'y+=4.7;',
  'y += 2.7;',
  'y+=2.7;',
  r'selbst.\n\nDu musst jeden Monat eigenes Geld zuschießen.',
  "V8.320",
  "service-worker.js?v=8.320"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.320 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.320 PDF summary spacing and rental paragraph break applied")
