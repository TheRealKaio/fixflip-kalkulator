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

/* Put the existing calculator action bar in normal document flow above the footer. */
function positionCalculatorActions(){
 const footer=document.querySelector('.footer-note, .nic-shared-footer');
 const bar=document.querySelector('.app > .bottom, .bottom');
 if(!footer||!bar||bar===footer||bar.dataset.nicPositioned==='1')return;
 footer.before(bar);
 bar.dataset.nicPositioned='1';
 bar.classList.add('nic-actions-above-footer');
}
positionCalculatorActions();
/* All five calculators: align the footer to the visible shared brand header. */
function alignSharedFooter(){
 const header=document.querySelector('.app > .nic-brand-bar')||document.querySelector('.app > .hero');
 const footer=document.querySelector('.footer-note, .nic-shared-footer');
 if(!header||!footer)return;
 footer.style.removeProperty('transform');
 footer.style.setProperty('box-sizing','border-box','important');
 footer.style.setProperty('margin-left','0','important');
 footer.style.setProperty('margin-right','0','important');
 footer.style.setProperty('min-width','0','important');
 footer.style.setProperty('width','100%','important');
 footer.style.setProperty('max-width','100%','important');
 const headerRect=header.getBoundingClientRect();
 const footerRect=footer.getBoundingClientRect();
 if(headerRect.width<=0)return;
 footer.style.setProperty('width',headerRect.width+'px','important');
 footer.style.setProperty('max-width','none','important');
 footer.style.setProperty('transform','translateX('+(headerRect.left-footer.getBoundingClientRect().left)+'px)','important');
 footer.style.setProperty('border-radius','22px 22px 0 0','important');
}
alignSharedFooter();
if(typeof window.addEventListener==='function'){
 window.addEventListener('resize',alignSharedFooter,{passive:true});
 window.addEventListener('orientationchange',alignSharedFooter,{passive:true});
}
// Existing authentication capture handler keeps logged-in account behavior.
// Wait for initialization on a very early click instead of opening administration.
document.querySelector('.nic-login-button')?.addEventListener('click',async e=>{
 e.preventDefault();e.stopImmediatePropagation();
 try{const access=window.NICAccess;if(access&&await access.init())await access.login();}catch(error){alert(error.message);}
},true);
})();
