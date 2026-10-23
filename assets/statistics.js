(function(){
'use strict';
const C=window.NICStatsCore,S=window.NICSettings;if(!C||!S)return;
const STORAGE='nic_statistics_v1',CONSENT='nic_statistics_consent_v1';
let started=false,section='website',calculator=null,pageLogged=false,lastCalculator=null,pending=null,debounce=null,googleStarted=false;
const configured=new Set(),snapshots={};
const environment={...C.detectDevice(navigator),source:C.source(document.referrer,location.href)};
function readConsent(){try{const s=JSON.parse(localStorage.getItem(CONSENT));return s&&Date.now()-s.at<180*86400000&&['granted','denied'].includes(s.status)?s.status:null;}catch(_){return null;}}
function readData(){try{const s=JSON.parse(localStorage.getItem(STORAGE));return s?.version===1&&s.days?s:C.empty();}catch(_){return C.empty();}}
function tagFor(key){const m=S.current?.meta;return m?.[key]?.googleTag||m?.website?.googleTag||'';}
function campaign(){const params=new URL(location.href).searchParams,result={};for(const [key,target] of [['utm_source','campaign_source'],['utm_medium','campaign_medium']]){const value=params.get(key);if(value&&/^[a-zA-Z0-9_.-]{1,48}$/.test(value))result[target]=value;}return result;}
function googleTag(key){
 const id=tagFor(key);if(!id||readConsent()!=='granted')return null;
 if(!googleStarted){
  googleStarted=true;window.dataLayer=window.dataLayer||[];window.gtag=window.gtag||function(){window.dataLayer.push(arguments);};
  window.gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
  window.gtag('consent','update',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});
  window.gtag('js',new Date());const script=document.createElement('script');script.id='nic-google-tag';script.async=true;script.src='https://www.googletagmanager.com/gtag/js?id='+encodeURIComponent(id);document.head.append(script);
 }
 window['ga-disable-'+id]=false;
 if(!configured.has(id)){const path=S.pages.find(p=>p[0]===key)?.[2]||'';window.gtag('config',id,{send_page_view:false,allow_google_signals:false,allow_ad_personalization_signals:false,page_location:new URL(path,S.ROOT).href,page_referrer:cleanReferrer(),...campaign()});configured.add(id);}
 return id;
}
function cleanReferrer(){try{return new URL(document.referrer).origin+'/';}catch(_){return '';}}
function track(type,which=calculator,options={}){
 if(!started||readConsent()!=='granted'||!Object.hasOwn(C.EVENTS,type))return false;
 const calc=C.CALCULATORS.includes(which)?which:null,key=calc||section;
 try{const data=C.record(readData(),type,calc,environment);localStorage.setItem(STORAGE,JSON.stringify(data));window.dispatchEvent(new Event('nic:statistics-updated'));}catch(_){/* Statistics must never interrupt a calculation or PDF. */}
 try{const id=googleTag(key);if(id){const path=S.pages.find(p=>p[0]===key)?.[2]||'';window.gtag('event',C.EVENTS[type],{send_to:id,page_location:new URL(path,S.ROOT).href,page_title:S.pageMeta(S.current,key).title,page_referrer:cleanReferrer(),calculator_id:calc||'none',method:['save','share_fallback','web_share'].includes(options.method)?options.method:undefined});}}catch(_){/* Tag blockers do not affect calculator behavior. */}
 return true;
}
function rootFor(key){return document.getElementById(key==='rent'?'rentSection':key==='budget'?'budgetSection':'dealCalculatorContent');}
function fingerprint(key){const root=rootFor(key);return root?Array.from(root.querySelectorAll('input,select,textarea')).filter(el=>!el.readOnly&&el.type!=='hidden').map(el=>el.id+':'+(el.type==='checkbox'?el.checked:el.value)).join('|'):'';}
function validCalculation(key){const id=key==='budget'?'budgetNetIncome':key==='rent'?'rentPurchase':'purchase';const v=document.getElementById(id)?.value||'';return Number(v.replace(/\s/g,'').replace(/\./g,'').replace(',','.'))>0;}
function flush(){
 clearTimeout(debounce);debounce=null;const change=pending;pending=null;if(!change||readConsent()!=='granted')return;
 const {key,value,valid}=change;if(value!==snapshots[key]&&valid){snapshots[key]=value;track('calculate',key);}
}
function schedule(key){if(!C.CALCULATORS.includes(key)||readConsent()!=='granted')return;pending={key,value:fingerprint(key),valid:validCalculation(key)};clearTimeout(debounce);debounce=setTimeout(flush,900);}
function begin(){
 if(!started||readConsent()!=='granted')return;
 if(!pageLogged){pageLogged=true;track('page_view',C.CALCULATORS.includes(section)?section:null);}
 if(calculator&&calculator!==lastCalculator){lastCalculator=calculator;snapshots[calculator]=fingerprint(calculator);track('calculator_use',calculator);}
}
function start(info){if(started)return;section=C.SECTIONS.includes(info.section)?info.section:'website';calculator=C.CALCULATORS.includes(info.calculator)?info.calculator:null;started=true;begin();addConsentControl();if(!readConsent())openConsent();}
function changeSection(key){if(!started)return;flush();if(!C.SECTIONS.includes(key))return;section=key;calculator=C.CALCULATORS.includes(key)?key:null;begin();}
function setConsent(value){
 const next=value==='granted'?'granted':'denied';
 try{localStorage.setItem(CONSENT,JSON.stringify({status:next,at:Date.now()}));}catch(_){document.getElementById('nicConsentStatus').textContent='Die Auswahl konnte nicht gespeichert werden. Es wird keine Statistik erfasst.';return;}
 const dialog=document.getElementById('nicConsentDialog');dialog?.close();
 if(next==='granted'){begin();}else{clearTimeout(debounce);pending=null;for(const id of configured)window['ga-disable-'+id]=true;if(googleStarted){window.gtag?.('consent','update',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});location.reload();}}
}
function openConsent(){let dialog=document.getElementById('nicConsentDialog');if(!dialog){
 dialog=document.createElement('dialog');dialog.id='nicConsentDialog';dialog.className='nic-consent';dialog.setAttribute('aria-labelledby','nicConsentTitle');
 const title=document.createElement('h2');title.id='nicConsentTitle';title.textContent='Cookies zustimmen';
 const body=document.createElement('p');body.textContent='Du hast die Wahl: Unsere Kalkulatoren funktionieren auch ohne optionale Cookies. Mit „Zustimmen“ erlaubst du Cookies und ähnliche Speichertechniken für unsere freiwillige Nutzungsstatistik. Damit sehen wir, welche Seiten, Kalkulatoren und PDF-Funktionen genutzt werden. Erfasst werden Aufrufe, Berechnungen, PDF-Downloads und Teilen-Aktionen sowie Geräteart, Betriebssystem und erkennbare Herkunft.';
 const googleInfo=document.createElement('p');googleInfo.textContent='Sofern Google Analytics eingerichtet ist, werden diese Nutzungsdaten nach deiner Zustimmung auch von Google verarbeitet. Dabei können Online-Kennungen und Länderinformationen verarbeitet und Daten in die USA übermittelt werden. Deine eingegebenen Finanz- und Objektdaten werden nicht an Google übermittelt.';
 const hint=document.createElement('p');hint.className='nic-consent-hint';hint.textContent='Mit „Ablehnen“ bleiben die optionale Statistik und Google Analytics ausgeschaltet. Deine Auswahl merken wir bis zu 180 Tage. Du kannst deine Einwilligung jederzeit unten über „Cookie-Hinweis“ mit Wirkung für die Zukunft widerrufen oder ändern.';
 const actions=document.createElement('div');actions.className='nic-consent-actions';for(const [value,label] of [['denied','Ablehnen'],['granted','Zustimmen']]){const b=document.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',()=>setConsent(value));actions.append(b);}const status=document.createElement('p');status.id='nicConsentStatus';status.setAttribute('role','status');dialog.append(title,body,googleInfo,hint,actions,status);document.body.append(dialog);
 }if(!dialog.open)dialog.showModal();}
function addConsentControl(){const footer=document.querySelector('.footer-note')||document.querySelector('.public-footer');if(!footer||document.getElementById('nicConsentSettings'))return;const b=document.createElement('button');b.id='nicConsentSettings';b.type='button';b.className='nic-consent-settings';b.textContent='Cookie-Hinweis';b.addEventListener('click',openConsent);footer.append(b);}
document.addEventListener('input',e=>{if(!e.isTrusted||e.target.matches('[name="dealType"], [readonly]'))return;const root=e.target.closest('#budgetSection,#rentSection,#dealCalculatorContent');if(root&&calculator)schedule(calculator);});
document.addEventListener('change',e=>{if(!e.isTrusted||e.target.matches('[name="dealType"], [readonly]'))return;if(e.target.closest('#budgetSection,#rentSection,#dealCalculatorContent')&&calculator)schedule(calculator);});
document.addEventListener('click',e=>{if(!e.isTrusted)return;if(e.target.closest('#savePdf,#sharePdf'))flush();if(e.target.closest('#budgetApplySuggestions,#ownImportBudgetValues,#applyTradeSuggestions,#rentApplyTradeSuggestions,#saveTrades,#rentSaveTrades,[data-vk-source]')){const key=calculator;setTimeout(()=>schedule(key),0);}},true);
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden')flush();});
window.addEventListener('storage',e=>{if(e.key===CONSENT){if(readConsent()==='granted')begin();else if(googleStarted)location.reload();}});
window.NICAnalytics={start,changeSection,track,flush,readConsent,openConsent,STORAGE,CONSENT};
})();
