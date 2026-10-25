(function(){
  'use strict';
  const ROOT=new URL('.',document.currentScript.src);
  const KEY='nic_site_settings_v1';
  const companyFields=[
    ['name','Vollständiger Name / Firma'],['legalForm','Rechtsform (falls zutreffend)'],['representative','Vertretungsberechtigte Person(en)'],
    ['street','Straße und Hausnummer'],['postalCode','Postleitzahl'],['city','Ort'],['country','Land'],['email','E-Mail-Adresse'],['phone','Telefon / direkte Kontaktmöglichkeit'],['fax','Fax (optional)'],
    ['registerType','Registerart (falls eingetragen)'],['registerCourt','Registergericht / registerführende Stelle'],['registerNumber','Registernummer'],
    ['vatId','Umsatzsteuer-Identifikationsnummer (falls vorhanden)'],['businessId','Wirtschafts-Identifikationsnummer (falls vorhanden)'],
    ['authority','Zuständige Aufsichtsbehörde (bei erlaubnispflichtiger Tätigkeit)'],['profession','Gesetzliche Berufsbezeichnung (bei reglementiertem Beruf)'],['professionalCountry','Staat der Verleihung'],['chamber','Zuständige Kammer'],['professionalRules','Berufsrechtliche Regelungen und Fundstelle'],
    ['capital','Stamm-/Grundkapital und ausstehende Einlagen (falls angegeben)'],['liquidation','Abwicklung / Liquidation (falls zutreffend)'],['mediaState','Sitzland (bei audiovisuellen Mediendiensten)'],['mediaAuthority','Medienaufsicht (falls zutreffend)'],
    ['editorialResponsible','Redaktionell verantwortlich (falls erforderlich)'],['editorialAddress','Anschrift der redaktionell verantwortlichen Person'],['disputeResolution','Angaben zur Verbraucherstreitbeilegung (falls zutreffend)'],['additional','Weitere Angaben']
  ];
  const imageAltDefaults={websiteLogo:'Neustart ImmoCheck – Immobilien-Kalkulatoren',favicon:'Haus-Symbol von Neustart ImmoCheck',appleTouchIcon:'Neustart ImmoCheck – Haus-Symbol',sharing:'Neustart ImmoCheck – Immobilien verstehen. Sicherer entscheiden.'};
  const portals=[['instagram','Instagram'],['facebook','Facebook'],['youtube','YouTube'],['linkedin','LinkedIn'],['tiktok','TikTok'],['pinterest','Pinterest'],['x','X'],['threads','Threads'],['xing','XING'],['whatsapp','WhatsApp']];
  const pages=[['website','Webseite',''],['company','Unternehmen','unternehmen/'],['budget','Budget','budget/'],['own','Eigennutzung','eigennutzung/'],['rent','Vermietung','vermietung/'],['flip','Fix & Flip','fix-flip/']];
  const fonts={system:'-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',arial:'Arial,Helvetica,sans-serif',verdana:'Verdana,Geneva,sans-serif',georgia:'Georgia,"Times New Roman",serif',trebuchet:'"Trebuchet MS",Arial,sans-serif'};
  const layoutDefaults={font:'system',bodySize:16,h1:30,h2:18,h3:22,h4:16,background:'#F5F7FB',text:'#172033',buttonBackground:'#0F172A',buttonText:'#FFFFFF'};
  let published=null,current=null;
  const text=(v,max=2000)=>typeof v==='string'?v.trim().slice(0,max):'';
  function httpUrl(v){try{const u=new URL(text(v));return /^https?:$/.test(u.protocol)&&!u.username&&!u.password?u.href:'';}catch(_){return '';}}
  function validFavicon(v){return typeof v==='string' && v.length<=400000 && /^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(v)?v:'';}
  function normalize(raw){
    if(!raw||typeof raw!=='object'||Array.isArray(raw)||raw.version!==1)throw new Error('Ungültiges Konfigurationsformat (Version 1 erforderlich).');
    const s={version:1,company:{},layout:{},social:{},favicon:validFavicon(raw.favicon),websiteLogo:validFavicon(raw.websiteLogo),appleTouchIcon:typeof raw.appleTouchIcon==='string' && raw.appleTouchIcon.length<=400000 && /^data:image\/png;base64,[A-Za-z0-9+/=]+$/.test(raw.appleTouchIcon)?raw.appleTouchIcon:'',meta:{},reporting:{},sharing:{text:text(raw.sharing?.text??'Immobilien verstehen. Sicherer entscheiden.',160),image:validFavicon(raw.sharing?.image)}};
    companyFields.forEach(([k])=>s.company[k]=text(raw.company?.[k]));
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
  function applyLogo(value,alt=current?.imageAlts?.websiteLogo??imageAltDefaults.websiteLogo){
    const src=validFavicon(value)||new URL('neustart-immocheck-logo.svg',ROOT).href;
    document.querySelectorAll('.brand-logo-wrap').forEach(wrap=>{
      let img=wrap.querySelector('img.brand-logo');
      if(!img){img=document.createElement('img');img.className='brand-logo';img.alt='Neustart ImmoCheck';wrap.replaceChildren(img);}
      img.alt=alt;img.src=src;img.style.maxHeight='72px';img.style.objectFit='contain';
    });
  }
  function apply(s,key){
    current=normalize(s);const l=current.layout;
    let style=document.getElementById('nic-custom-layout');if(!style){style=document.createElement('style');style.id='nic-custom-layout';document.head.append(style);}
    style.textContent=`:root{--bg:${l.background};--ink:${l.text};--nic-button-bg:${l.buttonBackground};--nic-button-text:${l.buttonText}}body:not(.nic-admin){font-family:${fonts[l.font]};font-size:${l.bodySize}px;color:${l.text};background:${l.background}}body:not(.nic-admin) :is(button,input,select,textarea){font-family:inherit}body:not(.nic-admin) h1{font-size:${l.h1}px!important}body:not(.nic-admin) h2{font-size:${l.h2}px!important}body:not(.nic-admin) h3{font-size:${l.h3}px!important}body:not(.nic-admin) h4{font-size:${l.h4}px!important}body:not(.nic-admin) :is(.bottom-pdf,.bottom-save,.btn.primary,.save-reno-btn,.budget-apply-btn){background:${l.buttonBackground}!important;color:${l.buttonText}!important}`;
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
    for(const [keys,label] of [
      [['name','legalForm'],'Anbieter'],[['representative'],'Vertreten durch'],[['street','postalCode','city','country'],'Anschrift'],[['email','phone','fax'],'Kontakt'],
      [['registerType','registerCourt','registerNumber'],'Register'],[['vatId'],'Umsatzsteuer-ID'],[['businessId'],'Wirtschafts-ID'],[['authority'],'Aufsichtsbehörde'],[['profession','professionalCountry','chamber','professionalRules'],'Berufsrechtliche Angaben'],[['capital'],'Kapitalangaben'],[['liquidation'],'Abwicklung / Liquidation'],[['mediaState','mediaAuthority'],'Audiovisuelle Mediendienste'],[['editorialResponsible','editorialAddress'],'Redaktionell verantwortlich'],[['disputeResolution'],'Verbraucherstreitbeilegung'],[['additional'],'Weitere Angaben']
    ]){const values=label==='Anschrift'?[c.street,[c.postalCode,c.city].filter(Boolean).join(' '),c.country]:keys.map(k=>c[k]);const value=values.filter(Boolean).join('\n');if(value)lines.push({label,value});}return lines;
  }
  window.NICSettings={ROOT,KEY,companyFields,imageAltDefaults,portals,pages,fonts,layoutDefaults,normalize,httpUrl,validFavicon,applyLogo,apply,applyMeta,pageMeta,save,discard,imprint,init,get current(){return current;},get published(){return published;},get isLocal(){return !!readLocal();}};
})();
