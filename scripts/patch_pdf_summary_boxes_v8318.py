from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Budget-PDF: Zusammenfassungsbox ohne feste Höhe, mindestens ~10px Innenabstand,
# oben ausgerichtet und im Blocksatz.
old_budget='''  const recommendationPadding=4;
  const recommendationH=26;
  const recommendationInnerW=contentW-(recommendationPadding*2);
  let recommendationFontSize=8.2;
  let recommendationLines=[];
  let recommendationLineH=3.7;
  while(recommendationFontSize>=6.6){
    doc.setFont("helvetica","normal");
    doc.setFontSize(recommendationFontSize);
    recommendationLines=doc.splitTextToSize(pdfSafeText(recommendation),recommendationInnerW);
    recommendationLineH=recommendationFontSize*0.46;
    if(recommendationLines.length*recommendationLineH <= recommendationH-(recommendationPadding*2)-1) break;
    recommendationFontSize-=0.2;
  }
  doc.setTextColor(55,65,81);
  doc.setFillColor(239,246,255); doc.setDrawColor(191,219,254);
  doc.roundedRect(left,y,contentW,recommendationH,3,3,"FD");
  doc.text(recommendationLines,left+recommendationPadding,y+recommendationPadding+1.7);
  y += recommendationH + 10;'''
new_budget='''  const recommendationPadding=4;
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
rep(old_budget,new_budget,"budget summary box")

# Gemeinsamer PDF-Helper für Eigennutzung/Fix & Flip:
# tight=true berechnet die Höhe rein aus Inhalt + Padding.
old_main='''    const fixedHeight = options.fixedHeight || null;
    let bodySize = options.bodySize || 8.7;
    let lines = [];
    let lineH = bodySize*0.46;
    const bodyTop = title ? 10 : 5;'''
new_main='''    const fixedHeight = options.fixedHeight || null;
    const tight = options.tight === true;
    const justify = options.justify === true;
    let bodySize = options.bodySize || 8.7;
    let lines = [];
    let lineH = bodySize*0.46;
    const bodyTop = title ? 10 : padding;'''
rep(old_main,new_main,"main info helper flags")

old_main_height='''    const boxHeight = fixedHeight || Math.max(options.minHeight || 18, bodyTop + lines.length*4.2 + padding);'''
new_main_height='''    const naturalHeight = bodyTop + Math.max(lineH,lines.length*lineH) + padding;
    const boxHeight = fixedHeight || (tight ? naturalHeight : Math.max(options.minHeight || 18, bodyTop + lines.length*4.2 + padding));'''
rep(old_main_height,new_main_height,"main dynamic info height")

old_main_text='''    doc.text(lines, left+padding, y+bodyTop);'''
new_main_text='''    doc.text(lines, left+padding, y+bodyTop, justify ? {
      align:"justify",
      maxWidth:boxWidth-padding*2,
      baseline:"top",
      lineHeightFactor:1.15
    } : undefined);'''
rep(old_main_text,new_main_text,"main justified info text")

rep(
'''  drawInfoBox("", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, fixedHeight:34, padding:4});''',
'''  drawInfoBox("", recommendationText, {fill:[239,246,255], stroke:[191,219,254], bodySize:8.4, titleSize:9.5, padding:4, tight:true, justify:true});''',
"main summary call"
)

# Vermietungs-PDF besitzt einen eigenen drawInfoBox-Helper.
old_rental='''      const fixedHeight=options.fixedHeight||null;
      let bodySize=options.bodySize||8.7;
      let lines=[];
      let lineH=bodySize*.46;
      const bodyTop=title?10:5;'''
new_rental='''      const fixedHeight=options.fixedHeight||null;
      const tight=options.tight===true;
      const justify=options.justify===true;
      let bodySize=options.bodySize||8.7;
      let lines=[];
      let lineH=bodySize*.46;
      const bodyTop=title?10:padding;'''
rep(old_rental,new_rental,"rental info helper flags")

old_rental_height='''      const boxHeight=fixedHeight||Math.max(options.minHeight||18,bodyTop+lines.length*4.2+padding);'''
new_rental_height='''      const naturalHeight=bodyTop+Math.max(lineH,lines.length*lineH)+padding;
      const boxHeight=fixedHeight||(tight?naturalHeight:Math.max(options.minHeight||18,bodyTop+lines.length*4.2+padding));'''
rep(old_rental_height,new_rental_height,"rental dynamic info height")

old_rental_text='''      doc.text(lines,L+padding,y+bodyTop);'''
new_rental_text='''      doc.text(lines,L+padding,y+bodyTop,justify?{
        align:"justify",
        maxWidth:W-padding*2,
        baseline:"top",
        lineHeightFactor:1.15
      }:undefined);'''
rep(old_rental_text,new_rental_text,"rental justified info text")

old_rental_call='''    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      bodySize:m.cashflow<0?7.4:8.4,
      fixedHeight:m.cashflow<0?64:34,
      padding:4
    });'''
new_rental_call='''    drawInfoBox('',recommendation,{
      fill:[239,246,255],
      stroke:[191,219,254],
      bodySize:m.cashflow<0?7.4:8.4,
      padding:4,
      tight:true,
      justify:true
    });'''
rep(old_rental_call,new_rental_call,"rental summary call")

s=s.replace("V8.317","V8.318")
s=s.replace("service-worker.js?v=8.317","service-worker.js?v=8.318")

required=[
  'align:"justify"',
  'baseline:"top"',
  'tight:true',
  'justify:true',
  'const naturalHeight = bodyTop + Math.max(lineH,lines.length*lineH) + padding;',
  'const naturalHeight=bodyTop+Math.max(lineH,lines.length*lineH)+padding;',
  "V8.318",
  "service-worker.js?v=8.318"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.318 missing: "+", ".join(missing))

for forbidden in [
  "const recommendationH=26;",
  "fixedHeight:34, padding:4",
  "fixedHeight:m.cashflow<0?64:34"
]:
    if forbidden in s:
        raise SystemExit("V8.318 legacy fixed summary height remains: "+forbidden)

p.write_text(s,encoding="utf-8")
print("V8.318 PDF summary boxes now fit content with justified top-aligned text")
