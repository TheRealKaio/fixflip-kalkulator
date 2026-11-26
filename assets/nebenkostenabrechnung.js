(function(){
  'use strict';
  if(!/\/nebenkostenabrechnung\/?$/.test(location.pathname))return;

  const state={
    open:false,source:'',step:0,fileName:'',file:null,year:'',propertyName:'',street:'',zip:'',city:'',
    totalArea:'',unitCount:'',totalMea:'',unitName:'',unitArea:'',unitMea:'',totalConsumption:'',unitConsumption:'',
    ownerName:'',ownerAddress:'',tenantName:'',tenantAddress:'',rentStart:'',rentEnd:'',advance:'',
    positions:[]
  };
  const categories=['Umlagefähig','Nicht umlagefähig','Erhaltungsrücklage','Einnahme','Prüfbedürftig'];
  const keys=['Wohnfläche','Wohneinheit','MEA','Verbrauch','Direktzuordnung'];
  const money=new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2});
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const numeric=value=>{let s=String(value??'').trim().replace(/[^\d,.-]/g,'');if(s.includes(','))s=s.replace(/\./g,'').replace(',','.');const n=Number(s);return Number.isFinite(n)?n:0};
  const fmt=value=>money.format(Number(value)||0)+' €';
  let host=null,landing=null,root=null;

  function styles(){
    if(document.getElementById('nicSettlementWorkspaceStyles'))return;
    const style=document.createElement('style');style.id='nicSettlementWorkspaceStyles';
    style.textContent=`
      .nic-settlement-landing{display:block}
      .nic-settle-launch{margin:26px auto 4px;display:flex;justify-content:center}
      .nic-settle-launch button{min-height:52px;padding:13px 26px;border:0;border-radius:12px;background:#075c55;color:#fff;font:700 16px/1.3 system-ui,sans-serif;cursor:pointer;box-shadow:0 5px 16px rgba(7,92,85,.16)}
      .nic-settlement-root[hidden],.nic-settlement-landing[hidden]{display:none!important}
      .nic-settlement-root{--ss-green:#075c55;--ss-mint:#e8f2ef;--ss-line:#dce5e1;--ss-muted:#687385;--ss-ink:#172033;color:var(--ss-ink);width:100%;min-height:calc(100vh - 72px);background:#f4f6f5;font:inherit}
      .nic-settlement-root *{box-sizing:border-box}
      .nic-settle-apphead{height:58px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 24px;background:#fff;border-bottom:1px solid var(--ss-line)}
      .nic-settle-appbrand{display:flex;align-items:center;gap:10px;color:var(--ss-green);font-weight:800;font-size:15px}
      .nic-settle-appmark{width:30px;height:30px;display:grid;place-items:center;border:2px solid var(--ss-green);border-radius:9px 9px 9px 2px}
      .nic-settle-backlink{border:0;background:transparent;color:var(--ss-green);font:650 13px/1.4 system-ui,sans-serif;cursor:pointer;min-height:42px}
      .nic-settle-layout{display:grid;grid-template-columns:230px minmax(0,1fr);min-height:calc(100vh - 130px)}
      .nic-settle-sidebar{padding:20px 14px;background:#fff;border-right:1px solid var(--ss-line)}
      .nic-settle-sidebar-title{padding:0 10px 12px;color:#7b8783;font-size:11px;font-weight:750;letter-spacing:.08em;text-transform:uppercase}
      .nic-settle-nav{display:grid;gap:5px}
      .nic-settle-nav button{width:100%;min-height:42px;padding:10px;text-align:left;border:0;border-radius:9px;background:transparent;color:#44524f;font:600 13px/1.35 system-ui,sans-serif;cursor:pointer}
      .nic-settle-nav button:hover,.nic-settle-nav button[aria-current=page]{background:var(--ss-mint);color:var(--ss-green)}
      .nic-settle-sidebar-note{margin:22px 8px 0;padding:12px;border-radius:10px;background:#f7f9f8;color:var(--ss-muted);font-size:11px;line-height:1.5}
      .nic-settle-work{width:100%;max-width:1280px;margin:0 auto;padding:28px clamp(18px,3.5vw,48px) 44px}
      .nic-settle-crumb{margin-bottom:7px;color:#7d8985;font-size:12px}
      .nic-settle-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}
      .nic-settle-work h1{margin:0 0 6px;color:var(--ss-ink);font-size:clamp(23px,2.2vw,30px);line-height:1.2;letter-spacing:-.02em}
      .nic-settle-lead{margin:0 0 20px;color:var(--ss-muted);font-size:14px;line-height:1.5}
      .nic-settle-status{flex:0 0 auto;padding:5px 9px;border-radius:99px;background:#eef2f0;color:#687385;font-size:11px;font-weight:700}
      .nic-settle-progress{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7px;margin:0 0 6px}
      .nic-settle-progress span{height:5px;border-radius:99px;background:#dfe6e3}
      .nic-settle-progress span.active{background:var(--ss-green)}
      .nic-settle-progress-labels{display:flex;justify-content:space-between;gap:8px;margin:0 0 19px;color:#75817d;font-size:11px}
      .nic-settle-progress-labels .active{color:var(--ss-green);font-weight:750}
      .nic-settle-card{margin:0 0 14px;padding:22px;background:#fff;border:1px solid var(--ss-line);border-radius:15px;min-width:0}
      .nic-settle-card h2{margin:0 0 7px;font-size:19px;line-height:1.3}
      .nic-settle-card h3{margin:0 0 12px;font-size:16px;line-height:1.3}
      .nic-settle-card>p{margin:0 0 17px;color:var(--ss-muted);font-size:13px;line-height:1.5}
      .nic-settle-choices{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
      .nic-settle-choice{min-height:132px;padding:18px;text-align:left;border:1px solid var(--ss-line);border-radius:12px;background:#fff;color:var(--ss-ink);cursor:pointer}
      .nic-settle-choice:hover,.nic-settle-choice.selected{border-color:var(--ss-green);box-shadow:0 0 0 2px rgba(7,92,85,.09);background:#fbfdfc}
      .nic-settle-choice-icon{width:34px;height:34px;margin-bottom:10px;display:grid;place-items:center;border-radius:10px;background:var(--ss-mint);color:var(--ss-green);font-size:18px}
      .nic-settle-choice strong,.nic-settle-choice span{display:block}
      .nic-settle-choice strong{margin-bottom:5px;font-size:14px}
      .nic-settle-choice span{color:var(--ss-muted);font-size:12px;line-height:1.45}
      .nic-settle-filebox{display:none;margin-top:13px;padding:15px;border:1px dashed #a8c3ba;border-radius:11px;background:#f7fbfa}
      .nic-settle-filebox.visible{display:block}
      .nic-settle-filebox input{max-width:100%;font:inherit}
      .nic-settle-note{margin-top:14px;padding:12px 14px;border-left:3px solid var(--ss-green);border-radius:7px;background:#f1f8f6;color:#50605c;font-size:12px;line-height:1.55}
      .nic-settle-empty{padding:16px;border:1px dashed #cbd8d3;border-radius:11px;background:#fafcfb;color:var(--ss-muted);font-size:13px;line-height:1.5}
      .nic-settle-empty strong{display:block;margin-bottom:4px;color:#394743}
      .nic-settle-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px 16px}
      .nic-settle-field{min-width:0}
      .nic-settle-field label{display:block;margin-bottom:5px;color:#53615d;font-size:12px;font-weight:700}
      .nic-settle-field input,.nic-settle-field select{width:100%;min-height:42px;padding:9px 11px;border:1px solid #d5dfdb;border-radius:9px;background:#fff;color:var(--ss-ink);font:14px/1.3 system-ui,sans-serif}
      .nic-settle-field input::placeholder{color:#9ba5a1}
      .nic-settle-field small{display:block;margin-top:4px;color:var(--ss-muted);font-size:11px;line-height:1.4}
      .nic-settle-full{grid-column:1/-1}
      .nic-settle-section{margin-top:20px;padding-top:17px;border-top:1px solid #edf0ef}
      .nic-settle-actions{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:20px}
      .nic-settle-btn{min-height:44px;padding:10px 15px;border:1px solid #cbd8d3;border-radius:9px;background:#fff;color:#40504c;font:700 13px/1.3 system-ui,sans-serif;cursor:pointer}
      .nic-settle-btn.primary{min-width:200px;border-color:var(--ss-green);background:var(--ss-green);color:#fff}
      .nic-settle-btn.gold{border-color:#e5ba36;background:#f6c944;color:#302600}
      .nic-settle-btn:disabled{opacity:.45;cursor:default}
      .nic-settle-position{display:grid;grid-template-columns:minmax(140px,1.3fr) minmax(125px,1fr) minmax(130px,1fr) minmax(95px,.8fr) 38px;gap:9px;align-items:end;padding:12px 0;border-bottom:1px solid #edf0ef}
      .nic-settle-position-head{display:grid;grid-template-columns:minmax(140px,1.3fr) minmax(125px,1fr) minmax(130px,1fr) minmax(95px,.8fr) 38px;gap:9px;padding:0 0 8px;color:#74807c;font-size:11px;font-weight:750}
      .nic-settle-delete{height:42px;width:38px;border:1px solid var(--ss-line);border-radius:8px;background:white;color:#a5362b;font-size:20px;cursor:pointer}
      .nic-settle-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:16px 0}
      .nic-settle-metric{padding:12px 13px;border:1px solid var(--ss-line);border-radius:11px;background:#fbfcfc}
      .nic-settle-metric small{display:block;color:var(--ss-muted);font-size:11px}
      .nic-settle-metric strong{display:block;margin-top:4px;font-size:15px}
      .nic-settle-table-wrap{overflow-x:auto}
      .nic-settle-table{width:100%;border-collapse:collapse;font-size:12px}
      .nic-settle-table th,.nic-settle-table td{padding:9px 7px;text-align:left;border-bottom:1px solid #edf0ef;vertical-align:top}
      .nic-settle-table th{color:#5b6965;font-size:11px}
      .nic-settle-paper{max-width:900px;margin:16px auto;padding:28px 30px;border:1px solid var(--ss-line);background:#fff;color:#172033}
      .nic-settle-paper-head{display:flex;justify-content:space-between;gap:20px;padding-bottom:14px;border-bottom:2px solid var(--ss-green)}
      .nic-settle-paper-head h2{color:var(--ss-green)}
      .nic-settle-footer{margin-top:22px;padding-top:12px;border-top:1px solid #d8dfdc;color:#5b6965;font-size:11px}
      body.nic-settlement-fullscreen{overflow-x:hidden;background:#f4f6f5!important}
      body.nic-settlement-fullscreen .app>.hero,body.nic-settlement-fullscreen .app>.bottom,body.nic-settlement-fullscreen .app>.footer-note,body.nic-settlement-fullscreen .app>.nic-shared-footer{display:none!important}
      body.nic-settlement-fullscreen .app>main.nic-content-main{width:100%!important;max-width:none!important;margin:0!important;padding:0!important;flex:1 0 auto!important}
      body.nic-settlement-fullscreen .nic-content-card{width:100%!important;max-width:none!important;min-height:calc(100dvh - 72px)!important;margin:0!important;padding:0!important;border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
      body.nic-settlement-fullscreen .app>.nic-brand-bar{position:sticky;top:0;z-index:30;background:#fff!important}
      @media(max-width:760px){
        .nic-settlement-root{min-height:calc(100dvh - 58px)}
        .nic-settle-apphead{height:52px;padding:0 12px}
        .nic-settle-appbrand{font-size:13px}
        .nic-settle-backlink{font-size:11px}
        .nic-settle-layout{display:block;min-height:calc(100dvh - 110px)}
        .nic-settle-sidebar{padding:8px 10px;border-right:0;border-bottom:1px solid var(--ss-line)}
        .nic-settle-sidebar-title,.nic-settle-sidebar-note{display:none}
        .nic-settle-nav{display:flex;overflow:auto;gap:4px}
        .nic-settle-nav button{width:auto;flex:0 0 auto;white-space:nowrap;font-size:11px;padding:8px}
        .nic-settle-work{padding:19px 12px 28px}
        .nic-settle-work h1{font-size:23px}
        .nic-settle-status{font-size:10px}
        .nic-settle-card{padding:16px}
        .nic-settle-choices,.nic-settle-fields{grid-template-columns:1fr}
        .nic-settle-full{grid-column:auto}
        .nic-settle-choice{min-height:0}
        .nic-settle-progress-labels{font-size:9px}
        .nic-settle-position-head{display:none}
        .nic-settle-position{grid-template-columns:1fr 1fr;gap:10px}
        .nic-settle-delete{grid-column:2;justify-self:end}
        .nic-settle-summary{grid-template-columns:1fr 1fr}
        .nic-settle-paper{padding:18px 13px}
        .nic-settle-paper-head{display:block}
        .nic-settle-actions .nic-settle-btn{min-width:0;flex:1;padding:9px 8px}
      }
      @media print{
        body.nic-settlement-printing *{visibility:hidden!important}
        body.nic-settlement-printing .nic-settle-paper,body.nic-settlement-printing .nic-settle-paper *{visibility:visible!important}
        body.nic-settlement-printing .nic-settle-paper{position:absolute;top:0;left:0;width:100%;max-width:none;margin:0;padding:0;border:0;box-shadow:none}
      }
    `;
    document.head.appendChild(style);
  }

  function launcher(){
    const old=[...landing.querySelectorAll('a,button,[role="button"]')];
    old.forEach(control=>{
      const label=(control.innerText||control.getAttribute('aria-label')||'').replace(/\s+/g,' ').trim().toLocaleLowerCase('de-DE');
      if(label.includes('weg-abrechnung hochladen')||label.includes('manuelle erfassung')){
        const container=control.closest('.nic-settle-start,.nic-settle-launches,.button-grid,.button-row');
        if(container)container.remove();else control.remove();
      }
    });
    const wrap=document.createElement('div');wrap.className='nic-settle-launch';
    const button=document.createElement('button');button.type='button';button.textContent='Nebenkostenabrechnung starten →';button.addEventListener('click',()=>openApp());
    wrap.appendChild(button);landing.appendChild(wrap);
  }
  function openApp(){
    state.open=true;state.step=0;
    document.body.classList.add('nic-settlement-fullscreen');
    landing.hidden=true;root.hidden=false;render();
    history.pushState({nicSettlementApp:true},'',location.pathname+location.search+'#mieterabrechnung');
    window.scrollTo({top:0,behavior:'smooth'});
  }
  function closeApp(fromHistory){
    state.open=false;document.body.classList.remove('nic-settlement-fullscreen');
    if(root)root.hidden=true;if(landing)landing.hidden=false;
    if(!fromHistory&&location.hash==='#mieterabrechnung')history.back();
    window.scrollTo({top:0,behavior:'smooth'});
  }
  function mount(){
    host=document.getElementById('nicContentView');
    if(!host||host.querySelector('.nic-settlement-root'))return;
    styles();
    landing=document.createElement('div');landing.className='nic-settlement-landing';
    while(host.firstChild)landing.appendChild(host.firstChild);
    host.appendChild(landing);
    root=document.createElement('div');root.className='nic-settlement-root';root.hidden=true;root.setAttribute('aria-live','polite');
    host.appendChild(root);launcher();root.addEventListener('click',handleClick);root.addEventListener('input',handleInput);root.addEventListener('change',handleChange);
  }
  function progress(){
    const labels=['Start','Angaben','Kosten','Vorschau'];
    return '<div class="nic-settle-progress">'+labels.map((_,i)=>'<span class="'+(i<=state.step?'active':'')+'"></span>').join('')+'</div><div class="nic-settle-progress-labels">'+labels.map((l,i)=>'<span class="'+(i===state.step?'active':'')+'">'+(i+1)+' · '+l+'</span>').join('')+'</div>';
  }
  function sidebar(){
    const items=[['start','Neue Abrechnung',0],['details','Objekte & Einheiten',1],['contacts','Kontakte',1],['costs','Kosten & Verteilung',2],['preview','Vorschau',3]];
    return '<aside class="nic-settle-sidebar"><div class="nic-settle-sidebar-title">Mieterabrechnung</div><nav class="nic-settle-nav" aria-label="Abrechnungsbereiche">'+items.map(([key,label,step])=>'<button type="button" data-nav="'+key+'" aria-current="'+(step===state.step?'page':'false')+'">'+label+'</button>').join('')+'</nav><div class="nic-settle-sidebar-note">Noch keine gespeicherten Daten. Lege nur die Angaben an, die du für diese Abrechnung benötigst.</div></aside>';
  }
  function appHeader(){return '<header class="nic-settle-apphead"><div class="nic-settle-appbrand"><span class="nic-settle-appmark">N</span><span>Abrechnung erstellen</span></div><button type="button" class="nic-settle-backlink" data-action="close">← Zur Informationsseite</button></header>';}
  function startView(){
    return '<section class="nic-settle-card"><h2>Wie möchtest du beginnen?</h2><p>Wähle einen Erfassungsweg. Es sind noch keine Objekte, Kontakte oder Kosten eingetragen.</p><div class="nic-settle-choices"><button type="button" class="nic-settle-choice '+(state.source==='weg'?'selected':'')+'" data-source="weg"><span class="nic-settle-choice-icon">⇧</span><strong>WEG-Abrechnung auswählen</strong><span>Wähle die Jahresabrechnung als PDF oder Foto aus. Die Inhalte werden in dieser Entwicklungsfassung noch nicht automatisch ausgelesen.</span></button><button type="button" class="nic-settle-choice '+(state.source==='manual'?'selected':'')+'" data-source="manual"><span class="nic-settle-choice-icon">✎</span><strong>Manuell erfassen</strong><span>Ohne WEG-Datei beginnen und Angaben sowie Betriebskosten selbst eintragen.</span></button></div><div class="nic-settle-filebox '+(state.source==='weg'?'visible':'')+'"><div class="nic-settle-field"><label for="nicSettleFile">WEG-Abrechnung · PDF oder Foto</label><input type="file" id="nicSettleFile" data-file accept="application/pdf,image/*"><small>'+(state.fileName?'Ausgewählt: '+esc(state.fileName):'Noch keine Datei ausgewählt.')+'</small></div></div><div class="nic-settle-note"><b>Leerer Start:</b> Es werden keine Beispieldaten eingesetzt. Eine ausgewählte Datei wird nur während dieser Sitzung im Browser gehalten und weder hochgeladen noch ausgelesen. Dauerhafte Speicherung ist noch nicht angebunden.</div><div class="nic-settle-actions"><button type="button" class="nic-settle-btn" data-action="close">Abbrechen</button><button type="button" class="nic-settle-btn primary" data-action="next" '+(state.source==='manual'||(state.source==='weg'&&state.file)?'':'disabled')+'>Weiter zu den Angaben →</button></div></section>';
  }
  function detailsView(){
    const field=(key,label,placeholder,type='text',hint='')=>'<div class="nic-settle-field"><label for="s-'+key+'">'+label+'</label><input id="s-'+key+'" data-field="'+key+'" type="'+type+'" value="'+esc(state[key])+'" placeholder="'+esc(placeholder)+'">'+(hint?'<small>'+hint+'</small>':'')+'</div>';
    return '<section class="nic-settle-card"><h2>Objekt, Wohnung und Abrechnungszeitraum</h2><p>Trage die Angaben für diese Abrechnung ein. Felder bleiben leer, solange du nichts ergänzt.</p><div class="nic-settle-fields">'+field('propertyName','Objektbezeichnung','Name des Objekts')+field('year','Abrechnungsjahr','z. B. 2026','text','Das Abrechnungsjahr wird nicht vorausgefüllt.')+field('street','Straße und Hausnummer','Anschrift')+field('zip','Postleitzahl','PLZ')+field('city','Ort','Ort')+field('totalArea','Gesamtwohnfläche','m²','text','Für eine Verteilung nach Wohnfläche.')+field('unitCount','Anzahl der Wohneinheiten','Anzahl','text','Für eine Verteilung je Wohneinheit.')+field('totalMea','Gesamt-MEA','MEA','text','Nur falls die WEG nach Miteigentumsanteilen verteilt.')+field('totalConsumption','Gesamtverbrauch','z. B. kWh oder m³','text','Einheit und Gesamtverbrauch müssen zum Wohnungswert passen.')+'</div><div class="nic-settle-section"><h3>Wohnung / Einheit</h3><div class="nic-settle-fields">'+field('unitName','Wohnungsbezeichnung','z. B. 1. OG links')+field('unitArea','Wohnfläche der Einheit','m²')+field('unitMea','Miteigentumsanteil','MEA')+field('unitConsumption','Verbrauch der Einheit','z. B. kWh oder m³')+'</div></div><div class="nic-settle-section"><h3>Vermieter/in und Mietverhältnis</h3><div class="nic-settle-fields">'+field('ownerName','Vermieter/in','Name oder Firma')+field('ownerAddress','Anschrift Vermieter/in','Anschrift')+field('tenantName','Mieter/in','Name')+field('tenantAddress','Anschrift Mieter/in','Anschrift')+field('rentStart','Mietbeginn','','date')+field('rentEnd','Mietende, falls ausgezogen','','date')+field('advance','Geleistete Vorauszahlungen','€','text','Gesamtbetrag für den eingetragenen Abrechnungszeitraum.')+'</div></div><div class="nic-settle-actions"><button type="button" class="nic-settle-btn" data-action="back">← Zurück</button><button type="button" class="nic-settle-btn primary" data-action="next">Weiter zu den Kosten →</button></div></section>';
  }
  function newPosition(){return {name:'',category:'',key:'',amount:''};}
  function positionsView(){
    const rows=state.positions.map((p,i)=>'<div class="nic-settle-position"><div class="nic-settle-field"><label>Position</label><input data-pos="'+i+'" data-col="name" value="'+esc(p.name)+'" placeholder="Kostenart"></div><div class="nic-settle-field"><label>Kategorie</label><select data-pos="'+i+'" data-col="category"><option value="">Bitte wählen</option>'+categories.map(c=>'<option '+(p.category===c?'selected':'')+'>'+c+'</option>').join('')+'</select></div><div class="nic-settle-field"><label>Verteilerschlüssel</label><select data-pos="'+i+'" data-col="key"><option value="">Bitte wählen</option>'+keys.map(k=>'<option '+(p.key===k?'selected':'')+'>'+k+'</option>').join('')+'</select></div><div class="nic-settle-field"><label>Gesamtbetrag</label><input data-pos="'+i+'" data-col="amount" inputmode="decimal" value="'+esc(p.amount)+'" placeholder="€"></div><button type="button" class="nic-settle-delete" data-action="delete-position" data-index="'+i+'" aria-label="Position löschen">×</button></div>').join('');
    return '<section class="nic-settle-card"><div class="nic-settle-title-row"><div><h2>Kosten und Verteilung</h2><p>Erfasse jede Position und ordne ihr einen Verteilerschlüssel zu. Es sind keine Positionen vorausgefüllt.</p></div><button type="button" class="nic-settle-btn" data-action="add-position">＋ Position hinzufügen</button></div>'+(rows?'<div class="nic-settle-position-head"><span>Position</span><span>Kategorie</span><span>Verteilerschlüssel</span><span>Gesamtbetrag</span><span></span></div>'+rows:'<div class="nic-settle-empty"><strong>Noch keine Kostenpositionen erfasst.</strong>Füge eine Position hinzu, um den Betrag und die Verteilung einzutragen.</div>')+'<div class="nic-settle-note">WEG-Verteilung und mietvertraglich zulässige Verteilung können voneinander abweichen. Prüfe jede Zuordnung vor der Abrechnung.</div><div class="nic-settle-actions"><button type="button" class="nic-settle-btn" data-action="back">← Zurück</button><button type="button" class="nic-settle-btn primary" data-action="next">Zur Vorschau →</button></div></section>';
  }
  function ratio(p){
    const unitArea=numeric(state.unitArea),totalArea=numeric(state.totalArea),unitMea=numeric(state.unitMea),totalMea=numeric(state.totalMea),units=numeric(state.unitCount);
    if(p.key==='Wohnfläche')return totalArea>0&&unitArea>0?unitArea/totalArea:null;
    if(p.key==='Wohneinheit')return units>0?1/units:null;
    if(p.key==='MEA')return totalMea>0&&unitMea>0?unitMea/totalMea:null;
    if(p.key==='Verbrauch'){const total=numeric(state.totalConsumption),unit=numeric(state.unitConsumption);return total>0&&state.unitConsumption!==''?unit/total:null;}
    if(p.key==='Direktzuordnung')return 1;
    return null;
  }
  function allocationRows(){return state.positions.filter(p=>p.name.trim()||p.amount.trim()).map(p=>{const share=ratio(p),amount=numeric(p.amount);return {p,share,amount,unit:share===null?null:Math.round(amount*share*100)/100};});}
  function previewView(){
    const rows=allocationRows(),billable=rows.filter(r=>r.p.category==='Umlagefähig'&&r.unit!==null),tenantTotal=billable.reduce((sum,r)=>sum+r.unit,0),advance=numeric(state.advance),balance=tenantTotal-advance;
    const rowHtml=rows.map(({p,share,amount,unit})=>'<tr><td>'+esc(p.name||'Position ohne Bezeichnung')+'</td><td>'+esc(p.category||'Nicht zugeordnet')+'</td><td>'+esc(p.key||'Nicht zugeordnet')+'</td><td>'+fmt(amount)+'</td><td>'+(share===null?'Angabe fehlt':money.format(share*100)+' %')+'</td><td>'+(unit===null?'Noch offen':fmt(unit))+'</td></tr>').join('');
    return '<section class="nic-settle-card"><h2>Vorschau und Endkontrolle</h2><p>Die Vorschau enthält nur deine eingegebenen Werte. Fehlende Angaben werden sichtbar markiert und nicht geschätzt.</p><article class="nic-settle-paper"><div class="nic-settle-paper-head"><div><h2>Mieterabrechnung '+(state.year?esc(state.year):'')+'</h2><b>'+(state.tenantName?esc(state.tenantName):'Mieter/in noch nicht eingetragen')+'</b><p>'+esc(state.propertyName||'Objekt noch nicht eingetragen')+(state.unitName?' · '+esc(state.unitName):'')+'</p><p>'+esc([state.street,state.zip,state.city].filter(Boolean).join(', '))+'</p></div><div><b>Abrechnungszeitraum</b><br>'+(state.year?'01.01.'+esc(state.year)+' – 31.12.'+esc(state.year):'Noch nicht eingetragen')+'</div></div>'+(rows.length?'<div class="nic-settle-table-wrap"><table class="nic-settle-table"><thead><tr><th>Position</th><th>Kategorie</th><th>Schlüssel</th><th>Gesamt</th><th>Anteil</th><th>Wohnungsbetrag</th></tr></thead><tbody>'+rowHtml+'</tbody></table></div>':'<div class="nic-settle-empty"><strong>Noch keine Kosten erfasst.</strong>Die Vorschau wird befüllt, sobald du Positionen ergänzt.</div>')+'<div class="nic-settle-summary"><div class="nic-settle-metric"><small>Umlagefähige Kosten dieser Wohnung</small><strong>'+(billable.length?fmt(tenantTotal):'Noch offen')+'</strong></div><div class="nic-settle-metric"><small>Vorauszahlungen</small><strong>'+(state.advance?fmt(advance):'Noch nicht eingetragen')+'</strong></div><div class="nic-settle-metric"><small>Zwischenergebnis</small><strong>'+(state.advance&&billable.length?fmt(balance):'Noch offen')+'</strong></div></div><div class="nic-settle-footer">Vor der Ausgabe bitte Zeitraum, Mietverhältnis, Vorauszahlungen und Umlagefähigkeit prüfen. Die automatische WEG-Texterkennung und dauerhafte Speicherung sind in dieser Entwicklungsfassung noch nicht angebunden.</div></article><div class="nic-settle-actions"><button type="button" class="nic-settle-btn" data-action="back">← Zurück zu den Kosten</button><button type="button" class="nic-settle-btn gold" data-action="print" '+(rows.length?'':'disabled')+'>Drucken / PDF →</button></div></section>';
  }
  function render(){
    if(!root||!root.isConnected)return;
    const headings=['Neue Abrechnung starten','Objekt, Wohnung und Kontakte','Kosten und Verteilung','Vorschau'];
    const descriptions=['Wähle deinen Erfassungsweg.','Ergänze die Angaben für diese Abrechnung.','Trage Kostenpositionen ein und ordne den Schlüssel zu.','Prüfe die eingegebenen Werte vor der Ausgabe.'];
    const views=[startView,detailsView,positionsView,previewView];
    root.innerHTML=appHeader()+'<div class="nic-settle-layout">'+sidebar()+'<main class="nic-settle-work"><div class="nic-settle-crumb">Mieterabrechnung&nbsp; / &nbsp;'+esc(headings[state.step])+'</div><div class="nic-settle-title-row"><div><h1>'+esc(headings[state.step])+'</h1><p class="nic-settle-lead">'+esc(descriptions[state.step])+'</p></div><span class="nic-settle-status">Entwurf · leer</span></div>'+progress()+views[state.step]()+'<p class="nic-settle-lead" style="font-size:11px;margin:12px 0 0">Entwicklungsansicht: Eingaben werden nicht dauerhaft gespeichert. Bitte keine echten Mieterdokumente hochladen.</p></main></div>';
  }
  function updateField(el){if(el.dataset.field){state[el.dataset.field]=el.value;return;}if(el.dataset.pos!==undefined){const i=Number(el.dataset.pos),col=el.dataset.col;if(state.positions[i]&&col)state.positions[i][col]=el.value;}}
  function handleInput(event){updateField(event.target);}
  function handleChange(event){
    const el=event.target;updateField(el);
    if(el.hasAttribute('data-file')){state.file=el.files&&el.files[0]?el.files[0]:null;state.fileName=state.file?state.file.name:'';render();return;}
    if(el.dataset.pos!==undefined){const i=Number(el.dataset.pos),col=el.dataset.col;if(state.positions[i]&&col)state.positions[i][col]=el.value;}
  }
  function handleClick(event){
    const button=event.target.closest('button');if(!button)return;
    if(button.dataset.source){state.source=button.dataset.source;if(state.source!=='weg'){state.file=null;state.fileName='';}render();return;}
    if(button.dataset.nav){state.step=({start:0,details:1,contacts:1,costs:2,preview:3})[button.dataset.nav]??0;render();return;}
    if(button.dataset.action==='close'){closeApp(false);return;}
    if(button.dataset.action==='next'){
      if(state.step===0&&!state.source)return;
      state.step=Math.min(3,state.step+1);render();return;
    }
    if(button.dataset.action==='back'){state.step=Math.max(0,state.step-1);render();return;}
    if(button.dataset.action==='add-position'){state.positions.push(newPosition());render();return;}
    if(button.dataset.action==='delete-position'){state.positions.splice(Number(button.dataset.index),1);render();return;}
    if(button.dataset.action==='print'){document.body.classList.add('nic-settlement-printing');window.print();window.addEventListener('afterprint',()=>document.body.classList.remove('nic-settlement-printing'),{once:true});}
  }
  window.addEventListener('popstate',()=>{if(state.open)closeApp(true);});
  function observe(){
    const observer=new MutationObserver(()=>{if(!root&&document.getElementById('nicContentView'))mount();});
    if(document.body)observer.observe(document.body,{childList:true,subtree:true});
  }
  function boot(){mount();observe();}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
