/* Presentation only: keep calculator inputs, IDs, events and calculations intact. */
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

/* Shared action bar: one initialization, with original calculator event handlers retained. */
function setupCalculatorActions(){
 const footer=document.querySelector('.footer-note, .nic-shared-footer');
 document.querySelectorAll('.bottom-actions').forEach(actions=>{
  const bar=actions.closest('.bottom');
  const buttons=Array.from(actions.querySelectorAll('button'));
  if(!bar||!footer||buttons.length<3)return;
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
    const accepted=confirmOriginal.call(window,'Möchtest du wirklich neu kalkulieren und deine bisherigen Eingaben löschen?');
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
   if(reset.textContent.trim()!=='Neu kalkulieren')reset.textContent='Neu kalkulieren';
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
// Existing authentication capture handler keeps logged-in account behavior.
// Wait for initialization on a very early click instead of opening administration.
document.querySelector('.nic-login-button')?.addEventListener('click',async e=>{
 e.preventDefault();e.stopImmediatePropagation();
 try{const access=window.NICAccess;if(access&&await access.init())await access.login();}catch(error){alert(error.message);}
},true);
})();
