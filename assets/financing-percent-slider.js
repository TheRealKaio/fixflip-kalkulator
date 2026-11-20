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
.nic-finance-percent-control{position:relative}
.nic-finance-percent-control::before{content:"";position:absolute;top:17px;left:var(--nic-finance-snap-position,83.33%);height:16px;border-left:2px solid var(--ink,#172033);opacity:.5;pointer-events:none;z-index:1}
.nic-finance-percent-control.nic-finance-at-100::before{opacity:1;border-left-width:3px}

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

 // The owner/flip calculator shares DOM input IDs but keeps separate saved states.
 const mode=()=>id==='rentLtv'?'rent':(activeMode()==='flip'?'flip':'own');
 const manualKey=()=> 'nic_finance_equity_manual_v2_'+mode();
 const flags=new Map();
 const isManual=()=>{
  const key=manualKey();
  if(!flags.has(key)){
   const saved=localStorage.getItem(key);
   // Existing installations may predate the explicit user-input flag.
   flags.set(key,saved===null ? parseNumber(equity.value)>0 : saved==='1');
  }
  return flags.get(key);
 };
 const setManual=(state)=>{
  const key=manualKey();
  flags.set(key,state);
  localStorage.setItem(key,state?'1':'0');
 };
 let updating=false;
 const changedFinance=()=>{
  original.dispatchEvent(new Event('input',{bubbles:true}));
 };
 const refresh=()=>{
  const share=Math.max(0,parseNumber(original.value));
  const c=costs(id);
  const necessary=c.base>0?100*c.total/c.base:100;
  const maximum=Math.max(120,Math.ceil(Math.max(share,necessary)/20)*20);
  slider.max=String(maximum);
  slider.value=String(Math.min(share,maximum));
  wrapper.style.setProperty('--nic-finance-snap-position',(100/maximum*100)+'%');
  out.textContent=format(share)+' %';
  high.textContent=format(maximum)+' %';
  slider.setAttribute('aria-valuetext',out.textContent);
 };
 const syncAutoEquity=()=>{
  if(isManual())return;
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
 const syncManualPercentage=()=>{
  if(!isManual())return;
  const c=costs(id);
  if(!(c.base>0&&c.total>0))return;
  // Fixed user equity determines the effective debt, not a second deduction
  // from the already reduced financing percentage.
  const borrowed=Math.max(0,c.total-Math.max(0,parseNumber(equity.value)));
  const percentage=Math.round(borrowed/c.base*10000)/100;
  if(Math.abs(parseNumber(original.value)-percentage)<0.005){refresh();return;}
  original.value=percentage.toFixed(2);
  changedFinance();
  refresh();
 };
 const userEquity=event=>{
  if(updating||!event.isTrusted)return;
  setManual(true);
  queueMicrotask(syncManualPercentage);
 };
 equity.addEventListener('input',userEquity,true);
 equity.addEventListener('change',userEquity,true);
 const changedBySlider=()=>{
  let next=Number(slider.value);
  // Magnetic detent at 100%; a deliberate drag past the 1% zone still works.
  if(Math.abs(next-100)<=1){
   next=100;
   slider.value='100';
   if(!wrapper.classList.contains('nic-finance-at-100') && navigator.vibrate)
    try{navigator.vibrate(8);}catch(_error){}
   wrapper.classList.add('nic-finance-at-100');
  }else wrapper.classList.remove('nic-finance-at-100');
  original.value=next.toFixed(2);
  if(!isManual())syncAutoEquity();
  changedFinance();
  refresh();
 };
 slider.addEventListener('input',changedBySlider);
 slider.addEventListener('change',()=>original.dispatchEvent(new Event('change',{bubbles:true})));
 original.addEventListener('input',refresh);
 const observed=id==='rentLtv'
  ? ['rentPurchase','rentRenovation','rentNotary','rentBroker','rentState','rentFinanceAcquisition']
  : ['purchase','financeAcquisition','notary','buyBroker','state','buffer'];
 const synchronize=()=>{
  if(isManual())syncManualPercentage();
  else{refresh();syncAutoEquity();}
 };
 for(const sourceId of observed){
  const onChange=()=>queueMicrotask(synchronize);
  byId(sourceId)?.addEventListener('change',onChange);
  byId(sourceId)?.addEventListener('input',onChange);
 }
 const acquisitionOutput=id==='rentLtv'?'rentAcquisitionDisplay':'acquisitionCostsTotal';
 if(byId(acquisitionOutput)){
  const watcher=new MutationObserver(()=>queueMicrotask(synchronize));
  watcher.observe(byId(acquisitionOutput),{subtree:true,childList:true,characterData:true});
 }
 // A confirmed calculator reset restores automatic equity generation.
 byId('recalc')?.addEventListener('click',()=>{
  setTimeout(()=>{
   if(parseNumber(equity.value)===0 && Math.abs(parseNumber(original.value)-100)<0.01){
    setManual(false);
    refresh();
   }
  },0);
 },true);

 controllers.set(id,{refresh,isManual,synchronize});
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
window.NICFinancingPercent={managed:id=>controllers.has(id),sync:()=>{for(const x of controllers.values())x.synchronize();}};
})();