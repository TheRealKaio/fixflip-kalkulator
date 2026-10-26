(function(){
'use strict';
const key='nic_calculator_navigation_v1';
const paths=new Set(['/budget/','/eigennutzung/','/vermietung/','/fix-flip/','/finanzierungsrechner/']);
// Only calculator menu transitions carry their scroll position to the new document.
document.addEventListener('click',event=>{
 if(event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 const card=event.target.closest('[data-href],#nicFinancingTab');if(!card)return;
 const url=new URL(card.dataset.href||card.href,location.href);
 if(url.origin!==location.origin||!paths.has(url.pathname)||url.pathname===location.pathname)return;
 try{sessionStorage.setItem(key,JSON.stringify({path:url.pathname,y:window.scrollY,at:Date.now()}));}catch(_){}
},true);
let saved;
try{saved=JSON.parse(sessionStorage.getItem(key)||'null');sessionStorage.removeItem(key);}catch(_){}
if(!saved||saved.path!==location.pathname||Date.now()-saved.at>15000||!Number.isFinite(saved.y)||saved.y<0)return;
const previous=history.scrollRestoration,root=document.documentElement,previousMinHeight=root.style.minHeight;history.scrollRestoration='manual';
// Make the previous scroll offset available even while the destination body is parsing.
root.style.minHeight=Math.max(root.getBoundingClientRect().height,innerHeight+saved.y)+'px';
const release=()=>{root.style.minHeight=previousMinHeight;history.scrollRestoration=previous;};
const started=Date.now();let cancelled=false;
const cancel=()=>{cancelled=true;release();};
for(const name of ['wheel','touchstart','pointerdown','keydown'])window.addEventListener(name,cancel,{once:true,passive:true});
function restore(){
 if(cancelled||Date.now()-started>5000){release();return;}
 const hero=document.querySelector('.hero');
 if(!window.NICSettings?.current||!hero?.classList.contains('nic-fixed-header')){requestAnimationFrame(restore);return;}
 window.scrollTo({top:saved.y,left:0,behavior:'instant'});
 if(document.readyState==='complete')release();
 else requestAnimationFrame(restore);
}
window.NICCalculatorNavigation={restore};
requestAnimationFrame(restore);
})();
