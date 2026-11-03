(function(){
'use strict';
const message='Nur für angemeldete Nutzer sichtbar.';
const style=document.createElement('style');
style.id='nic-content-section-access-styles';
style.textContent=`
[data-nic-content-key].nic-content-box-hidden{display:none!important}
[data-nic-content-key].nic-content-box-guest-locked{position:relative!important;isolation:isolate}
[data-nic-content-key].nic-content-box-guest-locked > :not(.nic-content-box-guest-overlay){pointer-events:none!important;user-select:none!important}
[data-nic-content-key]>.nic-content-box-guest-overlay{
 position:absolute!important;inset:0!important;z-index:100!important;display:flex!important;
 align-items:center;justify-content:center;padding:20px;box-sizing:border-box;
 background:rgba(245,247,250,.72)!important;color:#94a3b8!important;
 font-family:var(--nic-body-font-family,inherit)!important;font-size:var(--nic-body-font-size,16px)!important;
 font-weight:500;text-align:center;line-height:1.5;cursor:not-allowed;
}
[data-nic-content-key].nic-content-box-guest-locked .nic-masked-value{
 color:transparent!important;text-shadow:none!important;position:relative!important;
 display:inline-block!important;width:fit-content!important;max-width:100%!important;
 box-sizing:border-box!important;vertical-align:middle!important;
 background:#252525!important;border-radius:2px!important;
}
[data-nic-content-key].nic-content-box-guest-locked .cost-row{
 min-width:0!important;grid-template-columns:minmax(0,1fr) max-content!important;
}
[data-nic-content-key].nic-content-box-guest-locked .cost-row>span:first-child{
 min-width:0!important;overflow-wrap:anywhere!important;
}
[data-nic-content-key].nic-content-box-guest-locked .cost-row>strong.nic-masked-value{
 display:inline-block!important;width:max-content!important;justify-self:end!important;
}
[data-nic-content-key].nic-content-box-guest-locked input:not([type=checkbox]):not([type=radio]),
[data-nic-content-key].nic-content-box-guest-locked output{
 color:transparent!important;text-shadow:none!important;
 background-image:linear-gradient(#252525,#252525)!important;
 background-repeat:no-repeat!important;background-position:center!important;
 background-size:46px 12px!important;
}
html:not(.nic-content-ready) [data-nic-content-key]{visibility:hidden!important}
`;
(document.head||document.documentElement).appendChild(style);
let resolved=null;
let queued=false;
const controlStates=new Map();
const propertyStates=new Map();
function enforceProperty(element,key,value,active){
 let state=propertyStates.get(element);
 if(active){
   if(!state){state={};propertyStates.set(element,state);}
   if(!(key in state))state[key]=element[key];
   element[key]=value;
 }else if(state&&key in state){
   element[key]=state[key];delete state[key];
   if(!Object.keys(state).length)propertyStates.delete(element);
 }
}
const observerOptions={childList:true,subtree:true,characterData:true,attributes:true,
 attributeFilter:['class','hidden','inert','disabled','aria-disabled','style','data-nic-content-key']};
function watch(){observer.observe(document.documentElement,observerOptions);}
function blocked(target){
 return target?.closest?.('.nic-content-box-hidden,.nic-content-box-guest-locked');
}
// Capture before calculator listeners, including keyboard and synthetic clicks.
for(const type of ['click','dblclick','keydown','beforeinput','input','change','submit','reset']){
 document.addEventListener(type,event=>{
   if(!blocked(event.target))return;
   event.preventDefault();event.stopImmediatePropagation();
 },true);
}
function syncControls(){
 document.querySelectorAll('[data-nic-content-key] input,[data-nic-content-key] select,[data-nic-content-key] textarea,[data-nic-content-key] button').forEach(control=>{
   if(blocked(control)){
     if(!controlStates.has(control))controlStates.set(control,control.disabled);
     control.disabled=true;
   }
 });
 for(const [control,disabled] of controlStates){
   if(!control.isConnected||!blocked(control)){
     control.disabled=disabled;
     controlStates.delete(control);
   }
 }
}
function maskValues(box,locked){
 // Mask numbers not only inside named result classes, but also leaf-level text nodes.
 // Leave explanatory copy and headings readable.
 const named='.value,.amount,.kpi-value,.result-value,.result-amount,.metric-value,.budget-result-value,.stat-value';
 box.querySelectorAll(named).forEach(el=>el.classList.toggle('nic-masked-value',locked));
 box.querySelectorAll('span,strong,b,output,div,p,td').forEach(el=>{
   if(el.closest('.nic-content-box-guest-overlay')||el.matches(named))return;
   if(el.children.length||el.matches('[data-nic-content-key],.field,.card'))return;
   const value=(el.textContent||'').trim();
   const isAmount=/^(?:[-+]?\s*\d[\d.,\s]*(?:\s*(?:€|%|EUR|Jahre?|Monate?))?|(?:€\s*\d[\d.,\s]*))$/.test(value);
   el.classList.toggle('nic-masked-value',locked&&isAmount);
 });
}
function apply(settings){
 if(!settings||!document.body)return;
 observer.disconnect();
 try{
 resolved=settings;
 const loggedIn=!!window.NICAccess?.user;
 document.querySelectorAll('[data-nic-content-key]').forEach(box=>{
   const rule=settings.contentSections?.[box.dataset.nicContentKey]||{};
   const hidden=rule.visible===false;
   const locked=!hidden&&!loggedIn&&rule.guestAllowed===false;
   box.classList.toggle('nic-content-box-hidden',hidden);
   box.classList.toggle('nic-content-box-guest-locked',locked);
   maskValues(box,locked);
   enforceProperty(box,'hidden',true,hidden);
   enforceProperty(box,'inert',true,hidden||locked);
   let overlay=Array.from(box.children).find(el=>el.classList.contains('nic-content-box-guest-overlay'));
   if(locked&&!overlay){
     overlay=document.createElement('div');
     overlay.className='nic-content-box-guest-overlay';
     overlay.setAttribute('role','note');
     overlay.textContent=message;
     box.appendChild(overlay);
   }else if(!locked&&overlay)overlay.remove();

   if(locked)box.setAttribute('aria-disabled','true');
   else box.removeAttribute('aria-disabled');
 });
 for(const [element] of propertyStates)if(!element.isConnected)propertyStates.delete(element);
 syncControls();
 document.documentElement.classList.add('nic-content-ready');
 }finally{watch();}
}
window.NICContentSections={apply};
window.addEventListener('nic-auth-changed',()=>{if(resolved)apply(resolved);});
window.addEventListener('nic-settings-updated',()=>{if(window.NICSettings?.current)apply(window.NICSettings.current);});
const observer=new MutationObserver(records=>{
 if(!resolved||queued)return;
 if(!records.some(record=>{
   const target=record.target.nodeType===1?record.target:record.target.parentElement;
   return target?.closest?.('[data-nic-content-key]')||
     Array.from(record.addedNodes||[]).some(node=>node.nodeType===1&&
       (node.closest?.('[data-nic-content-key]')||node.querySelector?.('[data-nic-content-key]')));
 }))return;
 queued=true;
 queueMicrotask(()=>{queued=false;apply(resolved);});
});
watch();
window.addEventListener('pageshow',()=>{if(resolved)apply(resolved);});
const settingsApi=window.NICSettings;
if(settingsApi?.init){
 settingsApi.init().then(settings=>{
   settingsApi.apply(settings);
   apply(settings);
 }).catch(error=>console.warn('Zentrale Box-Einstellungen:',error.message));
}
})();
