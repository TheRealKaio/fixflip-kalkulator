/* Shared percent slider for existing own/flip/rental financing fields.
   Existing input IDs and formulas remain the single calculation source. */
(()=>{
'use strict';
const parseNumber=value=>{
 const raw=String(value??'').trim().replace(/\s|€/g,'').replace(/%/g,'');
 const clean=raw.includes(',')?raw.replace(/\./g,'').replace(',','.'):raw;
 const number=Number(clean.replace(/[^0-9.+-]/g,''));
 return Number.isFinite(number)?number:0;
};
const value=id=>parseNumber(document.getElementById(id)?.value);
const euroText=id=>parseNumber(document.getElementById(id)?.textContent);
const byId=id=>document.getElementById(id);
const format=value=>new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(value);
const activeMode=()=>document.documentElement.dataset.calculator||document.body.dataset.calculator||'';
const controllers=new Map();
const style=document.createElement('style');
style.id='nic-financing-percent-slider-style';
style.textContent=`
/* Full-width financing control, identical on phone and desktop. */
.nic-finance-percent-field{grid-column:1 / -1!important;width:100%;min-width:0}
.nic-finance-percent-native{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;border:0!important;overflow:hidden!important;clip-path:inset(50%)!important;white-space:nowrap!important}
.nic-finance-percent-control{display:block;width:100%;min-width:0;padding:4px 0 7px}
.nic-finance-percent-range{display:block;width:100%!important;min-width:0;height:36px;accent-color:var(--nic-accent,#2463e6);cursor:pointer;touch-action:pan-y}
.nic-finance-percent-labels{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:var(--nic-subtext-font-size,14px);font-variant-numeric:tabular-nums}
.nic-finance-percent-labels output{font-weight:800;color:var(--ink,#172033)}
@media(max-width:700px){.nic-finance-percent-control{grid-column:1 / -1!important}.nic-finance-percent-labels{flex-wrap:wrap}}
/* Rental financing: two equal rate columns on tablet/desktop.
   The finance percentage slider keeps its own full-width row. */
@media(min-width:701px){
 #rentFinanceCard .finance-rate-grid{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  align-items:start!important;column-gap:12px!important;row-gap:14px!important;
 }
 #rentFinanceCard .finance-rate-grid>.field{
  width:100%!important;min-width:0!important;max-width:none!important;
 }
 #rentFinanceCard .finance-rate-grid>.field.nic-finance-percent-field{
  grid-column:1/-1!important;
 }
}
/* Identical top baseline and label heights for purchase-fee fields. */
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker){
 align-items:start!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker)>.field{
 display:flex!important;flex-direction:column!important;align-self:stretch!important;
 min-width:0!important;margin-top:0!important;padding-top:0!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker)>.field>label{
 display:flex!important;align-items:center!important;min-height:24px!important;
 margin:0 0 5px!important;line-height:1.3!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker)>.field>.input-wrap{
 margin-top:0!important;width:100%!important;
}
/* Caption centered over the actual checkbox, including its help icon. */
#rentFinanceCard .finance-acq-option{
 display:flex!important;flex-direction:column!important;align-items:center!important;
 justify-content:flex-end!important;text-align:center!important;min-width:0!important;
}
#rentFinanceCard .finance-acq-option>.finance-check-label{
 display:flex!important;align-items:center!important;justify-content:center!important;
 gap:5px!important;text-align:center!important;width:100%!important;
}
#rentFinanceCard .finance-acq-option>.finance-check-box{
 display:flex!important;align-items:center!important;justify-content:center!important;
 width:100%!important;min-width:0!important;margin-inline:auto!important;
}

`;
(document.head||document.documentElement).appendChild(style);
function costs(id){
 if(id==='rentLtv' && typeof window.rentalCalculation==='function'){
  const m=window.rentalCalculation();
  return {total:m.totalInvestment,base:m.financingBase};
 }
 // These outputs are already calculated by the existing own/flip model.
 // No second loan/debt/interest formula is introduced here.
 if(id==='ltv'){
  // Owner-use exposes these same financing totals in its existing model.
  // Reuse them when available, rather than recalculate ancillary costs.
  if(typeof window.model==='function' && activeMode()==='own'){
   try{
    const m=window.model();
    if(Number.isFinite(m.initialOwnUseCosts)&&Number.isFinite(m.financingBase))
     return {total:Math.max(0,m.initialOwnUseCosts),base:Math.max(0,m.financingBase)};
   }catch(_error){/* Fall back to the displayed project fields. */}
  }
  const purchase=Math.max(0,value('purchase'));
  const acquisition=Math.max(0,euroText('acquisitionCostsTotal'));
  const extra=Math.max(0,value('renovationTotal')) || Math.max(0,value('renoTotal'));
  const total=purchase+acquisition+extra;
  const base=purchase+extra+(byId('financeAcquisition')?.checked?acquisition:0);
  return {total,base};
 }
 return {total:0,base:0};
}
function install(id,equityId){
 const original=byId(id),equity=byId(equityId);
 if(!original||!equity||controllers.has(id))return;
 const field=original.closest('.field');
 if(!field)return;
 const oldWrap=original.closest('.input-wrap')||original;
 const wrapper=document.createElement('div');
 wrapper.className='nic-finance-percent-control';
 const slider=document.createElement('input');
 slider.type='range';slider.className='nic-finance-percent-range';
 slider.min='0';slider.step='0.01';slider.max='120';slider.setAttribute('aria-label','Finanzierungsanteil in Prozent');
 const line=document.createElement('div');line.className='nic-finance-percent-labels';
 const low=document.createElement('span');low.textContent='0 %';
 const out=document.createElement('output');out.setAttribute('aria-live','off');
 const high=document.createElement('span');
 line.append(low,out,high);wrapper.append(slider,line);
 oldWrap.insertAdjacentElement('afterend',wrapper);
 oldWrap.classList.add('nic-finance-percent-native');
 field.classList.add('nic-finance-percent-field');
 let manual=Boolean(parseNumber(equity.value)>0);
 let updating=false;
 equity.addEventListener('beforeinput',()=>{if(!updating)manual=true;},true);
 equity.addEventListener('input',event=>{if(!updating&&event.isTrusted)manual=true;},true);
 const refresh=()=>{
  const share=Math.max(0,parseNumber(original.value));
  const c=costs(id);
  const necessary=c.base>0?100*c.total/c.base:100;
  const maximum=Math.max(120,Math.ceil(Math.max(share,necessary)/20)*20);
  slider.max=String(Math.min(500,maximum));
  slider.value=String(Math.min(share,Number(slider.max)));
  out.textContent=format(share)+' %';
  high.textContent=format(Number(slider.max))+' %';
  slider.setAttribute('aria-valuetext',out.textContent);
 };
 const syncAutoEquity=()=>{
  if(manual)return;
  const c=costs(id);
  if(!(c.total>=0&&c.base>0))return;
  const share=Math.max(0,parseNumber(original.value));
  const required=Math.round(Math.max(0,c.total-c.base*share/100)*100)/100;
  if(Math.abs(parseNumber(equity.value)-required)<0.005)return;
  updating=true;
  try{
   equity.value=String(required);
   equity.dispatchEvent(new Event('input',{bubbles:true}));
  }finally{updating=false;}
 };
 const changedBySlider=()=>{
  original.value=Number(slider.value).toFixed(2);
  // Reuse the native field listeners; do not create a second loan calculation.
  syncAutoEquity();
  original.dispatchEvent(new Event('input',{bubbles:true}));
  refresh();
 };
 slider.addEventListener('input',changedBySlider);
 slider.addEventListener('change',()=>original.dispatchEvent(new Event('change',{bubbles:true})));
 original.addEventListener('input',refresh);
 const observed=['purchase','financeAcquisition','notary','buyBroker','state','buffer','rentPurchase','rentRenovation','rentNotary','rentBroker','rentState','rentFinanceAcquisition'];
 for(const sourceId of observed){
  const onChange=()=>queueMicrotask(()=>{refresh();syncAutoEquity();});
  byId(sourceId)?.addEventListener('change',onChange);
  byId(sourceId)?.addEventListener('input',onChange);
 }
 const acquisitionOutput=id==='rentLtv'?'rentAcquisitionDisplay':'acquisitionCostsTotal';
 if(byId(acquisitionOutput)){
  const watcher=new MutationObserver(()=>queueMicrotask(()=>{refresh();syncAutoEquity();}));
  watcher.observe(byId(acquisitionOutput),{subtree:true,childList:true,characterData:true});
 }
 controllers.set(id,{refresh});
 refresh();
}
function setup(){
 install('ltv','ownEquityInput');
 install('rentLtv','rentEquity');
 for(const x of controllers.values())x.refresh();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
window.addEventListener('nic-calculator-changed',setup);
window.addEventListener('nic-route-changed',setup);
})();