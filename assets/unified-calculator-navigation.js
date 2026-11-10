/* One controller for all five calculator tiles. Financing remains an isolated module. */
(()=>{
'use strict';
/* FINANCE_MODULE */
/* CALCULATOR_REGISTRY */
const routes=Object.fromEntries(calculators.map(item=>[item.path,item.id]));
window.NICCalculators=Object.freeze({
 list:Object.freeze(calculators.map(item=>Object.freeze(item))),
 get active(){return active;},
 get(id){return calculators.find(item=>item.id===id)||null;}
});
let active=null,financeRoot=null,bypass=false;
function select(key,push=false){
 if(!calculators.some(item=>item.id===key))throw new Error('Unknown calculator: '+key);
 document.body.classList.remove('nic-home-active');
 if(active===key)return;
 const menu=document.querySelector('.deal-type-card');if(!menu)return;
 const y=scrollY,previousURL=location.href;
 if(key==='finance'&&!financeRoot){
  const host=document.createElement('div');host.id='nicFinanceModule';host.hidden=true;menu.after(host);
  financeRoot=createFinance(host);
 }
 document.body.classList.toggle('nic-finance-active',key==='finance');
 const host=document.getElementById('nicFinanceModule');if(host)host.hidden=key!=='finance';
 bypass=true;
 try{
  // The legacy handler recognizes only budget, own, rent and flip.
  // Financing has its own Shadow DOM module; forwarding 'finance' to the
  // legacy four-calculator handler leaves its DOM and calculations undefined.
  if(key!=='finance')window.dispatchEvent(new CustomEvent('nic-select-calculator',{detail:key}));
 }finally{bypass=false;}
 if(key==='finance'){
  document.getElementById('heroTitle').innerHTML=financeHeader[0];
  document.getElementById('heroText').textContent=financeHeader[1];
 }
 window.NICHeader?.refresh();
 active=key;
 document.documentElement.dataset.calculator=key;
 document.body.dataset.calculator=key;
 window.dispatchEvent(new CustomEvent('nic-calculator-changed',{detail:{id:key}}));
 const path=Object.keys(routes).find(p=>routes[p]===key);
 if(push){history.replaceState(history.state,'',previousURL);history.pushState({calculator:key},'',path+location.search);}
 try{localStorage.setItem('nic_last_calculator_v1',key);}catch(_){}
 window.NICSettings?.syncCalculatorMenu(key);
 window.scrollTo({top:y,left:0,behavior:'instant'});
}
document.addEventListener('click',event=>{
 if(bypass||event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 const tile=event.target.closest('.deal-type-row > .deal-type-option');
 if(tile){
  const key=tile.dataset.calculator||routes[new URL(tile.dataset.href||tile.href||location.href,location.href).pathname.toLowerCase()];
  if(!key)return;
  event.preventDefault();event.stopImmediatePropagation();select(key,true);return;
 }
 if(active==='finance'){
  const button=event.target.closest('.bottom button');if(!button)return;
  const id=button.classList.contains('bottom-primary')?'newCalc':button.classList.contains('bottom-save')?'download':'share';
  event.preventDefault();event.stopImmediatePropagation();financeRoot.getElementById(id).click();
 }
},true);
window.addEventListener('popstate',()=>{const key=routes[location.pathname.toLowerCase()];if(key)select(key);else if(['/', '/index.html'].includes(location.pathname.toLowerCase()))initWelcome();});
function createSiteNavigation(){
 const links=[['/nebenkostenabrechnung/','Mieterabrechnung'],['/preise/','Preise'],['/warum-immocheck/','Warum ImmoCheck?']];
 const header=document.querySelector('.nic-brand-bar')||document.querySelector('.brand-logo-wrap')?.closest('header')||document.querySelector('header');
 if(header&&!header.querySelector('[data-nic-site-nav]')){
  const nav=document.createElement('nav');nav.dataset.nicSiteNav='';nav.setAttribute('aria-label','Hauptnavigation');
  for(const [href,label] of links){const a=document.createElement('a');a.href=href;a.textContent=label;nav.append(a);}
  nav.id='nicSiteNavigation';
  const toggle=document.createElement('button');toggle.type='button';toggle.className='nic-menu-toggle';toggle.setAttribute('aria-label','Menü öffnen');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls',nav.id);toggle.innerHTML='<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';
  function setOpen(open){toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Menü schließen':'Menü öffnen');nav.classList.toggle('is-open',open);}
  toggle.addEventListener('click',()=>setOpen(toggle.getAttribute('aria-expanded')!=='true'));
  document.addEventListener('click',event=>{if(!header.contains(event.target))setOpen(false);});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){setOpen(false);toggle.focus();}});
  nav.addEventListener('click',event=>{if(event.target.closest('a'))setOpen(false);});
  header.append(nav,toggle);
 }
}
function initWelcome(){
 if(document.documentElement.dataset.nicPage!=='website')return;
 const main=document.querySelector('main.section')||document.querySelector('main'),menu=document.querySelector('.deal-type-card');
 if(!main)return;
 const title=document.getElementById('heroTitle'),text=document.getElementById('heroText');
 const settings=window.NICSettings.current,home=settings.meta.website;
 if(!/^#(?:admin(?:-|$)|account$|impressum$|agbs$|datenschutz$|haftungsausschluss$|cookie-hinweis$)/.test(location.hash)){
  if(title&&title.textContent!==home.homeTitle)title.textContent=home.homeTitle;
  if(text&&text.textContent!==home.homeDescription)text.textContent=home.homeDescription;
  window.NICSettings.applyMeta(settings,'website');window.NICHeader?.refresh();
 }
 let intro=document.getElementById('nic-home-intro');
 if(!intro){
  const template=document.createElement('template');template.innerHTML=''/* HOME_MARKUP */;
  intro=template.content.firstElementChild;
 }
 if(intro.parentElement!==main)main.prepend(intro);
 const settlement=intro.querySelector('[data-home-settlement]');
 settlement.querySelector('strong').textContent=home.settlementButtonTitle;
 settlement.querySelector('small').textContent=home.settlementButtonText;
 if(home.settlementButtonUrl){settlement.href=home.settlementButtonUrl;settlement.removeAttribute('aria-disabled');}else{settlement.removeAttribute('href');settlement.setAttribute('aria-disabled','true');}
 const content=window.NICSettings.current.content.welcome;
 intro.querySelector('[data-home-title]').textContent=content.title;
 intro.querySelector('[data-home-description]').replaceChildren(window.NICSettings.legalFragment(content.description,window.NICSettings.current));

 // Copy the existing controls' content and classes; do not create a second
 // visual button system or duplicate calculator radio inputs and IDs.
 if(menu&&!intro.dataset.controlsSynced){
  for(const link of intro.querySelectorAll('a[data-calculator]')){
   const item=calculators.find(item=>item.id===link.dataset.calculator);
   const original=menu.querySelector('[data-href="'+item.path+'"]');
   if(!original)continue;
   if(!original.querySelector('.nic-menu-icon')&&link.querySelector('.nic-menu-icon'))continue;
   link.className=original.className.replace(/\b(?:nic-tile-active|current)\b/g,'').trim();
   link.dataset.href=item.path;
   link.innerHTML=original.innerHTML;
   link.querySelectorAll('input').forEach(input=>input.remove());
  }
  intro.dataset.controlsSynced='true';
 }
 document.body.classList.remove('nic-finance-active');
 document.body.classList.add('nic-home-active');
 active=null;
 document.documentElement.dataset.calculator='home';document.body.dataset.calculator='home';
 // The real calculator menu becomes visible again when a calculator opens.
 if(menu){menu.hidden=false;menu.removeAttribute('aria-hidden');}
}
document.addEventListener('click',event=>{const button=event.target.closest('[data-nic-show-calculators]');if(!button)return;const menu=document.querySelector('.deal-type-card');if(menu){menu.hidden=false;menu.removeAttribute('aria-hidden');menu.scrollIntoView({behavior:'smooth',block:'start'});}});
window.addEventListener('nic-settings-updated',()=>{if(document.body.classList.contains('nic-home-active'))initWelcome();});
window.addEventListener('DOMContentLoaded',()=>{
 const css=document.createElement('style');css.textContent='.nic-finance-active main.section > :not(.deal-type-card):not(#nicFinanceModule):not(#nic-home-intro){display:none!important}#nicFinanceModule[hidden]{display:none!important}.deal-type-card[hidden]{display:none!important}.nic-home-intro{margin:20px 0 24px;padding:26px 30px;border:1px solid #e2e9e5;border-radius:12px;background:#f6f1e9;color:#263b3a}.nic-home-intro h2{margin:0;color:#075c55;font-size:26px}.nic-home-description{margin-top:10px;max-width:780px;line-height:1.55}.nic-home-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.nic-home-actions a,.nic-home-actions button{display:inline-flex;min-height:44px;align-items:center;padding:10px 18px;border:1px solid #075c55;border-radius:12px;background:linear-gradient(135deg,#16867a,#075c55);color:#fff;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}.nic-home-actions a{background:#fff;color:#075c55}[data-nic-site-nav]{display:flex;align-items:center;justify-content:flex-end;gap:clamp(10px,1.4vw,20px);margin-left:auto}[data-nic-site-nav] a{color:#263b3a;font-size:14px;text-decoration:none;white-space:nowrap}.nic-brand-bar:has([data-nic-site-nav]){grid-template-columns:170px minmax(0,1fr) auto}.nic-brand-bar [data-nic-site-nav]{grid-column:1/-1;grid-row:2;padding-top:9px;border-top:1px solid #e9e1d6}.nic-menu-toggle{display:none;border:1px solid #dce6e1;border-radius:10px;background:#fff;color:#075c55;font-size:22px;padding:5px 10px}@media(max-width:700px),(max-width:1024px) and (max-height:600px) and (orientation:landscape){.nic-brand-bar:has([data-nic-site-nav]){grid-template-columns:minmax(0,1fr) auto auto!important;position:relative}.nic-brand-bar a.nic-login-button{grid-column:2!important;grid-row:1!important}.nic-brand-bar .nic-brand-description{display:none!important}.nic-brand-bar [data-nic-site-nav]{display:none;position:absolute;z-index:100;top:100%;left:0;right:0;grid-column:auto;grid-row:auto;margin:0;padding:16px;background:#fff;border-top:1px solid #e2e9e5;box-shadow:0 10px 20px #263b3a18;flex-direction:column;align-items:flex-start}.nic-brand-bar [data-nic-site-nav].is-open{display:flex}.nic-brand-bar .nic-menu-toggle{display:inline-flex!important;grid-column:3!important;grid-row:1!important;align-items:center;justify-content:center;box-sizing:border-box;width:44px;height:44px;min-width:44px;padding:9px;margin:0;flex:none;cursor:pointer}.nic-brand-bar .nic-menu-toggle:focus-visible{outline:3px solid #b37b00;outline-offset:3px}.nic-home-intro{padding:22px 18px}.nic-home-actions{flex-direction:column}.nic-home-actions>*{justify-content:center}}';css.textContent+='@media(max-width:700px) and (orientation:portrait){.nic-brand-bar a.nic-login-button{box-sizing:border-box!important;width:44px!important;height:44px!important;padding:9px!important;gap:0!important}.nic-brand-bar a.nic-login-button>span{display:none!important}}';document.head.append(css);
 createSiteNavigation();
 const homeHeadingObserver=new MutationObserver(()=>window.NICHome?.refresh());
 for(const el of [document.getElementById('heroTitle'),document.getElementById('heroText')])if(el)homeHeadingObserver.observe(el,{childList:true,characterData:true,subtree:true});
 window.NICSettings.init().then(()=>{const key=routes[location.pathname.toLowerCase()];if(key)select(key);else if(document.documentElement.dataset.nicPage==='website')initWelcome();}).catch(console.error);
});
window.NICHome={refresh(){if(document.body.classList.contains('nic-home-active'))initWelcome();}};
window.NICCalculatorNavigation={select,restore(){}};
})();
