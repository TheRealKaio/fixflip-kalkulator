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
    if(key==='cookie-hinweis')return '<p>Du hast die Wahl: Unsere Kalkulatoren funktionieren auch ohne optionale Cookies. Mit „Zustimmen“ erlaubst du Cookies und ähnliche Speichertechniken für unsere freiwillige Nutzungsstatistik. Damit sehen wir, welche Seiten, Kalkulatoren und PDF-Funktionen genutzt werden. Erfasst werden Aufrufe, Berechnungen, PDF-Downloads und Teilen-Aktionen sowie Geräteart, Betriebssystem und erkennbare Herkunft.</p>\n<p>Sofern Google Analytics eingerichtet ist, werden diese Nutzungsdaten nach deiner Zustimmung auch von Google verarbeitet. Dabei können Online-Kennungen und Länderinformationen verarbeitet und Daten in die USA übermittelt werden. Deine eingegebenen Finanz- und Objektdaten werden nicht an Google übermittelt.</p>\n<p>Mit „Ablehnen“ bleiben die optionale Statistik und Google Analytics ausgeschaltet. Deine Auswahl merken wir bis zu 180 Tage. Du kannst deine Einwilligung jederzeit unten über „Cookie-Hinweis“ mit Wirkung für die Zukunft widerrufen oder ändern.</p>';
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
  const pages=[['website','Webseite',''],['company','Unternehmen','unternehmen/'],['budget','Budget','budget/'],['own','Eigennutzung','eigennutzung/'],['rent','Vermietung','vermietung/'],['flip','Fix & Flip','fix-flip/']];
  const fonts={system:'-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',arial:'Arial,Helvetica,sans-serif',verdana:'Verdana,Geneva,sans-serif',georgia:'Georgia,"Times New Roman",serif',trebuchet:'"Trebuchet MS",Arial,sans-serif'};
  const layoutDefaults={font:'system',bodySize:16,h1:30,h2:18,h3:22,h4:16,background:'#F5F7FB',text:'#172033',buttonBackground:'#0F172A',buttonText:'#FFFFFF'};
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
      else if(typeof v==='number'){const n=Number(x);s.layout[k]=Number.isFinite(n)&&n>=10&&n<=72?n:v;}
      else s.layout[k]=/^#[0-9a-f]{6}$/i.test(x)?x.toUpperCase():v;
    }
    portals.forEach(([k])=>s.social[k]=httpUrl(raw.social?.[k]));
    pages.forEach(([k])=>{const tag=text(raw.meta?.[k]?.googleTag,40).toUpperCase();s.meta[k]={title:text(raw.meta?.[k]?.title,200),description:text(raw.meta?.[k]?.description,500),googleTag:/^(G|GT)-[A-Z0-9]{4,30}$/.test(tag)?tag:''};});
    const propertyId=text(raw.reporting?.propertyId,20),clientId=text(raw.reporting?.clientId,200);
    s.reporting={propertyId:/^[0-9]{1,20}$/.test(propertyId)?propertyId:'',clientId:/^[0-9]+-[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com$/.test(clientId)?clientId:''};
    s.legal={};for(const key of Object.keys(legalLabels)){const value=raw.legal?.[key];if(value!==undefined&&typeof value!=='string')throw new Error('Ungültiger HTML-Text: '+legalLabels[key]);if(value?.length>100000)throw new Error('HTML-Text zu lang (maximal 100.000 Zeichen): '+legalLabels[key]);s.legal[key]=value||'';}
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
    const src=validFavicon(value)||new URL('neustart-immocheck-logo.svg',ROOT).href;
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
    style.textContent=`:root{--bg:${l.background};--ink:${l.text};--nic-header-h1-max:${l.h1}px;--nic-button-bg:${l.buttonBackground};--nic-button-text:${l.buttonText}}body:not(.nic-admin){font-family:${fonts[l.font]};font-size:${l.bodySize}px;color:${l.text};background:${l.background}}body:not(.nic-admin) :is(button,input,select,textarea){font-family:inherit}body:not(.nic-admin) h1{font-size:${l.h1}px!important}body:not(.nic-admin) h2{font-size:${l.h2}px!important}body:not(.nic-admin) h3{font-size:${l.h3}px!important}body:not(.nic-admin) h4{font-size:${l.h4}px!important}body:not(.nic-admin) :is(.bottom-pdf,.bottom-save,.btn.primary,.save-reno-btn,.budget-apply-btn){background:${l.buttonBackground}!important;color:${l.buttonText}!important}`;
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
    setMeta('meta[property="og:image:alt"]',{property:'og:image:alt'},current.imageAlts.sharing);
    setMeta('meta[name="twitter:image:alt"]',{name:'twitter:image:alt'},current.imageAlts.sharing);
    if(key)applyMeta(current,key);
    window.NICHeader?.refresh();
  }
  function readLocal(){try{const raw=localStorage.getItem(KEY);return raw?normalize(JSON.parse(raw)):null;}catch(_){return null;}}
  async function init(){
    const response=await fetch(new URL('site-settings.json',ROOT),{cache:'no-store'});
    if(!response.ok)throw new Error('Veröffentlichte Einstellungen konnten nicht geladen werden.');
    published=normalize(await response.json());current=readLocal()||published;return current;
  }
  function save(s){const safe=normalize(s);localStorage.setItem(KEY,JSON.stringify(safe));current=safe;return safe;}
  function discard(){localStorage.removeItem(KEY);current=published;return published;}
  function imprint(s){const c=s.company,lines=[];
    for(const [keys,label] of imprintGroups){const values=label==='Anschrift'?[c.street,[c.postalCode,c.city].filter(Boolean).join(' '),c.country]:keys.map(k=>c[k]);const value=values.filter(Boolean).join('\n');if(value)lines.push({label,value});}return lines;
  }
  window.NICSettings={ROOT,KEY,legalLabels,legalSource,legalIssues,legalFragment,companyFields,imageAltDefaults,portals,pages,fonts,layoutDefaults,normalize,httpUrl,websiteUrl,validFavicon,applyLogo,apply,applyMeta,pageMeta,save,discard,imprint,init,get current(){return current;},get published(){return published;},get isLocal(){return !!readLocal();}};
  // Apply the versioned public configuration before the first rendered frame.
  const bootstrap=document.getElementById?.('nic-published-settings');
  if(bootstrap){try{published=normalize(JSON.parse(bootstrap.textContent));apply(readLocal()||published);}catch(err){console.warn('Initiale Einstellungen:',err.message);}}
})();
