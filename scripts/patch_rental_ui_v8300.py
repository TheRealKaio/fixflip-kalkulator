from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+' anchor missing')
    s=s.replace(old,new,1)

flip='''        <label class="deal-type-option" for="dealTypeFlip">
          <input type="radio" name="dealType" value="flip" id="dealTypeFlip">
          <span>
            <strong>Fix und Flip</strong>
            <small>Kauf, Sanierung und Verkauf</small>
          </span>
        </label>
        <button type="button" class="deal-type-option rent-tab-button" id="dealTypeRent" aria-pressed="false">
          <span class="rent-radio-dot" aria-hidden="true"></span>
          <span class="rent-tab-copy">
            <strong>Vermietung</strong>
            <small>Mietwohnung als Kapitalanlage prüfen</small>
          </span>
        </button>'''
rentfirst='''        <button type="button" class="deal-type-option rent-tab-button" id="dealTypeRent" aria-pressed="false">
          <span class="rent-radio-dot" aria-hidden="true"></span>
          <span class="rent-tab-copy">
            <strong>Vermietung</strong>
            <small>Mietwohnung als Kapitalanlage prüfen</small>
          </span>
        </button>
        <label class="deal-type-option" for="dealTypeFlip">
          <input type="radio" name="dealType" value="flip" id="dealTypeFlip">
          <span>
            <strong>Fix und Flip</strong>
            <small>Kauf, Sanierung und Verkauf</small>
          </span>
        </label>'''
rep(flip,rentfirst,'tab reorder')

old='''          <div class="field">
            <label>Einmalige Sanierung / Renovierung</label>
            <div class="input-wrap"><input id="rentRenovation" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>'''
new='''          <div class="field rent-reno-field">
            <label>Einmalige Sanierung / Renovierung <span class="hint">inkl. Puffer</span></label>
            <div class="rent-reno-input-row">
              <div class="input-wrap"><input id="rentRenovation" class="readonly-input" inputmode="decimal" value="0" readonly><span class="unit">€</span></div>
              <button class="plus-btn" id="rentOpenReno" type="button" aria-label="Sanierungsgewerke öffnen" aria-expanded="false" aria-controls="rentRenoPanel">+</button>
            </div>
          </div>'''
rep(old,new,'rental renovation field')

anchor='''        </div>
      </section>

      <section class="card">
        <h2>2. Laufende Vermietung</h2>'''
panel='''        </div>
        <div class="reno-inline-panel rent-reno-inline-panel" id="rentRenoPanel">
          <div class="reno-sheet">
            <div class="reno-head">
              <div>
                <h3>Sanierung aufteilen</h3>
                <p class="sub" style="margin:4px 0 0">Richtwerte erscheinen dezent als Vorschlag. Erst über den Button werden sie in die Berechnung übernommen.</p>
              </div>
              <div class="reno-head-actions">
                <button type="button" class="budget-apply-btn reno-suggestion-btn" id="rentApplyTradeSuggestions">Vorschlag übernehmen</button>
                <div class="reno-total-pill" id="rentRenoSheetTotal">0 €</div>
              </div>
            </div>
            <div class="reno-note"><strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €. Graue Werte sind unverbindliche Richtwerte. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen.</div>
            <div id="rentTradeList" class="trade-list"></div>
            <div class="quick-grid rent-reno-buffer-grid"><div class="field"><label>Sanierungs-Puffer</label><div class="input-wrap"><input id="rentRenoBuffer" inputmode="decimal" value="5.00"><span class="unit">%</span></div><div class="mini">Renovierungsaufschlag für Unerwartetes</div></div></div>
            <div class="reno-actions">
              <button class="reset-btn" id="rentResetTrades" type="button">Auf 0 zurücksetzen</button>
              <button class="save-reno-btn" id="rentSaveTrades" type="button">Übernehmen</button>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>2. Laufende Vermietung</h2>'''
rep(anchor,panel,'rental reno panel')

infos={
'Nettokaltmiete pro Monat':'Monatliche Miete ohne Betriebs- und Heizkosten. Sie ist die zentrale Einnahmegröße für die Renditeberechnung.',
'Hausgeld gesamt pro Monat':'Monatliche Zahlung an die Wohnungseigentümergemeinschaft. Nicht jeder Bestandteil kann auf den Mieter umgelegt werden.',
'Davon nicht umlagefähig':'Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet.',
'Mietausfall / Leerstand':'Sicherheitsabschlag für Zeiträume ohne Mieteinnahmen. Er reduziert die für die Kalkulation angesetzte Miete.',
'Verwaltung pro Monat':'Kosten für externe oder interne Verwaltung der vermieteten Wohnung.',
'Zusätzliche Instandhaltung':'Monatliche Rücklage für Reparaturen und Instandhaltung zusätzlich zu bereits im Hausgeld enthaltenen Beträgen.',
'Sonstige Vermieterkosten':'Weitere laufende Kosten, die nicht auf den Mieter umgelegt werden können und in keiner anderen Position enthalten sind.'}
for label,txt in infos.items():
    old=f'<label>{label}</label>'
    new=f'<label class="label-with-info"><span>{label}</span><button type="button" class="info-dot rent-info-dot" aria-label="Info zu {label}" data-info="{txt}">i</button></label>'
    rep(old,new,'info '+label)

css=r'''
<style id="rental-ui-v8300">
.app{max-width:630px}
.deal-type-row{align-items:stretch}
.deal-type-option,.rent-tab-button{box-sizing:border-box;min-height:78px;align-items:center;padding:12px 10px!important}
.deal-type-option>span:not(.rent-radio-dot),.rent-tab-copy{display:flex!important;flex-direction:column!important;justify-content:center!important;min-width:0}
.deal-type-option strong,.rent-tab-copy strong{font-size:14px!important;line-height:1.2!important;font-weight:700!important;color:#0f172a!important}
.deal-type-option small,.rent-tab-copy small{font-size:10.5px!important;line-height:1.25!important;font-weight:400!important;color:#64748b!important;margin-top:3px!important}
.rent-reno-input-row{display:grid;grid-template-columns:minmax(0,1fr) 50px;gap:8px;align-items:center}
.rent-reno-inline-panel{grid-column:1/-1;margin-top:10px}
.rent-reno-buffer-grid{margin-top:10px}
.label-with-info{display:flex!important;align-items:center;gap:6px;min-height:18px}
.info-dot{width:18px!important;height:18px!important;min-width:18px!important;min-height:18px!important;padding:0!important;border:1px solid #94a3b8!important;border-radius:50%!important;background:#fff!important;color:#475569!important;font-size:11px!important;font-weight:800!important;line-height:16px!important;text-align:center!important;cursor:pointer}
.rent-info-popover{position:fixed;z-index:99999;left:50%;bottom:24px;transform:translateX(-50%);width:min(420px,calc(100vw - 28px));background:#0f172a;color:#fff;border-radius:14px;padding:14px 16px;box-shadow:0 18px 48px rgba(15,23,42,.28);font-size:13px;line-height:1.45}
.rent-info-popover[hidden]{display:none!important}
@media (orientation:landscape) and (max-height:600px) and (max-width:1000px){
  .app{max-width:none!important;width:calc(100% - 10px)!important;margin:0 5px!important}
  main{max-width:none!important;width:100%!important}
}
</style>
'''
rep('</head>',css+'\n</head>','head css')

s=s.replace('''      if(sharePdf) sharePdf.style.display="none";
      if(savePdf) savePdf.style.display="none";''','''      if(sharePdf) sharePdf.style.display="";
      if(savePdf) savePdf.style.display="";
      document.querySelectorAll('input[name="dealType"]').forEach(function(input){ input.checked=false; });''',1)

s=s.replace('''    localStorage.setItem(PREFIX+"active","1");
    renderRent();''','''    localStorage.setItem(PREFIX+"active","1");
    try{ if(window.resetRentRenoV8300) window.resetRentRenoV8300(false); }catch(_err){}
    renderRent();''',1)

js=r'''
<script id="rental-ui-script-v8300">
(function(){
  const RP="ff_rent_reno_";
  const $r=id=>document.getElementById(id);
  const money=n=>new Intl.NumberFormat("de-DE",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(Number(n)||0);
  const num=v=>{let x=String(v??"").trim().replace(/\s/g,"");if(x.includes(",")&&x.includes(".")){x=x.lastIndexOf(",")>x.lastIndexOf(".")?x.replace(/\./g,"").replace(",","."):x.replace(/,/g,"");}else{x=x.replace(",",".");}x=x.replace(/[^0-9.-]/g,"");const n=Number(x);return Number.isFinite(n)?n:0;};
  const vals={}; const manual=new Set();
  function areaKey(h){return RP+"area_"+h.areaKey}
  function getArea(h){return h&&h.areaKey?num(localStorage.getItem(areaKey(h))||0):0}
  function suggestion(t){
    if(!t) return 0;
    if(t.mode==="sqm") return t.defaultOff?0:Math.max(0,Math.round(num($r("rentArea")?.value)*Number(t.rate||0)));
    const h=window.fixedTradeHints?fixedTradeHints[t.name]:null;
    return h&&h.rate&&h.areaKey?Math.max(0,Math.round(getArea(h)*h.rate)):0;
  }
  function load(){
    trades.forEach(t=>{const v=localStorage.getItem(RP+"trade_"+t.key); vals[t.key]=v===null?0:num(v); if(localStorage.getItem(RP+"manual_"+t.key)==="1") manual.add(t.key);});
    const b=localStorage.getItem(RP+"buffer"); if($r("rentRenoBuffer")) $r("rentRenoBuffer").value=b===null?"5.00":b;
  }
  function saveTrade(t){localStorage.setItem(RP+"trade_"+t.key,String(vals[t.key]||0));localStorage.setItem(RP+"manual_"+t.key,manual.has(t.key)?"1":"0")}
  function total(){const base=trades.reduce((a,t)=>a+(Number(vals[t.key])||0),0);const buffer=Math.max(0,num($r("rentRenoBuffer")?.value))/100;return Math.round(base*(1+buffer));}
  function sync(){const t=total();if($r("rentRenovation")){$r("rentRenovation").value=String(t);localStorage.setItem("ff_rent_rentRenovation",String(t));}if($r("rentRenoSheetTotal"))$r("rentRenoSheetTotal").textContent=money(t);}
  function render(){
    const list=$r("rentTradeList"); if(!list) return;
    const a=num($r("rentArea")?.value);
    const sqm=trades.filter(t=>t.mode==="sqm").sort((x,y)=>x.name.localeCompare(y.name,"de"));
    const fixed=trades.filter(t=>t.mode!=="sqm").sort((x,y)=>x.name.localeCompare(y.name,"de"));
    let html='<div class="trade-section-label">Nach Wohnfläche berechnete Vorschläge</div>';
    sqm.forEach(t=>{const sug=suggestion(t),act=Math.round(vals[t.key]||0);html+='<div class="trade-row trade-row-sqm"><div class="trade-top"><div><div class="trade-name">'+t.name+'</div><div class="trade-basis">'+t.rate+' €/m² × '+a.toLocaleString("de-DE")+' m²'+(t.defaultOff?' · optional':'')+'</div><div class="trade-auto">'+(act>0?'übernommener oder eigener Wert':(t.defaultOff?'optional · Standardwert 0 €':'grauer Wert = Vorschlag · Standardwert 0 €'))+'</div></div><div class="input-wrap"><input class="rent-trade-amount" data-trade="'+t.key+'" inputmode="decimal" value="'+(act>0?act:'')+'" placeholder="'+(sug>0?sug:'0')+'"><span class="unit">€</span></div></div></div>';});
    html+='<div class="trade-section-label">Pauschal / Stück</div>';
    fixed.forEach(t=>{const h=fixedTradeHints[t.name],av=h&&h.areaKey?getArea(h):0,sug=suggestion(t),act=Math.round(vals[t.key]||0);html+='<div class="trade-row trade-row-fixed"><div class="trade-top"><div class="trade-copy"><div class="trade-name">'+t.name+'</div><div class="trade-basis">'+(h?h.basis:(t.unit+' · individuell eintragen'))+'</div>'+(h&&h.auto?'<div class="trade-auto">'+h.auto+'</div>':'')+'</div><div class="trade-inputs-inline">'+(h&&h.areaKey?'<div class="input-wrap trade-area-input"><input class="rent-trade-area" data-area-key="'+h.areaKey+'" data-trade-key="'+t.key+'" inputmode="decimal" value="'+(av||'')+'" placeholder="0"><span class="unit">m²</span></div>':'')+'<div class="input-wrap trade-money-input"><input class="rent-trade-amount" data-trade="'+t.key+'" inputmode="decimal" value="'+(act>0?act:'')+'" placeholder="'+(sug>0?sug:'0')+'"><span class="unit">€</span></div></div></div></div>';});
    list.innerHTML=html;
    list.querySelectorAll('.rent-trade-amount').forEach(inp=>inp.addEventListener('input',()=>{const t=trades.find(x=>x.key===inp.dataset.trade);vals[inp.dataset.trade]=num(inp.value);manual.add(inp.dataset.trade);if(t)saveTrade(t);sync();}));
    list.querySelectorAll('.rent-trade-area').forEach(inp=>inp.addEventListener('input',()=>{const t=trades.find(x=>x.key===inp.dataset.tradeKey),h=t?fixedTradeHints[t.name]:null;if(h){localStorage.setItem(areaKey(h),String(num(inp.value)));if(!manual.has(t.key)) vals[t.key]=0;render();sync();}}));
    sync();
  }
  function reset(ask=true){if(ask&&!confirm('Möchtest du wirklich alle Sanierungswerte der Vermietung auf 0 zurücksetzen?'))return; trades.forEach(t=>{vals[t.key]=0;manual.delete(t.key);localStorage.removeItem(RP+'trade_'+t.key);localStorage.removeItem(RP+'manual_'+t.key);const h=fixedTradeHints[t.name];if(h&&h.areaKey)localStorage.removeItem(areaKey(h));});localStorage.removeItem(RP+'buffer');if($r('rentRenoBuffer'))$r('rentRenoBuffer').value='5.00';render();sync();}
  window.resetRentRenoV8300=reset;
  load(); render();
  $r('rentOpenReno')?.addEventListener('click',()=>{const p=$r('rentRenoPanel');const open=!p.classList.contains('show');p.classList.toggle('show',open);$r('rentOpenReno').textContent=open?'−':'+';$r('rentOpenReno').setAttribute('aria-expanded',open?'true':'false');if(open)render();});
  $r('rentApplyTradeSuggestions')?.addEventListener('click',()=>{trades.forEach(t=>{const v=suggestion(t);vals[t.key]=v;manual.delete(t.key);saveTrade(t)});render();sync();});
  $r('rentResetTrades')?.addEventListener('click',()=>reset(true));
  $r('rentSaveTrades')?.addEventListener('click',()=>{$r('rentRenoPanel')?.classList.remove('show');if($r('rentOpenReno')){$r('rentOpenReno').textContent='+';$r('rentOpenReno').setAttribute('aria-expanded','false')}});
  $r('rentRenoBuffer')?.addEventListener('input',e=>{localStorage.setItem(RP+'buffer',e.target.value);sync();});
  $r('rentArea')?.addEventListener('input',()=>{render();sync();});
  const pop=document.createElement('div');pop.className='rent-info-popover';pop.hidden=true;document.body.appendChild(pop);
  document.addEventListener('click',e=>{const b=e.target.closest?.('.rent-info-dot');if(b){e.preventDefault();e.stopPropagation();pop.textContent=b.dataset.info||'';pop.hidden=false;clearTimeout(pop._t);pop._t=setTimeout(()=>pop.hidden=true,7000);}else if(!pop.hidden){pop.hidden=true;}});
  function rentalActive(){return $r('rentSection')&&!$r('rentSection').classList.contains('mode-hidden');}
  function rn(id){return num($r(id)?.value)}
  function rentalModel(){const purchase=Math.max(0,rn('rentPurchase')),area=Math.max(0,rn('rentArea')),coldRent=Math.max(0,rn('rentColdRent')),renovation=Math.max(0,rn('rentRenovation')),vacancy=Math.min(.95,Math.max(0,rn('rentVacancy')/100)),nonAlloc=Math.max(0,rn('rentNonAlloc')),management=Math.max(0,rn('rentManagement')),maintenance=Math.max(0,rn('rentMaintenance')),other=Math.max(0,rn('rentOtherCosts')),equity=Math.max(0,rn('rentEquity')),interest=Math.max(0,rn('rentInterest')/100),repayment=Math.max(0,rn('rentRepayment')/100),notary=Math.max(0,rn('rentNotary')/100),broker=Math.max(0,rn('rentBroker')/100),state=$r('rentState')?.value||'Hamburg',transferRate=(states[state]||0)/100,transferTax=purchase*transferRate,acquisition=purchase*(notary+broker)+transferTax,totalInvestment=purchase+acquisition+renovation,equityUsed=Math.min(equity,totalInvestment),loan=Math.max(0,totalInvestment-equityUsed),debt=loan*(interest+repayment)/12,effective=coldRent*(1-vacancy),owner=nonAlloc+management+maintenance+other,cashflow=effective-owner-debt,annualGross=coldRent*12,noi=effective*12-owner*12;return{purchase,area,coldRent,renovation,vacancy,nonAlloc,management,maintenance,other,equity,equityUsed,interest,repayment,state,transferTax,acquisition,totalInvestment,loan,debt,effective,owner,cashflow,grossYield:purchase?annualGross/purchase:null,netYield:totalInvestment?noi/totalInvestment:null,cashOnCash:equityUsed?cashflow*12/equityUsed:null,factor:annualGross?purchase/annualGross:null,principal:loan*repayment,breakEven:(1-vacancy)?(owner+debt)/(1-vacancy):null};}
  function pct(v){return v==null||!Number.isFinite(v)?'–':new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(v*100)+' %'}
  function buildRentalPdf(){if(!window.jspdf||!window.jspdf.jsPDF)throw new Error('PDF-Bibliothek konnte nicht geladen werden.');const {jsPDF}=window.jspdf,doc=new jsPDF({unit:'mm',format:'a4'}),m=rentalModel(),L=16,R=194,W=178;drawPdfBrandHeader(doc,'Vermietung - Deal Report','Rentabilität, laufende Kosten und Finanzierung',new Date().toLocaleDateString('de-DE'));let y=43;const sec=t=>{doc.setFont('helvetica','bold');doc.setFontSize(13);doc.setTextColor(23,32,51);doc.text(pdfSafeText(t),L,y);y+=7};const row=(a,b)=>{doc.setFont('helvetica','normal');doc.setFontSize(8.5);doc.setTextColor(100,110,125);doc.text(pdfSafeText(a),L,y);doc.setFont('helvetica','bold');doc.setTextColor(23,32,51);doc.text(pdfSafeText(b),R,y,{align:'right'});y+=6};const box=(title,value,note)=>{doc.setFillColor(247,249,252);doc.setDrawColor(225,229,236);doc.roundedRect(L,y,W,22,3,3,'FD');doc.setFont('helvetica','normal');doc.setFontSize(7.5);doc.setTextColor(100,110,125);doc.text(pdfSafeText(title),L+5,y+6);doc.setFont('helvetica','bold');doc.setFontSize(13);doc.setTextColor(23,32,51);doc.text(pdfSafeText(value),L+5,y+13);if(note){doc.setFont('helvetica','normal');doc.setFontSize(6.8);doc.setTextColor(100,110,125);doc.text(pdfSafeText(note),R-5,y+13,{align:'right'});}y+=26};
    sec('Ergebnis auf einen Blick');box('Monatlicher Cashflow',money(m.cashflow),'vor Steuer');row('Bruttomietrendite',pct(m.grossYield));row('Nettomietrendite',pct(m.netYield));row('Rendite auf Eigenkapital',pct(m.cashOnCash));row('Kaufpreisfaktor',m.factor==null?'–':m.factor.toFixed(1).replace('.',',')+' ×');row('Break-even-Nettokaltmiete',m.breakEven==null?'–':money(m.breakEven)+' / Monat');y+=4;sec('Objekt und Investition');row('Kaufpreis',money(m.purchase));row('Wohnfläche',new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(m.area)+' m²');row('Nettokaltmiete',money(m.coldRent)+' / Monat');row('Sanierung inkl. Puffer',money(m.renovation));row('Kaufnebenkosten',money(m.acquisition));row('Gesamtinvestition',money(m.totalInvestment));y+=4;sec('Laufende Vermietung');row('Nicht umlagefähiges Hausgeld',money(m.nonAlloc)+' / Monat');row('Verwaltung',money(m.management)+' / Monat');row('Zusätzliche Instandhaltung',money(m.maintenance)+' / Monat');row('Sonstige Vermieterkosten',money(m.other)+' / Monat');row('Mietausfall / Leerstand',new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.vacancy*100)+' %');y+=4;sec('Finanzierung');row('Eigenkapital',money(m.equityUsed));row('Darlehen',money(m.loan));row('Zins p.a.',new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.interest*100)+' %');row('Tilgung p.a.',new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.repayment*100)+' %');row('Monatliche Kreditrate',money(m.debt));row('Tilgung / Vermögensaufbau',money(m.principal)+' / Jahr');doc.setFont('helvetica','normal');doc.setFontSize(7.5);doc.setTextColor(100,110,125);const note='Orientierungsrechnung ohne individuelle Steuer-, Rechts- oder Finanzierungsberatung. Einkommensteuer, Abschreibung, Mietsteigerungen und Wertentwicklung sind nicht vollständig berücksichtigt.';doc.text(doc.splitTextToSize(pdfSafeText(note),W),L,276);drawPdfBrandLogo(doc);drawPdfFooter(doc,1,1,'V8.300');return doc;}
  async function rentalPdf(kind){await preparePdfBrandLogo();const doc=buildRentalPdf(),name='Vermietung_Deal_Report_'+new Date().toISOString().slice(0,10)+'.pdf';if(kind==='save'){doc.save(name);return;}const blob=doc.output('blob'),file=new File([blob],name,{type:'application/pdf'});if(navigator.canShare&&navigator.canShare({files:[file]})&&navigator.share){await navigator.share({title:'Vermietung - Deal Report',text:'Meine Vermietungs-Kalkulation',files:[file]});}else{const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),15000);}}
  $r('sharePdf')?.addEventListener('click',e=>{if(!rentalActive())return;e.preventDefault();e.stopImmediatePropagation();rentalPdf('share').catch(err=>{console.error(err);alert('Das Vermietungs-PDF konnte nicht erstellt werden.');});},true);
  $r('savePdf')?.addEventListener('click',e=>{if(!rentalActive())return;e.preventDefault();e.stopImmediatePropagation();rentalPdf('save').catch(err=>{console.error(err);alert('Das Vermietungs-PDF konnte nicht gespeichert werden.');});},true);
})();
</script>
'''
rep('</body>',js+'\n</body>','body js')

s=s.replace('V8.299','V8.300')
s=s.replace('service-worker.js?v=8.299','service-worker.js?v=8.300')

required=['id="rental-ui-v8300"','id="rentRenoPanel"','id="rentApplyTradeSuggestions"','ff_rent_reno_','Vermietung - Deal Report','V8.300','service-worker.js?v=8.300']
missing=[x for x in required if x not in s]
if missing: raise SystemExit('V8.300 missing: '+', '.join(missing))
p.write_text(s,encoding='utf-8')
print('V8.300 patch applied')
