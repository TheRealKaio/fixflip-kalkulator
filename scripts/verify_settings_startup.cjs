'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const config=JSON.parse(fs.readFileSync('assets/site-settings.json','utf8'));
const source=fs.readFileSync('assets/site-settings.js','utf8');
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
function setup(){
 const values=new Map();let requests=0,cloud=deferred();
 const context={URL,console,document:{currentScript:{src:'https://example.test/site-settings.js'}},
 localStorage:{getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)},
 fetch:async()=>{requests++;return {ok:true,json:async()=>config};},
 NICAccess:{loadSettings:()=>cloud.promise}};
 context.window=context;vm.createContext(context);vm.runInContext(source,context);
 return {S:context.NICSettings,context,get requests(){return requests;},get cloud(){return cloud;},retry(){cloud=deferred();}};
}
(async()=>{
 const a=setup(),S=a.S;
 assert.equal(S.ready,false);
 const first=S.init(),second=S.init();assert.equal(first,second,'concurrent startup calls share one request');
 await Promise.resolve();assert.equal(S.ready,false,'bundled defaults cannot authorize first display');
 a.cloud.resolve({...config,contentSections:{'budget.deine-mogliche-finanzierung':{visible:false,guestAllowed:false}}});
 await first;assert.equal(a.requests,1);assert.equal(S.ready,true);assert.equal(S.current.contentSections['budget.deine-mogliche-finanzierung'].visible,false);
 const b=setup();const failed=b.S.init();b.cloud.reject(Error('offline'));await assert.rejects(failed,/offline/);assert.equal(b.S.ready,false,'failed startup remains closed');
 b.retry();const retried=b.S.init();b.cloud.resolve(config);await retried;assert.equal(b.S.ready,true,'retry can complete initialization');
 // An older refresh must not overwrite an intervening settings edit.
 b.retry();const stale=b.S.init();const edited=b.S.save({...config,layout:{...config.layout,subtextSize:19}});
 b.cloud.resolve({...config,layout:{...config.layout,subtextSize:11}});
 await stale;assert.equal(b.S.current.layout.subtextSize,19);assert.equal(b.S.current,edited);
 for(const [oldKey,newKey] of [
 ['budget.deine-mogliche-finanzierung','budget.wieviel-haus-kann-ich-mir-leisten'],
 ['budget.3-annahme-zur-moglichen-finanzierung','budget.3-finanzierung-und-nebenkosten'],
 ['budget.monatliche-belastung-und-restschuld','budget.monatliche-tilgung-und-restschuld']]){
  const migrated=S.normalize({...config,contentSections:{[newKey]:{visible:false,guestAllowed:false}}});
  assert.equal(migrated.contentSections[oldKey].visible,false);
  assert.equal(migrated.contentSections[oldKey].guestAllowed,false);
  const explicit=S.normalize({...config,contentSections:{[oldKey]:{visible:true,guestAllowed:true},[newKey]:{visible:false,guestAllowed:false}}});
  assert.equal(explicit.contentSections[oldKey].visible,true,'an explicit canonical admin edit wins');
 }
 console.log('Settings startup passed: shared requests, delayed rules, failed-load gate, retry, stale-refresh protection and heading aliases.');
})().catch(error=>{console.error(error);process.exit(1);});
