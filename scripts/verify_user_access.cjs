'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const site=process.argv[2]||'_site';
const config=JSON.parse(fs.readFileSync('assets/backend-config.json','utf8'));
assert.equal(config.enabled,false,'Backend must remain opt-in until STRATO setup');
assert.equal(new URL(config.apiUrl).protocol,'https:');
const source=fs.readFileSync('assets/user-access.js','utf8');
function environment(enabled,role='admin'){
 const calls=[],store=new Map();let revision=1;
 const settings=JSON.parse(fs.readFileSync('assets/site-settings.json','utf8'));
 function el(){return{setAttribute(){},append(){},addEventListener(){},textContent:'',className:''};}
 const document={currentScript:{src:'https://www.neustart-immocheck.de/user-access.js'},createElement:el,head:{append(){}},body:{classList:{contains:()=>true}},addEventListener(){},getElementById:()=>null};
 const ctx={URL,AbortSignal,console,document,Event:class{},setInterval(){},dispatchEvent(){},fetch:async(url,options={})=>{
  const u=new URL(url);if(u.pathname.endsWith('backend-config.json'))return{ok:true,json:async()=>({enabled,apiUrl:config.apiUrl})};
  calls.push({route:u.searchParams.get('r'),options});const r=u.searchParams.get('r');
  if(r==='me')return{ok:true,json:async()=>({user:{id:'u',first_name:'Test',last_name:'Person',email:'test@example.com',role},csrf:'test-csrf'})};
  if(r==='settings'&&options.method==='POST'){const body=JSON.parse(options.body);assert.equal(body.revision,revision);assert.equal(options.headers['X-NIC-CSRF'],'test-csrf');revision++;return{ok:true,json:async()=>({settings:body.settings,revision})};}
  if(r==='settings')return{ok:true,json:async()=>({settings,revision})};
  if(r==='authorize')return{ok:true,json:async()=>({ok:true})};
  throw Error('Unexpected route '+r);
 }};ctx.window=ctx;vm.createContext(ctx);vm.runInContext(source,ctx);return{A:ctx.NICAccess,calls,ctx,settings};
}
(async()=>{
 const off=environment(false);assert.equal(await off.A.init(),false);assert.equal(await off.A.authorize('pdfDownload'),true);assert.equal(off.calls.length,0);
 const normal=environment(true,'user');assert.equal(await normal.A.requireAdmin(),false);assert.equal(normal.calls.filter(x=>x.route==='settings').length,0);
 const admin=environment(true);await admin.A.init();assert.equal(await admin.A.requireAdmin(),true);await admin.A.loadSettings();const next={...admin.settings,access:{calculators:true,pdfDownload:false,pdfShare:true}};assert.equal((await admin.A.saveSettings(next)).access.pdfDownload,false);await admin.A.authorize('pdfShare');
 assert(admin.calls.every(x=>x.options.credentials==='include'));assert(admin.calls.every(x=>x.options.cache==='no-store'));
 // Cloud settings supersede old local drafts; public defaults still work offline mode.
 const settingsSource=fs.readFileSync('assets/site-settings.js','utf8'),local=new Map();
 admin.ctx.document.currentScript.src='https://www.neustart-immocheck.de/site-settings.js';admin.ctx.localStorage={getItem:k=>local.get(k)||null,setItem:(k,v)=>local.set(k,v),removeItem:k=>local.delete(k)};
 const originalFetch=admin.ctx.fetch;admin.ctx.fetch=async(u,o)=>String(u).endsWith('site-settings.json')?{ok:true,json:async()=>admin.settings}:originalFetch(u,o);
 vm.runInContext(settingsSource,admin.ctx);const S=admin.ctx.NICSettings;
 const stale={...admin.settings,access:{calculators:false,pdfDownload:false,pdfShare:false}};S.save(stale);const loaded=await S.init();assert.equal(loaded.access.calculators,true,'local draft must not override server policy');
 const html=fs.readFileSync(site+'/finanzierungsrechner/index.html','utf8');assert(html.includes('user-access.js'));assert(html.indexOf('user-access.js')<html.indexOf('site-settings.js'));
 const root=fs.readFileSync(site+'/index.html','utf8');for(const action of ['pdfShare','pdfDownload'])assert(root.includes("NICAccess.authorize('"+action+"')"));
 const finance=fs.readFileSync('assets/pdf-reports.js','utf8');assert(finance.includes("authorize(download?'pdfDownload':'pdfShare')"));assert(finance.includes("authorize('pdfDownload')"));
 const api=fs.readFileSync('server/webspace/immocheck-private/app.php','utf8');assert(api.includes("$admin=nic_admin($db,$c)"));assert(api.includes('FOR UPDATE'));assert(api.includes('revision=?'));assert(api.includes("'httponly'=>true"));assert(!fs.existsSync('server/webspace/immocheck-private/config.php'));
 console.log('User access passed: opt-in mode, admin role, CSRF, credentialed requests, global save revision, local draft isolation, all report gates, no shipped server secrets.');
})().catch(error=>{console.error(error);process.exit(1);});
