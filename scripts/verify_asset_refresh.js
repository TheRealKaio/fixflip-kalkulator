'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const site=process.argv[2]||'_site',manifest=JSON.parse(fs.readFileSync(path.join(site,'.asset-manifest.json'),'utf8'));
for(const [original,hashed] of Object.entries(manifest)){
 const bytes=fs.readFileSync(path.join(site,original));assert.deepEqual(fs.readFileSync(path.join(site,hashed)),bytes);
 assert(hashed.includes(crypto.createHash('sha256').update(bytes).digest('hex').slice(0,16)));
}
function pages(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?pages(path.join(dir,e.name)):e.name.endsWith('.html')?[path.join(dir,e.name)]:[]);}
let checked=0;for(const file of pages(site)){const html=fs.readFileSync(file,'utf8');for(const [,attr,quote,value] of html.matchAll(/\b(src|href)=(['"])([^'"]+)\2/g)){
 if(/^https?:\/\//.test(value))continue;
 const base=value.split(/[?#]/)[0].split('/').pop();
 assert(!Object.hasOwn(manifest,base),'Unversioned asset reference: '+file+' '+value);
 if(/\.[a-f0-9]{16}\.(js|css)$/.test(base)){assert(fs.existsSync(path.join(site,base)));checked++;}
}}
const handlers={},calls=[];const context={URL,self:{location:{origin:'https://example.org'},addEventListener:(name,fn)=>handlers[name]=fn},fetch:async(request,options)=>{calls.push({request,options});return {ok:true};},caches:{match:async()=>({offline:true})}};vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(site,'service-worker.js'),'utf8'),context);
async function request(url,destination,mode='cors',method='GET'){let promise;handlers.fetch({request:{url,destination,mode,method},respondWith:p=>promise=p});return await promise;}
(async()=>{
 await request('https://example.org/','document','navigate');assert.equal(calls.at(-1).options.cache,'no-store');
 for(const destination of ['script','style','iframe','frame']){await request('https://example.org/asset',destination);assert.equal(calls.at(-1).options.cache,'no-store');}
 await request('https://www.googletagmanager.com/gtag/js','script');assert.equal(calls.at(-1).options,undefined);
 await request('https://example.org/api','', 'cors','POST');assert.equal(calls.at(-1).options,undefined);
 context.fetch=async()=>{throw Error('offline');};assert.equal((await request('https://example.org/','document','navigate')).offline,true);
 assert(checked>=30);console.log('Asset refresh passed: '+checked+' fingerprinted script/style links, correct content hashes, HTTP-cache bypass and offline fallback.');
})().catch(e=>{console.error(e);process.exit(1);});
