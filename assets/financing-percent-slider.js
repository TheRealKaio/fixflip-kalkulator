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
.nic-finance-equity-hint{margin:5px 0 0;color:var(--muted,#777f89);font-size:var(--nic-hint-font-size,13px);line-height:1.45}
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
@media(min-width:701px){
/* The purchase fee fields share one identical label row and input row.
   Remove inherited per-field offsets rather than adjusting individual inputs. */
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker){
 display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
 gap:10px!important;align-items:start!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker) > .field{
 display:grid!important;grid-template-rows:28px minmax(40px,auto)!important;
 align-content:start!important;align-self:start!important;
 width:100%!important;min-width:0!important;
 padding:0!important;margin:0!important;
 border:0!important;transform:none!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker) > .field > label{
 display:flex!important;align-items:flex-start!important;justify-content:flex-start!important;
 box-sizing:border-box!important;height:28px!important;min-height:28px!important;
 margin:0!important;padding:0!important;line-height:20px!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker) > .field > .input-wrap{
 align-self:start!important;width:100%!important;
 margin:0!important;transform:none!important;
}
#rentFinanceCard .quick-grid:has(#rentNotary):has(#rentBroker) :is(#rentNotary,#rentBroker){
 box-sizing:border-box!important;margin:0!important;
}
}
/* Caption centered over the actual checkbox, including its help icon. */
body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-option{
 display:flex!important;flex-direction:column!important;align-items:center!important;
 justify-content:flex-end!important;text-align:center!important;min-width:0!important;
}
body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-option>.finance-check-label{
 display:flex!important;align-items:center!important;justify-content:center!important;
 gap:5px!important;text-align:center!important;width:100%!important;margin-inline:auto!important;
}
body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-option>.finance-check-box{
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
  // Owner and Fix & Flip both expose exact acquisition components. For Flip,
  // do not use model.financingBase in the special zero-cash full-finance case:
  // that amount also capitalizes holding costs/interest.
  if(typeof window.model==='function' && activeMode()==='flip'){
   try{
    const m=window.model();
    const purchase=Math.max(0,m.p||0),renovation=Math.max(0,m.reno||0);
    const fees=Math.max(0,m.tax||0)+Math.max(0,m.notary||0)+Math.max(0,m.buyBroker||0);
    if(purchase>0)return {total:purchase+renovation+fees,
     base:purchase+renovation+(byId('financeAcquisition')?.checked?fees:0)};
   }catch(_error){/* Fall back to visible project totals. */}
  }
  // Owner-use uses the existing calculator financing totals.
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
 const hint=document.createElement('p');
 hint.className='nic-finance-equity-hint';
 hint.setAttribute('aria-live','polite');
 wrapper.appendChild(hint);
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
 // The calculator's legacy input stores percent of the FINANCEABLE basis.
 // Present percent of the TOTAL investment to the user, without touching
 // Fix & Flip's separate financing / reserve model.
 // Also show Fix & Flip's selected acquisition/renovation loan as a share
 // of initial investment. The Flip model separately adds holding/interest
 // capitalization when truly no cash is available.
 const effectiveMode=()=>true;
 const effectiveShare=(internal,c)=>{
  return effectiveMode()&&c.total>0 ? internal*c.base/c.total : internal;
 };
 const internalShare=(effective,c)=>{
  return effectiveMode()&&c.base>0 ? effective*c.total/c.base : effective;
 };
 const refresh=()=>{
  const internal=Math.max(0,parseNumber(original.value));
  const c=costs(id);
  const share=effectiveShare(internal,c);
  const maximum=Math.max(120,Math.ceil(share/20)*20);
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
  // Use six percentage decimals for calculation; only the displayed slider
  // caption rounds to two. Rounding to 0.01 percentage points can otherwise
  // change a six-figure loan by several euros after a manual cash entry.
  const percentage=Math.round(borrowed/c.base*100000000)/1000000;
  if(Math.abs(parseNumber(original.value)-percentage)<0.0000005){refresh();return;}
  original.value=percentage.toFixed(6);
  changedFinance();
  refresh();
 };
 // Direct cash entry is authoritative. If the cash is too small to pay
 // every acquisition cost, some of those costs necessarily enter the loan.
 // Turn the checkbox ON, without a confirmation or a second equity rewrite.
 // Do not turn it OFF automatically: users may deliberately choose to
 // finance ancillary costs even if they have enough cash to pay them.
 let automaticCheckboxChange=false;
 const userEquity=event=>{
  if(updating||!event.isTrusted)return;
  setManual(true);
  queueMicrotask(()=>{
   const box=byId(id==='rentLtv'?'rentFinanceAcquisition':'financeAcquisition');
   const c=costs(id);
   const cash=Math.max(0,parseNumber(equity.value));
   const unfinancedCosts=Math.max(0,c.total-c.base);
   if(box&&!box.checked&&cash+0.005<unfinancedCosts){
    automaticCheckboxChange=true;
    try{
     box.checked=true;
     box.dispatchEvent(new Event('change',{bubbles:true}));
    }finally{automaticCheckboxChange=false;}
   }
   // The new financeable base must be read only after the checkbox changes.
   syncManualPercentage();
  });
 };
 equity.addEventListener('input',userEquity,true);
 equity.addEventListener('change',userEquity,true);
 let equityBeforeDrag=null;
 const changedBySlider=()=>{
  if(equityBeforeDrag===null)equityBeforeDrag=Math.max(0,parseNumber(equity.value));
  let next=Number(slider.value);
  // Magnetic detent at 100%; a deliberate drag past the 1% zone still works.
  if(Math.abs(next-100)<=1){
   next=100;
   slider.value='100';
   if(!wrapper.classList.contains('nic-finance-at-100') && navigator.vibrate)
    try{navigator.vibrate(8);}catch(_error){}
   wrapper.classList.add('nic-finance-at-100');
  }else wrapper.classList.remove('nic-finance-at-100');
  const c=costs(id);
  // Without acquisition-cost financing, the loan may not exceed the
  // acquisition-cost-excluding basis. Keep the displayed share honest.
  const permitted=effectiveMode() && c.total>0 &&
    !(byId(id==='rentLtv'?'rentFinanceAcquisition':'financeAcquisition')?.checked)
    ? 100*c.base/c.total : Number(slider.max);
  if(next>permitted){next=Math.max(0,permitted);slider.value=String(next);}
  original.value=internalShare(next,c).toFixed(6);
  // Moving the financing slider is an explicit user decision to recalculate
  // equity. A previously typed amount must not silently lock this control.
  setManual(false);
  syncAutoEquity();
  const difference=Math.round((Math.max(0,parseNumber(equity.value))-equityBeforeDrag)*100)/100;
  hint.textContent=Math.abs(difference)<0.01?'Eigenkapitalbedarf unverändert.':difference>0
   ?'Du benötigst '+format(difference)+' € mehr Eigenkapital.'
   :'Du benötigst '+format(-difference)+' € weniger Eigenkapital.';
  changedFinance();
  refresh();
 };
 slider.addEventListener('pointerdown',()=>{equityBeforeDrag=Math.max(0,parseNumber(equity.value));});
 slider.addEventListener('input',changedBySlider);
 slider.addEventListener('change',()=>{equityBeforeDrag=null;original.dispatchEvent(new Event('change',{bubbles:true}));});
 original.addEventListener('input',refresh);
 // Use one confirmation and recalculation policy for own-use and rental.
 const acquisitionCheckbox=byId(id==='rentLtv'?'rentFinanceAcquisition':'financeAcquisition');
 if(acquisitionCheckbox){
  let shareBeforeToggle=null;
  acquisitionCheckbox.addEventListener('click',event=>{
   // Remember the current loan before the checkbox changes the financeable
   // basis; changing the checkbox must not accidentally finance ancillary costs.
   const before=costs(id);
   shareBeforeToggle=Math.max(0,before.base*parseNumber(original.value)/100);
   if(!event.isTrusted||acquisitionCheckbox.checked)return;
   const accepted=window.confirm('Möchtest du die Kaufnebenkosten wirklich aus deinem Eigenkapital finanzieren?\n\nOhne Mitfinanzierung steigt dein Eigenkapitalbedarf.');
   if(!accepted){
    shareBeforeToggle=null;
    event.preventDefault();
    event.stopImmediatePropagation();
   }
  },true);
  acquisitionCheckbox.addEventListener('change',()=>{
   // The auto-check from a manual cash edit is not a new financing decision.
   // Let the cash amount drive the ratio, and skip the delayed checkbox
   // handler which would otherwise clear the fixed-equity state.
   if(automaticCheckboxChange)return;
   const previouslyBorrowed=shareBeforeToggle;
   shareBeforeToggle=null;
   setManual(false);
   // Recalculate after native calculator listeners. When ancillary financing is
   // removed, cap the old loan at the new financeable amount. This makes the
   // effective slider share fall (e.g. 330k -> 300k of a 330k investment).
   setTimeout(()=>{
    if(!original.isConnected||!equity.isConnected)return;
    const c=costs(id);
    if(!(c.base>0))return;
    const borrowed=previouslyBorrowed===null
      ? c.base*parseNumber(original.value)/100
      : Math.min(previouslyBorrowed,c.base);
    const percentage=borrowed/c.base*100;
    original.value=percentage.toFixed(6);
    syncAutoEquity();
    changedFinance();
    refresh();
   },0);
  });
 }
 const observed=id==='rentLtv'
  ? ['rentPurchase','rentRenovation','rentNotary','rentBroker','rentState','rentFinanceAcquisition']
  : ['purchase','financeAcquisition','notary','buyBroker','state','buffer'];
 const synchronize=()=>{
  if(isManual())syncManualPercentage();
  else{refresh();syncAutoEquity();}
 };
 // Output widgets also refresh after LTV-only changes. Those must not
 // re-derive the LTV from fixed equity unless PURCHASE COSTS actually changed.
 let lastCosts=null;
 const onCostChange=()=>{
  const c=costs(id);
  const current=Math.round(c.total*100)+'/'+Math.round(c.base*100);
  if(current===lastCosts)return;
  lastCosts=current;
  synchronize();
 };
 for(const sourceId of observed){
  const onChange=()=>queueMicrotask(onCostChange);
  byId(sourceId)?.addEventListener('change',onChange);
  byId(sourceId)?.addEventListener('input',onChange);
 }
 const acquisitionOutput=id==='rentLtv'?'rentAcquisitionDisplay':'acquisitionCostsTotal';
 if(byId(acquisitionOutput)){
  const watcher=new MutationObserver(()=>queueMicrotask(onCostChange));
  watcher.observe(byId(acquisitionOutput),{subtree:true,childList:true,characterData:true});
 }
 const initial=costs(id);
 lastCosts=Math.round(initial.total*100)+'/'+Math.round(initial.base*100);

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
 // The legacy owner-use restore path stores LTV with only two decimals.
 // After all initial model/input restore handlers finish, derive the precise
 // financing percentage again from the saved, user-fixed cash amount.
 // Otherwise a reload can silently alter the loan by several euros.
 setTimeout(()=>{
  if(!original.isConnected||!equity.isConnected)return;
  if(isManual())syncManualPercentage();
  else refresh();
 },0);
}
function setup(){
 install('ltv','ownEquityInput');
 install('rentLtv','rentEquity');
 for(const x of controllers.values())x.refresh();
 // The shared navigation activates own-use after the initial DOM startup.
 // The owner calculator may then reload its stored two-decimal LTV, overwriting
 // the high-precision cash-derived ratio. Reconcile AFTER route activation.
 setTimeout(()=>{
  const active=activeMode();
  for(const [id,controller] of controllers){
   if(id==='ltv'&&active!=='own'&&active!=='flip')continue;
   if(controller.isManual())controller.synchronize();
   else controller.refresh();
  }
 },80);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',setup);else setup();
window.addEventListener('nic-calculator-changed',setup);
window.addEventListener('nic-route-changed',setup);
window.NICFinancingPercent={managed:id=>controllers.has(id),sync:()=>{for(const x of controllers.values())x.synchronize();}};
})();