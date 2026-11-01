const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.NIC_CHROMIUM_BIN?{executablePath:process.env.NIC_CHROMIUM_BIN,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-zygote','--single-process']}: {})});
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});
  for(const slug of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']){
   const errors=[];const listener=e=>errors.push(e.message);page.on('pageerror',listener);
   const response=await page.goto('http://127.0.0.1:8766/'+slug+'/',{waitUntil:'domcontentloaded'});
   assert.equal(response.status(),200);await page.waitForTimeout(800);
   assert.equal(await page.locator('.nic-step-nav').count(),0,'Redesign step navigation must be absent');
   assert(await page.locator('.brand-logo').evaluate(el=>el.tagName==='IMG'&&el.complete&&el.naturalWidth===920));
   assert(await page.locator('.hero').evaluate(el=>getComputedStyle(el).backgroundImage.includes('immocheck-hero.jpg')));
   if(slug==='finanzierungsrechner'){
    await page.evaluate(()=>{for(const [id,value] of Object.entries({loan:300000,interest:4,repay:2,extra:5,years:10})){const el=document.getElementById(id);el.value=value;el.dispatchEvent(new Event('input',{bubbles:true}));}});
    let expected=300000;const r=.04/12,f=Math.pow(1+r,12);
    for(let y=0;y<10;y++)expected=Math.max(0,expected*f-1500*(f-1)/r-15000);
    const actual=Number((await page.locator('#balance').innerText()).replace(/[^0-9,-]/g,'').replace(',','.'));
    assert(Math.abs(actual-expected)<1,'Remaining debt differs');
    assert(await page.locator('#repayChart path').count()>0);
   }
   assert.deepEqual(errors,[]);page.removeListener('pageerror',listener);
   console.log('PASS original',width,slug);
  }
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
