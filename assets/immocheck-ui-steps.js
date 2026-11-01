/* Non-destructive calculator card navigation.
   Keeps nodes in place, never clones inputs, never changes IDs, values, charts or handlers. */
(()=>{
'use strict';
function init(){
 const page=location.pathname.includes('finanzierungsrechner')?'finance':(document.documentElement.dataset.nicPage||'');
 const root=page==='finance'?document.querySelector('main.section'):({'budget':'#budgetSection','rent':'#rentSection','own':'#dealCalculatorContent','flip':'#dealCalculatorContent'}[page] ? document.querySelector({'budget':'#budgetSection','rent':'#rentSection','own':'#dealCalculatorContent','flip':'#dealCalculatorContent'}[page]) : null);
 if(!root || root.classList.contains('mode-hidden'))return;
 const cards=[...root.children].filter(el=>el.matches('.card, section.card, div.card')&&!el.classList.contains('deal-type-card')&&!el.classList.contains('mode-hidden'));
 // The visible original card structure is the only source of step counts.
 if(cards.length<2)return;
 // Financing retains all native result, interest-curve, and refinance controls inside their original cards.
 if(page==='finance' && (!root.querySelector('#repayChart') || !root.querySelector('#rateChart') || !root.querySelector('#refinanceChange'))){console.warn('Financing navigation disabled: original results missing');return;}
 // Do not replace the six-box Budget UI with an incorrect number of steps.
 if(page==='budget' && cards.length!==6){console.warn('Budget step layout skipped: expected 6 original cards, found',cards.length);return;}
 // Preserve original section, slider, chart and expandable-field structure.
 const nav=document.createElement('nav');nav.className='nic-step-nav';nav.setAttribute('aria-label','Rechner-Schritte');
 const counter=document.createElement('span');counter.className='nic-step-count';nav.append(counter);
 const steps=document.createElement('div');steps.className='nic-step-buttons';nav.append(steps);
 const prev=document.createElement('button'),next=document.createElement('button');prev.type=next.type='button';prev.className='nic-step-prev';next.className='nic-step-next';prev.textContent='Zurück';next.textContent='Weiter';
 const controls=document.createElement('div');controls.className='nic-step-controls';controls.append(prev,next);
 let current=0;
 // Preserve original inline display values; result sections may have stronger visibility CSS.
 const originalDisplays=cards.map(c=>({value:c.style.getPropertyValue('display'),priority:c.style.getPropertyPriority('display')}));
 const buttons=cards.map((card,i)=>{const b=document.createElement('button');b.type='button';b.className='nic-step-dot';b.textContent=String(i+1);const heading=card.querySelector('h2,h3,.section-title');b.setAttribute('aria-label','Schritt '+(i+1)+(heading?' – '+heading.textContent.trim():''));b.addEventListener('click',()=>show(i));steps.append(b);return b;});
 function show(index){current=Math.max(0,Math.min(index,cards.length-1));cards.forEach((c,i)=>{c.classList.toggle('nic-step-inactive',i!==current);if(i!==current)c.style.setProperty('display','none','important');else if(originalDisplays[i].value)c.style.setProperty('display',originalDisplays[i].value,originalDisplays[i].priority);else c.style.removeProperty('display');c.setAttribute('data-nic-step',String(i+1));});buttons.forEach((b,i)=>{b.setAttribute('aria-current',i===current?'step':'false')});counter.textContent='Schritt '+(current+1)+' von '+cards.length;prev.disabled=current===0;next.disabled=current===cards.length-1;}
 prev.addEventListener('click',()=>show(current-1));next.addEventListener('click',()=>show(current+1));
 root.insertBefore(nav,cards[0]);root.insertBefore(controls,cards[cards.length-1].nextSibling);root.classList.add('nic-step-enabled');show(0);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();