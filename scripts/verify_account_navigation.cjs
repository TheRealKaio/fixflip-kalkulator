'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('assets/user-access.js','utf8');
const elements=[];let destination=null,fail=false;
function element(tag,text,attrs={}){const el={tag,text,attrs,children:[],events:{},append(...items){this.children.push(...items)},addEventListener(name,fn){this.events[name]=fn},showModal(){this.open=true},close(){this.open=false},remove(){this.removed=true}};elements.push(el);return el;}
const ctx={URL,element,ROOT:new URL('https://www.neustart-immocheck.de/'),user:{role:'admin',first_name:'Test',last_name:'Admin',email:'admin@example.test'},csrf:'token',init:async()=>true,api:async()=>{if(fail)throw Error('logout failed')},Event:class{},document:{body:{append(){}}},window:{dispatchEvent(){},top:{location:{replace(url){destination=url}}}}};
vm.createContext(ctx);
vm.runInContext(source.slice(source.indexOf('async function logout()'),source.indexOf('function mountUsers()')),ctx);
(async()=>{
 await ctx.profile();const modal=elements.find(x=>x.tag==='dialog'),link=elements.find(x=>x.tag==='a');assert(modal.open);link.events.click();assert.equal(modal.open,false);assert.equal(modal.removed,true,'account modal must stop blocking admin tabs');
 await ctx.logout();assert.equal(destination,'https://www.neustart-immocheck.de/?logged-out=1');assert.equal(ctx.user,null);
 destination=null;fail=true;await assert.rejects(ctx.logout());assert.equal(destination,null,'failed logout must not show success');
 const profileSource=fs.readFileSync('assets/user-data.js','utf8');
 const begin=profileSource.indexOf("yes.addEventListener('click',async()=>");
 const callback=profileSource.slice(begin+"yes.addEventListener('click',".length,profileSource.indexOf(');actions.append',begin));
 const deletion={A:{deleteOwn:async()=>({ok:true})},yes:{},no:{},choice:{checked:true},notice:{},URL,document:{baseURI:'https://www.neustart-immocheck.de/user-data.html?embedded=1'},window:{top:{location:{replace(url){destination=url}}}}};
 vm.createContext(deletion);await vm.runInContext('('+callback+')()',deletion);
 assert.equal(destination,'https://www.neustart-immocheck.de/?account-deleted=1','deletion must leave iframe and restore top-level homepage');
 assert.equal(deletion.notice.textContent,undefined,'successful deletion must not report an error');
 console.log('Account navigation passed: modal released before admin navigation, top-level calculator return, success marker only after logout.');
})().catch(error=>{console.error(error);process.exitCode=1});
