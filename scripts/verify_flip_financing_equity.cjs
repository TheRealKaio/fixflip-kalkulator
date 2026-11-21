// Real-browser parity test for Fix & Flip's special capital/reserve waterfall.
// Exercises checked -> unchecked -> partial cash -> zero cash -> reload.
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
   if(await consent.isVisible())await consent.click();
   await page.waitForFunction(()=>document.body.dataset.calculator==='flip'&&window.NICCalculators?.active==='flip'&&typeof window.model==='function',{timeout:25000});
   const slider=page.locator('#ltv').locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," field ")][1]').locator('.nic-finance-percent-range');
   if(!(await slider.isVisible())){
    const ancestors=await slider.evaluate(el=>{
      const a=[];for(let p=el;p;p=p.parentElement){
        const st=getComputedStyle(p);
        if(st.display==='none'||st.visibility==='hidden'||p.hidden||p.tagName==='DETAILS')
         a.push({tag:p.tagName,id:p.id,cls:String(p.className).slice(0,65),hidden:p.hidden,open:p.open,display:st.display});
      }return a;
    });
    console.log('Fix & Flip slider visibility diagnosis:',JSON.stringify(ancestors));
    await slider.evaluate(el=>{
      for(let p=el;p;p=p.parentElement){
        if(p.tagName==='DETAILS')p.open=true;
      }
    });
   }
   await slider.waitFor({state:'visible',timeout:5000});
   const checkbox=page.locator('#financeAcquisition'),equity=page.locator('#ownEquityInput');
   assert.equal(await page.locator('#equityShortfallWarning').count(),0,'Duplicate red equity warning removed');
   await page.locator('#purchase').fill('300000');
   await page.evaluate(()=>{
    const box=document.getElementById('financeAcquisition');
    if(!box.checked){box.checked=true;box.dispatchEvent(new Event('change',{bubbles:true}));}
    const el=document.getElementById('ltv').closest('.field').querySelector('.nic-finance-percent-range');
    el.value='100';el.dispatchEvent(new Event('input',{bubbles:true}));
   });
   await page.waitForTimeout(150);
   let dialogCount=0;
   const accept=async dialog=>{dialogCount++;await dialog.accept()};
   page.on('dialog',accept);
   await checkbox.focus();await checkbox.press('Space');
   await page.waitForTimeout(150);
   page.off('dialog',accept);
   assert.equal(dialogCount,1,'Trusted user uncheck requires confirmation');
   assert.equal(await checkbox.isChecked(),false);
   const state=()=>page.evaluate(()=>{
    const m=window.model();
    const investment=(m.p||0)+(m.reno||0)+(m.tax||0)+(m.notary||0)+(m.buyBroker||0);
    const fees=(m.tax||0)+(m.notary||0)+(m.buyBroker||0);
    const range=document.getElementById('ltv').closest('.field').querySelector('.nic-finance-percent-range');
    return {investment,fees,base:investment-fees,loan:m.debt,grossDebt:m.grossDebt,
      capital:Number(document.getElementById('ownEquityInput').value),ratio:Number(document.getElementById('ltv').value),
      visible:Number(range.value),full:m.fullFinanceMode,shortfall:m.equityShortfall,
      holding:m.holding,interest:m.interest,need:m.equity,
      checkbox:document.getElementById('financeAcquisition').checked};
   });
   const before=await state();
   assert(before.fees>5000,'Acquisition fee test fixture');
   assert(before.visible<100,'Removing acquisition financing reduces Flip displayed percentage');
   assert(Math.abs(before.capital-before.fees)<1,'Unfinanced fees included in available cash');
   await equity.fill('5000');await page.waitForTimeout(200);
   const partial=await state();
   assert(partial.checkbox,'Partial cash automatically re-enables acquisition financing');
   assert.equal(partial.capital,5000,'Typed partial cash preserved');
   assert(Math.abs(partial.grossDebt-(partial.investment-5000))<1,'Gross debt accounts for typed cash only once');
   assert(Math.abs(partial.loan-partial.grossDebt)<1,'No double cash deduction from Flip loan');
   assert(partial.need>=5000,'Project reserve waterfall includes project costs');
   await equity.fill('0');await page.waitForTimeout(200);
   const zero=await state();
   assert(zero.checkbox,'Zero cash preserves auto-financed acquisition costs');
   assert.equal(zero.capital,0,'Zero cash remains zero');
   assert(zero.full,'Flip zero-cash special full-finance branch remains active');
   assert(zero.loan>=zero.investment,'Full finance includes initial investment plus financing reserves');
   assert(zero.shortfall<1,'Fully financed zero-cash project does not report a phantom cash gap');
   await equity.fill('5000');await page.waitForTimeout(250);
   const saved=await state();
   await page.reload({waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>document.body.dataset.calculator==='flip'&&window.NICCalculators?.active==='flip',{timeout:25000});
   await page.waitForTimeout(400);
   const restored=await state();
   assert(restored.checkbox,'Auto-enabled checkbox is saved');
   assert.equal(restored.capital,5000,'Partial cash is saved');
   assert(Math.abs(restored.grossDebt-saved.grossDebt)<1,
    'Financing ratio and gross loan survive reload: '+JSON.stringify({saved,restored}));
   assert(Math.abs(restored.loan-saved.loan)<1,'Flip loan survives reload');
   assert.deepEqual(errors,[],'No browser runtime exceptions');
   console.log('Fix & Flip financing, equity, reserves and reload PASS:',width,JSON.stringify({before,partial,zero,restored}));
   await page.close();
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
