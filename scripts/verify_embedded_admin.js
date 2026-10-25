const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
class El {
 constructor(tag='div'){this.tag=tag;this.attrs={};this.children=[];this.listeners={};this.style={};this.classList={add(){},remove(){}};this.contentWindow={postMessage(){}};this.innerHTML='Budget prüfen';this.textContent='Budget description';}
 addEventListener(k,f){(this.listeners[k]??=[]).push(f)}
 append(...x){this.children.push(...x)} after(x){this.sibling=x}setAttribute(k,v){this.attrs[k]=v}getAttribute(k){return this.attrs[k]}focus(){this.focused=true}
 click(){for(const f of this.listeners.click||[])f({preventDefault(){}})}
}
(async()=>{
const root=new El(),hero=new El(),account=new El(),title=new El(),text=new El();
const ids={nicAccountLink:account,heroTitle:title,heroText:text};const events={};
const current={websiteLogo:'saved-logo'},S={ROOT:new URL('https://example.test/'),KEY:'settings',pages:[['budget','Budget','budget/']],current,init:async()=>current,apply(){},applyLogo(value){this.lastLogo=value},portals:[]};
const location={origin:'https://example.test',pathname:'/budget/',search:'',hash:'#admin-social'};
const document={documentElement:{dataset:{nicPage:'budget',nicRelease:'8.339'}},body:root,title:'Budget',getElementById:id=>ids[id],querySelector:s=>s==='.app > .hero'?hero:null,querySelectorAll:()=>[],createElement:tag=>new El(tag)};
const context={URL,console,document,location,history:{pushState(_,__,url){location.hash=new URL(url,location.origin).hash},replaceState(_,__,url){location.hash=new URL(url,location.origin).hash}},NICSettings:S,addEventListener(k,f){(events[k]??=[]).push(f)}};context.window=context;
vm.createContext(context);vm.runInContext(fs.readFileSync('assets/site-integration.js','utf8'),context);await new Promise(setImmediate);
assert.equal(title.textContent,'Admin-Bereich');const panel=hero.sibling;assert(panel);const frame=panel.children[1];assert.equal(frame.src,'https://example.test/admin.html?embedded=1&release=8.339#social');assert.equal(document.title,'Admin-Bereich | Neustart ImmoCheck');
for(const f of events.message)f({origin:location.origin,source:frame.contentWindow,data:{type:'nic-logo-preview',value:'preview-logo'}});assert.equal(S.lastLogo,'preview-logo');
for(const f of events.message)f({origin:'https://evil.test',source:frame.contentWindow,data:{type:'nic-logo-preview',value:'evil-logo'}});assert.equal(S.lastLogo,'preview-logo');
for(const f of events.message)f({origin:location.origin,source:frame.contentWindow,data:{type:'nic-admin-height',height:2000}});assert.equal(frame.style.height,'2000px');
panel.children[0].click();assert(panel.hidden);assert.equal(title.innerHTML,'Budget prüfen');assert.equal(S.lastLogo,'saved-logo');assert(account.focused);
account.click();assert.equal(panel.hidden,false);assert.equal(hero.sibling,panel);assert.equal(location.hash,'#admin');
location.hash='';for(const f of events.popstate)f();assert(panel.hidden);
console.log('Embedded admin checks passed: deep link, shared heading, same frame on reopen, back navigation, saved logo restore, live preview and message origin protection.');
})().catch(e=>{console.error(e);process.exit(1)});
