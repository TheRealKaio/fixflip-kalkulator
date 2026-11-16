// Numbering must survive direct routes, shared navigation and recalculation.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const routes={budget:'budget',own:'eigennutzung',rent:'vermietung',flip:'fix-flip',finance:'finanzierungsrechner'};
const expected={budget:['3. Dein monatlich verfügbares Budget','4. Wieviel Haus kann ich mir leisten?','5. Monatliche Tilgung- und Restschuld'],own:['4. Ergebnis Eigennutzung'],rent:['4. Ergebnis Vermietung'],flip:['4. Ergebnis Fix und Flip'],finance:['1. Finanzierung einstellen','2. Finanzierungsergebnis','3. Anschlussfinanzierung']};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'}),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
    if(u.hostname!=='localhost')return route.fulfill(route.request().resourceType()==='script'?{contentType:'application/javascript',body:''}:{json:{user:null,settings:require('../assets/site-settings.json'),csrf:'headings-test',ok:true}});
    let name=u.pathname;if(name.endsWith('/'))name+='index.html';
    const file=path.join('_site',name);
    if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
    return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.svg':'image/svg+xml','.jpg':'image/jpeg'})[path.extname(file)]||'application/octet-stream'});
   });
   async function check(key,entry){
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    const snapshot=await page.locator('main').evaluate(root=>({headings:[...root.querySelectorAll('h1,h2,h3,h4')].filter(el=>el.getBoundingClientRect().height).map(el=>el.textContent.trim()),decisions:[...root.querySelectorAll('[class*="decision"]')].map(el=>({tag:el.tagName,id:el.id,class:el.className,text:el.textContent.trim().slice(0,250),display:getComputedStyle(el).display})),scripts:[...document.scripts].filter(el=>/neutral|result-heading/.test(el.id)).map(el=>el.id)}));
    console.log('RESULT HEADINGS',width,key,entry,JSON.stringify(snapshot));
    for(const title of expected[key])assert(await page.getByRole('heading',{name:title,exact:true}).isVisible(),key+' '+entry+' must show '+title);
   }
   for(const [key,slug] of Object.entries(routes)){
    await page.goto('http://localhost/'+slug+'/',{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady);
    if(await page.locator('#nicConsentDialog[open]').count())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
    await check(key,'direct');
    const input=page.locator('main input:not([type="hidden"]):not([type="checkbox"]):not([type="radio"]):not([type="range"])').filter({visible:true}).first();
    if(await input.count()){await input.fill('123456');await input.dispatchEvent('change');await input.press('Tab');}
    await check(key,'recalculate');
   }
   await page.goto('http://localhost/',{waitUntil:'networkidle'});
   for(const key of Object.keys(routes)){await page.evaluate(key=>NICCalculatorNavigation.select(key,true),key);await check(key,'internal navigation');}
   assert.deepEqual(errors,[]);await page.close();
  }
  console.log('Numbered headings passed for all five calculators, direct/navigation/recalculation, mobile and desktop.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
