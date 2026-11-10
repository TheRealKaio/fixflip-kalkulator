/* Run in the head before the app exists. Keep its normal layout measurable,
   but reveal it only after published settings and shared content are applied. */
(()=>{
'use strict';
const root=document.documentElement;
root.classList.add('nic-layout-loading');
const style=document.createElement('style');style.id='nic-initial-layout';
style.textContent='html.nic-layout-loading .app{visibility:hidden!important;pointer-events:none!important}';
document.head.append(style);
const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
let released=false;
let resolveReady;
window.NICInitialLayout={ready:new Promise(resolve=>{resolveReady=resolve;})};
function reveal(fallback){
 if(released)return;
 released=true;clearTimeout(watchdog);
 root.dataset.nicLayoutReady=fallback?'fallback':'ready';
 root.classList.remove('nic-layout-loading');
 resolveReady();
}
function applyCurrent(){
 const S=window.NICSettings;
 if(S?.current)S.apply(S.current,root.dataset.nicPage||'website');
 window.NICShell?.refresh();
 window.NICHeader?.refresh();
}
// A failed optional backend or blocked font/image must never leave the app hidden.
const watchdog=setTimeout(()=>{try{applyCurrent();}finally{reveal(true);}},30000);
async function initialize(){
 let fallback=false;
 try{
  const S=window.NICSettings;
  if(S){await S.init();applyCurrent();}
  await document.fonts?.ready;
  await Promise.all([...document.querySelectorAll('.nic-brand-bar img')].map(img=>img.decode?.().catch(()=>{})));
 }catch(error){
  fallback=true;applyCurrent();
  const key=root.dataset.nicPage||'website';
  if(['website','budget','own','rent','flip','finance','settlement','prices','why'].includes(key))window.NICCalculatorNavigation?.select(key==='website'?'home':key);
 }
 // Let the existing route callbacks and scheduled header measurement finish.
 window.NICHeader?.refresh();
 await frame();await frame();
 reveal(fallback);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialize,{once:true});
else initialize();
})();
