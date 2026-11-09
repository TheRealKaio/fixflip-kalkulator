(function(){
'use strict';
const S=window.NICSettings;if(!S)return;
const page=document.documentElement.dataset.nicPage||'website';
let activePage=page;
const contentPage=['settlement','prices','why','about','contact','login'].includes(page);
function company(s){if(/\/impressum\/?$/.test(location.pathname)&&!document.getElementById('heroTitle')){location.replace(new URL('#impressum',S.ROOT).href);return;}const root=document.getElementById('companyContent');if(!root)return;root.replaceChildren();const parts=S.imprint(s);if(!parts.length){const p=document.createElement('p');p.textContent='Die Anbieterangaben wurden noch nicht hinterlegt.';root.append(p);return;}for(const {label,value} of parts){const h=document.createElement('h2');h.textContent=label;const p=document.createElement('p');p.textContent=value;root.append(h,p);}}
function apply(){if(!S.current)return;S.apply(S.current,activePage);syncCalculatorMenu();window.NICShell?.refresh(S.current);company(S.current);if(adminOpen)document.title=(location.hash==='#account'?'Deine Nutzerdaten':'Admin-Bereich')+' | Neustart ImmoCheck';window.NICLegal?.refresh();}
// A single route-based selection for every navigation card, including financing.
function syncCalculatorMenu(){
 S.syncCalculatorMenu(activePage);
}

function modePage(){if(document.getElementById('dealTypeRent')?.getAttribute('aria-pressed')==='true')return 'rent';return document.querySelector('input[name="dealType"]:checked')?.value||'budget';}
function updateMode(){activePage=modePage();try{localStorage.setItem('nic_last_calculator_v1',activePage);}catch(_){}const path=S.pages.find(p=>p[0]===activePage)?.[2],accountRoute=/^#(?:admin(?:-|$)|account$)/.test(location.hash);if(path!==undefined&&!contentPage&&!accountRoute)history.replaceState(null,'',new URL(path,S.ROOT).pathname+location.search+(/^#(?:impressum$|datenschutz$|agbs$|haftungsausschluss$|cookie-hinweis$)/.test(location.hash)?location.hash:''));apply();window.NICAnalytics?.changeSection(activePage);}
function activate(key){if(key==='rent')document.getElementById('dealTypeRent')?.click();else{const id={budget:'dealTypeBudget',own:'dealTypeOwn',flip:'dealTypeFlip'}[key],el=document.getElementById(id);if(el){el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));}}}
window.addEventListener('nic-select-calculator',event=>{
 const key=event.detail;
 if(key==='finance'){activePage=key;apply();window.NICAnalytics?.changeSection(key);return;}
 activate(key);
 activePage=key;apply();
});
document.querySelectorAll('[data-legal-placeholder="impressum"]').forEach(a=>a.href=new URL('impressum/',S.ROOT).href);
document.querySelectorAll('input[name="dealType"]').forEach(el=>el.addEventListener('change',()=>{if(el.checked)updateMode();}));
document.getElementById('dealTypeRent')?.addEventListener('click',updateMode);
window.addEventListener('storage',e=>{if(e.key===S.KEY)S.init().then(apply).catch(()=>{});});
window.addEventListener('nic-settings-updated',apply);
window.addEventListener('pageshow',()=>{if(S.current)S.init().then(apply).catch(()=>{});});
// Keep the calculator header and state while opening administration below it.
const account=document.getElementById('nicAccountLink'),hero=document.querySelector('.app > .hero');
let adminPanel=null,adminFrame=null,adminLogout=null,headerSnapshot=null,adminOpen=false,accountReturnUrl=null;
function syncAccountLink(){
 if(!account)return;
 const access=window.NICAccess,authenticated=!!(access?.enabled&&access.user),admin=authenticated&&access.user.role==='admin';
 const label=account.querySelector?.('span');
 const destination=admin?'#admin':authenticated?'#account':'#anmelden';
 const accountLabel=admin?'Zum Adminportal':authenticated?'Zum Nutzerportal':'Jetzt anmelden';
 if(label)label.textContent=accountLabel;
 account.href=new URL(destination,S.ROOT).href;
 account.setAttribute('aria-label',accountLabel);
 if(authenticated)account.setAttribute('data-nic-destination',admin?'admin':'portal');else account.removeAttribute?.('data-nic-destination');
 if(adminLogout)adminLogout.hidden=!(adminOpen&&authenticated&&access.user.role==='admin');
}
window.addEventListener('nic-auth-changed',syncAccountLink);
function adminPanelRoute(){
 const profile=location.hash==='#account';
 const section=location.hash.startsWith('#admin-')?location.hash.slice(7):'';
 const allowed=['company','layout','social','meta','legal','users','stats'];
 const selected=allowed.includes(section)?section:'';
 return {profile,section:selected,key:profile?'account':'admin'+(selected?'-'+selected:'')};
}
function adminPanelUrl(route){
 const release=encodeURIComponent(document.documentElement.dataset.nicRelease||'current');
 if(route.profile)return new URL('user-data.html?embedded=1&release='+release,S.ROOT).href;
 return new URL('admin.html?embedded=1&release='+release+(route.section?'#'+route.section:''),S.ROOT).href;
}
function setAdmin(open){
 if(!hero||!account)return;
 if(open&&location.hash==='#account'&&location.pathname!==new URL('/',S.ROOT).pathname){accountReturnUrl=location.pathname+location.search;history.replaceState(null,'',new URL('#account',S.ROOT).href);}
 if(!open&&adminOpen){
  adminOpen=false;document.body.classList.remove('nic-admin-open');document.documentElement.classList.remove('nic-admin-open');adminPanel.hidden=true;syncAccountLink();
  document.getElementById('heroTitle').innerHTML=headerSnapshot.title;document.getElementById('heroText').textContent=headerSnapshot.text;document.title=headerSnapshot.titleAttr;
  account.setAttribute('aria-expanded','false');if(S.current)S.applyLogo(S.current.websiteLogo);account.focus();
  return;
 }
 if(!open)return;
 if(!adminOpen)headerSnapshot={title:document.getElementById('heroTitle').innerHTML,text:document.getElementById('heroText').textContent,titleAttr:document.title};
 if(!adminPanel){
  adminPanel=document.createElement('section');adminPanel.id='nicAdminPanel';adminPanel.setAttribute('aria-label','Admin-Bereich');
  const toolbar=document.createElement('div');toolbar.className='nic-admin-toolbar';
  const close=document.createElement('button');close.type='button';close.className='nic-admin-back';close.textContent='← Zu den Kalkulatoren';close.addEventListener('click',()=>{history.pushState(null,'',accountReturnUrl||location.pathname+location.search);accountReturnUrl=null;setAdmin(false);});
  adminLogout=document.createElement('button');adminLogout.type='button';adminLogout.className='nic-admin-logout';adminLogout.textContent='ABMELDEN';adminLogout.hidden=true;adminLogout.addEventListener('click',async()=>{if(!window.NICAccess?.logout)return;adminLogout.disabled=true;try{await window.NICAccess.logout();}catch(error){adminLogout.disabled=false;window.alert(error.message||'Abmelden fehlgeschlagen.');}});
  toolbar.append(close,adminLogout);
  adminFrame=document.createElement('iframe');adminFrame.title='Einstellungen im Admin-Bereich';adminFrame.id='nicAdminFrame';
  adminPanel.append(toolbar,adminFrame);hero.after(adminPanel);
 }
 adminOpen=true;document.body.classList.add('nic-admin-open');document.documentElement.classList.add('nic-admin-open');adminPanel.hidden=false;syncAccountLink();
 const route=adminPanelRoute();
 if(adminFrame.dataset.nicRoute!==route.key){adminFrame.dataset.nicRoute=route.key;adminFrame.src=adminPanelUrl(route);}
 adminPanel.setAttribute('aria-label',route.profile?'Deine Nutzerdaten':'Admin-Bereich');adminFrame.title=route.profile?'Deine Nutzerdaten':'Einstellungen im Admin-Bereich';
 document.getElementById('heroTitle').textContent=route.profile?'Deine Nutzerdaten':'Admin-Bereich';document.getElementById('heroText').textContent=route.profile?'Hier kannst du deine Daten ändern oder dein Benutzerkonto unwiderruflich löschen.':'Verwalte Unternehmensdaten, Layout, Logos, Social Media, Meta-Daten, Nutzereinstellungen und Statistik.';
 document.title=(route.profile?'Deine Nutzerdaten':'Admin-Bereich')+' | Neustart ImmoCheck';account.setAttribute('aria-expanded','true');account.setAttribute('aria-controls','nicAdminPanel');
 adminFrame.contentWindow?.postMessage({type:'nic-request-logo'},location.origin);
}
if(account&&hero){
 account.addEventListener('click',e=>{
  if(e.button||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
  if(window.NICAccess?.enabled&&window.NICAccess.user){
   e.preventDefault();
   if(!adminOpen)accountReturnUrl=location.pathname+location.search;
   const target=new URL(window.NICAccess.user.role==='admin'?'#admin':'#account',S.ROOT);
   if(location.pathname!==target.pathname||location.hash!==target.hash)history.pushState(null,'',target.href);
   setAdmin(true);
   return;
  }
  e.preventDefault();if(!adminOpen)history.pushState(null,'',location.pathname+location.search+'#admin');setAdmin(true);
 });
 const syncAdminRoute=()=>{const open=/^#(?:admin(?:-|$)|account$)/.test(location.hash);if(!open)accountReturnUrl=null;setAdmin(open);};
 window.addEventListener('popstate',syncAdminRoute);
 window.addEventListener('hashchange',syncAdminRoute);
 window.addEventListener('message',e=>{if(e.origin!==location.origin||e.source!==adminFrame?.contentWindow)return;
  if(e.data?.type==='nic-auth-changed'){window.NICAccess?.refresh?.().then(syncAccountLink).catch(()=>syncAccountLink());return;}
  if(e.data?.type==='nic-admin-height'&&Number.isFinite(e.data.height))adminFrame.style.height=Math.min(50000,Math.max(300,e.data.height))+'px';
  if(adminOpen&&e.data?.type==='nic-logo-preview')S.applyLogo(e.data.value,e.data.alt,e.data.website);
 });
}
window.NICAccess?.init?.().then(syncAccountLink).catch(()=>syncAccountLink());
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
        if(!window.confirm('Möchtest du die Eingaben dieser Maske wirklich löschen?'))return;
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
        if(!window.confirm('Möchtest du die Eingaben dieser Maske wirklich löschen?'))return;
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
        if(!window.confirm('Möchtest du die Eingaben dieser Maske wirklich löschen?'))return;
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
  function tidyTotals(){
    if(typeof document.querySelectorAll!=='function')return;
    const renovation=document.getElementById('renoBackdrop');
    if(renovation){
      const totals=[...renovation.querySelectorAll('*')].filter(el=>!el.children.length && /^Vorschlag gesamt\s*:/i.test((el.textContent||'').trim()));
      if(totals.length>1)totals.slice(1).forEach(el=>{el.hidden=true;el.style.display='none'});
    }
    const rent=document.getElementById('rentRenoPanel');
    const total=document.getElementById('rentRenoSheetTotal');
    if(rent&&total){
      const fields=[...rent.querySelectorAll('input.rent-trade-amount')];
      const values=fields.map(el=>Number((el.placeholder||'0').replace(/\./g,'').replace(',','.'))||0);
      const amount=values.reduce((a,b)=>a+b,0);
      total.textContent='Vorschlag gesamt: '+amount.toLocaleString('de-DE')+' € · ohne Puffer';
      total.classList.add('nic-rental-proposal-total');
    }
  }
  function markBudgetTransferButtons(){
    document.querySelectorAll('button,input[type="button"],input[type="submit"]').forEach(button=>{
      const label=(button.tagName==='INPUT'?button.value:button.textContent||'').trim().replace(/\s+/g,' ');
      if(/^Budgetwerte übernehmen$/i.test(label))button.classList.add('nic-green-budget-transfer');
    });
  }
  markBudgetTransferButtons();
  enhance();
  enhanceBudget();
  enhanceRent();
  tidyTotals();
  if(typeof document.addEventListener==='function')document.addEventListener('click',()=>queueMicrotask(()=>{enhance();enhanceBudget();enhanceRent();tidyTotals();markBudgetTransferButtons();}));
})();
})();
