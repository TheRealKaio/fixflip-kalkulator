(function(){
'use strict';
const titles={budget:'Budget',own:'Eigennutzung',rent:'Vermietung',flip:'Fix und Flip',finance:'Finanzierungsrechner'};
const defaults=JSON.parse(document.getElementById('nic-pdf-defaults')?.textContent||'{}');
let prepared=null,latest=null;
const snapshots=new WeakMap();
const safe=s=>String(s??'').replace(/€/g,'EUR').replace(/[–−]/g,'-').replace(/\u00ad/g,'');
const money=n=>new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n)+' EUR';
const percent=n=>new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n)+' %';
const date=()=>new Intl.DateTimeFormat('de-DE',{timeZone:'Europe/Berlin'}).format(new Date());
function settings(doc){return (doc&&snapshots.get(doc))||latest||window.NICSettings?.current||{company:{},layout:{},meta:{},legal:{}};}
function rgb(value,fallback){return /^#[a-f\d]{6}$/i.test(value||'')?[1,3,5].map(i=>parseInt(value.slice(i,i+2),16)):fallback;}
function font(s){return s.layout?.font==='georgia'?'times':'helvetica';}
function filename(mode,now=new Date()){
 const parts=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Berlin',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(now),v=k=>parts.find(p=>p.type===k).value;
 return 'Neustart ImmoCheck '+titles[mode]+' Bericht '+v('year')+'-'+v('month')+'-'+v('day')+' '+v('hour')+'-'+v('minute')+'.pdf';
}
async function prepare(){
 const S=window.NICSettings;if(S){try{latest=await S.init();}catch(err){let raw;try{raw=JSON.parse(localStorage.getItem(S.KEY)||'null');}catch(_){}latest=raw?S.normalize(raw):S.current;if(!latest)throw err;}S.apply(latest);}
 const s=settings(),source=s.websiteLogo||defaults.logo;
 if(prepared?.source===source)return prepared;
 const img=await new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>resolve(im);im.onerror=()=>reject(new Error('Das hinterlegte Logo konnte nicht geladen werden.'));im.src=source;});
 const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=680;const c=canvas.getContext('2d');c.fillStyle='#ffffff';c.fillRect(0,0,1800,680);
 const scale=Math.min(1800/img.naturalWidth,680/img.naturalHeight),w=img.naturalWidth*scale,h=img.naturalHeight*scale;c.drawImage(img,(1800-w)/2,(680-h)/2,w,h);
 prepared={source,data:canvas.toDataURL('image/png')};return prepared;
}
function create(options={},mode){
 if(!window.jspdf?.jsPDF)throw Error('PDF-Bibliothek konnte nicht geladen werden.');
 const doc=new window.jspdf.jsPDF(options),s=JSON.parse(JSON.stringify(settings()));snapshots.set(doc,s);
 const setFont=doc.setFont.bind(doc),setTextColor=doc.setTextColor.bind(doc),setFillColor=doc.setFillColor.bind(doc);
 doc.setFont=(name,style,...rest)=>setFont(name==='helvetica'?font(s):name,style,...rest);
 doc.setTextColor=(...args)=>setTextColor(...(args.length===3&&args[0]===23&&args[1]===32&&args[2]===51?rgb(s.layout?.text,args):args));
 doc.setFillColor=(...args)=>setFillColor(...(args.length===3&&args[0]===15&&args[1]===23&&args[2]===42?rgb(s.layout?.buttonBackground,args):args.length===3&&args[0]===247&&args[1]===249&&args[2]===252?rgb(s.layout?.background,args):args));
 doc.setProperties({author:s.company?.name||'Neustart ImmoCheck',creator:'Neustart ImmoCheck '+defaults.version,title:s.meta?.[mode]?.title||(mode?filename(mode).slice(0,-4):''),subject:s.meta?.[mode]?.description||''});return doc;
}
function logo(doc){
 doc.setFillColor(255,255,255);doc.roundedRect(16,5,58,24,3,3,'F');
 const image=prepared?.data||defaults.logo;if(image)doc.addImage(image,'PNG',18,7,54,20,undefined,'FAST');
}
function header(doc,title,subtitle,dateText=date()){
 const s=settings(doc);doc.setFillColor(...rgb(s.layout?.buttonBackground,[15,23,42]));doc.rect(0,0,210,34,'F');logo(doc);
 doc.setTextColor(...rgb(s.layout?.buttonText,[255,255,255]));doc.setFont('helvetica','bold');doc.setFontSize(14);
 const lines=doc.splitTextToSize(safe(title),114);doc.text(lines.slice(0,2),80,lines.length>1?11:14,{lineHeightFactor:1.05});
 doc.setFont('helvetica','normal');doc.setFontSize(8.2);doc.text(doc.splitTextToSize(safe(subtitle),108).slice(0,2),80,lines.length>1?23:20);
 if(dateText){doc.setFontSize(7.5);doc.text(safe(dateText),194,30,{align:'right'});}doc.setTextColor(23,32,51);
}
function footer(doc,page,total,version){
 const s=settings(doc),c=s.company||{};let domain='neustart-immocheck.de';try{if(c.website)domain=new URL(window.NICSettings.websiteUrl(c.website)).hostname.replace(/^www\./,'');}catch(_){}
 doc.setFont('helvetica','normal');doc.setFontSize(7.5);doc.setTextColor(100,110,125);doc.text(safe(domain),16,289);doc.text(version||defaults.version,105,289,{align:'center'});doc.text('Seite '+page+' von '+total,194,289,{align:'right'});
 if(c.name){doc.setFontSize(6.7);doc.text(doc.splitTextToSize(safe(c.name),95)[0],16,285);}
 if(page===total){doc.setFontSize(6.7);doc.text('Datenschutz · Haftungsausschluss',194,285,{align:'right'});}doc.setTextColor(23,32,51);
}
function legalBlocks(s){
 const S=window.NICSettings,source=S.legalSource(s,'haftungsausschluss',defaults.disclaimer||''),root=document.createElement('div');root.append(S.legalFragment(source,s));
 const blocks=[];
 function visit(node){
  if(node.nodeType===3){const text=node.textContent.replace(/\s+/g,' ').trim();if(text&&text!=='Hinweise zur Nutzung der Kalkulatoren und PDF-Berichte')blocks.push({text,bold:false});return;}
  if(node.nodeType!==1)return;const tag=node.tagName;
  if(/^H[1-6]$/.test(tag)){const text=node.textContent.trim();if(text&&!/^Haftungsausschluss(?:\s*\/\s*Disclaimer)?$/i.test(text))blocks.push({text,bold:true});return;}
  if(['P','LI','BLOCKQUOTE','TR'].includes(tag)){let text=node.textContent.trim();if(tag==='LI')text='- '+text;if(text&&text!=='Hinweise zur Nutzung der Kalkulatoren und PDF-Berichte')blocks.push({text,bold:false,align:node.style?.textAlign||'justify'});return;}
  for(const child of node.childNodes)visit(child);
 }
 for(const child of root.childNodes)visit(child);
 return blocks;
}
function disclaimer(doc){
 const blocks=legalBlocks(settings(doc));doc.addPage();header(doc,'Haftungsausschluss / Disclaimer','Hinweise zur Nutzung der Kalkulatoren und PDF-Berichte');let y=45;
 const drawHeader=()=>{doc.addPage();header(doc,'Haftungsausschluss / Disclaimer','Fortsetzung der rechtlichen Hinweise');y=45;};
 for(const block of blocks){
  doc.setFont('helvetica',block.bold?'bold':'normal');doc.setFontSize(block.bold?9.2:7.8);doc.setTextColor(...(block.bold?[15,23,42]:[71,85,105]));
  const lines=doc.splitTextToSize(safe(block.text),178),height=block.bold?4.6:3.8;
  if(y+Math.min(lines.length,3)*height>277)drawHeader();
  if(y+lines.length*height<=277){doc.text(lines,16,y,{align:block.bold?'left':(block.align||'justify'),maxWidth:178,lineHeightFactor:1.25});y+=lines.length*height;}
  else for(const line of lines){if(y+height>277)drawHeader();doc.text(line,16,y);y+=height;}
  y+=block.bold?1.2:5.5;
 }
 doc.setTextColor(23,32,51);
}
function model(v){
 const loan=Math.max(0,Math.min(1e9,Number(v.loan)||0)),interest=Number(v.interest)||0,repay=Number(v.repay)||0,extra=Number(v.extra)||0,years=Number(v.years)||10;
 const monthly=loan*(interest+repay)/1200,annualExtra=loan*extra/100;let balance=loan,interestTotal=0;const balances=[loan];
 for(let m=1;m<=years*12;m++){if(balance>0){const i=balance*interest/1200;interestTotal+=i;balance=Math.max(0,balance-Math.max(0,Math.min(balance,monthly-i)));if(m%12===0)balance=Math.max(0,balance-annualExtra);}if(m%12===0)balances.push(balance);}
 return {loan,interest,repay,extra,years,monthly,annualExtra,balance,interestTotal,paid:loan-balance,interestMonthly:loan*interest/1200,repayMonthly:loan*repay/1200,balances};
}
function financeOutlook(doc,m,values){
 doc.addPage();header(doc,'Finanzierungsrechner - Bericht','Anschlussfinanzierung und historische Hypothekenzinsen');
 doc.setFont('helvetica','bold');doc.setFontSize(13);doc.setTextColor(23,32,51);doc.text('4. Anschlussfinanzierung',16,45);
 doc.setFont('helvetica','normal');doc.setFontSize(8.2);doc.setTextColor(100,110,125);
 doc.text(doc.splitTextToSize('Wir können die Zinsen für die Zukunft nicht seriös vorhersagen. Wir können aber historische Schwankungen verwenden, um mögliche Belastungsszenarien zu simulieren.',178),16,52,{lineHeightFactor:1.3});
 [['Zinssatz fällt',-1.5],['Zinssatz stabil',0],['Zinssatz steigt',2]].forEach(([label,delta],i)=>{
  const x=16+i*60,rate=m.interest+delta;doc.setFillColor(247,249,252);doc.roundedRect(x,65,58,36,3,3,'F');
  doc.setFont('helvetica','normal');doc.setFontSize(9);doc.setTextColor(100,110,125);doc.text(label,x+3,72);
  doc.setFont('helvetica','bold');doc.setFontSize(12);doc.setTextColor(23,32,51);doc.text(money(m.balance*(rate+m.repay)/1200),x+3,81);
  doc.setFont('helvetica','normal');doc.setFontSize(7);doc.setTextColor(100,110,125);doc.text('pro Monat · '+(delta>0?'+':'')+String(delta).replace('.',',')+' Prozentpunkte',x+3,88);doc.text(percent(rate)+' Sollzins p. a.',x+3,95);
 });
 doc.setFontSize(7.4);doc.setTextColor(148,163,184);doc.text(doc.splitTextToSize('Annuitätendarlehen mit konstantem Sollzins und gleichbleibender Monatsrate während der ersten Zinsbindung. Die Anschlussrate wird aus der Restschuld, dem Szenariozins und der gewählten neuen Anfangstilgung berechnet. Keine Sondertilgungen, Gebühren oder Zinsänderungen während der jeweiligen Bindung berücksichtigt.',178),16,108,{lineHeightFactor:1.3});
 doc.setFont('helvetica','bold');doc.setFontSize(13);doc.setTextColor(23,32,51);doc.text('5. Hypothekenzinsen - rollierende 10 Jahre',16,135);
 doc.setFont('helvetica','normal');doc.setFontSize(7.8);doc.setTextColor(100,110,125);doc.text(doc.splitTextToSize('Bundesweiter durchschnittlicher Effektivzins für neue Wohnungsbaukredite mit über 1 bis 5 Jahren (SUD117) und über 5 bis 10 Jahren (SUD118) Zinsbindung.',178),16,142,{lineHeightFactor:1.25});
 const series=(Array.isArray(values.rateSeries)?values.rateSeries:[]).filter(r=>/^\d{4}-\d{2}$/.test(r.month)&&(Number.isFinite(r.five)||Number.isFinite(r.ten))).sort((a,b)=>a.month.localeCompare(b.month)).slice(-121);
 const colors=[[13,148,136],[99,102,241],[234,88,12]];
 ['1-5 Jahre','5-10 Jahre','Dein Sollzins'].forEach((label,i)=>{const x=16+i*59;doc.setDrawColor(...colors[i]);doc.setLineWidth(i===2?.74:.66);doc.setLineDashPattern(i===2?[2,1.5]:[],0);doc.line(x,157,x+8,157);doc.setLineDashPattern([],0);doc.setFont('helvetica',i===2?'bold':'normal');doc.setFontSize(8);doc.text(label,x+10,158);});
 doc.setFont('helvetica','normal');
 if(series.length){
  const all=series.flatMap(r=>[r.five,r.ten]).filter(Number.isFinite).concat(m.interest),low=Math.max(0,Math.floor(Math.min(...all)*2)/2-.5),high=Math.max(low+2,Math.ceil(Math.max(...all)*2)/2+.5);
  const left=31,right=190,top=168,bottom=236,X=i=>left+i/Math.max(1,series.length-1)*(right-left),Y=v=>bottom-(v-low)/(high-low)*(bottom-top);
  doc.setFontSize(7);
  for(let i=0;i<=4;i++){const v=low+(high-low)*i/4,y=Y(v);doc.setDrawColor(220,225,232);doc.setLineWidth(.2);doc.line(left,y,right,y);doc.text(percent(v),left-3,y+1,{align:'right'});}
  for(const [key,c] of [['five',colors[0]],['ten',colors[1]]]){doc.setDrawColor(...c);doc.setLineWidth(.66);for(let i=1;i<series.length;i++)if(Number.isFinite(series[i-1][key])&&Number.isFinite(series[i][key]))doc.line(X(i-1),Y(series[i-1][key]),X(i),Y(series[i][key]));}
  doc.setDrawColor(...colors[2]);doc.setLineWidth(.74);doc.setLineDashPattern([2,1.5],0);doc.line(left,Y(m.interest),right,Y(m.interest));doc.setLineDashPattern([],0);
  for(let i=0;i<series.length;i+=24)doc.text(series[i].month.slice(0,4),X(i),bottom+5,{align:'center'});
  doc.setFontSize(7.4);doc.text('Datenstand: '+series.at(-1).month.slice(5)+'.'+series.at(-1).month.slice(0,4),16,250);
 }else{doc.setFontSize(9);doc.text('Keine historischen Monatswerte verfügbar.',16,190);}
 doc.setFontSize(7.4);doc.setTextColor(100,110,125);doc.text(doc.splitTextToSize('Quelle: Deutsche Bundesbank, MFI-Zinsstatistik. Die Statistik zeigt Effektivzinsen; der Rechner kalkuliert mit dem eingestellten Sollzins. Der Vergleich dient der Orientierung und ist keine Zinsprognose.',178),16,258,{lineHeightFactor:1.3});
}

function financeDocument(values){
 const m=model(values),doc=create({unit:'mm',format:'a4'},'finance'),s=settings(doc);
 doc.setProperties({title:s.meta?.finance?.title||filename('finance').slice(0,-4),subject:s.meta?.finance?.description||'Finanzierung und Restschuld'});
 header(doc,'Finanzierungsrechner - Bericht','Darlehen, monatliche Kreditrate, Tilgung und Restschuld');
 doc.setFont('helvetica','bold');doc.setFontSize(13);doc.text('Wichtigste Ergebnisse auf einen Blick',16,45);
 doc.setFont('helvetica','normal');doc.setFontSize(8.2);doc.setTextColor(100,110,125);doc.text('Deine Finanzierung und die voraussichtliche Restschuld im Zusammenhang.',16,51);
 const boxes=[['Darlehenssumme',money(m.loan)],['Mtl. Kreditrate inkl. Tilgung',money(m.monthly)],['Restschuld nach '+m.years+' Jahren',money(m.balance)]];
 boxes.forEach(([label,value],i)=>{const x=16+i*60;doc.setFillColor(247,249,252);doc.roundedRect(x,56,58,26,3,3,'F');doc.setFont('helvetica','normal');doc.setFontSize(7);doc.setTextColor(100,110,125);doc.text(label,x+3,63);doc.setFont('helvetica','bold');doc.setFontSize(12);doc.setTextColor(23,32,51);doc.text(value,x+3,74);});
 let y=94;
 const section=title=>{doc.setFont('helvetica','bold');doc.setFontSize(13);doc.setTextColor(23,32,51);doc.text(title,16,y);y+=8;};
 const row=(label,value)=>{doc.setFont('helvetica','normal');doc.setFontSize(8.2);doc.setTextColor(100,110,125);doc.text(label,16,y);doc.setFont('helvetica','bold');doc.setTextColor(23,32,51);doc.text(value,194,y,{align:'right'});y+=6;};
 section('1. Deine Finanzierung');
 row('Darlehensbetrag',money(m.loan));row('Sollzins p. a.',percent(m.interest));row('Anfängliche Tilgung p. a.',percent(m.repay));row('Sondertilgung pro Jahr',money(m.annualExtra)+' ('+percent(m.extra)+')');row('Betrachtungszeitraum',m.years+' Jahre');
 y+=5;section('2. Monatliche Belastung und Ergebnis');
 row('Mtl. Kreditrate inkl. Tilgung',money(m.monthly));row('Zinsen zu Beginn pro Monat',money(m.interestMonthly));row('Tilgung zu Beginn pro Monat',money(m.repayMonthly));row('Gezahlte Zinsen im Betrachtungszeitraum',money(m.interestTotal));row('Getilgter Kreditbetrag inkl. Sondertilgung',money(m.paid));
 y+=6;section('3. Tilgungsverlauf');
 const top=y+2,bottom=top+34,left=22,right=190;doc.setDrawColor(225,229,236);doc.line(left,top,left,bottom);doc.line(left,bottom,right,bottom);doc.setDrawColor(13,148,136);doc.setLineWidth(.8);
 for(let i=1;i<m.balances.length;i++)doc.line(left+(i-1)/m.years*(right-left),bottom-m.balances[i-1]/Math.max(m.loan,1)*32,left+i/m.years*(right-left),bottom-m.balances[i]/Math.max(m.loan,1)*32);
 doc.setFont('helvetica','normal');doc.setFontSize(7);doc.setTextColor(100,110,125);doc.text('Start',left,bottom+5);doc.text('Jahr '+m.years,right,bottom+5,{align:'right'});
 y=bottom+13;doc.setFontSize(7.4);doc.text(doc.splitTextToSize('Modellrechnung mit konstantem Sollzins und konstanter Monatsrate. Sondertilgungen zusätzlich jeweils am Jahresende. Der Betrachtungszeitraum ist nicht mit der Zinsbindung gleichzusetzen.',178),16,y,{lineHeightFactor:1.2});
 financeOutlook(doc,m,values);disclaimer(doc);const total=doc.getNumberOfPages();for(let p=1;p<=total;p++){doc.setPage(p);footer(doc,p,total,defaults.version);}return doc;
}
async function exportFinance(values,download){
 if(window.NICAccess&&!await window.NICAccess.authorize(download?'pdfDownload':'pdfShare'))return;
 await prepare();if(!values.rateSeries?.length){try{const response=await fetch('/mortgage-rates.json',{cache:'no-store'});if(response.ok)values={...values,rateSeries:(await response.json()).series};}catch(err){console.warn('Historische Zinsdaten für den Bericht nicht verfügbar',err);}}const doc=financeDocument(values),name=filename('finance');
 if(download){doc.save(name);return;}
 const blob=doc.output('blob'),file=new File([blob],name,{type:'application/pdf'});
 if(navigator.canShare?.({files:[file]})&&navigator.share)await navigator.share({files:[file],title:name.slice(0,-4),text:name.slice(0,-4)});else{if(window.NICAccess&&!await window.NICAccess.authorize('pdfDownload'))return;doc.save(name);}
}
window.NICPDF={prepare,create,logo,header,footer,disclaimer,filename,financeDocument,exportFinance,model,legalBlocks};
})();
