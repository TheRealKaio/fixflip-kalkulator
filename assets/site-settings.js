(function(){
  'use strict';
  const ROOT=new URL('.',document.currentScript.src);
  const KEY='nic_site_settings_v1';
  const companyFields=[
    ['name','Vollständiger Name / Firma'],['legalForm','Rechtsform (falls zutreffend)'],['representative','Vertretungsberechtigte Person(en)'],
    ['street','Straße und Hausnummer'],['postalCode','Postleitzahl'],['city','Ort'],['country','Land'],['email','E-Mail-Adresse'],['website','Internetadresse'],['phone','Telefon / direkte Kontaktmöglichkeit'],['fax','Fax (optional)'],
    ['registerType','Registerart (falls eingetragen)'],['registerCourt','Registergericht / registerführende Stelle'],['registerNumber','Registernummer'],
    ['vatId','Umsatzsteuer-Identifikationsnummer (falls vorhanden)'],['businessId','Wirtschafts-Identifikationsnummer (falls vorhanden)'],
    ['authority','Zuständige Aufsichtsbehörde (bei erlaubnispflichtiger Tätigkeit)'],['profession','Gesetzliche Berufsbezeichnung (bei reglementiertem Beruf)'],['professionalCountry','Staat der Verleihung'],['chamber','Zuständige Kammer'],['professionalRules','Berufsrechtliche Regelungen und Fundstelle'],
    ['capital','Stamm-/Grundkapital und ausstehende Einlagen (falls angegeben)'],['liquidation','Abwicklung / Liquidation (falls zutreffend)'],['mediaState','Sitzland (bei audiovisuellen Mediendiensten)'],['mediaAuthority','Medienaufsicht (falls zutreffend)'],
    ['editorialResponsible','Redaktionell verantwortlich (falls erforderlich)'],['editorialAddress','Anschrift der redaktionell verantwortlichen Person'],['disputeResolution','Angaben zur Verbraucherstreitbeilegung (falls zutreffend)'],['additional','Weitere Angaben']
  ];
  const imprintGroups=[
      [['name','legalForm'],'Anbieter'],[['representative'],'Vertreten durch'],[['street','postalCode','city','country'],'Anschrift'],[['email','website','phone','fax'],'Kontakt'],
      [['registerType','registerCourt','registerNumber'],'Register'],[['vatId'],'Umsatzsteuer-ID'],[['businessId'],'Wirtschafts-ID'],[['authority'],'Aufsichtsbehörde'],[['profession','professionalCountry','chamber','professionalRules'],'Berufsrechtliche Angaben'],[['capital'],'Kapitalangaben'],[['liquidation'],'Abwicklung / Liquidation'],[['mediaState','mediaAuthority'],'Audiovisuelle Mediendienste'],[['editorialResponsible','editorialAddress'],'Redaktionell verantwortlich'],[['disputeResolution'],'Verbraucherstreitbeilegung'],[['additional'],'Weitere Angaben']
    ];
  const legalLabels={impressum:'Impressum',agbs:'AGBs',datenschutz:'Datenschutz',haftungsausschluss:'Haftungsausschluss','cookie-hinweis':'Cookie-Hinweis'};
  const escapeHTML=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function legalSource(s,key,disclaimer=''){
    if(s.legal?.[key])return s.legal[key];
    function operatorTemplate(all){
      const parts=[];for(const [keys,label]of imprintGroups){if(!all&&!['Anbieter','Vertreten durch','Anschrift','Kontakt'].includes(label))continue;const token=k=>s.company[k]?'{{company.'+k+'}}':'';const values=label==='Anschrift'?[token('street'),['postalCode','city'].map(token).filter(Boolean).join(' '),token('country')]:keys.map(token);const value=values.filter(Boolean).join('\n');if(value)parts.push((all?'<h2>'+escapeHTML(label)+'</h2>':'')+'<p>'+value+'</p>');}
      return parts.join('\n')||'<p>Die Betreiberangaben wurden noch nicht veröffentlicht.</p>';
    }
    if(key==='impressum')return operatorTemplate(true);
    if(key==='haftungsausschluss')return disclaimer;
    if(key==='cookie-hinweis')return '<p>Du hast die Wahl: Unsere Kalkulatoren funktionieren auch ohne optionale Statistik. Mit „Zustimmen“ erlaubst du, Nutzungszahlen in zusammengefasster Form auf unserem Server zu speichern. Erfasst werden Seiten- und Rechneraufrufe, Berechnungen, PDF-Downloads und Teilen-Aktionen sowie bei Seitenaufrufen Geräteart, Betriebssystem und erkennbare Herkunft. Deine Finanz- und Objektdaten werden nicht erfasst.</p>\n<p>Sofern Google Analytics eingerichtet ist, werden diese Nutzungsdaten nach deiner Zustimmung auch von Google verarbeitet. Dabei können Online-Kennungen und Länderinformationen verarbeitet und Daten in die USA übermittelt werden. Deine eingegebenen Finanz- und Objektdaten werden nicht an Google übermittelt.</p>\n<p>Mit „Ablehnen“ bleiben die optionale Statistik und Google Analytics ausgeschaltet. Deine Auswahl merken wir bis zu 180 Tage. Du kannst deine Einwilligung jederzeit unten über „Cookie-Hinweis“ mit Wirkung für die Zukunft widerrufen oder ändern.</p>';
    const heading=key==='datenschutz'?'Verantwortlicher':'Anbieter';
    return '<h2>'+heading+'</h2>\n'+operatorTemplate(false)+'\n<h2>Inhalt noch nicht hinterlegt</h2>\n<p>'+(key==='datenschutz'?'Die vollständige Datenschutzerklärung wird noch erstellt. Die hier angezeigten Betreiberangaben ersetzen keine vollständige Datenschutzerklärung.':'Ein vollständiger AGB-Text wurde noch nicht hinterlegt. Die hier angezeigten Anbieterangaben stellen keine Allgemeinen Geschäftsbedingungen dar.')+'</p>';
  }
  function legalIssues(html,s){const issues=new Set();for(const m of html.matchAll(/{{\s*([^{}]+?)\s*}}/g)){const token=m[1].trim(),field=token.startsWith('company.')?token.slice(8):'';if(!companyFields.some(([k])=>k===field))issues.add('Unbekannter Platzhalter: '+token);else if(!s.company[field])issues.add('Kein Wert hinterlegt: '+companyFields.find(([k])=>k===field)[1]);}return [...issues];}
  function legalFragment(html,s){
    const tpl=document.createElement('template');tpl.innerHTML=html;
    const allowed=new Set(['H1','H2','H3','H4','H5','H6','P','BR','STRONG','B','EM','I','U','S','UL','OL','LI','A','BLOCKQUOTE','HR','DIV','SPAN','TABLE','THEAD','TBODY','TR','TH','TD']);
    for(const el of [...tpl.content.querySelectorAll('*')]){
      if(!allowed.has(el.tagName)){el.remove();continue;}
      const href=el.getAttribute('href'),align=el.style.textAlign||el.getAttribute('align');
      for(const attr of [...el.attributes])el.removeAttribute(attr.name);
      if(['left','right','center','justify'].includes(align))el.style.textAlign=align;
      if(el.tagName==='A'&&href){let value=href.replace(/{{\s*company\.(\w+)\s*}}/g,(_,k)=>s.company[k]||'');try{const u=new URL(value,ROOT);if(['https:','http:','mailto:','tel:'].includes(u.protocol)){el.setAttribute('href',u.href);el.setAttribute('rel','noopener noreferrer');}}catch(_){}}
    }
    const walker=document.createTreeWalker(tpl.content,4);let node;while((node=walker.nextNode()))node.textContent=node.textContent.replace(/{{\s*company\.(\w+)\s*}}/g,(token,k)=>Object.hasOwn(s.company,k)?s.company[k]:token);
    return tpl.content;
  }
  const imageAltDefaults={websiteLogo:'Neustart ImmoCheck – Immobilien-Kalkulatoren',favicon:'Haus-Symbol von Neustart ImmoCheck',appleTouchIcon:'Neustart ImmoCheck – Haus-Symbol',sharing:'Neustart ImmoCheck – Immobilien verstehen. Sicherer entscheiden.'};
  const portals=[['instagram','Instagram'],['facebook','Facebook'],['youtube','YouTube'],['linkedin','LinkedIn'],['tiktok','TikTok'],['pinterest','Pinterest'],['x','X'],['threads','Threads'],['xing','XING'],['whatsapp','WhatsApp']];
  const pages=[['website','Webseite',''],['company','Unternehmen','unternehmen/'],['budget','Budget','budget/'],['own','Eigennutzung','eigennutzung/'],['rent','Vermietung','vermietung/'],['flip','Fix & Flip','fix-flip/'],['finance','Finanzierungsrechner','finanzierungsrechner/']];
  const fonts={system:'-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',arial:'Arial,Helvetica,sans-serif',verdana:'Verdana,Geneva,sans-serif',georgia:'Georgia,"Times New Roman",serif',trebuchet:'"Trebuchet MS",Arial,sans-serif'};
  const layoutDefaults={font:'system',bodySize:16,subtextSize:14,hintSize:12,h1:30,h2:18,h3:22,h4:16,cornerRadius:22,background:'#F5F7FB',text:'#172033',buttonBackground:'#0F172A',buttonText:'AUTO',greenBackground:'#075C55',greenText:'AUTO',redBackground:'#B42318',redText:'AUTO',highlightBackground:'#FDE68A',highlightGoodBackground:'#F0FDF4',highlightWarningBackground:'#FECACA',outerBackground:'#F6F1E9'};
  let published=null,current=null;
  const text=(v,max=2000)=>typeof v==='string'?v.trim().slice(0,max):'';
  function httpUrl(v){try{const u=new URL(text(v));return /^https?:$/.test(u.protocol)&&!u.username&&!u.password?u.href:'';}catch(_){return '';}}
  function websiteUrl(v){const value=text(v);return httpUrl(/^[a-z0-9.-]+\.[a-z]{2,}(?:[/?#]|$)/i.test(value)?'https://'+value:value);}
  function validFavicon(v){return typeof v==='string' && v.length<=400000 && /^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(v)?v:'';}
  function normalize(raw){
    if(!raw||typeof raw!=='object'||Array.isArray(raw)||raw.version!==1)throw new Error('Ungültiges Konfigurationsformat (Version 1 erforderlich).');
    const s={version:1,company:{},layout:{},social:{},favicon:validFavicon(raw.favicon),websiteLogo:validFavicon(raw.websiteLogo),appleTouchIcon:typeof raw.appleTouchIcon==='string' && raw.appleTouchIcon.length<=400000 && /^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(raw.appleTouchIcon)?raw.appleTouchIcon:'',meta:{},reporting:{},sharing:{text:text(raw.sharing?.text??'Immobilien verstehen. Sicherer entscheiden.',160),image:validFavicon(raw.sharing?.image)}};
    companyFields.forEach(([k])=>s.company[k]=text(raw.company?.[k]));
    s.company.website=websiteUrl(raw.company?.website);
    for(const key of ['postalCode','city'])s.company[key]=s.company[key].replace(/\s+/g,' ');
    s.imageAlts={};Object.entries(imageAltDefaults).forEach(([k,v])=>s.imageAlts[k]=text(raw.imageAlts?.[k]??v,300).replace(/\s+/g,' '));
    for(const [k,v] of Object.entries(layoutDefaults)){
      const x=raw.layout?.[k];
      if(k==='font')s.layout[k]=Object.hasOwn(fonts,x)?x:v;
      else if(typeof v==='number'){const n=Number(x);const min=k==='cornerRadius'?0:10,max=k==='cornerRadius'?40:72;s.layout[k]=Number.isFinite(n)&&n>=min&&n<=max?n:v;}
      else s.layout[k]=/Text$/.test(k)&&x==='AUTO'?'AUTO':/^#[0-9a-f]{6}$/i.test(x)?x.toUpperCase():v;
    }
    portals.forEach(([k])=>s.social[k]=httpUrl(raw.social?.[k]));
    if(!raw.meta?.finance)raw={...raw,meta:{...raw.meta,finance:{"title": "Finanzierungsrechner: Rate & Restschuld | Neustart ImmoCheck", "description": "Berechne deine monatliche Kreditrate, Zinsen, Tilgung und Restschuld. Vergleiche Laufzeiten und prüfe, wie Sondertilgungen deine Finanzierung verändern.", "googleTag": ""}}};
    pages.forEach(([k])=>{const tag=text(raw.meta?.[k]?.googleTag,40).toUpperCase();s.meta[k]={title:text(raw.meta?.[k]?.title,200),description:text(raw.meta?.[k]?.description,500),googleTag:/^(G|GT)-[A-Z0-9]{4,30}$/.test(tag)?tag:''};});
    const propertyId=text(raw.reporting?.propertyId,20),clientId=text(raw.reporting?.clientId,200);
    s.reporting={propertyId:/^[0-9]{1,20}$/.test(propertyId)?propertyId:'',clientId:/^[0-9]+-[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com$/.test(clientId)?clientId:''};
    s.legal={};for(const key of Object.keys(legalLabels)){const value=raw.legal?.[key];if(value!==undefined&&typeof value!=='string')throw new Error('Ungültiger HTML-Text: '+legalLabels[key]);if(value?.length>100000)throw new Error('HTML-Text zu lang (maximal 100.000 Zeichen): '+legalLabels[key]);s.legal[key]=value||'';}
    s.access={};for(const key of ['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare','budgetInsightsLoginRequired']){const value=raw.access?.[key];if(value!==undefined&&typeof value!=='boolean')throw new Error('Ungültige Zugangsregel: '+key);s.access[key]=value??!['registrationBlocked','loginBlocked','budgetInsightsLoginRequired'].includes(key);}
    s.contentSections={};const sectionSettings=raw.contentSections??{};if(!sectionSettings||typeof sectionSettings!=='object'||Array.isArray(sectionSettings)||Object.keys(sectionSettings).length>200)throw new Error('Ungültige Box-Einstellungen.');
    for(const [key,value] of Object.entries(sectionSettings)){if(!/^[a-z0-9][a-z0-9._-]{0,120}$/.test(key)||!value||typeof value!=='object'||Array.isArray(value))throw new Error('Ungültige Box-Einstellung: '+key);for(const field of ['visible','guestAllowed'])if(value[field]!==undefined&&typeof value[field]!=='boolean')throw new Error('Ungültige Box-Einstellung: '+key);s.contentSections[key]={visible:value.visible??true,guestAllowed:value.guestAllowed??true};}
    if(raw.access?.budgetInsightsLoginRequired===true)for(const [key,field] of [['wo-geht-das-geld-hin','guestAllowed'],['szenario-was-ware-wenn','guestAllowed']]){const match=Object.keys(s.contentSections).find(k=>k.includes(key));if(match)s.contentSections[match][field]=false;}
    return s;
  }
  function pageMeta(s,key){const m=s.meta[key]||{};return {title:m.title||s.meta.website.title||'Neustart ImmoCheck',description:m.description||s.meta.website.description||''};}
  function setMeta(selector,attrs,value){let el=document.head.querySelector(selector);if(!el){el=document.createElement('meta');Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));document.head.append(el);}el.content=value;}
  function applyMeta(s,key){
    const m=pageMeta(s,key);document.title=m.title;
    setMeta('meta[name="description"]',{name:'description'},m.description);
    setMeta('meta[property="og:title"]',{property:'og:title'},m.title);
    setMeta('meta[property="og:description"]',{property:'og:description'},m.description);
    setMeta('meta[name="twitter:title"]',{name:'twitter:title'},m.title);
    setMeta('meta[name="twitter:description"]',{name:'twitter:description'},m.description);
    const path=(key==='company' && /\/impressum\//.test(location.pathname))?'impressum/':(pages.find(p=>p[0]===key)?.[2]||'');
    let canonical=document.querySelector('link[rel="canonical"]');if(!canonical){canonical=document.createElement('link');canonical.rel='canonical';document.head.append(canonical);}canonical.href=new URL(path,ROOT).href;
    setMeta('meta[property="og:url"]',{property:'og:url'},canonical.href);
  }
  function applyLogo(value,alt=current?.imageAlts?.websiteLogo??imageAltDefaults.websiteLogo,website=current?.company?.website){
    const src=validFavicon(value)||new URL('header-logo.png',ROOT).href;
    document.querySelectorAll('.brand-logo-wrap').forEach(wrap=>{
      const inline=wrap.querySelector('svg.brand-logo');
      if(!validFavicon(value)&&inline){const link=wrap.querySelector('a.nic-logo-link');if(link)link.href=websiteUrl(website)||ROOT.href;inline.removeAttribute('aria-labelledby');inline.setAttribute('role','img');inline.setAttribute('aria-label',alt);return;}
      let img=wrap.querySelector('img.brand-logo');
      if(!img){img=document.createElement('img');img.className='brand-logo';img.alt='Neustart ImmoCheck';wrap.replaceChildren(img);}
      let link=wrap.querySelector('a.nic-logo-link');if(!link){link=document.createElement('a');link.className='nic-logo-link';wrap.replaceChildren(link);link.append(img);}link.href=websiteUrl(website)||ROOT.href;link.removeAttribute('target');
      img.alt=alt;img.src=src;img.style.maxHeight='72px';img.style.objectFit='contain';
    });
  }
  function apply(s,key){
    current=normalize(s);const l=current.layout;
    let style=document.getElementById('nic-custom-layout');if(!style){style=document.createElement('style');style.id='nic-custom-layout';document.head.append(style);}
    const contrastText=(bg,choice)=>{if(choice!=='AUTO')return choice;const rgb=[1,3,5].map(i=>parseInt(bg.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:Math.pow((v+.055)/1.055,2.4));return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722>.179?'#000000':'#FFFFFF';};
    const greenText=contrastText(l.greenBackground,l.greenText),blackText=contrastText(l.buttonBackground,l.buttonText),redText=contrastText(l.redBackground,l.redText);
    const scaledRadius=original=>Math.round(l.cornerRadius*original/22);
    style.textContent=`:root{--bg:${l.background};--ink:${l.text};--nic-outer-bg:${l.outerBackground};--nic-green-bg:${l.greenBackground};--nic-green-text:${greenText};--nic-black-bg:${l.buttonBackground};--nic-black-text:${blackText};--nic-red-bg:${l.redBackground};--nic-red-text:${redText};--nic-highlight-bg:${l.highlightBackground};--nic-highlight-good-bg:${l.highlightGoodBackground};--nic-highlight-warning-bg:${l.highlightWarningBackground};--nic-body-font-size:${l.bodySize}px;--nic-body-font-family:${fonts[l.font]};--nic-header-h1-max:${l.h1}px;--nic-menu-title-size:${l.h2}px;--nic-button-bg:${l.buttonBackground};--nic-button-text:${blackText};--nic-brand-radius:${l.cornerRadius}px;--nic-footer-radius:${l.cornerRadius}px;--nic-menu-radius:${scaledRadius(16)}px;--nic-bottom-button-radius:${scaledRadius(17)}px}body:not(.nic-admin){font-family:${fonts[l.font]};font-size:${l.bodySize}px;color:${l.text};background:${l.outerBackground}!important}body:not(.nic-admin),body:not(.nic-admin) *{font-family:${fonts[l.font]}!important}
body:not(.nic-admin) :is(p,li,td,th,label,button,input,select,textarea,.mini,.hint,.nic-consent,.nic-cookie-custom,.public-footer,.nic-brand-description,.footer-note,.footer-note *,.nic-legal-card,.nic-legal-card :where(:not(h1,h2,h3,h4)),.legal-page-card p,.legal-page-card li){font-size:${l.bodySize}px!important;line-height:1.5}
body:not(.nic-admin) :is(p,li,.footer-note,.nic-legal-card){overflow-wrap:anywhere}
body:not(.nic-admin) .footer-note{height:auto!important;min-height:0!important}
body:not(.nic-admin) h1{font-size:${l.h1}px!important}body:not(.nic-admin) h2{font-size:${l.h2}px!important}body:not(.nic-admin) h3{font-size:${l.h3}px!important}body:not(.nic-admin) h4{font-size:${l.h4}px!important}
body:not(.nic-admin) :is(.card,.form-card,.budget-summary,.scenario-card){border-radius:${l.cornerRadius}px!important}
body:not(.nic-admin) .nic-brand-bar{border-radius:0!important}
body:not(.nic-admin) .app>.hero{border-radius:0 0 var(--nic-brand-radius,22px) var(--nic-brand-radius,22px)!important}
body:not(.nic-admin):not(.nic-embed) :is(.app>.footer-note,.app>.nic-shared-footer,.footer-note,.nic-shared-footer){border-radius:var(--nic-footer-radius,22px) var(--nic-footer-radius,22px) 0 0!important}
body:not(.nic-admin) .kpi{border-radius:${scaledRadius(17)}px!important}
body:not(.nic-admin) :is(.metric-box,.info-box,.info-card,.tip-box,.note-box){border-radius:${scaledRadius(14)}px!important}
body:not(.nic-admin) .equity-capital-note{border-radius:${scaledRadius(12)}px!important}
body:not(.nic-admin) :is(.finance-full-warning,.equity-shortfall-warning){border-radius:${scaledRadius(10)}px!important}
body:not(.nic-admin) :is(input:not([type="checkbox"]):not([type="radio"]):not([type="range"]),select,textarea,button,.button,.btn,[role="button"],.import-label,.nic-clear-reno,.nic-login-button,.nic-account-link,.budget-apply-btn,.save-reno-btn,.nic-green-budget-transfer){border-radius:${scaledRadius(10)}px!important}
body:not(.nic-admin) :is(.deal-type-option,.budget-result-card){border-radius:${scaledRadius(16)}px!important}
body:not(.nic-admin) :is(.nic-actions-above-footer .bottom-actions>button,.bottom .bottom-actions>button,.bottom-actions>button){border-radius:var(--nic-bottom-button-radius,17px)!important}
body:not(.nic-admin) .deal-type-row>.deal-type-option{border-radius:${scaledRadius(16)}px!important}
body:not(.nic-admin) .nic-brand-bar .nic-login-button{border-radius:${scaledRadius(16)}px!important}
body:not(.nic-admin) :is(.info-btn,.nic-menu-icon){border-radius:50%!important}
body:not(.nic-admin) .flip-section-card summary{font-size:${l.h2}px!important}body:not(.nic-admin) .section-summary-title{font-size:${l.h2}px!important}body:not(.nic-admin) .section-summary-subtitle{font-size:${l.bodySize}px!important;line-height:1.5}body:not(.nic-admin) .flip-section-card .advanced>summary:after{border-radius:${scaledRadius(11)}px!important}.nic-content-box-hidden{display:none!important}
body:not(.nic-admin) .nic-content-box-guest-overlay{position:absolute;inset:0;z-index:30;display:flex;align-items:center;justify-content:center;padding:18px;box-sizing:border-box;border-radius:inherit;background:rgba(248,250,252,.82);color:#94a3b8;text-align:center;font-size:${l.subtextSize}px!important;line-height:1.5;cursor:not-allowed;backdrop-filter:blur(1px)}
body:not(.nic-admin) .nic-content-box-guest-locked{position:relative!important;isolation:isolate}
body:not(.nic-admin) :is(.sub,.subtitle,.card>h2+p,.card>h3+p,.section-subtitle,.nic-brand-description){font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) #budgetExpensesSection .budget-expense-guidance,body:not(.nic-admin) #budgetExpensesSection .budget-expense-guidance *{font-size:var(--nic-body-font-size, ${l.bodySize}px)!important;line-height:1.5!important}
body:not(.nic-admin) .nic-household-net-income-guidance,body:not(.nic-admin) .nic-household-net-income-guidance *{font-size:var(--nic-body-font-size, ${l.bodySize}px)!important;line-height:1.5!important}
body:not(.nic-admin) :is(#budgetSuggestionTotal,.budget-suggestion-actions .suggestion-total,.reno-head-actions .suggestion-total){font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) #budgetExpensesSection .budget-expense-list .budget-expense-name{font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) #budgetExpensesSection .budget-expense-list .budget-expense-name :is(strong,b,.name,.budget-expense-title),body:not(.nic-admin) #budgetExpensesSection .budget-expense-list .budget-expense-name > :first-child{font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) #budgetExpensesSection .budget-expense-list .budget-expense-name :is(small,.mini,.sub,.hint,.description,.budget-expense-description),body:not(.nic-admin) #budgetExpensesSection .budget-expense-list .budget-expense-name > :not(:first-child){font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.mini,.hint,.note,.info-text,.tip,.helper,.rent-maintenance-status,.kpi .note,.field .mini,.field .hint,.field label .hint,.metric-box .metric-label){font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.kpi .name,.kpi .value,.metric-box .metric-value,.info-box,.info-box p,.info-box strong,.info-box span,.info-box label,.info-card p,.tip-box p,.equity-capital-note){font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) .budget-result-card .name{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.budget-result-card:has(#budgetLoan),.budget-result-card:has(#budgetEquityResult),.budget-result-card:has(#budgetAllIn),.budget-result-card:has(#budgetAncillaryAmount),.budget-result-card:has(#budgetExtraCostsAmount),.budget-result-card:has(#budgetPropertyPrice)) .name{font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.budget-summary-row,.budget-summary-row span,.budget-summary-row strong){font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) .own-budget-transfer-copy>.name{font-size:${l.bodySize}px!important;line-height:1.5}
body:not(.nic-admin) .own-budget-transfer-copy>.note{font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) .own-budget-transfer-status{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) .own-budget-household-row,body:not(.nic-admin) .own-budget-household-row strong{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.cost-row,.cost-row span,.cost-row strong,.cost-total,.cost-total span,.cost-total strong,.budget-rate-slider-head,.budget-rate-slider-head span,.budget-rate-slider-head strong,.budget-rate-slider-note,.budget-rate-slider-warning,.budget-rate-guidance,.budget-rate-guidance *,.rent-note,.rent-note *, .legend,.legend *){font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) #rentSection .rent-note,body:not(.nic-admin) #rentSection .rent-note *{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) .source,body:not(.nic-admin) .source *{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) .status,body:not(.nic-admin) .status *{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) .rate-actions button,body:not(.nic-admin) .rate-actions button *{font-size:${l.hintSize}px!important;line-height:1.5}
body:not(.nic-admin) #scenarioDetails>summary{font-size:${l.bodySize}px!important}
body:not(.nic-admin) .reno-note,body:not(.nic-admin) .reno-note *{font-size:${l.subtextSize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.card h2~p,.rent-finance-head h2~p,.section-intro h2~p,.section-heading h2~p,.flip-section-subtitle){font-size:${l.bodySize}px!important;line-height:1.5}
body:not(.nic-admin) :is(.bottom-pdf,.bottom-save,#share,#downloadPDF,.bottom-share){background:var(--nic-black-bg)!important;color:var(--nic-black-text)!important;border-color:var(--nic-black-bg)!important}
body:not(.nic-admin) :is(.nic-login-button,.nic-account-link,.budget-apply-btn,.save-reno-btn,#applyTradeSuggestions,.nic-green-budget-transfer,.btn.primary){background:var(--nic-green-bg)!important;color:var(--nic-green-text)!important;border-color:var(--nic-green-bg)!important}
body:not(.nic-admin) :is(.nic-clear-reno,.bottom-primary,#newCalc){background:var(--nic-red-bg)!important;color:var(--nic-red-text)!important;border-color:var(--nic-red-bg)!important}
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer){background:var(--nic-green-bg)!important;color:var(--nic-green-text)!important}
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer) :is(a,.footer-version,.nic-consent-settings){color:var(--nic-green-text)!important}
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer) :is(.nic-consent-settings,#nicConsentSettings){text-decoration:none!important}
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer) :is(.nic-consent-settings,#nicConsentSettings):hover{text-decoration:underline!important}
body:not(.nic-admin) .deal-type-row>.deal-type-option:is(:has(input:checked),[aria-pressed="true"],.current,[aria-current="page"]){background:var(--nic-green-bg)!important;border-color:var(--nic-green-bg)!important;color:var(--nic-green-text)!important}
body:not(.nic-admin) .deal-type-row>.deal-type-option:is(:has(input:checked),[aria-pressed="true"],.current,[aria-current="page"]) :is(strong,small,.nic-menu-icon){color:var(--nic-green-text)!important}
body:not(.nic-admin) .deal-type-option:is(:has(input:checked),[aria-pressed="true"],.current,[aria-current="page"])::after{background:var(--nic-green-bg)!important}
body:not(.nic-embed) .deal-type-row>.deal-type-option{box-sizing:border-box!important;border:2px solid #dce8e2!important;border-radius:${scaledRadius(16)}px!important}
body:not(.nic-embed) .deal-type-row>.deal-type-option.nic-tile-active{border:2px solid var(--nic-green-bg,#075c55)!important;background:var(--nic-green-bg,#075c55)!important;color:var(--nic-green-text,#fff)!important}
body:not(.nic-embed) .deal-type-row>.deal-type-option.nic-tile-active :is(strong,small){color:var(--nic-green-text,#fff)!important}`;
    const publicBody=document.querySelector('body:not(.nic-admin)');
    if(publicBody){
      const forceFont=(selector,size)=>publicBody.querySelectorAll(selector).forEach(el=>el.style.setProperty('font-size',size+'px','important'));
      forceFont('.kpi .name,.kpi .value,.metric-box .metric-value,.info-box,.info-box p,.info-box strong,.info-box span,.info-box label,.info-box div,.info-card p,.tip-box p,.equity-capital-note',l.subtextSize);
      forceFont('.mini,.hint,.note,.info-text,.helper,.metric-label,.rent-maintenance-status,.field label .hint,.kpi .note',l.hintSize);
      forceFont('h2,.flip-section-card .advanced>summary',l.h2);
      forceFont('.flip-section-subtitle,#rentFinanceCard .rent-finance-head h2 + p,#rentFinanceCard .rent-finance-head .sub',l.bodySize);
      publicBody.querySelectorAll('h2').forEach(heading=>{let paragraph=heading.nextElementSibling;while(paragraph&&paragraph.tagName==='P'){paragraph.style.setProperty('font-size',l.bodySize+'px','important');paragraph=paragraph.nextElementSibling;}});
    }
    // Preserve semantic red reset buttons and the green/amber/red result indicators.
    {
      for(const rel of ['icon','apple-touch-icon']){
        const links=Array.from(document.head.querySelectorAll(`link[rel="${rel}"]`));let el=links.shift();links.forEach(x=>x.remove());
        if(!el){el=document.createElement('link');el.rel=rel;document.head.append(el);}
        if(rel==='apple-touch-icon'){el.href=current.appleTouchIcon||new URL('apple-touch-icon.png',ROOT).href;el.type='image/png';el.setAttribute('sizes','180x180');}
        else{el.href=current.favicon||new URL('icon.svg',ROOT).href;el.type=current.favicon?'image/png':'image/svg+xml';}
      }
    }
    applyLogo(current.websiteLogo,current.imageAlts.websiteLogo);
    window.NICContentSections?.apply(current);
    setMeta('meta[property="og:image:alt"]',{property:'og:image:alt'},current.imageAlts.sharing);
    setMeta('meta[name="twitter:image:alt"]',{name:'twitter:image:alt'},current.imageAlts.sharing);
    if(key)applyMeta(current,key);
    syncCalculatorMenu(key);
    window.NICHeader?.refresh();
  }
  if(typeof window.addEventListener==='function')window.addEventListener('nic-auth-changed',()=>{if(current)apply(current);});
  // Shared five-tile active state for all calculator routes.
  const calculatorKeys=['budget','own','rent','flip','finance'];
  function syncCalculatorMenu(active){
    if(!calculatorKeys.includes(active)){
      const route={'/budget/':'budget','/eigennutzung/':'own','/vermietung/':'rent','/fix-flip/':'flip','/finanzierungsrechner/':'finance'}[window.location?.pathname];
      const page=route||document.documentElement?.dataset?.nicPage;
      active=calculatorKeys.includes(page)?page:document.getElementById('dealTypeRent')?.getAttribute('aria-pressed')==='true'?'rent':document.querySelector('input[name="dealType"]:checked')?.value||'budget';
    }
    document.querySelectorAll('.deal-type-row > .deal-type-option').forEach((tile,index)=>{
      const key=tile.dataset.calculator||calculatorKeys[index];
      const selected=key===active;
      tile.dataset.calculator=key;
      if(tile.hasAttribute?.('aria-pressed'))tile.setAttribute('aria-pressed',String(selected));
      tile.classList.toggle('current',selected);
      tile.classList.toggle('nic-tile-active',selected);
      if(selected)tile.setAttribute('aria-current','page');
      else tile.removeAttribute('aria-current');
      tile.querySelectorAll('input[type="radio"]').forEach(input=>{
        input.checked=selected;
      });
    });
  }
  function readLocal(){try{const raw=localStorage.getItem(KEY);return raw?normalize(JSON.parse(raw)):null;}catch(_){return null;}}
  async function init(){
    const response=await fetch(new URL('site-settings.json',ROOT),{cache:'no-store'});
    if(!response.ok)throw new Error('Veröffentlichte Einstellungen konnten nicht geladen werden.');
    published=normalize(await response.json());if(window.NICAccess){const cloud=await window.NICAccess.loadSettings();if(cloud){published=normalize(cloud);current=published;return current;}}current=readLocal()||published;return current;
  }
  function save(s){const safe=normalize(s);localStorage.setItem(KEY,JSON.stringify(safe));current=safe;return safe;}
  async function saveGlobal(s){const safe=normalize(s);if(!window.NICAccess?.enabled)return save(safe);const result=normalize(await window.NICAccess.saveSettings(safe));localStorage.removeItem(KEY);published=current=result;return result;}
  function discard(){localStorage.removeItem(KEY);current=published;return published;}
  function imprint(s){const c=s.company,lines=[];
    for(const [keys,label] of imprintGroups){const values=label==='Anschrift'?[c.street,[c.postalCode,c.city].filter(Boolean).join(' '),c.country]:keys.map(k=>c[k]);const value=values.filter(Boolean).join('\n');if(value)lines.push({label,value});}return lines;
  }
  window.NICSettings={ROOT,KEY,legalLabels,legalSource,legalIssues,legalFragment,companyFields,imageAltDefaults,portals,pages,fonts,layoutDefaults,normalize,httpUrl,websiteUrl,validFavicon,applyLogo,apply,applyMeta,pageMeta,save,saveGlobal,discard,imprint,init,syncCalculatorMenu,get current(){return current;},get published(){return published;},get isLocal(){return !!readLocal();}};
  // Apply the versioned public configuration before the first rendered frame.
  const bootstrap=document.getElementById?.('nic-published-settings');
  if(bootstrap){try{published=normalize(JSON.parse(bootstrap.textContent));apply(readLocal()||published);}catch(err){console.warn('Initiale Einstellungen:',err.message);}}
  if(typeof window.dispatchEvent==='function'&&typeof Event==='function')window.dispatchEvent(new Event('nic-settings-ready'));
})();
