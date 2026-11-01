/* Non-destructive calculator card navigation.
   Keeps nodes in place, never clones inputs, never changes IDs, values, charts or handlers. */
(()=>{
'use strict';
function init(){
 const page=document.documentElement.dataset.nicPage || (location.pathname.includes('finanzierungsrechner')?'finance':'');
 const root=page==='finance'?document.querySelector('main.section'):document.querySelector('#budgetSection, #rentSection, #dealCalculatorContent');
 if(!root)return;
 const cards=[...root.children].filter(el=>el.matches('.card, section.card, div.card')&&!el.classList.contains('deal-type-card'));
 // The visible original card structure is the only source of step counts.
 if(cards.length<2)return;
 const nav=document.createElement('nav');nav.className='nic-step-nav';nav.setAttribute('aria-label','Rechner-Schritte');
 const counter=document.createElement('span');counter.className='nic-step-count';nav.append(counter);
 const steps=document.createElement('div');steps.className='nic-step-buttons';nav.append(steps);
 const prev=document.createElement('button'),next=document.createElement('button');prev.type=next.type='button';prev.className='nic-step-prev';next.className='nic-step-next';prev.textContent='Zurück';next.textContent='Weiter';
 const controls=document.createElement('div');controls.className='nic-step-controls';controls.append(prev,next);
 let current=0;
 const buttons=cards.map((card,i)=>{const b=document.createElement('button');b.type='button';b.className='nic-step-dot';b.textContent=String(i+1);const heading=card.querySelector('h2,h3,.section-title');b.setAttribute('aria-label','Schritt '+(i+1)+(heading?' – '+heading.textContent.trim():''));b.addEventListener('click',()=>show(i));steps.append(b);return b;});
 function show(index){current=Math.max(0,Math.min(index,cards.length-1));cards.forEach((c,i)=>{c.classList.toggle('nic-step-inactive',i!==current);c.setAttribute('data-nic-step',String(i+1));});buttons.forEach((b,i)=>{b.setAttribute('aria-current',i===current?'step':'false')});counter.textContent='Schritt '+(current+1)+' von '+cards.length;prev.disabled=current===0;next.disabled=current===cards.length-1;}
 prev.addEventListener('click',()=>show(current-1));next.addEventListener('click',()=>show(current+1));
 root.insertBefore(nav,cards[0]);root.insertBefore(controls,cards[cards.length-1].nextSibling);root.classList.add('nic-step-enabled');show(0);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();