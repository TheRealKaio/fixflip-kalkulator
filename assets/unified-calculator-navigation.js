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
 try{window.dispatchEvent(new CustomEvent('nic-select-calculator',{detail:key}));}finally{bypass=false;}
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
window.addEventListener('popstate',()=>{const key=routes[location.pathname.toLowerCase()]||'budget';select(key);});
function createSiteNavigation(){
 const links=[['/nebenkostenabrechnung/','Nebenkostenabrechnung'],['/preise/','Preise'],['/warum-immocheck/','Warum Immo-Kalkulator'],['/kontakt/','Kontakt'],['/anmelden/','Anmelden']];
 const header=document.querySelector('.brand-logo-wrap')?.closest('header')||document.querySelector('header');
 if(header&&!header.querySelector('[data-nic-site-nav]')){
  const nav=document.createElement('nav');nav.dataset.nicSiteNav='';nav.setAttribute('aria-label','Hauptnavigation');
  for(const [href,label] of links){const a=document.createElement('a');a.href=href;a.textContent=label;nav.append(a);}
  const toggle=document.createElement('button');toggle.type='button';toggle.className='nic-menu-toggle';toggle.setAttribute('aria-label','Menü öffnen');toggle.setAttribute('aria-expanded','false');toggle.textContent='☰';
  toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Menü schließen':'Menü öffnen');nav.classList.toggle('is-open',open);});
  header.append(nav,toggle);
 }
 const footer=document.querySelector('footer')||document.createElement('footer');
 if(!footer.isConnected)document.body.append(footer);
 if(!footer.querySelector('[data-nic-footer-nav]')){const nav=document.createElement('nav');nav.dataset.nicFooterNav='';nav.setAttribute('aria-label','Weitere Seiten');for(const [href,label] of links){const a=document.createElement('a');a.href=href;a.textContent=label;nav.append(a);}footer.append(nav);}
}
function initWelcome(){
 if(document.documentElement.dataset.nicPage!=='website')return;
 const main=document.querySelector('main.section')||document.querySelector('main'),menu=document.querySelector('.deal-type-card');
 if(!main)return;
 let intro=document.getElementById('nic-home-intro');
 if(!intro){
  intro=document.createElement('section');intro.id='nic-home-intro';intro.className='nic-home-intro';
  const content=window.NICSettings.current.content.welcome;
  const h=document.createElement('h2');h.textContent=content.title;
  const body=document.createElement('div');body.className='nic-home-description';body.append(window.NICSettings.legalFragment(content.description,window.NICSettings.current));
  const actions=document.createElement('div');actions.className='nic-home-actions';const button=document.createElement('button');button.type='button';button.dataset.nicShowCalculators='';button.textContent='Immobilie berechnen';const link=document.createElement('a');link.href='/nebenkostenabrechnung/';link.textContent='Nebenkosten abrechnen';actions.append(button,link);intro.append(h,body,actions);
  (menu||main.firstElementChild)?.before(intro);
 }
 if(menu){menu.hidden=true;menu.setAttribute('aria-hidden','true');}
}
document.addEventListener('click',event=>{const button=event.target.closest('[data-nic-show-calculators]');if(!button)return;const menu=document.querySelector('.deal-type-card');if(menu){menu.hidden=false;menu.removeAttribute('aria-hidden');menu.scrollIntoView({behavior:'smooth',block:'start'});}});
window.addEventListener('DOMContentLoaded',()=>{
 const css=document.createElement('style');css.textContent='.nic-finance-active main.section > :not(.deal-type-card):not(#nicFinanceModule):not(#nic-home-intro){display:none!important}#nicFinanceModule[hidden]{display:none!important}.deal-type-card[hidden]{display:none!important}.nic-home-intro{margin:20px 0 24px;padding:26px 30px;border:1px solid #e2e9e5;border-radius:12px;background:#f6f1e9;color:#263b3a}.nic-home-intro h2{margin:0;color:#075c55;font-size:26px}.nic-home-description{margin-top:10px;max-width:780px;line-height:1.55}.nic-home-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.nic-home-actions a,.nic-home-actions button{display:inline-flex;min-height:44px;align-items:center;padding:10px 18px;border:1px solid #075c55;border-radius:12px;background:linear-gradient(135deg,#16867a,#075c55);color:#fff;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}.nic-home-actions a{background:#fff;color:#075c55}header:has([data-nic-site-nav]){display:flex;align-items:center;gap:18px;flex-wrap:wrap}[data-nic-site-nav]{display:flex;align-items:center;justify-content:flex-end;gap:clamp(10px,1.4vw,20px);margin-left:auto}[data-nic-site-nav] a{color:#263b3a;font-size:14px;text-decoration:none;white-space:nowrap}.nic-menu-toggle{display:none;border:1px solid #dce6e1;border-radius:10px;background:#fff;color:#075c55;font-size:22px;padding:5px 10px}@media(max-width:900px){[data-nic-site-nav]{display:none;position:absolute;z-index:20;top:100%;left:0;right:0;padding:16px;background:#fff;border-top:1px solid #e2e9e5;box-shadow:0 10px 20px #263b3a18;flex-direction:column;align-items:flex-start}[data-nic-site-nav].is-open{display:flex}.nic-menu-toggle{display:block;margin-left:auto}header:has([data-nic-site-nav]){position:relative}.nic-home-intro{padding:22px 18px}.nic-home-actions{flex-direction:column}.nic-home-actions>*{justify-content:center}}[data-nic-footer-nav]{display:flex;flex-wrap:wrap;gap:18px;padding:18px 0}[data-nic-footer-nav] a{color:inherit}';document.head.append(css);
 createSiteNavigation();
 window.NICSettings.init().then(()=>{initWelcome();select(routes[location.pathname.toLowerCase()]||'budget');}).catch(console.error);
});
window.NICCalculatorNavigation={select,restore(){}};
})();
