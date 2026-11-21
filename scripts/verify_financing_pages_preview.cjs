/* Verify the ACTUAL GitHub Pages subpath preview artifact, not _site. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.join(process.cwd(),'_preview');
const parse=v=>Number(String(v).replace(/\./g,'').replace(',','.').replace(/[^\d-]/g,''))||0;
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'});
   const errors=[],missing=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname!=='localhost'){
     if(route.request().resourceType()==='script')return route.fulfill({status:200,contentType:'application/javascript',body:''});
     return route.abort();
    }
    const prefix='/fixflip-kalkulator/';
    if(!u.pathname.startsWith(prefix)){missing.push(u.pathname);return route.fulfill({status:404,body:''});}
    let file=u.pathname.slice(prefix.length);
    if(!file||file.endsWith('/'))file+='index.html';
    const absolute=path.resolve(root,file);
    if(!absolute.startsWith(root+path.sep)||!fs.existsSync(absolute)){missing.push(file);return route.fulfill({status:404,body:''});}
    return route.fulfill({status:200,body:fs.readFileSync(absolute),
     contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.jpg':'image/jpeg'})[path.extname(absolute)]||'text/plain'});
   });
   for(const test of [
    {slug:'vermietung',id:'rentLtv',eq:'rentEquity',purchase:'rentPurchase',checkbox:'rentFinanceAcquisition',mode:'rent'},
    {slug:'eigennutzung',id:'ltv',eq:'ownEquityInput',purchase:'purchase',checkbox:'financeAcquisition',mode:'own'}
   ]){
    await page.goto('http://localhost/fixflip-kalkulator/'+test.slug+'/',{waitUntil:'domcontentloaded'});
    const deny=page.getByRole('button',{name:'Ablehnen',exact:true});
    if(await deny.isVisible())await deny.click();
    await page.waitForFunction(mode=>document.body.dataset.calculator===mode&&window.NICCalculators?.active===mode&&!!window.NICFinancingPercent, test.mode,{timeout:30000});
    const slider=page.locator('#'+test.id).locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," field ")][1]').locator('.nic-finance-percent-range');
    if(!(await slider.isVisible())){
     if(test.mode==='rent'){
      const toggle=page.locator('#rentFinanceToggle');
      if(await toggle.isVisible()&&await toggle.getAttribute('aria-expanded')==='false')await toggle.click();
     }else{
      const details=page.locator('#ownFinanceCard details.advanced');
      if(await details.count())await details.evaluate(el=>el.open=true);
     }
    }
    await slider.waitFor({state:'visible'});
    await page.locator('#'+test.purchase).fill('300000');
    // The page may show persisted settings; explicitly reset cost financing and percentage.
    await page.evaluate(t=>{
     const box=document.getElementById(t.checkbox);
     if(!box.checked){box.checked=true;box.dispatchEvent(new Event('change',{bubbles:true}));}
     const slider=document.getElementById(t.id).closest('.field').querySelector('.nic-finance-percent-range');
     slider.value='100';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },test);
    await page.waitForTimeout(150);
    const before=await page.evaluate(t=>{
     const c=t.mode==='rent'?window.rentalCalculation():window.model();
     const total=t.mode==='rent'?c.totalInvestment:c.initialOwnUseCosts;
     const range=document.getElementById(t.id).closest('.field').querySelector('.nic-finance-percent-range');
     return {checked:document.getElementById(t.checkbox).checked,percent:Number(range.value),
      total,base:c.financingBase,equity:Number(document.getElementById(t.eq).value)};
    },test);
    assert(before.checked,'Financed acquisition initially enabled');
    assert(Math.abs(before.percent-100)<0.01,'Initial preview financing display is 100%');
    // Test a real trusted user interaction with a real confirm dialog.
    let prompts=0;
    page.on('dialog',async dialog=>{prompts++;await dialog.accept();});
    await page.locator('#'+test.checkbox).focus();
    await page.locator('#'+test.checkbox).press('Space');
    await page.waitForTimeout(200);
    const after=await page.evaluate(t=>{
     const c=t.mode==='rent'?window.rentalCalculation():window.model();
     const total=t.mode==='rent'?c.totalInvestment:c.initialOwnUseCosts;
     const range=document.getElementById(t.id).closest('.field').querySelector('.nic-finance-percent-range');
     const output=document.getElementById(t.id).closest('.field').querySelector('output');
     return {checked:document.getElementById(t.checkbox).checked,percent:Number(range.value),
      label:output.textContent,total,base:c.financingBase,equity:Number(document.getElementById(t.eq).value)};
    },test);
    assert.equal(prompts,1,'Checkbox uncheck confirmation shown on actual Pages preview');
    assert.equal(after.checked,false,'Confirmed box unchecked in actual Pages preview');
    assert(after.base<before.base,'Removing financing reduced eligible borrowing base');
    const expected=after.base/after.total*100;
    assert(Math.abs(after.percent-expected)<0.05,'Preview slider must visibly move below 100%: '+JSON.stringify({test,after,expected}));
    assert(after.percent<99.999,'Slider must not stay at 100%');
    assert(Math.abs(after.equity-(after.total-after.base))<1,'Equity increases by unfinanced acquisition costs');
    assert.deepEqual(errors,[],'No browser JS errors');
    console.log('GitHub Pages preview REAL UI financing switch PASS:',test.slug,width,before.percent,'->',after.percent,after.label);
   }
   assert.deepEqual(missing,[],'No missing preview-subpath assets');
   await page.close();
  }
 }finally{await browser.close();}
})().catch(err=>{console.error(err);process.exitCode=1;});
