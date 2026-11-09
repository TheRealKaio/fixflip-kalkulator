'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('assets/user-access.js','utf8');
const elements=[];let destination=null,fail=false;
function element(tag,text,attrs={}){const el={tag,text,attrs,children:[],events:{},append(...items){this.children.push(...items)},addEventListener(name,fn){this.events[name]=fn},showModal(){this.open=true},close(){this.open=false},remove(){this.removed=true}};elements.push(el);return el;}
const ctx={URL,location:{hash:''},element,ROOT:new URL('https://www.neustart-immocheck.de/'),user:{role:'admin',first_name:'Test',last_name:'Admin',email:'admin@example.test'},csrf:'token',init:async()=>true,api:async()=>{if(fail)throw Error('logout failed')},Event:class{},document:{body:{append(){}}},window:{dispatchEvent(){},top:{location:{replace(url){destination=url}}}}};
vm.createContext(ctx);
vm.runInContext(source.slice(source.indexOf('async function logout()'),source.indexOf('function mountUsers()')),ctx);
(async()=>{
 await ctx.profile();assert.equal(ctx.location.hash,'#admin','admin login must enter the integrated admin portal');assert.equal(elements.length,0,'portal login must not stop at a profile modal');ctx.user=null;ctx.location.hash='#anmelden';ctx.login=async()=>{ctx.user={role:'user'};return true;};await ctx.profile();assert.equal(ctx.location.hash,'#account','normal-user login must enter the integrated account view without a standalone-page redirect');ctx.user={role:'admin'};
 await ctx.logout();assert.equal(destination,'https://www.neustart-immocheck.de/?logged-out=1');assert.equal(ctx.user,null);
 destination=null;fail=true;await assert.rejects(ctx.logout());assert.equal(destination,null,'failed logout must not show success');
 // Opening the portal must use the account established by the page's initial /me call,
// without a second request that can incorrectly clear a valid signed-in state.
const accessSource=fs.readFileSync('assets/user-access.js','utf8');
const listenerStart=accessSource.indexOf("// The page's initial /me response already establishes the active account.");
const listenerEnd=accessSource.indexOf("},true);",listenerStart)+7;
assert(listenerStart>=0&&listenerEnd>listenerStart,'portal click handler must be present');
let clickHandler,loginCalls=0;
const navigation={document:{addEventListener(_name,handler){clickHandler=handler}},config:{enabled:true},location:{hash:''},profile:async()=>{navigation.location.hash=navigation.user.role==='admin'?'#admin':'#account';},user:{role:'admin'},alert(message){throw Error(message);}};
vm.createContext(navigation);vm.runInContext(accessSource.slice(listenerStart,listenerEnd),navigation);
let prevented=false,stopped=false;
clickHandler({target:{closest:()=>({})},button:0,ctrlKey:false,metaKey:false,shiftKey:false,altKey:false,preventDefault(){prevented=true;},stopImmediatePropagation(){stopped=true;}});
await new Promise(setImmediate);
assert.equal(prevented,true,'portal click must be handled by the access flow');
assert.equal(stopped,true,'the access flow must prevent a second navigation handler');
assert.equal(navigation.location.hash,'#admin','an already authenticated administrator must reach the integrated admin portal');
assert.equal(loginCalls,0,'portal navigation must not trigger another login request');

const profileSource=fs.readFileSync('assets/user-data.js','utf8');
 const begin=profileSource.indexOf("yes.addEventListener('click',async()=>");
 const callback=profileSource.slice(begin+"yes.addEventListener('click',".length,profileSource.indexOf(');actions.append',begin));
 const deletion={A:{deleteOwn:async()=>({ok:true})},yes:{},no:{},choice:{checked:true},notice:{},URL,document:{baseURI:'https://www.neustart-immocheck.de/user-data.html?embedded=1'},window:{top:{location:{replace(url){destination=url}}}}};
 vm.createContext(deletion);await vm.runInContext('('+callback+')()',deletion);
 assert.equal(destination,'https://www.neustart-immocheck.de/?account-deleted=1','deletion must leave iframe and restore top-level homepage');
 assert.equal(deletion.notice.textContent,undefined,'successful deletion must not report an error');
 console.log('Account navigation passed: admin and standard logins enter the integrated portal; logout and account deletion return safely.');
})().catch(error=>{console.error(error);process.exitCode=1});
