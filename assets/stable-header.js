(function(){
'use strict';
function initialize(){
const hero=document.querySelector('.app > .hero');
const data=document.getElementById('nic-header-variants');
if(!hero||!data)return;
const variants=JSON.parse(data.textContent);
hero.classList.add('nic-responsive-header');
let queued=false,lastWidth=0,renderScale=1;
// DOM rectangles include CSS zoom; CSS dimensions and padding do not.
// Convert once into layout units before sizing the hidden probe or live header.
function effectiveScale(el){
 if(el.currentCSSZoom>0)return el.currentCSSZoom;
 let scale=1;
 for(let node=el;node;node=node.parentElement){
  const raw=getComputedStyle(node).zoom,value=parseFloat(raw);
  if(Number.isFinite(value)&&value>0)scale*=raw.endsWith('%')?value/100:value;
 }
 return scale;
}
function geometry(el){
 const r=el.getBoundingClientRect();
 return {width:r.width/renderScale,height:r.height/renderScale,top:r.top/renderScale,bottom:r.bottom/renderScale};
}
function measure(){
 queued=false;
 renderScale=effectiveScale(hero);
 const width=geometry(hero).width;if(width<=0)return;
 const probe=hero.cloneNode(true);probe.classList.remove('nic-fixed-header');
 // The probe must measure CONTENT height, not inherit the previously reserved
 // height from the real header. Otherwise route changes cause a feedback loop.
 probe.style.setProperty('--nic-header-content-height','0px');
 probe.querySelectorAll('[id]').forEach(el=>el.removeAttribute('id'));
 // Isolate any cloned form controls from the live page's radio groups.
 // Inert/aria-hidden alone do not isolate native radio groups.
 probe.querySelectorAll('[name]').forEach(el=>el.removeAttribute('name'));
 probe.removeAttribute('id');probe.setAttribute('aria-hidden','true');probe.inert=true;
 Object.assign(probe.style,{position:'fixed',left:'-20000px',top:'0',visibility:'hidden',pointerEvents:'none',boxSizing:'border-box',width:width+'px',display:'flow-root'});
 for(const [property,value] of [['height','auto'],['min-height','0px'],['max-height','none']])probe.style.setProperty(property,value,'important');
 // Keep the same ancestor styles and inherited typography as the visible header.
 hero.parentElement.append(probe);
 try{
  const heading=probe.querySelector('h1'),description=probe.querySelector('p');
  let maximum=0;
  const configured=window.NICCalculators?Object.values(window.NICSettings?.current?.content||{})
   .map(({headerTitle,headerDescription})=>[headerTitle,headerDescription]):[];
  const states=[...(configured.length?configured:variants),
   [hero.querySelector('h1').textContent,hero.querySelector('p').textContent]];
  for(const [title,text] of states){
   heading.textContent=title;
   description.textContent=text;
   heading.style.display=title?'':'none';
   description.style.display=text?'':'none';
   maximum=Math.max(maximum,geometry(probe).height);
  }
  // Only the normal-flow box contributes to the reserved height. Sticky or
  // positioned children can report viewport-relative coordinates while scrolling.
  const value=Math.ceil(maximum+1)+'px';
  if(hero.style.getPropertyValue('--nic-header-content-height')!==value)hero.style.setProperty('--nic-header-content-height',value);
  if(!hero.classList.contains('nic-fixed-header'))hero.classList.add('nic-fixed-header');
  lastWidth=width;
 }finally{probe.remove();}
}
function schedule(){if(!queued){queued=true;requestAnimationFrame(measure);}}
new ResizeObserver(()=>{if(Math.abs(geometry(hero).width-lastWidth)>.5)schedule();}).observe(hero);
new MutationObserver(schedule).observe(hero,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['src','style']});
hero.addEventListener('load',schedule,true);
// Safari's browser bars change viewport height during scrolling; only width changes require remeasurement.
window.addEventListener('resize',()=>{if(Math.abs(geometry(hero).width-lastWidth)>.5)schedule();});
window.addEventListener('orientationchange',schedule);
document.fonts?.ready.then(schedule);
window.NICHeader={refresh:schedule};
// Reserve the largest variant synchronously on first load, before the next paint.
measure();
window.NICCalculatorNavigation?.restore();
}
window.NICInitializeHeader=initialize;
initialize();
})();
