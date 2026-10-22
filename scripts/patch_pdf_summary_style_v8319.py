from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Budget: Zusammenfassung mit 9 pt, 10 mm Padding, dunklerem Anthrazit,
#    groesserem Zeilenabstand und sauberem Seitenumbruch vor Ueberschrift + Box.
old_budget='''  doc.setFont("helvetica","bold"); doc.setFontSize(13); doc.setTextColor(23,32,51);
  doc.text("Zusammenfassung",left,y); y+=6;
  const recommendation = "Kaufe nicht die Immobilie, die dir die Bank maximal finanziert, sondern die Immobilie, die du dir langfristig und entspannt leisten kannst. Eine Immobilienfinanzierung ist häufig eine Verpflichtung über 20 bis 35 Jahre. Deshalb sollte man nicht nur auf den Zinssatz schauen, sondern auf die gesamte finanzielle Situation. Berücksichtige zur Überbrückung von Notar, Grundbuch etc. das notwendige Eigenkapital, da häufig schon Rechnungen fällig werden, bevor die Bank eine Auszahlung getätigt hat.";
  const recommendationPadding=4;
  const recommendationInnerW=contentW-(recommendationPadding*2);
  const recommendationFontSize=8.2;
  doc.setFont("helvetica","normal");
  doc.setFontSize(recommendationFontSize);
  const recommendationLines=doc.splitTextToSize(pdfSafeText(recommendation),recommendationInnerW);
  const recommendationLineH=recommendationFontSize*0.46;
  const recommendationH=(recommendationPadding*2)+Math.max(recommendationLineH,recommendationLines.length*recommendationLineH);
  doc.setTextColor(55,65,81);
  doc.setFillColor(239,246,255); doc.setDrawColor(191,219,254);
  doc.roundedRect(left,y,contentW,recommendationH,3,3,"FD");
  doc.text(recommendationLines,left+recommendationPadding,y+recommendationPadding,{
    align:"justify",
    maxWidth:recommendationInnerW,
    baseline:"top",
    lineHeightFactor:1.15
  });
  y += recommendationH + 6;'''

new_budget='''  const recommendation = "Kaufe nicht die Immobilie, die dir die Bank maximal finanziert, sondern die Immobilie, die du dir langfristig und entspannt leisten kannst. Eine Immobilienfinanzierung ist häufig eine Verpflichtung über 20 bis 35 Jahre. Deshalb sollte man nicht nur auf den Zinssatz schauen, sondern auf die gesamte finanzielle Situation. Berücksichtige zur Überbrückung von Notar, Grundbuch etc. das notwendige Eigenkapital, da häufig schon Rechnungen fällig werden, bevor die Bank eine Auszahlung getätigt hat.";
  const recommendationPadding=10;
  const recommendationFontSize=9;
  const recommendationLineHeightFactor=1.18;
  const recommendationInnerW=contentW-(recommendationPadding*2);
  doc.setFont("helvetica","normal");
  doc.setFontSize(recommendationFontSize);
  const recommendationLines=doc.splitTextToSize(pdfSafeText(recommendation),recommendationInnerW);
  const recommendationLineH=recommendationFontSize*0.3528*recommendationLineHeightFactor;
  const recommendationH=(recommendationPadding*2)+Math.max(recommendationLineH,recommendationLines.length*recommendationLineH);

  if(y+6+recommendationH>278){
    doc.addPage();
    drawPdfBrandHeader(doc,"Budget - Immobilien-Report","Wie viel Immobilie kann ich mir leisten?",new Date().toLocaleDateString("de-DE"));
    y=43;
  }

  doc.setFont("helvetica","bold");
  doc.setFontSize(13);
  doc.setTextColor(23,32,51);
  doc.text("Zusammenfassung",left,y);
  y+=6;

  doc.setFont("helvetica","normal");
  doc.setFontSize(recommendationFontSize);
  doc.setTextColor(45,55,70);
  doc.setFillColor(239,246,255);
  doc.setDrawColor(191,219,254);
  doc.roundedRect(left,y,contentW,recommendationH,3,3,"FD");
  doc.text(recommendationLines,left+recommendationPadding,y+recommendationPadding,{
    align:"justify",
    maxWidth:recommendationInnerW,
    baseline:"top",
    lineHeightFactor:recommendationLineHeightFactor
  });
  y += recommendationH + 6;'''
rep(old_budget,new_budget,"budget summary layout")

# 2) Gemeinsamer Helper Eigennutzung/Fix & Flip: Zeilenabstand als Option
#    und natuerliche Hoehe aus realer 9-pt-Zeilenhoehe berechnen.
old_main_flags='''    const fixedHeight = options.fixedHeight || null;
    const tight = options.tight === true;
    const justify = options.justify === true;
    let bodySize = options.bodySize || 8.7;
    let lines = [];
    let lineH = bodySize*0.46;
    const bodyTop = title ? 10 : padding;'''
new_main_flags='''    const fixedHeight = options.fixedHeight || null;
    const tight = options.tight === true;
    const justify = options.justify === true;
    const lineHeightFactor = options.lineHeightFactor || 1.15;
    let bodySize = options.bodySize || 8.7;
    let lines = [];
    let lineH = bodySize*0.3528*lineHeightFactor;
    const bodyTop = title ? 10 : padding;'''
rep(old_main_flags,new_main_flags,"main summary helper flags")

rep(
'''        lineH=bodySize*0.46;''',
'''        lineH=bodySize*0.3528*lineHeightFactor;''',
"main fixed-height line metric"
)

rep(
'''      lineHeightFactor:1.15''',
'''      lineHeightFactor:lineHeightFactor''',
"main line height option"
)

old_main_call='''  doc.setFont("helvetica","bold");
  doc.setFontSize(13);
  doc.text("Zusammenfassung", left, y);
  y += 4;
  drawInfoBox("", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, padding:4, tight:true, justify:true});
  y += 3;'''

new_main_call='''  const summaryPadding=10;
  const summaryFontSize=9;
  const summaryLineHeightFactor=1.18;
  doc.setFont("helvetica","normal");
  doc.setFontSize(summaryFontSize);
  const summaryPreviewLines=doc.splitTextToSize(pdfSafeText(recommendationText),178-summaryPadding*2);
  const summaryPreviewLineH=summaryFontSize*0.3528*summaryLineHeightFactor;
  const summaryPreviewH=summaryPadding*2+Math.max(summaryPreviewLineH,summaryPreviewLines.length*summaryPreviewLineH);
  ensureSpace(summaryPreviewH+12);

  doc.setFont("helvetica","bold");
  doc.setFontSize(13);
  doc.setTextColor(23,32,51);
  doc.text("Zusammenfassung", left, y);
  y += 4;
  drawInfoBox("", recommendationText, {
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
  y += 3;'''
rep(old_main_call,new_main_call,"main summary call")

# 3) Vermietung: gleicher Satz an Parametern und Textfarbe im eigenen Helper.
old_rental_flags='''      const fixedHeight=options.fixedHeight||null;
      const tight=options.tight===true;
      const justify=options.justify===true;
      let bodySize=options.bodySize||8.7;
      let lines=[];
      let lineH=bodySize*.46;
      const bodyTop=title?10:padding;'''
new_rental_flags='''      const fixedHeight=options.fixedHeight||null;
      const tight=options.tight===true;
      const justify=options.justify===true;
      const textColor=options.textColor||[71,85,105];
      const lineHeightFactor=options.lineHeightFactor||1.15;
      let bodySize=options.bodySize||8.7;
      let lines=[];
      let lineH=bodySize*0.3528*lineHeightFactor;
      const bodyTop=title?10:padding;'''
rep(old_rental_flags,new_rental_flags,"rental summary helper flags")

# zweite verbliebene 0.46-Zeile ist die Vermietungsvariante
rep(
'''          lineH=bodySize*.46;''',
'''          lineH=bodySize*0.3528*lineHeightFactor;''',
"rental fixed-height line metric"
)

rep(
'''      doc.setTextColor(71,85,105);
      doc.setFont('helvetica','normal');''',
'''      doc.setTextColor(textColor[0],textColor[1],textColor[2]);
      doc.setFont('helvetica','normal');''',
"rental text color option"
)

rep(
'''        lineHeightFactor:1.15''',
'''        lineHeightFactor:lineHeightFactor''',
"rental line height option"
)

old_rental_call='''    doc.setFont('helvetica','bold');
    doc.setFontSize(13);
    doc.setTextColor(23,32,51);
    doc.text('Zusammenfassung',L,y);
    y+=4;
    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      bodySize:m.cashflow<0?7.4:8.4,
      padding:4,
      tight:true,
      justify:true
    });
    y+=3;'''

new_rental_call='''    const summaryPadding=10;
    const summaryFontSize=9;
    const summaryLineHeightFactor=1.18;
    doc.setFont('helvetica','normal');
    doc.setFontSize(summaryFontSize);
    const summaryPreviewLines=doc.splitTextToSize(pdfSafeText(recommendation),W-summaryPadding*2);
    const summaryPreviewLineH=summaryFontSize*0.3528*summaryLineHeightFactor;
    const summaryPreviewH=summaryPadding*2+Math.max(summaryPreviewLineH,summaryPreviewLines.length*summaryPreviewLineH);
    ensureSpace(summaryPreviewH+12);

    doc.setFont('helvetica','bold');
    doc.setFontSize(13);
    doc.setTextColor(23,32,51);
    doc.text('Zusammenfassung',L,y);
    y+=4;
    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      textColor:[45,55,70],
      bodySize:summaryFontSize,
      padding:summaryPadding,
      tight:true,
      justify:true,
      lineHeightFactor:summaryLineHeightFactor
    });
    y+=3;'''
rep(old_rental_call,new_rental_call,"rental summary call")

s=s.replace("V8.318","V8.319")
s=s.replace("service-worker.js?v=8.318","service-worker.js?v=8.319")

required=[
  "const recommendationPadding=10;",
  "const recommendationFontSize=9;",
  "const recommendationLineHeightFactor=1.18;",
  "doc.setTextColor(45,55,70);",
  "const summaryPadding=10;",
  "const summaryFontSize=9;",
  "const summaryLineHeightFactor=1.18;",
  "textColor:[45,55,70]",
  "ensureSpace(summaryPreviewH+12);",
  "lineHeightFactor:summaryLineHeightFactor",
  "V8.319",
  "service-worker.js?v=8.319"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.319 missing: "+", ".join(missing))

for forbidden in [
  "bodySize:m.cashflow<0?7.4:8.4",
  "bodySize:8.4, titleSize:9.5, padding:4, tight:true",
  "const recommendationFontSize=8.2;",
  "const recommendationPadding=4;"
]:
    if forbidden in s:
        raise SystemExit("V8.319 legacy summary formatting remains: "+forbidden)

p.write_text(s,encoding="utf-8")
print("V8.319 PDF summary boxes standardized to 9pt, 10mm padding and page-safe dynamic height")
