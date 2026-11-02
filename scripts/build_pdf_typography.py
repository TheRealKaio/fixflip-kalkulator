"""Apply live typography to the generated PDF module, leaving its original immutable."""
from pathlib import Path
import sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
p=site/'pdf-reports.js';s=p.read_text()
needle=' const setFont=doc.setFont.bind(doc),setTextColor=doc.setTextColor.bind(doc),setFillColor=doc.setFillColor.bind(doc);'
assert needle in s
s=s.replace(needle,needle+'''
 const originalSize=doc.setFontSize.bind(doc);
 // PDF points preserve the established report scale; admin changes are proportional.
 // H2 governs report section titles independently from body text.
 doc.setFontSize=value=>{
  const heading=/bold/i.test(doc.getFont().fontStyle);
  const factor=heading?(s.layout?.h2||18)/18:value<=8?(s.layout?.hintSize||12)/12:value<9?(s.layout?.subtextSize||14)/14:(s.layout?.bodySize||16)/16;
  return originalSize(value*factor);
 };
''',1)
# Legal blocks own their pagination: measure using the actual configured font and size.
a=s.index('function disclaimer(doc){');b=s.index('\nfunction model(v){',a)
s=s[:a]+'''function disclaimer(doc){
 const s=settings(doc),blocks=legalBlocks(s);let y=45;
 const next=()=>{doc.addPage();header(doc,'Haftungsausschluss / Disclaimer','Hinweise zur Nutzung der Kalkulatoren und PDF-Berichte');y=45;};
 next();
 for(const block of blocks){
  doc.setFont('helvetica',block.bold?'bold':'normal');
  doc.setFontSize(block.bold?13:9);
  doc.setTextColor(...(block.bold?[15,23,42]:[71,85,105]));
  const size=doc.getFontSize(),height=size*1.3/doc.internal.scaleFactor;
  const lines=doc.splitTextToSize(safe(block.text),178);
  if(y+Math.min(lines.length,block.bold?lines.length:2)*height>277){next();doc.setFont('helvetica',block.bold?'bold':'normal');doc.setFontSize(block.bold?13:9);}
  for(const line of lines){
   if(y+height>277){next();doc.setFont('helvetica',block.bold?'bold':'normal');doc.setFontSize(block.bold?13:9);doc.setTextColor(...(block.bold?[15,23,42]:[71,85,105]));}
   doc.text(line,16,y);y+=height;
  }
  y+=block.bold?2:5.5;
 }
 doc.setTextColor(23,32,51);
}
'''+s[b:]
p.write_text(s)
print('PDF body/H2 typography bound to settings; legal pagination uses measured line height')
