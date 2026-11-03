/* One controller for all five calculator tiles. Financing remains an isolated module. */
(()=>{
'use strict';
/* FINANCE_MODULE */
const routes={'/budget/':'budget','/eigennutzung/':'own','/vermietung/':'rent','/fix-flip/':'flip','/finanzierungsrechner/':'finance'};
let active=null,financeRoot=null,bypass=false;
function select(key,push=false){
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
window.addEventListener('DOMContentLoaded',()=>{
 const css=document.createElement('style');css.textContent='.nic-finance-active main.section > :not(.deal-type-card):not(#nicFinanceModule){display:none!important}#nicFinanceModule[hidden]{display:none!important}';document.head.append(css);
 window.NICSettings.init().then(()=>select(routes[location.pathname.toLowerCase()]||'budget')).catch(console.error);
});
window.NICCalculatorNavigation={select,restore(){}};
})();
