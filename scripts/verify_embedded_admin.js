const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
class El {
 constructor(tag='div'){this.tag=tag;this.attrs={};this.children=[];this.listeners={};this.style={};this.dataset={};this.classList={add(){},remove(){}};this.contentWindow={postMessage(){}};this.innerHTML='Budget prüfen';this.textContent='Budget description';}
 addEventListener(k,f){(this.listeners[k]??=[]).push(f)}
 append(...x){this.children.push(...x)}
 after(x){this.sibling=x}setAttribute(k,v){this.attrs[k]=v}getAttribute(k){return this.attrs[k]}focus(){this.focused=true}
 click(){for(const f of this.listeners.click||[])f({preventDefault(){}})}
}
(async()=>{
const root=new El(),hero=new El(),account=new El(),title=new El(),text=new El();
const ids={nicAccountLink:account,heroTitle:title,heroText:text};const events={};
const current={websiteLogo:'saved-logo'},S={ROOT:new URL('https://example.test/'),KEY:'settings',pages:[['budget','Budget','budget/']],current,init:async()=>current,apply(){},syncCalculatorMenu(active){this.lastActiveTile=active},applyLogo(value){this.lastLogo=value},portals:[]};
const location={origin:'https://example.test',pathname:'/budget/',search:'',hash:'#admin-social'};
const document={documentElement:{dataset:{nicPage:'budget',nicRelease:'8.339'},classList:{add(){},remove(){}}},body:root,title:'Budget',getElementById:id=>ids[id],querySelector:s=>s==='.app > .hero'?hero:null,querySelectorAll:()=>[],createElement:tag=>new El(tag)};
const context={URL,console,fetch:async()=>{throw new Error('Native view fixture unavailable');},document,location,history:{pushState(_,__,url){location.hash=new URL(url,location.origin).hash},replaceState(_,__,url){location.hash=new URL(url,location.origin).hash}},NICSettings:S,addEventListener(k,f){(events[k]??=[]).push(f)}};context.window=context;
vm.createContext(context);vm.runInContext(fs.readFileSync('assets/site-integration.js','utf8'),context);await new Promise(setImmediate);
assert.equal(S.lastActiveTile,'budget');assert.equal(title.textContent,'Admin-Bereich');const panel=hero.sibling;assert(panel);assert.equal(document.title,'Admin-Bereich | Neustart ImmoCheck');
assert.equal(panel.children.some(el=>el.tag==='iframe'),false,'Admin must never create an iframe');
assert(panel.children.some(el=>el.id==='nicAdminContent'),'Native admin container is created');
panel.children[0].children[0].click();assert(panel.hidden);assert.equal(title.innerHTML,'Budget prüfen');assert.equal(S.lastLogo,'saved-logo');assert(account.focused);
account.click();assert.equal(panel.hidden,false);assert.equal(hero.sibling,panel);assert.equal(location.hash,'#admin');
context.NICAccess={enabled:true,user:{role:'admin'}};account.click();assert.equal(location.hash,'#admin');assert.equal(title.textContent,'Admin-Bereich');assert.equal(panel.hidden,false);
location.hash='';for(const f of events.popstate)f();assert(panel.hidden);
const userHero=new El(),userTitle=new El(),userText=new El(),userAccount=new El();
const userLocation={...location,hash:'#account'};
const userDoc={...document,body:new El(),getElementById:id=>({nicAccountLink:userAccount,heroTitle:userTitle,heroText:userText})[id],querySelector:s=>s==='.app > .hero'?userHero:null};
const userContext={...context,document:userDoc,location:userLocation,addEventListener(){}};userContext.window=userContext;
vm.createContext(userContext);vm.runInContext(fs.readFileSync('assets/site-integration.js','utf8'),userContext);await new Promise(setImmediate);
assert.equal(userTitle.textContent,'Deine Nutzerdaten');assert(userText.textContent.includes('unwiderruflich'));assert(userHero.sibling.children.some(el=>el.id==='nicAccountContent'));assert.equal(userDoc.title,'Deine Nutzerdaten | Neustart ImmoCheck');
console.log('Native admin shell checks passed: shared document, role-specific destination, heading, reusable panel and return navigation.');
})().catch(e=>{console.error(e);process.exit(1)});