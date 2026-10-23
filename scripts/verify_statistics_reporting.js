'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const site=process.argv[2]||'_site';
class Element{
 constructor(){this.value='';this.children=[];this.handlers={};this.hidden=false;this._text='';}
 append(...els){this.children.push(...els);}replaceChildren(...els){this.children=els;this._text='';}addEventListener(type,fn){this.handlers[type]=fn;}set textContent(v){this._text=String(v);this.children=[];}get textContent(){return this._text+this.children.map(c=>c.textContent).join(' ');}
}
const elements=new Map();const $=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
$('statsSource').value='google';$('statsDays').value='30';$('statsPropertyId').value='123456789';$('statsClientId').value='123-test.apps.googleusercontent.com';
const requests=[],storageWrites=[],authRequests=[];let fail=false;
const context={Intl,Date,URL,console,localStorage:{getItem:()=>null,setItem:(...a)=>storageWrites.push(a)},document:{getElementById:$,createElement:()=>new Element(),head:new Element()},addEventListener(){},google:{accounts:{oauth2:{initTokenClient:config=>({requestAccessToken:()=>{authRequests.push(config);config.callback({access_token:'TEST_ONLY',expires_in:3600});}})}}},fetch:async(url,options)=>{
 const body=JSON.parse(options.body);requests.push({url,body,authorization:options.headers.Authorization});if(fail)return {ok:false,status:401,json:async()=>({error:{message:'invalid token'}})};
 const dimensions=body.dimensions.map(x=>x.name).join(',');const row=(dims,count)=>({dimensionValues:dims.map(value=>({value})),metricValues:[{value:String(count)}]});
 const rows=dimensions==='eventName'?[row(['nic_page_view'],7),row(['nic_calculator_use'],4),row(['nic_calculate'],2),row(['nic_pdf_download'],1),row(['nic_pdf_share'],1)]:dimensions==='pagePath,eventName'?[row(['/vermietung/','nic_calculator_use'],3),row(['/vermietung/','nic_calculate'],2),row(['/eigennutzung/','nic_pdf_download'],1)]:dimensions==='country'?[row(['Germany'],7)]:dimensions==='deviceCategory'?[row(['mobile'],7)]:dimensions==='operatingSystem'?[row(['iOS'],7)]:[row(['google / organic'],7)];return {ok:true,json:async()=>({rows,rowCount:rows.length})};
 }};
context.window=context;vm.createContext(context);vm.runInContext(fs.readFileSync(site+'/statistics-core.js','utf8'),context);vm.runInContext(fs.readFileSync(site+'/statistics-admin.js','utf8'),context);
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 await tick();assert.equal(requests.length,0);assert($('statsNotice').textContent.includes('noch nicht'));
 await $('statsConnect').handlers.click();await tick();await tick();assert.equal(requests.length,6);assert.equal(authRequests[0].scope,'https://www.googleapis.com/auth/analytics.readonly');assert(requests.every(r=>r.authorization==='Bearer TEST_ONLY'&&r.url.includes('/properties/123456789:runReport')));assert(requests.every(r=>r.body.dateRanges[0].startDate==='29daysAgo'));
 assert.equal($('statsMetrics').children[0].children[1].textContent,'7');assert.equal($('statsMetrics').children[3].children[1].textContent,'1');assert($('statsCalculatorRows').textContent.includes('Vermietung'));assert($('statsCountries').textContent.includes('Germany'));assert($('statsSources').textContent.includes('google / organic'));assert.equal(storageWrites.length,0);
 fail=true;await $('statsRefresh').handlers.click();await tick();assert($('statsNotice').textContent.includes('abgelaufen'));const before=requests.length;await $('statsRefresh').handlers.click();await tick();assert.equal(requests.length,before);assert($('statsNotice').textContent.includes('noch nicht'));
 console.log('Statistics reporting passed: read-only OAuth scope, six filtered GA4 reports, calculator/country/source mapping, no token persistence and expired-token handling.');
})().catch(e=>{console.error(e);process.exit(1);});
