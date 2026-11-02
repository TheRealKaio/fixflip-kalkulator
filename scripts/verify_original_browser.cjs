const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.NIC_CHROMIUM_BIN?{executablePath:process.env.NIC_CHROMIUM_BIN,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-zygote','--single-process']}: {})});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:900},serviceWorkers:"block"});
 await page.route('http://127.0.0.1:8766/**',async route=>{
  const fs=require('node:fs'),path=require('node:path');let name=decodeURIComponent(new URL(route.request().url()).pathname);if(name.endsWith('/'))name+='index.html';
  const file=path.join(process.cwd(),'_site',name),ext=path.extname(file);
  if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
  await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'})[ext]||'application/octet-stream'});
 });
 await page.route('**/backend-config.json',route=>route.fulfill({json:{enabled:true,apiUrl:'https://neustart-immocheck.de/api/index.php'}}));
 await page.route('https://neustart-immocheck.de/api/**',route=>route.fulfill({json:{user:null,csrf:'ui-test',settings:require('../assets/site-settings.json'),revision:1}}));
 const geometry=new Map();
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});
  for(const slug of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']){
   const errors=[];const listener=e=>errors.push(e.message);page.on('pageerror',listener);
   const response=await page.goto('http://127.0.0.1:8766/'+slug+'/',{waitUntil:'domcontentloaded'});
   assert.equal(response.status(),200);await page.waitForTimeout(800);
   assert.equal(await page.locator('.nic-step-nav').count(),0,'Redesign step navigation must be absent');
   await page.waitForFunction(()=>document.querySelector('.brand-logo')?.complete&&document.querySelector('.brand-logo')?.naturalWidth>0);
   assert(await page.locator('.brand-logo').evaluate(el=>el.tagName==='IMG'&&el.complete&&el.naturalWidth>0));
   assert(await page.locator('.hero').evaluate(el=>getComputedStyle(el).backgroundImage.includes('immocheck-hero.jpg')));
   assert.equal(await page.locator('.nic-brand-bar').count(),1);
   assert.equal(await page.locator('.hero #nicAccountLink').count(),0);
   assert.equal(await page.locator('.nic-menu-icon').count(),5);
   assert.equal(await page.locator('.nic-tile-active').count(),1,'Exactly one active tile on every route');
   assert(await page.locator('.nic-tile-active').evaluate(el=>getComputedStyle(el).borderWidth==='2px'),'Active border is shared, including finance');
   assert(await page.locator('.deal-type-option').evaluateAll(els=>els.every(el=>Math.abs(el.getBoundingClientRect().height-els[0].getBoundingClientRect().height)<1)),'All five tile heights must be identical');
   assert(await page.locator('.nic-brand-bar').evaluate(bar=>[...bar.children].every(el=>{const r=el.getBoundingClientRect(),b=bar.getBoundingClientRect();return r.left>=b.left-1&&r.right<=b.right+1})), 'Brand bar content must stay inside its width');
   const shell=await page.evaluate(()=>{
    const box=e=>{const r=e.getBoundingClientRect();return [r.x,r.width,r.height].map(v=>Math.round(v));};
    return {header:box(document.querySelector('.hero')),menu:box(document.querySelector('.deal-type-row')),tiles:[...document.querySelectorAll('.deal-type-option')].map(box)};
   });
   if(!geometry.has(width))geometry.set(width,shell);else assert.deepEqual(shell,geometry.get(width),'Shared header and menu geometry must remain identical across routes');
   assert.equal(await page.locator('#nicAccountLink').innerText(),'Jetzt anmelden');
   if(slug!=='finanzierungsrechner')assert(!(await page.locator('.footer-note').innerText()).includes('Der Deal Check ist eine Kalkulationshilfe'));
   assert.equal(await page.locator('.footer-version').evaluate(el=>getComputedStyle(el).color),'rgb(255, 255, 255)');
   assert.equal(await page.locator('.hero').evaluate(el=>parseFloat(getComputedStyle(el).borderTopLeftRadius)),0,'Header top-left corner must be square');
   assert.equal(await page.locator('.hero').evaluate(el=>parseFloat(getComputedStyle(el).borderTopRightRadius)),0,'Header top-right corner must be square');
   assert.equal(await page.locator('.nic-brand-bar').evaluate(el=>parseFloat(getComputedStyle(el).borderTopLeftRadius)),0,'White header top-left corner must be square');
   assert.equal(await page.locator('.nic-brand-bar').evaluate(el=>parseFloat(getComputedStyle(el).borderTopRightRadius)),0,'White header top-right corner must be square');
   assert.equal(await page.locator('.footer-note').evaluate(el=>parseFloat(getComputedStyle(el).borderBottomLeftRadius)),0,'Footer bottom-left corner must be square');
   assert.equal(await page.locator('.footer-note').evaluate(el=>parseFloat(getComputedStyle(el).borderBottomRightRadius)),0,'Footer bottom-right corner must be square');
   const reject=page.getByRole('button',{name:'Ablehnen',exact:true});if(await reject.isVisible())await reject.click();
   const cookie=page.locator('#nicConsentSettings');if(await cookie.count())assert.equal(await cookie.evaluate(el=>getComputedStyle(el).color),'rgb(255, 255, 255)');
   await page.locator('#nicAccountLink').click();
   await page.locator('#nicLoginTitle').waitFor({state:'visible'});
   await page.getByRole('button',{name:'Abbrechen',exact:true}).click();
   for(const legal of ['impressum','agbs','datenschutz','haftungsausschluss']){
    await page.locator(`[data-legal-placeholder="${legal}"]`).click();
    await page.locator('#nicLegalPanel').waitFor({state:'visible'});
    assert((await page.locator('.nic-legal-card').innerText()).trim().length>0,'Legal content must exist on every route');
    await page.getByRole('button',{name:'← Zu den Kalkulatoren',exact:true}).click();
   }
   assert.equal(await page.locator('.nic-footer-cookie-pair #nicConsentSettings').count(),1,'Shared version/cookie layout must exist');
   if(slug==='finanzierungsrechner'){
    await page.evaluate(()=>{for(const [id,value] of Object.entries({loan:300000,interest:4,repay:2,extra:5,years:10})){const el=document.getElementById(id);el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));}});
    let expected=300000;const r=.04/12,f=Math.pow(1+r,12);
    for(let y=0;y<10;y++)expected=Math.max(0,expected*f-1500*(f-1)/r-15000);
    const actual=Number((await page.locator('#balance').innerText()).replace(/[^0-9,-]/g,'').replace(',','.'));
    assert(Math.abs(actual-expected)<1,'Remaining debt differs');
    assert(await page.locator('#repayChart path').count()>0);
   }
   await page.evaluate(()=>{const s=JSON.parse(JSON.stringify(NICSettings.current));s.layout.font='georgia';s.layout.bodySize=20;s.layout.h2=24;NICSettings.save(s);NICSettings.apply(s);});
   assert(await page.locator('.footer-note').evaluate(el=>getComputedStyle(el).fontSize==='20px'&&getComputedStyle(el).fontFamily.includes('Georgia')));
   assert(await page.locator('.deal-type-title').evaluate(el=>getComputedStyle(el).fontSize==='24px'));
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1?[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+1}).map(e=>({tag:e.tagName,id:e.id,c:e.className,w:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).slice(0,12):[]);
   assert.deepEqual(overflow,[],'No horizontal page overflow');
   assert.equal(await page.locator('.mini').first().evaluate(e=>getComputedStyle(e).fontSize),'12px');
   const sub=page.locator('.sub,.subtitle,.card>h2+p:not(.mini)').first();if(await sub.count())assert.equal(await sub.evaluate(e=>getComputedStyle(e).fontSize),await page.evaluate(()=>NICSettings.current.layout.bodySize+'px'));
   await page.screenshot({path:`tmp/${width}-${slug}.png`,fullPage:true});
   await page.evaluate(()=>{NICSettings.discard();});
   assert.deepEqual(errors,[]);page.removeListener('pageerror',listener);
   console.log('PASS original',width,slug);
  }
 }
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});
  await page.goto('http://127.0.0.1:8766/budget/',{waitUntil:'domcontentloaded'});
  for(const [slug,key] of [['fix-flip','flip'],['finanzierungsrechner','finance'],['eigennutzung','own'],['vermietung','rent'],['budget','budget']]){
   await page.locator(`.deal-type-option[data-href="/${slug}/"]`).click();
   await page.waitForURL('http://127.0.0.1:8766/'+slug+'/');
   await page.waitForFunction(k=>document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
   assert.equal(await page.locator('.nic-tile-active').count(),1);
   assert.equal(await page.locator('.nic-tile-active').evaluate(e=>getComputedStyle(e).borderWidth),'2px');
  }
  console.log('PASS real navigation transitions',width);
 }
 await page.route('**/backend-config.json',r=>r.fulfill({json:{enabled:false}}));
 await page.goto('http://127.0.0.1:8766/#admin-layout',{waitUntil:'domcontentloaded'});
 const admin=page.frameLocator('#nicAdminFrame');
 await admin.locator('#layout-subtextSize').waitFor({state:'visible'});
 assert.equal(await admin.locator('#layout-subtextSize').inputValue(),'14');
 assert.equal(await admin.locator('#layout-hintSize').inputValue(),'12');
 await admin.locator('#layout-subtextSize').fill('17');await admin.locator('#layout-hintSize').fill('11');
 await admin.locator('#saveSettings').click();
 assert.equal(await admin.locator('body').evaluate(()=>NICSettings.current.layout.subtextSize),17);
 assert.equal(await admin.locator('body').evaluate(()=>NICSettings.current.layout.hintSize),11);
 await page.reload({waitUntil:'domcontentloaded'});
 await admin.locator('#layout-subtextSize').waitFor({state:'visible'});
 assert.equal(await admin.locator('#layout-subtextSize').inputValue(),'17');
 assert.equal(await admin.locator('#layout-hintSize').inputValue(),'11');
 console.log('PASS admin: secondary typography fields, save and reload');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
