// Verify that the loan, equity and slider cover the same Fix & Flip costs.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'});
   const errors=[];
   page.on('pageerror',err=>errors.push(err.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname!=='localhost'){
     if(route.request().resourceType()==='script')return route.fulfill({status:200,contentType:'application/javascript',body:''});
     return route.fulfill({status:200,contentType:'application/json',body:'{}'});
    }
    let name=u.pathname;if(!name||name.endsWith('/'))name+='index.html';
    const full=path.join(process.cwd(),'_site',name);
    if(!fs.existsSync(full))return route.fulfill({status:404,body:''});
    return route.fulfill({status:200,body:fs.readFileSync(full),
      contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/jpeg'})[path.extname(full)]||'text/plain'});
   });
   await page.goto('http://localhost/fix-flip/',{waitUntil:'domcontentloaded'});
   const consent=page.getByRole('button',{name:'Ablehnen',exact:true});
   // Consent appears asynchronously; wait for it before touching calculator.
   await consent.waitFor({state:'visible',timeout:15000});
   await consent.click();
   await page.locator('#nicConsentDialog').waitFor({state:'hidden',timeout:10000});
   await page.waitForFunction(()=>document.body.dataset.calculator==='flip'&&window.NICCalculators?.active==='flip'&&typeof window.model==='function',{timeout:25000});
   const slider=page.locator('#ltv').locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," field ")][1]').locator('.nic-finance-percent-range');
   await slider.evaluate(el=>{
    for(let parent=el.parentElement;parent;parent=parent.parentElement){
     if(parent.tagName==='DETAILS')parent.open=true;
    }
   });
   await slider.waitFor({state:'visible',timeout:5000});
   const checkbox=page.locator('#financeAcquisition'),equity=page.locator('#ownEquityInput');
   await page.locator('#purchase').fill('300000');
   const state=()=>page.evaluate(()=>{
    const m=window.model();
    const control=document.getElementById('ltv').closest('.field');
    return {purchase:m.p, fees:m.acquisitionCosts, debt:m.debt, interest:m.interest,
     costs:m.p+m.reno+m.acquisitionCosts+m.holding+m.interest,
     equity:Number(document.getElementById('ownEquityInput').value),
     gap:m.equityShortfall, checked:document.getElementById('financeAcquisition').checked,
     slider:Number(control.querySelector('.nic-finance-percent-range').value),
     hint:control.querySelector('.nic-finance-equity-hint').textContent};
   });
   const verify=async expectedEquity=>{
    await page.waitForFunction(expected=>{
     const m=window.model();
     const control=document.getElementById('ltv').closest('.field');
     const slider=control.querySelector('.nic-finance-percent-range');
     return Number(document.getElementById('ownEquityInput').value)===expected &&
      Math.abs(Number(slider.value)-100*m.debt/m.p)<0.011;
    },expectedEquity);
    const current=await state();
    assert.equal(current.gap,0);
    assert(Math.abs(current.debt+current.equity-current.costs)<0.01);
    assert.match(current.hint,/% des Kaufpreises finanziert/);
    return current;
   };
   await equity.fill('0');
   const full=await verify(0);
   assert(full.slider>100 && full.checked);
   assert.equal(await page.locator('#financeFullWarning').isVisible(),false);

   await equity.fill('904');
   const withEquity=await verify(904);
   const money=amount=>new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(amount);
   const explanation=page.locator('#equityCapitalNeed');
   const note=await explanation.textContent();
   assert(note.includes('Darlehen sinkt um '+money(full.debt-withEquity.debt)));
   assert(note.includes(money(904)+' der Projektkosten'));
   const savedInterest=full.interest-withEquity.interest;
   if(savedInterest>=0.5)assert(note.includes(money(savedInterest)+' Zinsen'));

   await equity.fill('5000');
   const partial=await verify(5000);
   await page.waitForFunction(()=>window.NICSettings?.ready);
   const hintFont=await slider.evaluate(el=>{
    const settings=window.NICSettings;
    settings.apply({...settings.current,layout:{...settings.current.layout,bodySize:17,subtextSize:15,hintSize:19}});
    return getComputedStyle(el.parentElement.querySelector('.nic-finance-equity-hint')).fontSize;
   });
   assert.equal(hintFont,'19px','Fix & Flip hint uses the Admin hint size');
   const subtitles=await page.locator('#flipGoalsCard .section-summary-subtitle:visible,#flipGoalsSubtitle:visible,#decisionText:visible')
    .evaluateAll(nodes=>nodes.map(node=>getComputedStyle(node).fontSize));
   assert.deepEqual(subtitles,['15px','15px'],'Both grey subtitles use the Admin subtext size');
   assert.deepEqual(await explanation.evaluate(el=>[el.parentElement,el].map(node=>getComputedStyle(node).fontSize)),
    ['19px','19px'],'The entire equity box uses the Admin hint size');
   assert(partial.checked && partial.debt<full.debt);
   assert(Math.abs(full.debt-partial.debt-5000-full.interest+partial.interest)<0.01);
   await page.reload({waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.body.dataset.calculator==='flip'&&window.NICCalculators?.active==='flip');
   const restored=await verify(5000);
   assert(Math.abs(restored.debt-partial.debt)<0.01);
   await checkbox.evaluate(el=>{
    for(let parent=el.parentElement;parent;parent=parent.parentElement){
     if(parent.tagName==='DETAILS')parent.open=true;
    }
   });
   page.once('dialog',dialog=>dialog.accept());
   await checkbox.uncheck();
   await page.waitForFunction(()=>Number(document.getElementById('ownEquityInput').value)>=window.model().acquisitionCosts);
   assert.equal(await checkbox.isChecked(),false);
   assert((await state()).debt<restored.debt);
   await page.reload({waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.NICCalculators?.active==='flip');
   await checkbox.evaluate(el=>{
    for(let parent=el.parentElement;parent;parent=parent.parentElement){
     if(parent.tagName==='DETAILS')parent.open=true;
    }
   });
   await checkbox.check();
   const refinanced=await verify(5000);
   assert(Math.abs(refinanced.debt-partial.debt)<0.01);

   await equity.fill('0');
   await verify(0);
   page.once('dialog',dialog=>dialog.accept());
   await checkbox.uncheck();
   await page.waitForFunction(()=>Number(document.getElementById('ownEquityInput').value)>=window.model().acquisitionCosts);
   await checkbox.check();
   assert(Math.abs((await verify(0)).debt-full.debt)<0.01);

   await equity.fill('60000');
   const manual=await verify(60000);
   page.once('dialog',dialog=>dialog.accept());
   await checkbox.uncheck();
   await verify(60000);
   await checkbox.check();
   assert(Math.abs((await verify(60000)).debt-manual.debt)<0.01);
   await equity.fill('0');
   assert((await verify(0)).checked);

   await slider.evaluate(el=>{
    el.value='100';
    el.dispatchEvent(new Event('input',{bubbles:true}));
   });
   const atPurchase=await state();
   assert(Math.abs(atPurchase.debt-atPurchase.purchase)<0.02);
   assert(Math.abs(atPurchase.debt+atPurchase.equity-atPurchase.costs)<0.02);
   const maximumPurchaseBreakEven=await page.evaluate(()=>{
    const m=window.model();
    const atMaximum=window.model({purchase:m.maxBuy,sale:m.s});
    return {maximum:m.maxBuy, profit:atMaximum.profit,
     target:Number(document.getElementById('targetProfit').value)};
   });
   if(maximumPurchaseBreakEven.maximum>0){
    assert(Math.abs(maximumPurchaseBreakEven.profit-maximumPurchaseBreakEven.target)<0.02);
   }
   assert.deepEqual(errors,[]);
   console.log('Fix & Flip loan, equity, rate and reload PASS:',width);
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
