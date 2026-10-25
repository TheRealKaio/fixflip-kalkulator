(function(){
'use strict';
const S=window.NICSettings;if(!S)return;
const labels=S.legalLabels||{impressum:'Impressum',datenschutz:'Datenschutz',agbs:'AGBs',haftungsausschluss:'Haftungsausschluss'};
const hero=document.querySelector('.app > .hero'),title=document.getElementById('heroTitle'),text=document.getElementById('heroText');
if(!hero||!title){if(/\/impressum\/?$/.test(location.pathname))location.replace(new URL('#impressum',S.ROOT).href);return;}
let active=null,panel=null,article=null,snapshot=null,opener=null;
const key=()=>Object.hasOwn(labels,location.hash.slice(1))?location.hash.slice(1):null;
function node(tag,value,parent){const el=document.createElement(tag);if(value!==undefined)el.textContent=value;if(parent)parent.append(el);return el;}
function operator(){const s=S.current;if(!s)return;const box=node('section',undefined,article);box.className='nic-legal-operator';node('h2',active==='datenschutz'?'Verantwortlicher':'Anbieter',box);const wanted=['Anbieter','Vertreten durch','Anschrift','Kontakt'];const parts=S.imprint(s).filter(x=>wanted.includes(x.label));if(!parts.length){node('p','Die Betreiberangaben wurden noch nicht veröffentlicht.',box);return;}for(const item of parts){const p=node('p',item.value,box);p.dataset.companyGroup=item.label;}}
function render(){
 if(!article||!active)return;article.replaceChildren();
 if(S.current?.legal?.[active]){article.append(S.legalFragment(S.current.legal[active],S.current));}
 else if(active==='cookie-hinweis'){article.append(S.legalFragment(S.legalSource(S.current,active),S.current));}
 else if(active==='impressum'){
  const parts=S.current?S.imprint(S.current):[];
  if(!parts.length)node('p','Die Betreiberangaben wurden noch nicht veröffentlicht.',article);
  for(const {label,value} of parts){node('h2',label,article);node('p',value,article);}
 }else if(active==='haftungsausschluss'){
  const source=document.querySelector('#legalDisclaimerPage .legal-page-card');
  if(source)for(const child of source.children){if(child.tagName==='H1')continue;article.append(child.cloneNode(true));}
 }else{
  operator();
  node('h2','Inhalt noch nicht hinterlegt',article);
  node('p',active==='datenschutz'?'Die vollständige Datenschutzerklärung wird noch erstellt. Die hier angezeigten Betreiberangaben ersetzen keine vollständige Datenschutzerklärung.':'Ein vollständiger AGB-Text wurde noch nicht hinterlegt. Die hier angezeigten Anbieterangaben stellen keine Allgemeinen Geschäftsbedingungen dar.',article);
 }
 if(active==='cookie-hinweis'){const button=node('button','Cookie-Einstellungen ändern',article);button.type='button';button.addEventListener('click',()=>window.NICAnalytics?.openConsent());}
}
function close(){if(!active)return;active=null;document.body.classList.remove('nic-legal-open');panel.hidden=true;title.innerHTML=snapshot.title;text.textContent=snapshot.text;document.title=snapshot.documentTitle;}
function open(next){
 if(!next){const was=active;close();if(was)opener?.focus();return;}
 if(!active)snapshot={title:title.innerHTML,text:text.textContent,documentTitle:document.title};
 if(!panel){panel=node('section');panel.id='nicLegalPanel';const back=node('button','← Zu den Kalkulatoren',panel);back.type='button';back.className='nic-admin-back';back.addEventListener('click',()=>{history.pushState(null,'',location.pathname+location.search);open(null);});const nav=node('nav',undefined,panel);nav.setAttribute('aria-label','Rechtliche Bereiche');for(const [k,label]of Object.entries(labels)){const a=node('a',label,nav);a.href='#'+k;a.dataset.nicLegal=k;}article=node('article',undefined,panel);article.className='nic-legal-card';hero.after(panel);}
 active=next;panel.hidden=false;document.body.classList.add('nic-legal-open');panel.setAttribute('aria-label',labels[next]);title.textContent=labels[next];text.textContent='Rechtliche Informationen zu Neustart ImmoCheck';document.title=labels[next]+' | Neustart ImmoCheck';
 panel.querySelectorAll('[data-nic-legal]').forEach(a=>{if(a.dataset.nicLegal===next)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});render();
 document.getElementById('sheetBackdrop')?.classList.remove('show');document.getElementById('legalDisclaimerPage')?.classList.remove('show');
}
function route(){if(S.current)open(key());}
// Close before the admin takes its header snapshot; open after it restores the calculator header.
for(const event of ['popstate','hashchange']){window.addEventListener(event,()=>{if(active&&key()!==active)close();},true);window.addEventListener(event,route);}
document.querySelectorAll('[data-legal-placeholder]').forEach(a=>{const k=a.dataset.legalPlaceholder;if(Object.hasOwn(labels,k)){a.href='#'+k;a.removeAttribute('target');}});
window.addEventListener('click',e=>{
 const el=e.target.closest?.('[data-legal-placeholder],[data-nic-legal],#legalDisclaimerSheetCta,#nicAccountLink');if(!el||e.button||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
 if(el.id==='nicAccountLink'){close();return;}
 const next=el.dataset.legalPlaceholder||el.dataset.nicLegal||(el.id==='legalDisclaimerSheetCta'?'haftungsausschluss':null);if(!Object.hasOwn(labels,next))return;
 e.preventDefault();e.stopImmediatePropagation();opener=el;
 if(location.hash!=='#'+next)history.pushState(null,'',location.pathname+location.search+'#'+next);
 // Notify the existing admin router before displaying the legal content.
 window.dispatchEvent(new Event('hashchange'));title.setAttribute('tabindex','-1');title.focus({preventScroll:true});hero.scrollIntoView({block:'start'});
},true);
window.NICLegal={refresh(){if(active){title.textContent=labels[active];text.textContent='Rechtliche Informationen zu Neustart ImmoCheck';document.title=labels[active]+' | Neustart ImmoCheck';render();}else if(key())open(key());}};
route();
})();
