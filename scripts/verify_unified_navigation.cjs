const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname!=='localhost')return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
   let name=u.pathname;if(name.endsWith('/'))name+='index.html';
   const file=path.join(process.cwd(),'_site',name);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'text/plain'});
  });
  await page.goto('http://localhost/budget/');
  await page.evaluate(()=>{document.querySelectorAll('dialog').forEach(d=>d.close());});
  await page.waitForFunction(()=>window.NICCalculatorNavigation&&window.NICSettings.current);
  const origin=await page.evaluate(()=>performance.timeOrigin);
  for(const key of ['finance','own','rent','flip','budget','finance']){
   await page.locator(`.deal-type-option[data-calculator="${key}"]`).click();
   await page.waitForFunction(k=>document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
   assert.equal(await page.evaluate(()=>performance.timeOrigin),origin,'calculator changes must keep same document');
   assert.equal(await page.locator('.nic-tile-active').count(),1);
   if(key==='finance')assert(await page.locator('#nicFinanceModule #loan').isVisible());
  }
  await page.goBack();await page.waitForFunction(()=>!document.body.classList.contains('nic-finance-active'));
  await page.goForward();await page.waitForFunction(()=>document.body.classList.contains('nic-finance-active'));
  await page.reload();await page.waitForSelector('#nicFinanceModule #loan');
  assert.equal(await page.locator('.nic-tile-active').getAttribute('data-calculator'),'finance');
  assert.deepEqual(errors,[]);
  console.log('Unified navigation passed',width,'same document, all modes, history, direct finance reload');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
