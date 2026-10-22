from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

before_double=s.count('doc.text("Handlungsempfehlung"')
before_single=s.count("doc.text('Handlungsempfehlung'")
before=before_double+before_single
if before < 3:
    raise SystemExit(f"Expected at least 3 PDF recommendation headings, found {before}")

s=s.replace('doc.text("Handlungsempfehlung"', 'doc.text("Zusammenfassung"')
s=s.replace("doc.text('Handlungsempfehlung'", "doc.text('Zusammenfassung'")

if 'doc.text("Handlungsempfehlung"' in s or "doc.text('Handlungsempfehlung'" in s:
    raise SystemExit("Legacy PDF heading remains")

# Vermietungs-Untertitel bewusst auf demselben Stil wie Eigennutzung sichern.
rental_subtitle_style='''    doc.setFont('helvetica','normal');
    doc.setFontSize(8.2);
    doc.setTextColor(100,110,125);
    const overviewSubtitle='''

if rental_subtitle_style not in s:
    raise SystemExit("Rental overview subtitle style does not match Eigennutzung")

s=s.replace("V8.310","V8.311")
s=s.replace("service-worker.js?v=8.310","service-worker.js?v=8.311")

required=[
    "Zusammenfassung",
    "Wichtigste Ergebnisse auf einen Blick",
    "doc.setFontSize(8.2);",
    "V8.311",
    "service-worker.js?v=8.311"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.311 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print(f"V8.311 renamed {before} PDF heading occurrences to Zusammenfassung")
