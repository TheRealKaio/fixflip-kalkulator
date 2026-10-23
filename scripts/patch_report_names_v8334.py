from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else '_site/index.html')
s = p.read_text()
old = '(currentDealType()==="budget" ? "Budget_Immobilie_Report_" : (currentDealType()==="own" ? "Eigennutzung_Deal_Report_" : "FixFlip_Deal_Report_")) + new Date().toISOString().slice(0,10) + ".pdf"'
if s.count(old) != 2:
    raise SystemExit('Main PDF naming anchors missing')
s = s.replace(old, 'nicPdfReportName(currentDealType()) + ".pdf"')
helper = '''function nicPdfReportName(mode,now=new Date()){
  const titles={budget:"Budget",own:"Eigennutzung",rent:"Vermietung",flip:"Fix und Flip"};
  const parts=new Intl.DateTimeFormat("en-GB",{
    timeZone:"Europe/Berlin",year:"numeric",month:"2-digit",day:"2-digit",
    hour:"2-digit",minute:"2-digit",hourCycle:"h23"
  }).formatToParts(now);
  const value=type=>parts.find(part=>part.type===type).value;
  return "Neustart ImmoCheck "+titles[mode]+" Bericht "+value("year")+"-"+value("month")+"-"+value("day")+" "+value("hour")+"-"+value("minute");
}

'''
anchor = 'async function savePdf(){'
if s.count(anchor) != 1:
    raise SystemExit('PDF helper anchor missing')
s = s.replace(anchor, helper + anchor, 1)
replacements = {
    "'Vermietung_Deal_Report_'+new Date().toISOString().slice(0,10)+'.pdf'": "nicPdfReportName('rent')+'.pdf'",
    'title: currentDealType()==="budget" ? "Immobilien-Budget Report" : "Fix & Flip Deal Report",': 'title: filename.slice(0,-4),',
    'text: currentDealType()==="budget" ? "Meine Immobilien-Budget-Kalkulation" : "Meine Fix & Flip Kalkulation",': 'text: filename.slice(0,-4),',
    "title:'Vermietung - Deal Report',text:'Meine Vermietungs-Kalkulation'": "title:name.slice(0,-4),text:name.slice(0,-4)",
}
for old, new in replacements.items():
    if s.count(old) != 1:
        raise SystemExit('PDF name anchor missing or duplicated: ' + old)
    s = s.replace(old, new, 1)
p.write_text(s)
admin = p.parent / 'admin.html'
admin.write_text(admin.read_text().replace('V8.333', 'V8.334'))
print('V8.334 consistent branded PDF report names applied')
