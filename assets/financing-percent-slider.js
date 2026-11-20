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
const format=value=>new Intl.NumberFormat('de-DE',{maximumFractionDigits:1}).format(value);
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
 slider.min='0';slider.step='1';slider.max='100';slider.setAttribute('aria-label','Finanzierungsanteil in Prozent');
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
 const changedBySlider=()=>{
  const next=Number(slider.value);
  original.value=next.toFixed(2);
  // The native input continues to drive all historical calculation listeners.
  if(!manual){
   const c=costs(id);
   if(c.total>=0&&c.base>0){
    const required=Math.max(0,c.total-c.base*next/100);
    updating=true;
    equity.value=Math.round(required*100)/100;
    equity.dispatchEvent(new Event('input',{bubbles:true}));
    updating=false;
   }
  }
  original.dispatchEvent(new Event('input',{bubbles:true}));
  refresh();
 };
 slider.addEventListener('input',changedBySlider);
 slider.addEventListener('change',()=>original.dispatchEvent(new Event('change',{bubbles:true})));
 original.addEventListener('input',refresh);
 const observed=['purchase','financeAcquisition','acquisitionCostsTotal','rentPurchase','rentRenovation','rentNotary','rentBroker','rentState','rentFinanceAcquisition'];
 for(const sourceId of observed){
  byId(sourceId)?.addEventListener('change',refresh);
  byId(sourceId)?.addEventListener('input',refresh);
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