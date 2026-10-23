'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const site=process.argv[2]||'_site';
const store=new Map();let failStorage=false;
const context={URL,console,document:{currentScript:{src:'https://www.neustart-immocheck.de/site-settings.js'}},localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>{if(failStorage)throw new Error('quota');store.set(k,v);},removeItem:k=>store.delete(k)},fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync(site+'/site-settings.json','utf8'))})};
context.window=context;vm.createContext(context);vm.runInContext(fs.readFileSync(site+'/site-settings.js','utf8'),context);const S=context.window?.NICSettings;

(async()=>{
 const s=await S.init();assert.equal(S.portals.length,10);assert.equal(S.pages.length,6);assert.equal(S.companyFields.length,28);
 const raw=JSON.parse(JSON.stringify(s));raw.layout.background='red;display:none';raw.layout.h1=999;raw.layout.font='evil';raw.social.instagram='javascript:alert(1)';raw.social.facebook='https://www.facebook.com/example';raw.company.name='<img onerror=alert(1)>';raw.company.secret='ignored';raw.meta.rent.title='Mietwohnung prüfen';
 const safe=S.normalize(raw);assert.equal(safe.layout.background,'#F5F7FB');assert.equal(safe.layout.h1,30);assert.equal(safe.layout.font,'system');assert.equal(safe.social.instagram,'');assert.equal(safe.social.facebook,'https://www.facebook.com/example');assert.equal(safe.company.secret,undefined);assert.equal(S.pageMeta(safe,'rent').title,'Mietwohnung prüfen');assert(S.imprint(safe).some(x=>x.value==='<img onerror=alert(1)>'));
 assert.equal(S.validFavicon('data:image/svg+xml;base64,AAAA'),'');assert.equal(S.validFavicon('data:image/png;base64,AAAA'),'data:image/png;base64,AAAA');
 S.save(safe);assert(S.isLocal);assert.equal((await S.init()).meta.rent.title,'Mietwohnung prüfen');const exported=JSON.stringify(S.current);assert.equal(S.normalize(JSON.parse(exported)).meta.rent.title,'Mietwohnung prüfen');
 failStorage=true;assert.throws(()=>S.save(safe));failStorage=false;S.discard();assert(!S.isLocal);assert.notEqual((await S.init()).meta.rent.title,'Mietwohnung prüfen');
 for(const [key,label,path] of S.pages){const file=site+'/'+path+'index.html',html=fs.readFileSync(file,'utf8');assert(html.includes('data-nic-page="'+key+'"'));assert(html.includes(S.published.meta[key].title.replaceAll('&','&amp;')));assert(html.includes('rel="canonical"'));assert(html.includes('name="description"'));}
 const html=fs.readFileSync(site+'/index.html','utf8');assert.equal((html.match(/id="nicAccountLink"/g)||[]).length,1);assert(html.includes('href="admin.html"'));assert(fs.readFileSync(site+'/admin.html','utf8').includes('noindex,nofollow'));assert(fs.existsSync(site+'/icon.svg'));
 console.log('Site settings passed: fields, URL/CSS safety, local persistence, export/import roundtrip, quota error, reset and six static metadata pages.');
})().catch(e=>{console.error(e);process.exit(1);});
