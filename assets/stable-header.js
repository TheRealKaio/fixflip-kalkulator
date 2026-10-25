(function(){
'use strict';
const hero=document.querySelector('.app > .hero');
const data=document.getElementById('nic-header-variants');
if(!hero||!data)return;
const variants=JSON.parse(data.textContent);
let queued=false,lastWidth=0;
function measure(){
 queued=false;
 const width=hero.getBoundingClientRect().width;if(width<=0)return;
 const probe=hero.cloneNode(true);probe.classList.remove('nic-fixed-header');
 probe.querySelectorAll('[id]').forEach(el=>el.removeAttribute('id'));
 probe.removeAttribute('id');probe.setAttribute('aria-hidden','true');probe.inert=true;
 Object.assign(probe.style,{position:'fixed',left:'-20000px',top:'0',visibility:'hidden',pointerEvents:'none',boxSizing:'border-box',width:width+'px',height:'auto',minHeight:'0',maxHeight:'none',display:'flow-root'});
 document.body.append(probe);
 try{
  const heading=probe.querySelector('h1'),description=probe.querySelector('p');
  let maximum=0;
  const states=[...variants,[hero.querySelector('h1').innerHTML,hero.querySelector('p').textContent]];
  for(const [title,text]of states){heading.innerHTML=title;description.textContent=text;maximum=Math.max(maximum,probe.getBoundingClientRect().height);}
  const value=Math.ceil(maximum+1)+'px';
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
schedule();
})();
