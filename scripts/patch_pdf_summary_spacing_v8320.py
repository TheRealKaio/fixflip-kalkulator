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

# The existing helper adds 4 mm after each summary box. Use another 7 mm
# before the results heading, for a consistent 11 mm baseline gap.
rep(
'''  doc.text(recommendationLines,left+recommendationPadding,y+recommendationPadding,{
    align:"justify",
    maxWidth:recommendationInnerW,
    baseline:"top",
    lineHeightFactor:recommendationLineHeightFactor
  });
  y += recommendationH + 6;''',
'''  doc.text(recommendationLines,left+recommendationPadding,y+recommendationPadding,{
    align:"justify",
    maxWidth:recommendationInnerW,
    baseline:"top",
    lineHeightFactor:recommendationLineHeightFactor
  });
  y += recommendationH + 11;''',
"budget results-title gap"
)

rep(
'''  drawInfoBox("", recommendationText, {
    fill:[239,246,255],
    stroke:[191,219,254],
    textColor:[45,55,70],
    bodySize:summaryFontSize,
    titleSize:9.5,
    padding:summaryPadding,
    tight:true,
    justify:true,
    lineHeightFactor:summaryLineHeightFactor
  });
  y += 3;''',
'''  drawInfoBox("", recommendationText, {
    fill:[239,246,255],
    stroke:[191,219,254],
    textColor:[45,55,70],
    bodySize:summaryFontSize,
    titleSize:9.5,
    padding:summaryPadding,
    tight:true,
    justify:true,
    lineHeightFactor:summaryLineHeightFactor
  });
  y += 7;''',
"deal results-title gap"
)

rep(
'''    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      textColor:[45,55,70],
      bodySize:summaryFontSize,
      padding:summaryPadding,
      tight:true,
      justify:true,
      lineHeightFactor:summaryLineHeightFactor
    });
    y+=3;''',
'''    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      textColor:[45,55,70],
      bodySize:summaryFontSize,
      padding:summaryPadding,
      tight:true,
      justify:true,
      lineHeightFactor:summaryLineHeightFactor
    });
    y+=7;''',
"rental results-title gap"
)

# Eigennutzung and Fix & Flip: the optimization box is the last results box.
# Start the individual purchase/renovation positions on the next page.
rep(
'''  drawInfoBox("Optimierungspotenzial", optimizationText, {fill:[248,250,252], stroke:[226,232,240], bodySize:8.0, titleSize:9.5, minHeight:16});

  y += 1;
  section("Objekt & Ankauf", 74);''',
'''  drawInfoBox("Optimierungspotenzial", optimizationText, {fill:[248,250,252], stroke:[226,232,240], bodySize:8.0, titleSize:9.5, minHeight:16});

  addPage(null, "Übersicht der Einzelpositionen");
  section("Objekt & Ankauf", 74);''',
"deal details page break"
)

# Rental: keep the results grid on page 1 and move all itemized inputs/values
# to a new page with the same shared report header.
rep(
'''    drawKpiGrid([
      {title:'Bruttomietrendite',value:pct(m.grossYield),note:'Jahresnettokaltmiete ÷ Kaufpreis'},
      {title:'Nettomietrendite',value:pct(m.netYield),note:'Nettoertrag vor Finanzierung ÷ Gesamtinvestition'},
      {title:'Rendite auf dein Eigenkapital',value:pct(m.cashOnCash),note:'jährlicher Cashflow ÷ eingesetztes Eigenkapital'},
      {title:'Kaufpreisfaktor',value:m.factor==null?'–':m.factor.toFixed(1).replace('.',',')+' ×',note:'Kaufpreis ÷ Jahresnettokaltmiete'},
      {title:'Break-even-Nettokaltmiete',value:m.breakEven==null?'–':money(m.breakEven)+' / Monat',note:'notwendige Monatsmiete für Cashflow 0 €'}
    ]);

    section('Objekt & Investition',60);''',
'''    drawKpiGrid([
      {title:'Bruttomietrendite',value:pct(m.grossYield),note:'Jahresnettokaltmiete ÷ Kaufpreis'},
      {title:'Nettomietrendite',value:pct(m.netYield),note:'Nettoertrag vor Finanzierung ÷ Gesamtinvestition'},
      {title:'Rendite auf dein Eigenkapital',value:pct(m.cashOnCash),note:'jährlicher Cashflow ÷ eingesetztes Eigenkapital'},
      {title:'Kaufpreisfaktor',value:m.factor==null?'–':m.factor.toFixed(1).replace('.',',')+' ×',note:'Kaufpreis ÷ Jahresnettokaltmiete'},
      {title:'Break-even-Nettokaltmiete',value:m.breakEven==null?'–':money(m.breakEven)+' / Monat',note:'notwendige Monatsmiete für Cashflow 0 €'}
    ]);

    addPage('Übersicht der Einzelpositionen');
    section('Objekt & Investition',60);''',
"rental details page break"
)

# Budget: start the household/position breakdown on a new page directly after
# the final results card. The existing break before the fixed-expense table
# remains in place to keep that subsection together.
rep(
'''  budgetPdfCard(left+wideW+gap,y,wideW,18,"Frei verfügbares Monatsbudget",freeBudget);
  y += 22;


  section("Haushalt");''',
'''  budgetPdfCard(left+wideW+gap,y,wideW,18,"Frei verfügbares Monatsbudget",freeBudget);
  y += 22;

  doc.addPage();
  drawPdfBrandHeader(doc,"Budget - Immobilien-Report","Übersicht der Einzelpositionen",new Date().toLocaleDateString("de-DE"));
  y=43;
  section("Haushalt");''',
"budget details page break"
)

# Vermietung: Leerabsatz vor dem konkreten Eigenzuschuss-Hinweis.
rep(
"""Die Immobilie trägt sich aus der laufenden Vermietung nicht selbst. Du musst jeden Monat eigenes Geld zuschießen. """,
"""Die Immobilie trägt sich aus der laufenden Vermietung nicht selbst.\\n\\nDu musst jeden Monat eigenes Geld zuschießen. """,
"rental own contribution paragraph"
)

s=s.replace("V8.319","V8.320")
s=s.replace("service-worker.js?v=8.319","service-worker.js?v=8.320")


# Fix & Flip: die Einzelpositionen starten nach dem vereinbarten Umbruch
# bereits auf Seite 2. Vor dem Sanierungsblock keinen weiteren Seitenwechsel
# erzwingen, damit zusammengehörende Zahlen und Werte beisammenbleiben.
rep(
'''  if(!isOwnUse){
    addPage();
    page2Section("Sanierung", 32);
  } else {''',
'''  if(!isOwnUse){
    page2Section("Sanierung", 32);
  } else {''',
"fixflip extra page break"
)

required=[
  'y+=4.7;',
  'y += 2.7;',
  'y+=2.7;',
  r'selbst.\n\nDu musst jeden Monat eigenes Geld zuschießen.',
  "V8.320",
  "service-worker.js?v=8.320",
  'y += recommendationH + 11;',
  'y += 7;',
  'y+=7;',
  'addPage(null, "Übersicht der Einzelpositionen");',
  "addPage('Übersicht der Einzelpositionen');",
  'drawPdfBrandHeader(doc,"Budget - Immobilien-Report","Übersicht der Einzelpositionen",new Date().toLocaleDateString("de-DE"));'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.320 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.320 PDF summary spacing and rental paragraph break applied")
