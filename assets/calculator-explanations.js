/* Complete route copy is also rendered in the initial HTML for crawlers. */
/* EXPLANATION_TEMPLATES */
window.NICExplanations=(()=>{
 const compact=matchMedia('(max-width:700px), (max-width:1024px) and (max-height:600px) and (orientation:landscape)');
 const bound=new WeakSet(),observed=new WeakSet();
 let active=null,homeCard=null,homeCompact=null,queued=false,lastSignature='';
 function markup(key){
  const settings=window.NICSettings?.current,content=settings?.content?.[key];
  if(!content)return explanationTemplates[key];
  const holder=document.createElement('template');holder.innerHTML=explanationTemplates[key];
  const card=holder.content.firstElementChild;
  card.querySelector('h2').textContent=content.boxTitle||content.title;
  const body=window.NICSettings.contentFragment(content.description,settings);
  let intro=body.querySelector('p');
  if(intro)intro.remove();else{intro=document.createElement('p');intro.textContent=body.textContent;body.replaceChildren();}
  intro.classList.add('nic-explanation-intro');
  card.querySelector('.nic-explanation-intro').replaceWith(intro);
  const teaser=card.querySelector('.nic-explanation-teaser');
  const rest=card.querySelector('.nic-explanation-rest');
  const nodes=Array.from(body.childNodes);
  const secondIndex=nodes.findIndex(node=>node.nodeType===1&&node.matches('p'));
  if(secondIndex>=0){
   teaser.replaceChildren(...nodes.slice(0,secondIndex+1));
   rest.replaceChildren(...nodes.slice(secondIndex+1));
  }else{
   teaser.replaceChildren();
   rest.replaceChildren(body);
  }
  card.querySelector('details').hidden=!rest.textContent.trim();
  return card.outerHTML;
 }

 function bind(card){
  const details=card.querySelector(':scope > details'),summary=details.querySelector(':scope > summary');
  if(!bound.has(details)){
   bound.add(details);
   details.addEventListener('toggle',()=>{
    summary.textContent=details.open?'weniger anzeigen':'weiterlesen';
   });
  }
  return details;
 }
 function introText(key){
  const settings=window.NICSettings?.current;
  const content=settings?.content?.[key];
  if(content){
   const body=window.NICSettings.contentFragment(content.description,settings);
   return (body.querySelector('p')?.textContent??body.textContent).trim();
  }
  const template=document.createElement('template');
  template.innerHTML=explanationTemplates[key]||'';
  return template.content.querySelector('.nic-explanation-intro')?.textContent.trim()||'';
 }
 function measureMobile(card){
  const preview=card.querySelector(':scope > .nic-mobile-intro')||document.createElement('p');
  const text=introText(card===homeCard?'welcome':card.dataset.nicExplanation);
  if(!text){preview.remove();return;}
  preview.className='nic-mobile-intro nic-mobile-intro-probe';
  card.querySelector(':scope > h2').after(preview);
  let lines=Infinity;
  for(const key of ['welcome',...Object.keys(explanationTemplates).filter(key=>key!=='settlement')]){
   const paragraph=introText(key);
   if(!paragraph)continue;
   preview.textContent=paragraph;
   const lineHeight=parseFloat(getComputedStyle(preview).lineHeight);
   lines=Math.min(lines,Math.max(1,Math.round(preview.getBoundingClientRect().height/lineHeight)));
  }
  card.style.setProperty('--nic-mobile-intro-lines',String(lines));
  preview.textContent=text;
  preview.classList.remove('nic-mobile-intro-probe');
 }
 function measure(){
  queued=false;
  const card=homeCard||document.querySelector('[data-nic-explanation]'),main=card?.closest('main');
  if(!card||!main||!card.getBoundingClientRect().width)return;
  if(compact.matches){measureMobile(card);main.style.removeProperty('--nic-explanation-height');return;}
  if(card===homeCard)return;
  const rect=card.getBoundingClientRect(),style=getComputedStyle(card),width=parseFloat(style.width);
  if(!width||!rect.width)return;
  const signature=[width,style.font,getComputedStyle(card.querySelector('h2')).font,getComputedStyle(card.querySelector('h3')||card.querySelector('h2')).font].join('|');
  if(signature===lastSignature)return;
  lastSignature=signature;
  const scale=rect.width/width;
  let maximum=0;
  for(const key of Object.keys(explanationTemplates)){
   const html=markup(key);
   const holder=document.createElement('template');holder.innerHTML=html;
   const probe=holder.content.firstElementChild;
   probe.removeAttribute('id');probe.removeAttribute('data-nic-explanation');probe.removeAttribute('aria-labelledby');
   probe.querySelectorAll('[id]').forEach(e=>e.removeAttribute('id'));
   probe.inert=true;probe.setAttribute('aria-hidden','true');
   Object.assign(probe.style,{position:'fixed',left:'-20000px',top:'0',visibility:'hidden',width:width+'px',height:'auto',maxHeight:'none',pointerEvents:'none'});
   probe.style.setProperty('min-block-size','0','important');
   probe.querySelector('details').open=false;
   main.append(probe);
   maximum=Math.max(maximum,probe.getBoundingClientRect().height/scale);
   probe.remove();
  }
  main.style.setProperty('--nic-explanation-height',Math.ceil(maximum)+'px');
 }
 function schedule(){if(!queued){queued=true;requestAnimationFrame(measure);}}
 const observer=new ResizeObserver(schedule);
 function observe(main){
  if(!observed.has(main)){observer.observe(main);observed.add(main);}
 }
 function showHome(card){
  const details=bind(card);
  if(homeCard!==card||homeCompact!==compact.matches){
   homeCard=card;homeCompact=compact.matches;
   details.open=!homeCompact;
  }
  details.querySelector('summary').textContent=details.open?'weniger anzeigen':'weiterlesen';
  observe(card.closest('main'));
  schedule();
 }
 function show(key){
  if(key!=='home')homeCard=null;
  const main=document.querySelector('.app>main.section');if(!main)return;
  for(const card of main.querySelectorAll('[data-nic-explanation]'))if(card.dataset.nicExplanation!==key)card.remove();
  if(!explanationTemplates[key]){active=null;return;}
  let card=main.querySelector('[data-nic-explanation="'+key+'"]');
  if(!card){main.insertAdjacentHTML('afterbegin',explanationTemplates[key]);card=main.firstElementChild;}
  const html=markup(key),wasOpen=card.querySelector('details').open;
  if(card.dataset.contentSignature!==html){
   const holder=document.createElement('template');holder.innerHTML=html;
   card.replaceChildren(...holder.content.firstElementChild.childNodes);card.dataset.contentSignature=html;lastSignature='';
  }
  const details=bind(card);
  details.open=active===key&&wasOpen;
  card.querySelector('summary').textContent=details.open?'weniger anzeigen':'weiterlesen';
  active=key;
  observe(main);
  schedule();
 }
 compact.addEventListener('change',()=>{lastSignature='';if(homeCard)showHome(homeCard);else schedule();});
 window.addEventListener('nic-settings-updated',()=>{lastSignature='';schedule();});
 window.addEventListener('nic-auth-changed',()=>{lastSignature='';schedule();});
 document.fonts?.ready.then(()=>{lastSignature='';schedule();});
 function clear(){
  const main=document.querySelector('.app>main.section');
  if(main){main.querySelectorAll('[data-nic-explanation]').forEach(card=>card.remove());main.style.removeProperty('--nic-explanation-height');}
  active=null;homeCard=null;lastSignature='';
 }
 return {show,showHome,clear,refresh(){lastSignature='';if(active)show(active);else schedule();}};
})();
