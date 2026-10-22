from pathlib import Path
import sys
import re

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

pattern=r"  function buildRentalPdf\(\)\{.*?\n  async function rentalPdf\(kind\)\{"
m=re.search(pattern,s,re.S)
if not m:
    raise SystemExit("buildRentalPdf block missing")

new_func=r'''  function buildRentalPdf(){
    if(!window.jspdf||!window.jspdf.jsPDF) throw new Error('PDF-Bibliothek konnte nicht geladen werden.');
    const {jsPDF}=window.jspdf;
    const doc=new jsPDF({unit:'mm',format:'a4',orientation:'portrait'});
    const m=rentalModel();
    const L=16,R=194,W=178,pageBottom=278;
    let y=43;

    const housegeld=Math.max(0,rn('rentHousegeld'));
    const coldRentSqm=m.area>0 ? m.coldRent/m.area : 0;
    const monthlyInterest=Math.max(0,m.loan*m.interest/12);
    const monthlyRepayment=Math.max(0,m.loan*m.repayment/12);
    const buildYear=String($r('rentBuildYear')?.value||'').trim();
    const plotArea=Math.max(0,rn('rentPlotArea'));

    const addPage=(subtitle='Erstellt aus der Vermietungs-Kalkulation')=>{
      doc.addPage();
      drawPdfBrandHeader(doc,'Vermietung - Deal Report',subtitle,new Date().toLocaleDateString('de-DE'));
      y=43;
    };

    const ensureSpace=needed=>{
      if(y+needed>pageBottom) addPage();
    };

    const line=(label,value,bold=false)=>{
      ensureSpace(5.8);
      doc.setTextColor(23,32,51);
      doc.setFont('helvetica',bold?'bold':'normal');
      doc.setFontSize(9.2);
      doc.text(pdfSafeText(label),L,y);
      doc.text(pdfSafeText(value),R,y,{align:'right'});
      y+=5.1;
    };

    const section=(title,requiredHeight=18)=>{
      ensureSpace(requiredHeight);
      y+=3;
      doc.setFillColor(15,23,42);
      doc.roundedRect(L,y-4,W,9,2,2,'F');
      doc.setTextColor(255,255,255);
      doc.setFont('helvetica','bold');
      doc.setFontSize(11);
      doc.text(pdfSafeText(title),L+3,y+2);
      doc.setTextColor(23,32,51);
      y+=11;
    };

    const drawInfoBox=(title,text,options={})=>{
      const fill=options.fill||[248,250,252];
      const stroke=options.stroke||[226,232,240];
      const padding=options.padding||4;
      const fixedHeight=options.fixedHeight||null;
      let bodySize=options.bodySize||8.7;
      let lines=[];
      let lineH=bodySize*.46;
      const bodyTop=title?10:5;
      if(fixedHeight){
        while(bodySize>=6.8){
          doc.setFont('helvetica','normal');
          doc.setFontSize(bodySize);
          lines=doc.splitTextToSize(pdfSafeText(text),W-padding*2);
          lineH=bodySize*.46;
          if(lines.length*lineH<=fixedHeight-bodyTop-padding) break;
          bodySize-=.2;
        }
      }else{
        doc.setFontSize(bodySize);
        lines=doc.splitTextToSize(pdfSafeText(text),W-padding*2);
      }
      const boxHeight=fixedHeight||Math.max(options.minHeight||18,bodyTop+lines.length*4.2+padding);
      ensureSpace(boxHeight+3);
      doc.setFillColor(fill[0],fill[1],fill[2]);
      doc.setDrawColor(stroke[0],stroke[1],stroke[2]);
      doc.roundedRect(L,y,W,boxHeight,3,3,'FD');
      if(title){
        doc.setTextColor(15,23,42);
        doc.setFont('helvetica','bold');
        doc.setFontSize(options.titleSize||10);
        doc.text(pdfSafeText(title),L+padding,y+6);
      }
      doc.setTextColor(71,85,105);
      doc.setFont('helvetica','normal');
      doc.setFontSize(bodySize);
      doc.text(lines,L+padding,y+bodyTop);
      doc.setTextColor(23,32,51);
      y+=boxHeight+4;
    };

    const drawKpiCard=(x,y0,w,h,title,value,note='')=>{
      doc.setFillColor(248,250,252);
      doc.setDrawColor(226,232,240);
      doc.roundedRect(x,y0,w,h,3,3,'FD');
      doc.setTextColor(71,85,105);
      doc.setFont('helvetica','bold');
      doc.setFontSize(8.4);
      doc.text(pdfSafeText(title),x+4,y0+5.5);
      doc.setTextColor(15,23,42);
      doc.setFont('helvetica','bold');
      doc.setFontSize(12.5);
      doc.text(pdfSafeText(value),x+4,y0+12.5);
      if(note){
        doc.setTextColor(100,110,125);
        doc.setFont('helvetica','normal');
        doc.setFontSize(6.8);
        const lines=doc.splitTextToSize(pdfSafeText(note),w-8);
        doc.text(lines.slice(0,2),x+4,y0+17);
      }
      doc.setTextColor(23,32,51);
    };

    const drawKpiGrid=cards=>{
      const gap=6,colW=86,rowH=21,rowGap=3;
      const rows=Math.ceil(cards.length/2);
      ensureSpace(rows*(rowH+rowGap)+2);
      cards.forEach((c,idx)=>{
        const oddLast=cards.length%2===1&&idx===cards.length-1;
        const row=Math.floor(idx/2);
        if(oddLast){
          drawKpiCard(L,y+row*(rowH+rowGap),W,rowH,c.title,c.value,c.note||'');
        }else{
          const col=idx%2;
          drawKpiCard(L+col*(colW+gap),y+row*(rowH+rowGap),colW,rowH,c.title,c.value,c.note||'');
        }
      });
      y+=rows*rowH+Math.max(0,rows-1)*rowGap+5;
    };

    const recommendation=(()=>{
      if(!(m.purchase>0&&m.coldRent>0)){
        return 'Trage Kaufpreis, Nettokaltmiete, laufende Kosten und Finanzierung vollständig ein. Erst dann lassen sich Cashflow, Rendite und Kaufpreisfaktor sinnvoll einordnen.';
      }
      const cashRatio=m.coldRent>0?m.cashflow/m.coldRent:0;
      if(m.cashflow>=0 && m.factor!=null && m.factor<=25){
        return 'Die Vermietung wirkt auf Basis deiner Eingaben solide: Der laufende Cashflow ist positiv und der Kaufpreisfaktor liegt in einem attraktiven bis soliden Bereich. Prüfe trotzdem Mietansatz, Hausgeld, Instandhaltungsbedarf und Finanzierung anhand der Objektunterlagen.';
      }
      if(cashRatio>=-.10 && m.factor!=null && m.factor<=30){
        return 'Die Kalkulation liegt im prüfenswerten Bereich. Cashflow beziehungsweise Kaufpreisfaktor bieten noch keinen großen Sicherheitspuffer. Prüfe insbesondere nicht umlagefähige Kosten, Instandhaltung, realistische Miete und mögliche Zinsänderungen.';
      }
      return 'Die Vermietung wirkt mit den aktuellen Annahmen eher angespannt. Ein hoher Kaufpreisfaktor oder negativer Cashflow kann den laufenden Ertrag deutlich belasten. Prüfe Kaufpreis, Finanzierung, Miete und Eigentümerkosten erneut, bevor du die Immobilie wirtschaftlich bewertest.';
    })();

    drawPdfBrandHeader(
      doc,
      'Vermietung - Deal Report',
      'Erstellt aus der Vermietungs-Kalkulation',
      new Date().toLocaleDateString('de-DE')
    );

    doc.setFont('helvetica','bold');
    doc.setFontSize(13);
    doc.setTextColor(23,32,51);
    doc.text('Handlungsempfehlung',L,y);
    y+=4;
    drawInfoBox('',recommendation,{fill:[239,246,255],stroke:[191,219,254],bodySize:8.4,fixedHeight:34,padding:4});
    y+=3;

    doc.setFont('helvetica','bold');
    doc.setFontSize(12);
    doc.setTextColor(23,32,51);
    doc.text('Wichtigste Ergebnisse auf einen Blick',L,y);
    y+=5;

    doc.setFont('helvetica','normal');
    doc.setFontSize(8.2);
    doc.setTextColor(100,110,125);
    const overviewSubtitle=
      'Nettokaltmiete mtl.: '+money(m.coldRent)
      +'  ·  Nettokaltmiete pro m²: '+(m.area>0?new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(coldRentSqm)+' €':'–')
      +'  ·  Hausgeld gesamt pro Monat: '+money(housegeld)
      +'  ·  Davon nicht umlagefähig: '+money(m.nonAlloc);
    const overviewLines=doc.splitTextToSize(pdfSafeText(overviewSubtitle),W);
    doc.text(overviewLines,L,y);
    doc.setTextColor(23,32,51);
    y+=Math.max(7,overviewLines.length*4+2);

    drawKpiGrid([
      {title:'Bruttomietrendite',value:pct(m.grossYield),note:'Jahresnettokaltmiete ÷ Kaufpreis'},
      {title:'Nettomietrendite',value:pct(m.netYield),note:'Nettoertrag vor Finanzierung ÷ Gesamtinvestition'},
      {title:'Rendite auf dein Eigenkapital',value:pct(m.cashOnCash),note:'jährlicher Cashflow ÷ eingesetztes Eigenkapital'},
      {title:'Kaufpreisfaktor',value:m.factor==null?'–':m.factor.toFixed(1).replace('.',',')+' ×',note:'Kaufpreis ÷ Jahresnettokaltmiete'},
      {title:'Break-even-Nettokaltmiete',value:m.breakEven==null?'–':money(m.breakEven)+' / Monat',note:'notwendige Monatsmiete für Cashflow 0 €'}
    ]);

    section('Objekt & Investition',60);
    line('Kaufpreis',money(m.purchase),true);
    line('Wohnfläche',new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(m.area)+' m²');
    line('Kaufpreis pro m²',m.area>0?money(m.purchase/m.area)+' / m²':'–');
    line('Baujahr',buildYear&&buildYear!=='0'?buildYear:'–');
    line('Grundstücksgröße',plotArea>0?new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(plotArea)+' m²':'–');
    line('Modernisierung inkl. Puffer',money(m.renovation));
    line('Kaufnebenkosten',money(m.acquisition));
    line('Gesamtinvestition',money(m.totalInvestment),true);

    section('Laufende Vermietung',52);
    line('Nettokaltmiete pro Monat',money(m.coldRent));
    line('Hausgeld gesamt pro Monat',money(housegeld));
    line('Davon nicht umlagefähig',money(m.nonAlloc));
    line('Verwaltung pro Monat',money(m.management));
    line('Zusätzliche Instandhaltung',money(m.maintenance));
    line('Sonstige Vermieterkosten',money(m.other));
    line('Mietausfall / Leerstand',new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.vacancy*100)+' %');

    section('Finanzierung & Nebenkosten',62);
    line('Eigenkapital',money(m.equityUsed));
    line('Darlehen',money(m.loan),true);
    line('Zins p.a.',new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.interest*100)+' %');
    line('Tilgung p.a.',new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.repayment*100)+' %');
    line('Monatliche Zinsbelastung',money(monthlyInterest));
    line('Monatliche Tilgung',money(monthlyRepayment));
    line('Monatliche Kreditrate (Zins + Tilgung)',money(m.debt),true);
    line('Tilgung / Vermögensaufbau',money(m.principal)+' / Jahr');

    ensureSpace(25);
    drawInfoBox(
      'Hinweis zur Einordnung',
      'Der ausgewiesene Cashflow ist eine Orientierungsrechnung vor persönlicher Einkommensteuer. Eine mögliche AfA kann den steuerpflichtigen Überschuss reduzieren, ist aber kein eigener Geldzufluss. Mietsteigerungen und Wertentwicklung sind nicht garantiert und in der laufenden Cashflowrechnung nicht enthalten.',
      {fill:[248,250,252],stroke:[226,232,240],bodySize:7.8,titleSize:9.2,minHeight:20}
    );

    const totalPages=doc.getNumberOfPages();
    for(let pageNo=1;pageNo<=totalPages;pageNo++){
      doc.setPage(pageNo);
      drawPdfBrandLogo(doc);
      drawPdfFooter(doc,pageNo,totalPages,'V8.310');
    }
    return doc;
  }

  async function rentalPdf(kind){'''

s=s[:m.start()]+new_func+s[m.end():]
s=s.replace("V8.309","V8.310")
s=s.replace("service-worker.js?v=8.309","service-worker.js?v=8.310")

required=[
  "Wichtigste Ergebnisse auf einen Blick",
  "Erstellt aus der Vermietungs-Kalkulation",
  "Handlungsempfehlung",
  "Monatliche Zinsbelastung",
  "Monatliche Tilgung",
  "Nettokaltmiete pro m²",
  "Hausgeld gesamt pro Monat",
  "Davon nicht umlagefähig",
  "Rendite auf dein Eigenkapital",
  "Break-even-Nettokaltmiete",
  "Hinweis zur Einordnung",
  "drawPdfFooter(doc,pageNo,totalPages,'V8.310')",
  "V8.310",
  "service-worker.js?v=8.310"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.310 missing: "+", ".join(missing))

if "sec('Ergebnis auf einen Blick')" in s:
    raise SystemExit("V8.310 old rental PDF overview still present")

p.write_text(s,encoding="utf-8")
print("V8.310 rental PDF aligned with deal-report layout and monthly financing values")
