/* Complete route copy is also rendered in the initial HTML for crawlers. */
/* EXPLANATION_TEMPLATES */
window.NICExplanations=(()=>{
 const mobile=matchMedia('(max-width:760px),(max-width:1024px) and (max-height:600px) and (orientation:landscape)');
 const bound=new WeakSet(),observed=new WeakSet();
 let active=null,queued=false,lastSignature='';
 function bind(card){
  const details=card.querySelector('details'),summary=details.querySelector('summary');
  if(!bound.has(details)){
   bound.add(details);
   details.addEventListener('toggle',()=>{
    if(!mobile.matches&&!details.open){details.open=true;return;}
    summary.textContent=details.open?'weniger anzeigen':'weiterlesen';
   });
  }
  return details;
 }
 function measure(){
  queued=false;
  const card=document.querySelector('[data-nic-explanation]'),main=card?.parentElement;
  if(!card||!main)return;
  const rect=card.getBoundingClientRect(),style=getComputedStyle(card),width=parseFloat(style.width);
  if(!width||!rect.width)return;
  const signature=[width,mobile.matches,style.font, getComputedStyle(card.querySelector('h2')).font,getComputedStyle(card.querySelector('h3')).font].join('|');
  if(signature===lastSignature)return;
  lastSignature=signature;
  const scale=rect.width/width;
  let maximum=0;
  for(const markup of Object.values(explanationTemplates)){
   const holder=document.createElement('template');holder.innerHTML=markup;
   const probe=holder.content.firstElementChild;
   probe.removeAttribute('id');probe.removeAttribute('data-nic-explanation');probe.removeAttribute('aria-labelledby');
   probe.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));
   probe.inert=true;probe.setAttribute('aria-hidden','true');
   Object.assign(probe.style,{position:'fixed',left:'-20000px',top:'0',visibility:'hidden',width:width+'px',height:'auto',maxHeight:'none',pointerEvents:'none'});
   probe.style.setProperty('min-block-size','0','important');
   probe.querySelector('details').open=!mobile.matches;
   main.append(probe);
   maximum=Math.max(maximum,probe.getBoundingClientRect().height/scale);
   probe.remove();
  }
  main.style.setProperty('--nic-explanation-height',Math.ceil(maximum)+'px');
 }
 function schedule(){if(!queued){queued=true;requestAnimationFrame(measure);}}
 const observer=new ResizeObserver(schedule);
 function show(key){
  const main=document.querySelector('.app>main.section');if(!main)return;
  for(const card of main.querySelectorAll('[data-nic-explanation]'))if(card.dataset.nicExplanation!==key)card.remove();
  if(!explanationTemplates[key]){active=null;return;}
  let card=main.querySelector('[data-nic-explanation="'+key+'"]');
  if(!card){main.insertAdjacentHTML('afterbegin',explanationTemplates[key]);card=main.firstElementChild;}
  const details=bind(card);
  if(active!==key)details.open=!mobile.matches;
  card.querySelector('summary').textContent=details.open?'weniger anzeigen':'weiterlesen';
  active=key;
  if(!observed.has(main)){observer.observe(main);observed.add(main);}
  schedule();
 }
 mobile.addEventListener('change',()=>{
  const card=document.querySelector('[data-nic-explanation]');if(card){bind(card).open=!mobile.matches;lastSignature='';schedule();}
 });
 window.addEventListener('nic-settings-updated',()=>{lastSignature='';schedule();});
 window.addEventListener('nic-auth-changed',()=>{lastSignature='';schedule();});
 document.fonts?.ready.then(()=>{lastSignature='';schedule();});
 return {show,refresh(){lastSignature='';schedule();}};
})();
