(function(){
'use strict';
const EVENTS={page_view:'nic_page_view',calculator_use:'nic_calculator_use',calculate:'nic_calculate',pdf_download:'nic_pdf_download',pdf_share:'nic_pdf_share'};
const CALCULATORS=['budget','own','rent','flip'],SECTIONS=['website','company',...CALCULATORS];
function dayKey(date=new Date()){const p=new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Berlin',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(date);return ['year','month','day'].map(k=>p.find(x=>x.type===k).value).join('-');}
function empty(){return {version:1,startedAt:null,days:{}};}
function blankTotals(){return {events:Object.fromEntries(Object.keys(EVENTS).map(k=>[k,0])),calculators:Object.fromEntries(CALCULATORS.map(k=>[k,Object.fromEntries(Object.keys(EVENTS).map(e=>[e,0]))])),devices:{},systems:{},sources:{}};}
function detectDevice(nav){const ua=nav.userAgent||'',platform=nav.userAgentData?.platform||nav.platform||'';let device=/iPad|Tablet/i.test(ua)||(/Mac/i.test(platform)&&nav.maxTouchPoints>1)?'Tablet':/Mobi|iPhone|Android/i.test(ua)?'Smartphone':'Desktop';if(/Android/i.test(ua)&&!/Mobile/i.test(ua))device='Tablet';const os=/iPhone|iPad|iPod/i.test(ua)||(/Mac/i.test(platform)&&nav.maxTouchPoints>1)?'iOS / iPadOS':/Android/i.test(ua)?'Android':/Windows/i.test(ua+' '+platform)?'Windows':/CrOS/i.test(ua)?'ChromeOS':/Mac/i.test(ua+' '+platform)?'macOS':/Linux/i.test(ua+' '+platform)?'Linux':'Unbekannt';return {device,os};}
function source(referrer,href){try{const here=new URL(href),campaign=here.searchParams.get('utm_source');if(campaign&&/^[a-zA-Z0-9_.-]{1,48}$/.test(campaign))return campaign;const ref=new URL(referrer);return ref.hostname===here.hostname?'Interner Verweis':ref.hostname.replace(/^www\./,'').slice(0,100);}catch(_){return 'Direkt / unbekannt';}}
function increment(map,k,n=1){const prev=Object.hasOwn(map,k)?Number(map[k])||0:0;Object.defineProperty(map,k,{value:prev+n,writable:true,enumerable:true,configurable:true});}
function record(data,type,calculator,context,date=new Date()){
 if(!Object.hasOwn(EVENTS,type))return data;
 const today=dayKey(date),out=data&&data.version===1&&data.days&&typeof data.days==='object'?data:empty();
 const cutoff=dayKey(new Date(date.getTime()-89*86400000));for(const key of Object.keys(out.days))if(key<cutoff||!/^\d{4}-\d{2}-\d{2}$/.test(key))delete out.days[key];
 let d=out.days[today];if(!d||!d.events||!d.calculators||!d.devices||!d.systems||!d.sources)d=out.days[today]=blankTotals();out.startedAt=out.startedAt||date.toISOString();increment(d.events,type);
 if(CALCULATORS.includes(calculator))increment(d.calculators[calculator],type);
 if(type==='page_view'){increment(d.devices,context.device);increment(d.systems,context.os);increment(d.sources,context.source);}
 return out;
}
function summary(data,days=30,date=new Date()){
 const total=blankTotals(),cutoff=dayKey(new Date(date.getTime()-(days-1)*86400000));
 for(const [key,d] of Object.entries(data?.days||{})){if(key<cutoff||key>dayKey(date)||!d||typeof d!=='object')continue;
  for(const e of Object.keys(EVENTS))increment(total.events,e,Math.max(0,Number(d.events?.[e])||0));
  for(const c of CALCULATORS)for(const e of Object.keys(EVENTS))increment(total.calculators[c],e,Math.max(0,Number(d.calculators?.[c]?.[e])||0));
  for(const field of ['devices','systems','sources'])for(const [k,n] of Object.entries(d[field]||{}))increment(total[field],k,Math.max(0,Number(n)||0));
 }return total;
}
window.NICStatsCore={EVENTS,CALCULATORS,SECTIONS,dayKey,empty,blankTotals,detectDevice,source,record,summary};
})();
