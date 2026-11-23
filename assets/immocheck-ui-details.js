/* Presentation only: keep calculator inputs, IDs, events and calculations intact. */
(()=>{
'use strict';
const paths={
 settlement:'<path d="M6 2h9l4 4v16H5V2Z"/><path d="M14 2v5h5M8 11h8M8 15h8M8 19h5"/>',
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
  const key=el.dataset.icon||el.dataset.calculator||routed[el.dataset.href]||(el.id==='dealTypeRent'?'rent':el.id==='nicFinancingTab'?'finance':el.querySelector('input[name="dealType"]')?.value);
  if(!paths[key])return;
  const icon=document.createElementNS('http://www.w3.org/2000/svg','svg');
  icon.setAttribute('class','nic-menu-icon');icon.setAttribute('viewBox','0 0 24 24');icon.setAttribute('fill','none');icon.setAttribute('stroke','currentColor');icon.setAttribute('stroke-width','1.7');icon.setAttribute('stroke-linecap','round');icon.setAttribute('stroke-linejoin','round');icon.setAttribute('aria-hidden','true');icon.innerHTML=paths[key];
  el.prepend(icon);
  if(key==='finance'){
   el.querySelector('strong').textContent='Finanzierung & Restschuld';
   el.querySelector('small').textContent='Ermittle Rate, Zinsen und Restschuld';
  }
 });
}
decorate();
const row=document.querySelector('.deal-type-row');
if(row)new MutationObserver(decorate).observe(row,{childList:true});


// Bind the renovation split heading to Admin → Layout → H3 (px).
// Its existing element and all surrounding layout/behavior remain unchanged.
function bindRenovationSplitH3(){
 document.querySelectorAll('.reno-head').forEach(container=>{
  const labels=container.querySelectorAll('h1,h2,h3,h4,.reno-title,strong,span,div');
  for(const el of labels){
   if(el.textContent.trim()!=='Sanierung aufteilen')continue;
   const target=el.closest('h1,h2,h3,h4')||el;
   target.classList.add('nic-reno-split-h3');
   break;
  }
 });
}
bindRenovationSplitH3();
new MutationObserver(bindRenovationSplitH3).observe(document.body,{childList:true,subtree:true});

/* Keep SVG labels on the Admin subtext scale, independent of the viewBox scale. */
const chartObservers=new WeakMap();
let chartFrame=0;
function refreshChartLabels(){
 chartFrame=0;
 document.querySelectorAll('svg.chart[viewBox]').forEach(svg=>{
  if(!chartObservers.has(svg)){
   const observer=new ResizeObserver(scheduleChartLabels);
   observer.observe(svg);chartObservers.set(svg,{observer,key:''});
  }
  const width=svg.clientWidth,box=svg.viewBox.baseVal;
  if(!width||!box.width)return;
  svg.style.setProperty('--nic-chart-text-scale',String(box.width/width));
  const state=chartObservers.get(svg),key=width+':'+window.matchMedia('(max-width:700px) and (orientation:portrait)').matches+':'+getComputedStyle(svg).getPropertyValue('--nic-subtext-font-size');
  if(state.key!==key&&typeof svg.nicRedraw==='function'){state.key=key;svg.nicRedraw();}
  const years=[...svg.querySelectorAll('text')].filter(text=>/^\d{4}$/.test(text.textContent.trim()));
  years.forEach(text=>text.style.removeProperty('display'));
  if(svg.dataset.nicYearLayout==='uniform'&&years.length>1){
   // Choose a regular annual interval that fits every label, including both endpoints.
   // Centered endpoints have their own reserved margin in drawRates.
   years.forEach(text=>text.setAttribute('text-anchor','middle'));
   const gap=8*box.width/width,last=years.length-1;
   let selected=[years[0],years[last]];
   for(let step=1;step<=last;step++){
    if(last%step)continue;
    const candidate=years.filter((_,index)=>index%step===0);
    if(candidate.every((text,index)=>!index||candidate[index-1].getBBox().x+candidate[index-1].getBBox().width+gap<=text.getBBox().x)){
     selected=candidate;break;
    }
   }
   years.forEach(text=>{if(!selected.includes(text))text.style.display='none';});
   return;
  }
  years.at(-1)?.setAttribute('text-anchor','end');
  // Preserve the first/last year, skipping intermediate ticks when space is tight.
  const gap=8*box.width/width,visible=[];
  years.forEach((text,index)=>{
   const bounds=text.getBBox(),previous=visible.at(-1);
   if(index===years.length-1){
    while(visible.length>1&&visible.at(-1).right+gap>bounds.x){visible.pop().text.style.display='none';}
   }else if(previous&&previous.right+gap>bounds.x){text.style.display='none';return;}
   visible.push({text,right:bounds.x+bounds.width});
  });
 });
}
function scheduleChartLabels(){if(!chartFrame)chartFrame=requestAnimationFrame(refreshChartLabels);}
new MutationObserver(scheduleChartLabels).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
new MutationObserver(scheduleChartLabels).observe(document.head,{childList:true,subtree:true,characterData:true});
new MutationObserver(scheduleChartLabels).observe(document.documentElement,{attributes:true,attributeFilter:['style']});
window.addEventListener('resize',scheduleChartLabels);
window.addEventListener('nic-settings-ready',scheduleChartLabels);
document.fonts?.ready.then(scheduleChartLabels);
scheduleChartLabels();

/* Shared action bar: one initialization, with original calculator event handlers retained. */
function setupCalculatorActions(){
 const footer=document.querySelector('.footer-note, .nic-shared-footer');
 document.querySelectorAll('.bottom-actions').forEach(actions=>{
  const bar=actions.closest('.bottom');
  const buttons=Array.from(actions.querySelectorAll('button'));
  if(!bar||!footer||buttons.length<3||actions.dataset.nicActionConfigured==='1')return;
  const financeModule=bar.closest('#nicFinanceModule');
  if(financeModule)return;
  actions.dataset.nicActionConfigured='1';
  const [reset,share,download]=buttons;
  reset.classList.add('bottom-primary','nic-action-0');
  share.classList.add('bottom-pdf','nic-action-1');
  download.classList.add('bottom-save','nic-action-2');
  actions.classList.add('nic-unified-calculator-actions');
  if(!bar.classList.contains('nic-actions-above-footer')){
   footer.before(bar);
   bar.classList.add('nic-actions-above-footer');
  }
  // One confirmation for every calculator. Existing synchronous reset handlers
  // keep their own actions; suppress any redundant legacy confirm for this click.
  if(reset.dataset.nicConfirmReset!=='1'){
   reset.dataset.nicConfirmReset='1';
   reset.addEventListener('click',event=>{
    const confirmOriginal=window.confirm;
    const accepted=confirmOriginal.call(window,'Möchtest du wirklich neu berechnen und deine bisherigen Eingaben löschen?');
    if(!accepted){
     event.preventDefault();
     event.stopImmediatePropagation();
     return;
    }
    try{
     window.confirm=()=>true;
     queueMicrotask(()=>{
      if(window.confirm!==confirmOriginal)window.confirm=confirmOriginal;
     });
    }catch(_err){
     // Reset still proceeds if this browser does not permit overriding confirm.
    }
   },true);
  }
  const normalize=()=>{
   if(reset.textContent.trim()!=='Neu berechnen')reset.textContent='Neu berechnen';
   if(share.textContent.trim()!=='PDF teilen')share.textContent='PDF teilen';
  };
  normalize();
  // Legacy calculator code can reset captions on mode changes. Observe only labels.
  const observer=new MutationObserver(normalize);
  observer.observe(reset,{subtree:true,childList:true,characterData:true});
  observer.observe(share,{subtree:true,childList:true,characterData:true});
 });
}
setupCalculatorActions();
// Calculator views are mounted after the shared page scripts run; configure
// their action bars as soon as the view is inserted into the shared document.
new MutationObserver(setupCalculatorActions).observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['hidden']});
// Existing authentication capture handler keeps logged-in account behavior.
// Wait for initialization on a very early click instead of opening administration.
document.querySelector('.nic-login-button')?.addEventListener('click',async e=>{
 e.preventDefault();e.stopImmediatePropagation();
 try{const access=window.NICAccess;if(access&&await access.init())await access.login();}catch(error){alert(error.message);}
},true);
// Keep Budget's available-equity qualifier below its input as a proper hint.
// Do not alter field values, IDs or calculator events.
function bindBudgetAvailableEquityHint(){
 const section=document.querySelector('#budgetSection');
 if(!section)return;
 section.querySelectorAll('.field').forEach(field=>{
  const label=field.querySelector('label');
  if(!label||!/Eigenkapital/i.test(label.textContent||'')||!/verfügbar/i.test(label.textContent||''))return;
  const input=field.querySelector('.input-wrap')||field.querySelector('input');
  if(!input)return;
  const existing=field.querySelector('.nic-budget-free-equity-hint');
  if(existing)return;
  const hint=document.createElement('div');
  hint.className='hint nic-budget-free-equity-hint';
  hint.textContent='Frei verfügbarer Betrag';
  const labelLeaves=[...label.querySelectorAll('*')].filter(el=>el.children.length===0&&/^verfügbar$/i.test(el.textContent.trim()));
  if(labelLeaves.length===1)labelLeaves[0].remove();
  else {
   [...label.childNodes].filter(node=>node.nodeType===Node.TEXT_NODE).forEach(node=>{
    node.textContent=node.textContent.replace(/\bverfügbar\b/i,'');
   });
   if(/verfügbar/i.test(label.textContent))return; // Do not duplicate or damage ambiguous markup.
  }
  input.after(hint);
 });
}
function bindFlipSaleReviewHint(){
 document.querySelectorAll('#flipSection *, #result *').forEach(el=>{
  if(el.children.length||el.textContent.trim()!=='geändert (bitte prüfen)')return;
  el.classList.add('nic-flip-sale-review-hint');
 });
}

function alignPropertyFields(){
 document.querySelectorAll('.app main.section .field').forEach(field=>{
  const label=field.querySelector(':scope > label');
  if(label&&/^(?:Wohnfläche|Baujahr|Grundstück(?:sgröße)?)$|^Preis pro m/i.test(label.textContent.replace(/\s+/g,' ').trim()))field.classList.add('nic-property-aligned-field');
 });
}

alignPropertyFields();
bindBudgetAvailableEquityHint();
bindFlipSaleReviewHint();
new MutationObserver(()=>{alignPropertyFields();bindBudgetAvailableEquityHint();bindFlipSaleReviewHint();}).observe(document.body,{childList:true,subtree:true});
})();
