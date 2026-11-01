(function(){
'use strict';
const S=window.NICSettings;if(!S)return;
const page=document.documentElement.dataset.nicPage||'website';
let activePage=page;
function social(s){let nav=document.getElementById('nicSocialLinks');const footer=document.querySelector('.footer-note')||document.querySelector('.public-footer');if(!footer)return;if(!nav){nav=document.createElement('nav');nav.id='nicSocialLinks';nav.setAttribute('aria-label','Social Media');nav.className='nic-social-links';footer.append(nav);}nav.replaceChildren();S.portals.forEach(([key,label])=>{const url=s.social[key];if(!url)return;const a=document.createElement('a');a.href=url;a.textContent=label;a.target='_blank';a.rel='noopener noreferrer';nav.append(a);});nav.hidden=!nav.childElementCount;}
function company(s){if(/\/impressum\/?$/.test(location.pathname)&&!document.getElementById('heroTitle')){location.replace(new URL('#impressum',S.ROOT).href);return;}const root=document.getElementById('companyContent');if(!root)return;root.replaceChildren();const parts=S.imprint(s);if(!parts.length){const p=document.createElement('p');p.textContent='Die Anbieterangaben wurden noch nicht hinterlegt.';root.append(p);return;}for(const {label,value} of parts){const h=document.createElement('h2');h.textContent=label;const p=document.createElement('p');p.textContent=value;root.append(h,p);}}
function apply(){if(!S.current)return;S.apply(S.current,activePage);social(S.current);company(S.current);if(adminOpen)document.title=(location.hash==='#account'?'Deine Nutzerdaten':'Admin-Bereich')+' | Neustart ImmoCheck';window.NICLegal?.refresh();}
function modePage(){if(document.getElementById('dealTypeRent')?.getAttribute('aria-pressed')==='true')return 'rent';return document.querySelector('input[name="dealType"]:checked')?.value||'budget';}
function updateMode(){activePage=modePage();try{localStorage.setItem('nic_last_calculator_v1',activePage);}catch(_){}const path=S.pages.find(p=>p[0]===activePage)?.[2];if(path!==undefined)history.replaceState(null,'',new URL(path,S.ROOT).pathname+location.search+(/^#(?:admin(?:-|$)|account$|impressum$|datenschutz$|agbs$|haftungsausschluss$|cookie-hinweis$)/.test(location.hash)?location.hash:''));apply();window.NICAnalytics?.changeSection(activePage);}
function activate(key){if(key==='rent')document.getElementById('dealTypeRent')?.click();else{const id={budget:'dealTypeBudget',own:'dealTypeOwn',flip:'dealTypeFlip'}[key],el=document.getElementById(id);if(el){el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));}}}
document.querySelectorAll('[data-legal-placeholder="impressum"]').forEach(a=>a.href=new URL('impressum/',S.ROOT).href);
document.querySelectorAll('input[name="dealType"]').forEach(el=>el.addEventListener('change',()=>{if(el.checked)updateMode();}));
document.getElementById('dealTypeRent')?.addEventListener('click',updateMode);
window.addEventListener('storage',e=>{if(e.key===S.KEY)S.init().then(apply).catch(()=>{});});
window.addEventListener('nic-settings-updated',apply);
window.addEventListener('pageshow',()=>{if(S.current)S.init().then(apply).catch(()=>{});});
// Keep the calculator header and state while opening administration below it.
const account=document.getElementById('nicAccountLink'),hero=document.querySelector('.app > .hero');
let adminPanel=null,adminFrame=null,headerSnapshot=null,adminOpen=false;
function setAdmin(open){
 if(!hero||!account)return;
 if(open&&!adminOpen){
  headerSnapshot={title:document.getElementById('heroTitle').innerHTML,text:document.getElementById('heroText').textContent,titleAttr:document.title};
  if(!adminPanel){
   adminPanel=document.createElement('section');adminPanel.id='nicAdminPanel';adminPanel.setAttribute('aria-label','Admin-Bereich');
   const close=document.createElement('button');close.type='button';close.className='nic-admin-back';close.textContent='← Zu den Kalkulatoren';close.addEventListener('click',()=>{history.pushState(null,'',location.pathname+location.search);setAdmin(false);});
   adminFrame=document.createElement('iframe');adminFrame.title='Einstellungen im Admin-Bereich';adminFrame.id='nicAdminFrame';
   const profile=location.hash==='#account';const section=location.hash.slice(7);adminFrame.src=profile?new URL('user-data.html?embedded=1&release='+encodeURIComponent(document.documentElement.dataset.nicRelease||'current'),S.ROOT).href:new URL('admin.html?embedded=1&release='+encodeURIComponent(document.documentElement.dataset.nicRelease||'current')+(['company','layout','social','meta','legal','users','stats'].includes(section)?'#'+section:''),S.ROOT).href;
   adminPanel.append(close,adminFrame);hero.after(adminPanel);
  }
  adminOpen=true;document.body.classList.add('nic-admin-open');adminPanel.hidden=false;
  const profile=location.hash==='#account';adminPanel.setAttribute('aria-label',profile?'Deine Nutzerdaten':'Admin-Bereich');adminFrame.title=profile?'Deine Nutzerdaten':'Einstellungen im Admin-Bereich';document.getElementById('heroTitle').textContent=profile?'Deine Nutzerdaten':'Admin-Bereich';document.getElementById('heroText').textContent=profile?'Hier kannst du deine Daten ändern oder dein Benutzerkonto unwiderruflich löschen.':'Verwalte Unternehmensdaten, Layout, Logos, Social Media, Meta-Daten, Nutzereinstellungen und Statistik.';
  document.title=(location.hash==='#account'?'Deine Nutzerdaten':'Admin-Bereich')+' | Neustart ImmoCheck';account.setAttribute('aria-expanded','true');account.setAttribute('aria-controls','nicAdminPanel');
  adminFrame.contentWindow?.postMessage({type:'nic-request-logo'},location.origin);
 }else if(!open&&adminOpen){
  adminOpen=false;document.body.classList.remove('nic-admin-open');adminPanel.hidden=true;
  document.getElementById('heroTitle').innerHTML=headerSnapshot.title;document.getElementById('heroText').textContent=headerSnapshot.text;document.title=headerSnapshot.titleAttr;
  account.setAttribute('aria-expanded','false');if(S.current)S.applyLogo(S.current.websiteLogo);account.focus();
 }
}
if(account&&hero){
 account.addEventListener('click',e=>{if(e.button||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;e.preventDefault();if(!adminOpen)history.pushState(null,'',location.pathname+location.search+'#admin');setAdmin(true);});
 window.addEventListener('popstate',()=>setAdmin(/^#(?:admin(?:-|$)|account$)/.test(location.hash)));
 window.addEventListener('hashchange',()=>setAdmin(/^#(?:admin(?:-|$)|account$)/.test(location.hash)));
 window.addEventListener('message',e=>{if(e.origin!==location.origin||e.source!==adminFrame?.contentWindow)return;
  if(e.data?.type==='nic-admin-height'&&Number.isFinite(e.data.height))adminFrame.style.height=Math.min(50000,Math.max(300,e.data.height))+'px';
  if(adminOpen&&e.data?.type==='nic-logo-preview')S.applyLogo(e.data.value,e.data.alt,e.data.website);
 });
}
// Independent fifth main-menu entry. Existing modes and their storage remain untouched.
(function addFinancingTab(){
 const row=document.querySelector('.deal-type-row');
 if(!row||document.getElementById('nicFinancingTab'))return;
 const tab=document.createElement('a');
 tab.id='nicFinancingTab';
 tab.className='deal-type-option';
 tab.href=new URL('finanzierungsrechner/',S.ROOT).href;
 tab.innerHTML='<input type="radio" name="nicFinancingMenuSelect" aria-label="Finanzierungsrechner auswählen" tabindex="-1"><span><strong>Finanzierungsrechner</strong><small>Darlehen, Tilgung, Sondertilgung und Restschuld</small></span>';
 // The fifth option uses the exact same direct-child structure and the original
 // .deal-type-option typography, spacing and input-radio rules as the first four.
 tab.style.cssText='text-decoration:none;cursor:pointer;';
 tab.querySelector('input').addEventListener('click',event=>{event.preventDefault();location.href=tab.href;});

 row.append(tab);
 // Shared row-layout rule: any unpaired final calculator card spans both columns.
 if(!document.getElementById('nicMenuOddCardLayout')){
   const css=document.createElement('style');css.id='nicMenuOddCardLayout';
   css.textContent='.deal-type-row > :last-child:nth-child(odd){grid-column:1 / -1;}';
   document.head.append(css);
 }
})();
if(S.current){if(['budget','own','rent','flip'].includes(page))activate(page);activePage=page;apply();setAdmin(/^#(?:admin(?:-|$)|account$)/.test(location.hash));}
S.init().then(()=>{if(['budget','own','rent','flip'].includes(page))activate(page);activePage=page;apply();setAdmin(/^#(?:admin(?:-|$)|account$)/.test(location.hash));window.NICAnalytics?.start({section:page,calculator:document.getElementById('heroTitle')?modePage():null});}).catch(err=>console.warn('Einstellungen:',err.message));

/* Scoped renovation controls; keep calculation handlers intact. */
(function renovationControls(){
  function enhance(){
    if(typeof document.querySelectorAll!=='function')return;
    document.querySelectorAll('#applyTradeSuggestions').forEach(button=>{
      if(button.dataset.nicEnhanced==='1')return;
      const panel=button.closest('.reno-inline-panel, .reno-sheet, .card');
      if(!panel)return;
      button.dataset.nicEnhanced='1';
      button.textContent='Vorschläge übernehmen';
      const row=document.createElement('div');
      row.className='nic-reno-action-row';
      button.before(row);
      row.append(button);
      const clear=document.createElement('button');
      clear.type='button';
      clear.className='nic-clear-reno';
      clear.textContent='X';
      clear.setAttribute('aria-label','Sanierungseingaben dieser Maske löschen');
      clear.addEventListener('click',()=>{
        panel.querySelectorAll('#tradeList input.trade-amount, #tradeList input.trade-area').forEach(input=>{
          if(input.disabled)return;
          input.value='0';
          input.dispatchEvent(new Event('input',{bubbles:true}));
          input.dispatchEvent(new Event('change',{bubbles:true}));
        });
      });
      row.append(clear);
    });
  }
  function enhanceBudget(){
    if(typeof document.querySelectorAll!=='function')return;
    document.querySelectorAll('#budgetApplySuggestions').forEach(button=>{
      if(button.dataset.nicEnhanced==='1')return;
      const panel=document.getElementById('budgetExpensesSection');
      if(!panel)return;
      button.dataset.nicEnhanced='1';
      const row=document.createElement('div');
      row.className='nic-reno-action-row';
      button.before(row);
      row.append(button);
      const clear=document.createElement('button');
      clear.type='button';
      clear.className='nic-clear-reno';
      clear.textContent='X';
      clear.setAttribute('aria-label','Feste monatliche Ausgaben auf null setzen');
      clear.addEventListener('click',()=>{
        panel.querySelectorAll('#budgetExpensesBody input:not([type="hidden"]):not([type="range"])').forEach(input=>{
          if(input.disabled||input.readOnly)return;
          if(input.type==='checkbox'||input.type==='radio')return;
          input.value='0';
          input.dispatchEvent(new Event('input',{bubbles:true}));
          input.dispatchEvent(new Event('change',{bubbles:true}));
        });
      });
      row.append(clear);
      panel.querySelectorAll('*').forEach(el=>{
        if(!el.children.length && /^Vorschlag gesamt\s*:/i.test(el.textContent?.trim()||'')){
          el.classList.add('nic-budget-proposal-total');
        }
      });
    });
  }
  function enhanceRent(){
    if(typeof document.querySelectorAll!=='function')return;
    document.querySelectorAll('#rentApplyTradeSuggestions').forEach(button=>{
      if(button.dataset.nicEnhanced==='1')return;
      const panel=document.getElementById('rentRenoPanel')||button.closest('.card,section');
      if(!panel)return;
      button.dataset.nicEnhanced='1';
      button.textContent='Vorschläge übernehmen';
      const row=document.createElement('div');
      row.className='nic-reno-action-row';
      button.before(row);
      row.append(button);
      const clear=document.createElement('button');
      clear.type='button';
      clear.className='nic-clear-reno';
      clear.textContent='X';
      clear.setAttribute('aria-label','Modernisierungseingaben der Vermietung auf null setzen');
      clear.addEventListener('click',()=>{
        panel.querySelectorAll('input.rent-trade-amount,input.rent-trade-area').forEach(input=>{
          if(input.disabled)return;
          input.value='0';
          input.dispatchEvent(new Event('input',{bubbles:true}));
          input.dispatchEvent(new Event('change',{bubbles:true}));
        });
      });
      row.append(clear);
    });
  }
  enhance();
  enhanceBudget();
  enhanceRent();
  if(typeof document.addEventListener==='function')document.addEventListener('click',()=>queueMicrotask(()=>{enhance();enhanceBudget();enhanceRent();}));
})();
})();
