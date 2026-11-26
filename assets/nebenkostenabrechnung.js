(function(){
'use strict';
const SETTLEMENT_PATH=/\/nebenkostenabrechnung\/?$/.test(location.pathname);
if(!SETTLEMENT_PATH)return;
const objects=[
 {id:'harden',name:'WEG Hardenstraße',address:'Billhorner Mühlenweg 106 · 20539 Hamburg',units:12,rented:10,vacant:2,area:7754.38,mea:1000,heatingTotal:1884,unitList:[{name:'Wohnung 01 · EG links',area:68.4,mea:84,tenant:'Maria Beispiel',start:'01.04.2024',cold:680,operating:140,heating:90,heat:188.4},{name:'Wohnung 02 · EG rechts',area:72.1,mea:89,tenant:'Leerstand',start:'',cold:0,operating:0,heating:0,heat:0},{name:'Wohnung 03 · 1. OG links',area:68.4,mea:84,tenant:'Max Muster',start:'01.01.2023',cold:660,operating:130,heating:85,heat:160}]},
 {id:'marmoweg',name:'WEG Marmoweg',address:'Marmoweg 7 · 22395 Hamburg',units:6,rented:5,vacant:1,area:520.4,mea:100,heatingTotal:900,unitList:[{name:'Wohnung 01 · EG links',area:56.5,mea:16.67,tenant:'Thomas Muster',start:'01.06.2023',cold:620,operating:120,heating:80,heat:140},{name:'Wohnung 02 · EG rechts',area:62,mea:18.29,tenant:'Anna Beispiel',start:'01.03.2022',cold:640,operating:125,heating:85,heat:150},{name:'Wohnung 03 · 1. OG',area:56.5,mea:16.67,tenant:'Leerstand',start:'',cold:0,operating:0,heating:0,heat:0}]}
];
const keys=['Wohnfläche','Wohneinheit','MEA','Verbrauch','Direktzuordnung'];
const categories=['Umlagefähig','Nicht umlagefähig','Erhaltungsrücklage','Einnahme'];
const money=new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2});
const state={started:false,source:'manual',step:0,objectId:'harden',unitIndex:0,year:'2025',fileName:'',preview:'landlord',positions:[
 {name:'Heizkosten',category:'Umlagefähig',key:'Verbrauch',amount:1057.21},
 {name:'Hausreinigung',category:'Umlagefähig',key:'Wohnfläche',amount:18535.44},
 {name:'Verwalterhonorar',category:'Nicht umlagefähig',key:'MEA',amount:1240},
 {name:'Zuführung Erhaltungsrücklage',category:'Erhaltungsrücklage',key:'MEA',amount:723.23}
]};
const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const object=()=>objects.find(item=>item.id===state.objectId)||objects[0];
const unit=()=>object().unitList[state.unitIndex]||object().unitList[0];
const fmt=value=>money.format(Number(value)||0)+' €';
function amountFromInput(value){let s=String(value||'').trim().replace(/[^\d,.-]/g,'');if(s.includes(','))s=s.replace(/\./g,'').replace(',','.');return Number(s)||0}
function shareFor(position){
 const o=object(),u=unit();
 if(position.key==='Wohnfläche')return u.area/o.area;
 if(position.key==='Wohneinheit')return 1/o.units;
 if(position.key==='MEA')return u.mea/o.mea;
 if(position.key==='Verbrauch')return u.heat/o.heatingTotal;
 return 1;
}
function allocationRows(tenantOnly){
 return state.positions.filter(p=>!tenantOnly||p.category==='Umlagefähig').map(p=>{
  const share=shareFor(p);return {name:p.name,category:p.category,key:p.key,total:Number(p.amount)||0,share,unitAmount:Math.round((Number(p.amount)||0)*share*100)/100};
 });
}
function css(){
 if(document.getElementById('nicSettlementStyles'))return;
 const style=document.createElement('style');style.id='nicSettlementStyles';
 style.textContent='.nic-settlement-app{--settle-border:var(--nic-border,#e2e9e5);--settle-ink:var(--nic-design-ink,#263b3a);--settle-green:var(--nic-design-deep,#075c55);--settle-mint:var(--nic-design-mint,#ddece8);--settle-warm:var(--nic-design-warm,#f6f1e9);--settle-gold:var(--nic-highlight-bg,#fde68a);color:var(--settle-ink);font:inherit}.nic-settlement-app *{box-sizing:border-box}.nic-settlement-app h2,.nic-settlement-app h3{color:var(--settle-ink);margin-top:0}.nic-settlement-app h2{font-size:var(--nic-h2-font-size,20px)}.nic-settlement-app h3{font-size:var(--nic-h3-font-size,18px)}.nic-settle-card{background:#fff;border:1px solid var(--settle-border);border-radius:var(--nic-menu-radius,16px);padding:20px;min-width:0}.nic-settle-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.nic-settle-summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}.nic-settle-metric{border:1px solid var(--settle-border);border-radius:12px;padding:12px;background:#fbfcfc;min-width:0}.nic-settle-metric small{display:block;color:#687385;font-size:var(--nic-hint-font-size,14px)}.nic-settle-metric strong{display:block;margin-top:3px}.nic-settle-actions{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:20px}.nic-settle-btn{min-height:44px;border:1px solid var(--settle-green);border-radius:var(--nic-control-radius,10px);padding:10px 16px;background:#fff;color:var(--settle-green);font:inherit;font-weight:700;cursor:pointer}.nic-settle-btn:hover{filter:brightness(.96)}.nic-settle-next{min-width:230px;background:var(--settle-gold);border-color:var(--settle-gold);color:var(--nic-highlight-text,#172033)}.nic-settle-primary{background:var(--settle-green);color:#fff}.nic-settle-start{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:20px}.nic-settle-start button{min-height:150px;text-align:left;padding:22px}.nic-settle-start strong{display:block;font-size:var(--nic-h3-font-size,18px);margin-bottom:7px}.nic-settle-start span{display:block;color:#687385;font-weight:400}.nic-settlement-steps{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px;margin:18px 0 14px}.nic-settlement-step{border:1px solid var(--settle-border);border-radius:10px;padding:9px 8px;color:#687385;text-align:center;font-size:var(--nic-hint-font-size,14px);background:#fff}.nic-settlement-step[aria-current=step]{background:var(--settle-mint);border-color:var(--settle-green);color:var(--settle-green);font-weight:750}.nic-settle-panel{min-height:360px}.nic-settle-field label{display:block;margin-bottom:5px;color:#596674;font-size:var(--nic-subtext-font-size,16px)}.nic-settle-field input,.nic-settle-field select{width:100%;min-height:42px;border:1px solid #d8dfdc;border-radius:10px;background:#fff;padding:9px 11px;font:inherit;color:inherit}.nic-settle-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:13px}.nic-settle-full{grid-column:1/-1}.nic-settle-note{margin-top:12px;padding:12px 14px;border-left:3px solid var(--settle-green);border-radius:8px;background:#f1f8f6;font-size:var(--nic-hint-font-size,14px)}.nic-settle-list{display:grid;gap:10px}.nic-settle-position{display:grid;grid-template-columns:minmax(150px,1.4fr) minmax(130px,1fr) minmax(100px,.8fr) 38px;gap:8px;align-items:end;padding:12px 0;border-bottom:1px solid #edf0ef}.nic-settle-position .nic-settle-field{min-width:0}.nic-settle-delete{width:38px;height:42px;border:1px solid var(--settle-border);border-radius:9px;background:#fff;color:#8f3026;cursor:pointer}.nic-settle-rows{display:grid;gap:8px}.nic-settle-line{display:grid;grid-template-columns:minmax(140px,1.25fr) minmax(110px,1fr) repeat(3,minmax(80px,.8fr));gap:9px;align-items:center;padding:10px 8px;border-bottom:1px solid #edf0ef;font-size:var(--nic-subtext-font-size,16px)}.nic-settle-line.head{font-weight:700;color:#687385;font-size:var(--nic-hint-font-size,14px)}.nic-settle-table-wrap{width:100%;overflow-x:auto}.nic-settle-table{width:100%;border-collapse:collapse;font-size:12px}.nic-settle-table th,.nic-settle-table td{text-align:left;padding:7px 5px;border-bottom:1px solid #edf0ef;vertical-align:top}.nic-settle-table th{color:#596674}.nic-settle-paper{max-width:794px;margin:16px auto;padding:34px 38px;background:white;border:1px solid var(--settle-border);box-shadow:0 4px 18px rgba(23,32,51,.07);min-height:900px;color:#172033}.nic-settle-paper h2{color:#075c55}.nic-settle-paper-head{display:flex;justify-content:space-between;gap:16px;border-bottom:2px solid #075c55;padding-bottom:16px;margin-bottom:18px}.nic-settle-paper-foot{border-top:1px solid #d8dfdc;margin-top:30px;padding-top:12px;font-size:12px}.nic-settle-empty{color:#687385}.nic-settlement-app input[type=file]{max-width:100%}@media(max-width:850px){.nic-settle-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.nic-settle-grid{grid-template-columns:1fr}.nic-settle-position{grid-template-columns:repeat(2,minmax(0,1fr))}.nic-settle-line{grid-template-columns:minmax(100px,1fr) minmax(90px,1fr) repeat(3,minmax(60px,.8fr));gap:5px;padding:8px 4px;font-size:12px}.nic-settle-paper{padding:24px 18px;min-height:0}}@media(max-width:560px){.nic-settle-start{grid-template-columns:1fr}.nic-settle-start button{min-height:104px}.nic-settlement-steps{gap:4px}.nic-settlement-step{padding:7px 3px;font-size:10px;line-height:1.25}.nic-settle-fields{grid-template-columns:1fr}.nic-settle-summary{gap:7px}.nic-settle-metric{padding:9px}.nic-settle-actions{align-items:stretch}.nic-settle-actions .nic-settle-btn{min-width:0;flex:1;padding:9px 8px}.nic-settle-line{grid-template-columns:minmax(76px,1fr) minmax(80px,1fr) repeat(3,minmax(48px,.75fr));font-size:10px;gap:3px;padding:7px 1px}.nic-settle-position{grid-template-columns:1fr 1fr}.nic-settle-paper{padding:18px 10px}.nic-settle-table{font-size:9px}.nic-settle-table th,.nic-settle-table td{padding:5px 2px}}@media print{@page{size:A4 portrait;margin:12mm}body.nic-settlement-printing *{visibility:hidden!important}body.nic-settlement-printing .nic-settle-paper,body.nic-settlement-printing .nic-settle-paper *{visibility:visible!important}body.nic-settlement-printing .nic-settle-paper{position:absolute;inset:0 auto auto 0;width:186mm;max-width:none;min-height:0;margin:0;padding:0;border:0;box-shadow:none}body.nic-settlement-printing .nic-settle-paper-foot{position:fixed;bottom:0;left:0;right:0}}';
 document.head.appendChild(style);
}
let landingView=null;
function normalizedText(node){return (node&&node.innerText||'').replace(/\\s+/g,' ').trim().toLocaleLowerCase('de-DE')}
function startWizard(source,root){
 state.source=source;state.started=true;state.step=0;
 landingView.hidden=true;root.hidden=false;render(root);
 root.scrollIntoView({behavior:'smooth',block:'start'});
}
function mount(){
 if(!SETTLEMENT_PATH)return;
 const host=document.getElementById('nicContentView');
 if(!host||host.querySelector('.nic-settlement-app'))return;
 css();
 landingView=document.createElement('div');
 landingView.className='nic-settle-landing';
 while(host.firstChild)landingView.appendChild(host.firstChild);
 host.appendChild(landingView);
 const root=document.createElement('div');
 root.className='nic-settlement-app';
 root.setAttribute('aria-live','polite');
 root.hidden=true;
 host.appendChild(root);
 root.addEventListener('click',handleClick);
 root.addEventListener('change',handleChange);
 host.addEventListener('click',event=>{
  const control=event.target.closest('a,button,[role="button"]');
  if(!control||!landingView.contains(control))return;
  const label=normalizedText(control);
  const source=label.includes('weg-abrechnung hochladen')?'weg':label.includes('manuelle erfassung')?'manual':'';
  if(!source)return;
  event.preventDefault();
  startWizard(source,root);
 });
 const wired=[...landingView.querySelectorAll('a,button,[role="button"]')].some(control=>{
  const label=normalizedText(control);
  return label.includes('weg-abrechnung hochladen')||label.includes('manuelle erfassung');
 });
 if(!wired){
  const launches=document.createElement('section');
  launches.className='nic-settle-card nic-settle-launches';
  launches.innerHTML='<h2>Abrechnung starten</h2><p>Wähle den passenden Einstieg für deine Mieterabrechnung.</p>'+startView();
  landingView.appendChild(launches);
 }
}
function heading(title,description){return '<div class="nic-settle-card"><h2>'+escapeHtml(title)+'</h2><p>'+escapeHtml(description)+'</p></div>'}
function startView(){
 return '<section class="nic-settle-card"><h2>Jahresabrechnung starten</h2><p>Wähle, wie du die Betriebskosten für deine Wohnung erfassen möchtest.</p><div class="nic-settle-start"><button type="button" class="nic-settle-btn" data-start="weg"><strong>WEG-Abrechnung hochladen</strong><span>Fertige Jahresabrechnung als Beleg hinzufügen</span></button><button type="button" class="nic-settle-btn" data-start="manual"><strong>Manuelle Erfassung</strong><span>Kosten und Verteilung Schritt für Schritt selbst eintragen</span></button></div><p class="nic-settle-note">Deine Abrechnungen werden in dieser Testversion nicht dauerhaft gespeichert. Verwende bitte keine echten Mieterdaten.</p></section>';
}
function stepHeader(){
 const labels=['Objekt','Belege','Positionen','Verteilung','Vorschau'];
 return '<div class="nic-settle-card"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><div><h2 style="margin-bottom:2px">Abrechnung erstellen</h2><div class="nic-settle-empty">'+(state.source==='weg'?'WEG-Abrechnung hochladen':'Manuelle Erfassung')+' · Abrechnungsjahr '+escapeHtml(state.year)+'</div></div><button class="nic-settle-btn" type="button" data-action="home">Zurück zum Start</button></div><div class="nic-settlement-steps">'+labels.map((label,i)=>'<div class="nic-settlement-step" aria-current="'+(i===state.step?'step':'false')+'"><b>'+(i+1)+'</b> · '+label+'</div>').join('')+'</div></div>';
}
function objectView(){
 const o=object(),u=unit();
 return '<section class="nic-settle-card nic-settle-panel"><h3>Objekt und Wohneinheit</h3><div class="nic-settle-fields"><div class="nic-settle-field"><label for="settleObject">Objekt / WEG auswählen</label><select id="settleObject" data-field="object">'+objects.map(item=>'<option value="'+item.id+'" '+(item.id===o.id?'selected':'')+'>'+escapeHtml(item.name)+'</option>').join('')+'</select></div><div class="nic-settle-field"><label for="settleUnit">Wohneinheit</label><select id="settleUnit" data-field="unit">'+o.unitList.map((item,i)=>'<option value="'+i+'" '+(i===state.unitIndex?'selected':'')+'>'+escapeHtml(item.name)+'</option>').join('')+'</select></div><div class="nic-settle-field nic-settle-full"><label>Objektanschrift</label><input readonly value="'+escapeHtml(o.address)+'"></div><div class="nic-settle-field"><label>Abrechnungsjahr</label><input data-field="year" value="'+escapeHtml(state.year)+'" inputmode="numeric"></div><div class="nic-settle-field"><label>Abrechnungszeitraum</label><input value="01.01.'+escapeHtml(state.year)+' – 31.12.'+escapeHtml(state.year)+'" readonly></div></div><div class="nic-settle-summary"><div class="nic-settle-metric"><small>Wohneinheiten</small><strong>'+o.units+'</strong></div><div class="nic-settle-metric"><small>Aktuell vermietet</small><strong>'+o.rented+'</strong></div><div class="nic-settle-metric"><small>Wohnfläche gesamt</small><strong>'+fmt(o.area)+' m²</strong></div><div class="nic-settle-metric"><small>MEA gesamt</small><strong>'+o.mea+'</strong></div></div><h3>Ausgewählte Wohnung</h3><div class="nic-settle-grid"><div class="nic-settle-field"><label>Wohnfläche</label><input readonly value="'+money.format(u.area)+' m²"></div><div class="nic-settle-field"><label>Eigentumsanteil</label><input readonly value="'+money.format(u.mea)+' / '+o.mea+' MEA"></div><div class="nic-settle-field"><label>Mieter/in</label><input readonly value="'+escapeHtml(u.tenant)+'"></div><div class="nic-settle-field"><label>Mietbeginn</label><input readonly value="'+escapeHtml(u.start||'— Leerstand')+'"></div></div><div class="nic-settle-note"><b>Kontakte</b><br>Vermieter/in: [Kontaktdaten aus dem Objekt] · Mieter/in: '+escapeHtml(u.tenant)+'<br>Kontaktrollen und Bankverbindungen werden in der Stammdatenverwaltung hinterlegt.</div></section>';
}
function documentsView(){
 return '<section class="nic-settle-card nic-settle-panel"><h3>Belege hinzufügen</h3><p>Füge die WEG-Jahresabrechnung oder weitere Unterlagen hinzu. Die Dateien bleiben in dieser Testversion lokal und werden nicht an einen Server übertragen.</p><div class="nic-settle-fields"><div class="nic-settle-field nic-settle-full"><label for="settleFiles">PDF- oder Bildbelege</label><input id="settleFiles" type="file" accept=".pdf,image/*" multiple data-field="files"></div><div class="nic-settle-field"><label for="settleDocumentType">Belegart</label><select id="settleDocumentType"><option>WEG-Jahresabrechnung</option><option>Heizkostenabrechnung</option><option>Wasserabrechnung</option><option>Sonstiger Beleg</option></select></div><div class="nic-settle-field"><label>Gewählte Erfassung</label><input readonly value="'+(state.source==='weg'?'WEG-Abrechnung hochladen':'Manuelle Erfassung')+'"></div></div><div class="nic-settle-note">'+(state.fileName?'Datei ausgewählt: <b>'+escapeHtml(state.fileName)+'</b>':'Noch keine Datei ausgewählt.')+'<br>Die automatische Texterkennung und Betragsübernahme ist in dieser Testversion noch nicht angebunden. Erkannte Positionen werden im nächsten Schritt geprüft und können ergänzt werden.</div></section>';
}
function positionsView(){
 return '<section class="nic-settle-card nic-settle-panel"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px"><div><h3>Kostenpositionen</h3><p>Trenne umlagefähige Kosten, nicht umlagefähige Kosten, Rücklage und Einnahmen.</p></div><button type="button" class="nic-settle-btn" data-action="add-position">＋ Position hinzufügen</button></div><div class="nic-settle-list">'+state.positions.map((p,i)=>'<article class="nic-settle-position"><div class="nic-settle-field"><label>Einzelposition</label><input data-pos="'+i+'" data-col="name" value="'+escapeHtml(p.name)+'"></div><div class="nic-settle-field"><label>Kategorie</label><select data-pos="'+i+'" data-col="category">'+categories.map(c=>'<option '+(c===p.category?'selected':'')+'>'+c+'</option>').join('')+'</select></div><div class="nic-settle-field"><label>Gesamtbetrag</label><input data-pos="'+i+'" data-col="amount" inputmode="decimal" value="'+money.format(Number(p.amount)||0)+' €"></div><button type="button" class="nic-settle-delete" aria-label="Position löschen" data-action="delete-position" data-index="'+i+'">×</button></article>').join('')+'</div><div class="nic-settle-note">Geldbeträge werden in der Vorschau kaufmännisch auf zwei Nachkommastellen dargestellt. Rundungsreste bleiben in dieser Testversion sichtbar in der Summenbildung.</div></section>';
}
function distributionView(){
 const rows=allocationRows(false);
 return '<section class="nic-settle-card nic-settle-panel"><h3>Verteilung je Position</h3><p>Wähle für jede Kostenposition den passenden Schlüssel. Die Mieteransicht enthält nur als umlagefähig markierte Positionen.</p><div class="nic-settle-rows"><div class="nic-settle-line head"><span>Position / Kategorie</span><span>Verteilerschlüssel</span><span>Gesamt</span><span>Anteil</span><span>Wohnung</span></div>'+rows.map((r,i)=>'<div class="nic-settle-line"><span><b>'+escapeHtml(r.name)+'</b><br><small>'+escapeHtml(r.category)+'</small></span><span><select data-pos="'+i+'" data-col="key">'+keys.map(k=>'<option '+(k===r.key?'selected':'')+'>'+k+'</option>').join('')+'</select></span><span>'+fmt(r.total)+'</span><span>'+money.format(r.share*100)+' %</span><span><b>'+fmt(r.unitAmount)+'</b></span></div>').join('')+'</div><div class="nic-settle-summary"><div class="nic-settle-metric"><small>Umlagefähige Positionen</small><strong>'+fmt(rows.filter(r=>r.category==='Umlagefähig').reduce((a,r)=>a+r.unitAmount,0))+'</strong></div><div class="nic-settle-metric"><small>Nicht umlagefähig</small><strong>'+fmt(rows.filter(r=>r.category==='Nicht umlagefähig').reduce((a,r)=>a+r.unitAmount,0))+'</strong></div><div class="nic-settle-metric"><small>Erhaltungsrücklage</small><strong>'+fmt(rows.filter(r=>r.category==='Erhaltungsrücklage').reduce((a,r)=>a+r.unitAmount,0))+'</strong></div><div class="nic-settle-metric"><small>Summe Eigentümeranteil</small><strong>'+fmt(rows.reduce((a,r)=>a+r.unitAmount,0))+'</strong></div></div></section>';
}
function previewView(){
 const tenant=state.preview==='tenant',rows=allocationRows(tenant);
 const total=rows.reduce((sum,row)=>sum+row.unitAmount,0);
 return '<section class="nic-settle-card"><div class="nic-settle-actions" style="margin-top:0"><div><h3>Abrechnungsvorschau</h3><p>Wähle die vollständige Vermietervorschau oder die umlagefähige Mietervorschau.</p></div><div><button type="button" class="nic-settle-btn '+(!tenant?'nic-settle-primary':'')+'" data-preview="landlord">Vermieter</button> <button type="button" class="nic-settle-btn '+(tenant?'nic-settle-primary':'')+'" data-preview="tenant">Mieter</button></div></div><article class="nic-settle-paper"><div class="nic-settle-paper-head"><div><h2>Nebenkostenabrechnung '+escapeHtml(state.year)+'</h2><b>'+escapeHtml(tenant?'Mietervorschau · '+unit().name:'Vermietervorschau · vollständige Abrechnung')+'</b><p>'+escapeHtml(object().name)+' · '+escapeHtml(object().address)+'</p></div><div><b>Abrechnungszeitraum</b><br>01.01.'+escapeHtml(state.year)+' – 31.12.'+escapeHtml(state.year)+'</div></div><p>'+escapeHtml(tenant?'Umlagefähige Betriebskosten und dein Anteil.':'Alle Abrechnungspositionen für die Eigentümerübersicht.')+'</p><div class="nic-settle-table-wrap"><table class="nic-settle-table"><thead><tr><th>Einzelposition</th><th>Kategorie</th><th>Verteilerschlüssel</th><th>Gesamtbetrag</th><th>Wohnungsanteil</th><th>Betrag Wohnung</th></tr></thead><tbody>'+rows.map(r=>'<tr><td>'+escapeHtml(r.name)+'</td><td>'+escapeHtml(r.category)+'</td><td>'+escapeHtml(r.key)+'</td><td>'+fmt(r.total)+'</td><td>'+money.format(r.share*100)+' %</td><td><b>'+fmt(r.unitAmount)+'</b></td></tr>').join('')+'</tbody><tfoot><tr><th colspan="5">Summe dieser Vorschau</th><th>'+fmt(total)+'</th></tr></tfoot></table></div><p class="nic-settle-paper-foot">Vermieter/in · [Name und Anschrift] · Bankverbindung · [IBAN] · [BIC]<br>Beispielvorschau. Vorauszahlungen, Zeitraumwechsel und gesetzliche Prüfung werden in der finalen Abrechnung ergänzt.</p></article><div class="nic-settle-actions"><button type="button" class="nic-settle-btn" data-action="back">← Zur Verteilung</button><button type="button" class="nic-settle-btn nic-settle-next" data-action="print">Drucken / PDF</button></div></section>';
}
function render(root){
 if(!root.isConnected)return;
 if(!state.started){root.innerHTML=startView();return}
 const views=[objectView,documentsView,positionsView,distributionView,previewView];
 root.innerHTML=stepHeader()+views[state.step]().replace('<section class="nic-settle-card nic-settle-panel">','<section class="nic-settle-card nic-settle-panel">')+(state.step<4?'<div class="nic-settle-actions"><button type="button" class="nic-settle-btn" data-action="back">← Zurück</button><button type="button" class="nic-settle-btn nic-settle-next" data-action="next">'+(state.step===3?'Vorschau anzeigen':'Weiter zu '+['Belege','Positionen','Verteilung','Vorschau'][state.step])+' →</button></div>':'');
}
function handleClick(event){
 const button=event.target.closest('button');if(!button)return;
 if(button.dataset.start){startWizard(button.dataset.start,button.closest('.nic-settlement-app'));return}
 const root=button.closest('.nic-settlement-app');if(!root)return;
 if(button.dataset.preview){state.preview=button.dataset.preview;render(root);return}
 if(button.dataset.action==='home'){root.hidden=true;if(landingView)landingView.hidden=false;state.started=false;state.step=0;landingView?.scrollIntoView({behavior:'smooth',block:'start'})}
 else if(button.dataset.action==='next'){state.step=Math.min(4,state.step+1);render(root)}
 else if(button.dataset.action==='back'){state.step=Math.max(0,state.step-1);render(root)}
 else if(button.dataset.action==='add-position'){state.positions.push({name:'Neue Position',category:'Umlagefähig',key:'Wohnfläche',amount:0});render(root)}
 else if(button.dataset.action==='delete-position'){state.positions.splice(Number(button.dataset.index),1);render(root)}
 else if(button.dataset.action==='print'){document.body.classList.add('nic-settlement-printing');window.print();window.addEventListener('afterprint',()=>document.body.classList.remove('nic-settlement-printing'),{once:true})}
}
function handleChange(event){
 const el=event.target,root=el.closest('.nic-settlement-app');if(!root)return;
 if(el.dataset.field==='object'){state.objectId=el.value;state.unitIndex=0;render(root)}
 else if(el.dataset.field==='unit'){state.unitIndex=Number(el.value)||0;render(root)}
 else if(el.dataset.field==='year'){state.year=el.value.replace(/[^\d]/g,'').slice(0,4)||'2025';render(root)}
 else if(el.dataset.field==='files'){state.fileName=Array.from(el.files||[]).map(f=>f.name).join(', ');render(root)}
 else if(el.dataset.pos!==undefined){const i=Number(el.dataset.pos),col=el.dataset.col;if(state.step===2){state.positions[i][col]=col==='amount'?amountFromInput(el.value):el.value;render(root)}else if(state.step===3&&col==='key'){state.positions[i].key=el.value;render(root)}}
}
function onNavigation(){if(SETTLEMENT_PATH)mount()}
function observe(){
 const observer=new MutationObserver(()=>{if(SETTLEMENT_PATH&&document.getElementById('nicContentView')&&!document.querySelector('.nic-settlement-app'))mount()});
 if(document.body)observer.observe(document.body,{childList:true,subtree:true});
 window.addEventListener('popstate',onNavigation);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{mount();observe()},{once:true});else{mount();observe()}
})();