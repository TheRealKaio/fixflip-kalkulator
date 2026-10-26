(function(){
'use strict';
function initialize(){
const hero=document.querySelector('.app > .hero');
const data=document.getElementById('nic-header-variants');
if(!hero||!data)return;
const variants=JSON.parse(data.textContent);
hero.classList.add('nic-responsive-header');
let queued=false,lastWidth=0,lastSignature='',largestForLayout=0;
function measure(){
 queued=false;
 const width=hero.getBoundingClientRect().width;if(width<=0)return;
 const probe=hero.cloneNode(true);probe.classList.remove('nic-fixed-header');
 probe.querySelectorAll('[id]').forEach(el=>el.removeAttribute('id'));
 probe.removeAttribute('id');probe.setAttribute('aria-hidden','true');probe.inert=true;
 Object.assign(probe.style,{position:'fixed',left:'-20000px',top:'0',visibility:'hidden',pointerEvents:'none',boxSizing:'border-box',width:width+'px',height:'auto',minHeight:'0',maxHeight:'none',display:'flow-root'});
 // Keep the same ancestor styles and inherited typography as the visible header.
 hero.parentElement.append(probe);
 try{
  const heading=probe.querySelector('h1'),description=probe.querySelector('p');
  let maximum=0;
  const states=[...variants,[hero.querySelector('h1').innerHTML,hero.querySelector('p').textContent]];
  for(const [title,text]of states){
   heading.innerHTML=title;description.textContent=text;
   const rect=probe.getBoundingClientRect(),style=getComputedStyle(probe);
   const bottom=Math.max(rect.top,...Array.from(probe.children).map(el=>el.getBoundingClientRect().bottom));
   // Measure every variant's actual text extent, including rental, before fixing
   // the live height. This guard must not depend on visiting that calculator.
   const extent=bottom-rect.top+parseFloat(style.paddingBottom||0)+parseFloat(style.borderBottomWidth||0);
   maximum=Math.max(maximum,rect.height,extent);
  }
  // Include the actual rendered text, so inherited styles or late font changes
  // cannot make the live subtitle exceed the measured clone.
  const box=hero.getBoundingClientRect(),heroStyle=getComputedStyle(hero);
  const headingStyle=getComputedStyle(hero.querySelector('h1')),descriptionStyle=getComputedStyle(hero.querySelector('p'));
  const top=hero.querySelector('.hero-top');
  const signature=[width,heroStyle.padding,headingStyle.font,headingStyle.letterSpacing,descriptionStyle.font,descriptionStyle.letterSpacing,top?.getBoundingClientRect().height].join('|');
  const contentBottom=Math.max(...Array.from(hero.children).map(el=>el.getBoundingClientRect().bottom));
  maximum=Math.max(maximum,contentBottom-box.top+parseFloat(heroStyle.paddingBottom||0)+parseFloat(heroStyle.borderBottomWidth||0));
  if(signature!==lastSignature){largestForLayout=0;lastSignature=signature;}
  largestForLayout=Math.max(largestForLayout,maximum);
  const value=Math.ceil(largestForLayout+1)+'px';
  if(hero.style.getPropertyValue('--nic-header-content-height')!==value)hero.style.setProperty('--nic-header-content-height',value);
  if(!hero.classList.contains('nic-fixed-header'))hero.classList.add('nic-fixed-header');
  lastWidth=width;
 }finally{probe.remove();}
}
function schedule(){if(!queued){queued=true;requestAnimationFrame(measure);}}
new ResizeObserver(()=>{if(Math.abs(hero.getBoundingClientRect().width-lastWidth)>.5)schedule();}).observe(hero);
new MutationObserver(schedule).observe(hero,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:['src','style']});
hero.addEventListener('load',schedule,true);
window.addEventListener('resize',schedule);
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
