/* Development regression: financing sliders reuse the original inputs and preserve manual equity. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'}),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname!=='localhost'){
     if(route.request().resourceType()==='script')return route.fulfill({status:200,contentType:'application/javascript',body:''});
     return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
    }
    let name=u.pathname;if(name.endsWith('/'))name+='index.html';
    const file=path.join(process.cwd(),'_site',name);
    if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
    return route.fulfill({status:200,body:fs.readFileSync(file),
     contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'text/plain'});
   });
   for(const [route,input,equity] of [['vermietung','rentLtv','rentEquity'],['eigennutzung','ltv','ownEquityInput']]){
    await page.goto('http://localhost/'+route+'/',{waitUntil:'domcontentloaded'});
    const range=page.locator('#'+input).locator('xpath=following-sibling::*[contains(@class,"nic-finance-percent-control")]//input[@type="range"]');
    // Parent may be an input-wrap; locate the shared field rather than assuming sibling order.
    const slider=page.locator('#'+input).locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," field ")][1]').locator('.nic-finance-percent-range');
    await slider.waitFor({state:'visible',timeout:20000});
    assert.equal(await page.locator('#'+input).count(),1,'Original percent field is retained once');
    assert(Number(await slider.getAttribute('max'))>=120,'Slider supports 120 percent');
    assert.equal(await slider.evaluate(el=>Math.round(el.getBoundingClientRect().width)),
                 await slider.evaluate(el=>Math.round(el.closest('.field').getBoundingClientRect().width)),
                 'Slider spans its field');
    await page.locator('#'+equity).fill('0');
    await page.evaluate(({id})=>{
     const el=document.querySelector('#'+id+'~.nic-finance-percent-control input');
     const slider=el||document.getElementById(id).closest('.field').querySelector('input[type="range"]');
     slider.value='0';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    await page.waitForTimeout(100);
    const required=await page.locator('#'+equity).inputValue();
    const parse=v=>Number(v.replace(/\./g,'').replace(',','.'))||0;
    assert(parse(required)>=0,'Zero percent financing writes nonnegative equity');
    await page.locator('#'+equity).fill('17500');
    await page.evaluate(({id})=>{
     const slider=document.getElementById(id).closest('.field').querySelector('input[type="range"]');
     slider.value='80';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    assert.equal(parse(await page.locator('#'+equity).inputValue()),17500,'Manual equity remains authoritative');
    await page.evaluate(({id})=>{
     const slider=document.getElementById(id).closest('.field').querySelector('input[type="range"]');
     slider.value='120';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    assert.equal(Number(await page.locator('#'+input).inputValue()),120,'120 percent reaches the original model field');
   }
   assert.deepEqual(errors,[],'No uncaught browser errors');
   await page.close();
  }
  console.log('Financing sliders: rental and owner, 0–120 percent, manual equity, desktop/mobile passed');
 }finally{await browser.close();}
})().catch(err=>{console.error(err);process.exitCode=1;});
