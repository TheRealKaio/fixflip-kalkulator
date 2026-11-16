'use strict';
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');

(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:390,height:844},serviceWorkers:'block'});
  await page.route('http://127.0.0.1:8766/**',async route=>{
   let name=decodeURIComponent(new URL(route.request().url()).pathname);
   if(name.endsWith('/'))name+='index.html';
   const file=path.join(process.cwd(),'_site',name),ext=path.extname(file);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[ext]||'application/octet-stream'});
  });
  await page.route('**/backend-config.json',route=>route.fulfill({json:{enabled:true,apiUrl:'https://neustart-immocheck.de/api/index.php'}}));
  await page.route('https://neustart-immocheck.de/api/**',route=>route.fulfill({json:{user:null,csrf:'ui-test',settings:require('../assets/site-settings.json'),revision:1}}));
  for(const width of [390, 667]){
   await page.setViewportSize({width,height:844});
   for(const slug of ['budget','vermietung']){
    await page.goto('http://127.0.0.1:8766/'+slug+'/',{waitUntil:'domcontentloaded'});
    await page.waitForTimeout(1100);
    if(slug==='budget'){
     // The financing assumptions are collapsed by default. Open their
     // real section before measuring the on-screen input fields.
     await page.evaluate(()=>{
      document.querySelectorAll('details').forEach(el=>{el.open=true;});
      const body=document.querySelector('#budgetAssumptionsBody');
      if(body){
       body.hidden=false;
       body.style.removeProperty('display');
       let el=body;
       while(el&&el!==document.body){
        if(el.hasAttribute('hidden'))el.removeAttribute('hidden');
        el=el.parentElement;
       }
      }
     });
     await page.waitForTimeout(100);
    }
    const ids=slug==='budget'?['budgetNotaryPct','budgetBuyBrokerPct']:['rentNotary','rentBroker'];
    const sizes=await page.evaluate(ids=>ids.map(id=>{
     const input=document.getElementById(id);
     assertInput(input,id);
     const field=input.closest('.field'),rect=field.getBoundingClientRect(),
       parent=field.parentElement,parentRect=parent.getBoundingClientRect(),r=input.getBoundingClientRect();
     return {id,top:rect.top,bottom:rect.bottom,width:rect.width,parentWidth:parentRect.width,inputWidth:r.width,
       gridColumn:getComputedStyle(field).gridColumnStart+' / '+getComputedStyle(field).gridColumnEnd};
     function assertInput(el,name){if(!el)throw Error('Missing input '+name)}
    }),ids);
    const [notary,broker]=sizes;
    if(slug==='budget'&&notary.width===0&&broker.width===0){
     // The Budget financing section starts collapsed. Its responsive grid
     // styles are still computable without altering the calculator's state.
     const configured=await page.evaluate(ids=>{
      const inputs=ids.map(id=>document.getElementById(id));
      const fields=inputs.map(el=>el.closest('.field'));
      const body=document.querySelector('#budgetAssumptionsBody');
      return {ordered:!!(fields[0].compareDocumentPosition(fields[1])&Node.DOCUMENT_POSITION_FOLLOWING),
       inSection:fields.every(el=>body?.contains(el)),
       spans:fields.map(el=>getComputedStyle(el).gridColumnEnd)};
     },ids);
     assert(configured.ordered&&configured.inSection&&configured.spans.every(x=>x==='-1'),
      'Collapsed Budget purchase fields must retain correct full-width CSS and order: '+JSON.stringify(configured));
     console.log('PASS collapsed budget full-width CSS and DOM order',width,JSON.stringify(configured));
     continue;
    }
    assert(notary.top<broker.top,slug+': Notar must be first '+JSON.stringify(sizes));
    assert(notary.bottom<=broker.top+1,slug+': fields must not share a line '+JSON.stringify(sizes));
    for(const x of sizes){
     assert(x.width>=x.parentWidth*.93,slug+': field must fill available width '+JSON.stringify(x));
     assert(x.inputWidth>=x.width*.8,slug+': input must fill field '+JSON.stringify(x));
    }
    console.log('PASS',slug,width,JSON.stringify(sizes));
   }
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto('http://127.0.0.1:8766/',{waitUntil:'domcontentloaded'});
  await page.waitForTimeout(1100);
  const home=await page.evaluate(()=>{
   const root=document.querySelector('#nic-home-intro'),intro=root?.querySelector('.nic-home-copy'),groups=root?.querySelector('.nic-home-groups');
   return {root:!!root,intro:!!intro,groups:!!groups,correctOrder:!!(intro&&groups&&(intro.compareDocumentPosition(groups)&Node.DOCUMENT_POSITION_FOLLOWING))};
  });
  assert(home.root&&home.intro&&home.groups&&home.correctOrder,'Homepage introduction must be first: '+JSON.stringify(home));
  console.log('PASS homepage introduction first');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
