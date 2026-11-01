/* UI controls use existing calculator handlers; IDs and formulas stay intact. */
(()=>{
'use strict';
const paths={
 budget:'<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M5 8h14M9 12h.01M15 12h.01M9 16h.01M15 16h.01M9 19h.01M15 19h.01"/>',
 own:'<path d="m3 10 9-8 9 8v12h-6v-8H9v8H3Z"/>',
 rent:'<ellipse cx="15" cy="5" rx="6" ry="3"/><path d="M9 5v8c0 1.7 2.7 3 6 3s6-1.3 6-3V5M9 9c0 1.7 2.7 3 6 3s6-1.3 6-3"/><ellipse cx="7" cy="15" rx="6" ry="3"/><path d="M1 15v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/>',
 flip:'<path d="m3 20 10-10 3 3L6 23Zm9-12 3-3-2-3c5-2 9 1 9 5l-3 1-1 4-4-1Z"/>',
 finance:'<circle cx="12" cy="12" r="10"/><path d="m8 17 8-10"/><circle cx="8" cy="8" r="1.5"/><circle cx="16" cy="16" r="1.5"/>'
};
function decorate(){
 document.querySelectorAll('.deal-type-row>.deal-type-option').forEach(el=>{
  if(el.querySelector('.nic-menu-icon'))return;
  const routed={'/budget/':'budget','/eigennutzung/':'own','/vermietung/':'rent','/fix-flip/':'flip','/finanzierungsrechner/':'finance'};
  const key=routed[el.dataset.href]||(el.id==='dealTypeRent'?'rent':el.id==='nicFinancingTab'?'finance':el.querySelector('input[name="dealType"]')?.value);
  if(!paths[key])return;
  el.dataset.nicCalculator=key;
  const icon=document.createElementNS('http://www.w3.org/2000/svg','svg');
  icon.setAttribute('class','nic-menu-icon');icon.setAttribute('viewBox','0 0 24 24');icon.setAttribute('fill','none');icon.setAttribute('stroke','currentColor');icon.setAttribute('stroke-width','1.7');icon.setAttribute('stroke-linecap','round');icon.setAttribute('stroke-linejoin','round');icon.setAttribute('aria-hidden','true');icon.innerHTML=paths[key];
  el.prepend(icon);
  if(key==='finance'){
   el.querySelector('strong').textContent='Finanzierung & Restschuld';
   el.querySelector('small').textContent='Finanzierung berechnen und Restschuld ermitteln';
  }
 });
}
decorate();
const row=document.querySelector('.deal-type-row');
if(row)new MutationObserver(decorate).observe(row,{childList:true});
// Existing authentication capture handler keeps logged-in account behavior.
// Wait for initialization on a very early click instead of opening administration.
document.querySelector('.nic-login-button')?.addEventListener('click',async e=>{
 e.preventDefault();e.stopImmediatePropagation();
 try{const access=window.NICAccess;if(access&&await access.init())await access.login();}catch(error){alert(error.message);}
},true);
// Align the fixed action bar to the actual calculator, including scrollbar space.
function sizeActionBar(){
 const app=document.querySelector('.app');if(!app)return;
 const rect=app.getBoundingClientRect();
 document.documentElement.style.setProperty('--nic-calculator-width',rect.width+'px');
 document.documentElement.style.setProperty('--nic-calculator-left',rect.left+'px');
}
sizeActionBar();
window.addEventListener('resize',sizeActionBar);
const app=document.querySelector('.app');if(app)new ResizeObserver(sizeActionBar).observe(app);
function clearMask(selector){
 const mask=document.querySelector(selector);if(!mask)return;
 // Re-query each field: existing input handlers may render fresh trade inputs.
 const fields=[...mask.querySelectorAll('input:not([type="hidden"]):not([type="button"]),textarea')].filter(el=>!el.readOnly&&!el.disabled).map(el=>({id:el.id,trade:el.dataset.trade,area:el.dataset.areaKey,cls:el.className}));
 // Clear amounts first so clearing optional area fields cannot restore an amount.
 fields.sort((a,b)=>Number(!!b.trade)-Number(!!a.trade));
 for(const field of fields){
  const el=field.id?document.getElementById(field.id):field.trade?mask.querySelector('input[data-trade="'+CSS.escape(field.trade)+'"]'):field.area?mask.querySelector('input[data-area-key="'+CSS.escape(field.area)+'"]'):null;
  if(!el||!mask.contains(el))continue;
  if(el.type==='checkbox'||el.type==='radio')continue;
  el.value='';el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));
 }
}
for(const [id,selector] of [['budgetApplySuggestions','#budgetExpensesBody'],['applyTradeSuggestions','#renoBackdrop'],['rentApplyTradeSuggestions','#rentRenoPanel']]){
 const button=document.getElementById(id);if(!button||button.closest('.nic-suggestion-controls'))continue;
 const style=getComputedStyle(button),canvas=document.createElement('canvas'),context=canvas.getContext('2d');context.font=style.font;
 const naturalWidth=Math.ceil(context.measureText(button.textContent.trim()).width+parseFloat(style.paddingLeft)+parseFloat(style.paddingRight)+parseFloat(style.borderLeftWidth)+parseFloat(style.borderRightWidth));
 const width=button.getBoundingClientRect().width||naturalWidth;
 const controls=document.createElement('div');controls.className='nic-suggestion-controls';controls.style.setProperty('--nic-suggestion-width',width+'px');
 button.parentNode.insertBefore(controls,button);controls.append(button);
 button.textContent='Vorschläge übernehmen';
 const clear=document.createElement('button');clear.type='button';clear.className='nic-clear-mask';clear.textContent='X';clear.setAttribute('aria-label',id==='budgetApplySuggestions'?'Monatliche Ausgaben leeren':'Sanierungseingaben dieser Maske leeren');clear.dataset.clearMask=selector;
 clear.addEventListener('click',()=>clearMask(selector));controls.append(clear);
}
})();
