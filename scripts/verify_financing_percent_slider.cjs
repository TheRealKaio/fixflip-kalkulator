/* Development regression: manual equity drives LTV until an explicit slider move; the slider then updates equity. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [390,900,1440]){
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
    const consent=page.getByRole('button',{name:'Ablehnen',exact:true});
    if(route==='vermietung'){
     await consent.waitFor({state:'visible',timeout:15000});
     await consent.click();
    }
    const key=route==='vermietung'?'rent':'own';
    await page.waitForFunction(k=>document.body.dataset.calculator===k && window.NICCalculators?.active===k,key,{timeout:25000});
    const range=page.locator('#'+input).locator('xpath=following-sibling::*[contains(@class,"nic-finance-percent-control")]//input[@type="range"]');
    // Parent may be an input-wrap; locate the shared field rather than assuming sibling order.
    const slider=page.locator('#'+input).locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," field ")][1]').locator('.nic-finance-percent-range');
    if(!(await slider.isVisible())){
      const ancestors=await slider.evaluate(el=>{
       const result=[];for(let n=el;n&&result.length<16;n=n.parentElement){
        const style=getComputedStyle(n);
        if(style.display==='none'||style.visibility==='hidden'||n.hasAttribute('hidden'))
         result.push({id:n.id,cls:n.className,display:style.display,visibility:style.visibility,hidden:n.hidden});
       }return result;
      });
      console.log('Financing slider visibility diagnosis',route,JSON.stringify(ancestors));
      const toggle=page.locator('#rentFinanceToggle');
      if(route==='vermietung' && await toggle.isVisible() && await toggle.getAttribute('aria-expanded')==='false')
       await toggle.click();
      const ownDetails=page.locator('#ownFinanceCard details.advanced');
      if(route==='eigennutzung' && await ownDetails.count())
       await ownDetails.evaluate(el=>el.open=true);
    }
    await slider.waitFor({state:'visible',timeout:4000});
    assert.equal(await page.locator('#'+input).count(),1,'Original percent field is retained once');
    assert(Number(await slider.getAttribute('max'))>=120,'Slider supports 120 percent');
    assert.equal(await slider.evaluate(el=>Math.round(el.getBoundingClientRect().width)),
                 await slider.evaluate(el=>Math.round(el.closest('.field').getBoundingClientRect().width)),
                 'Slider spans its field');
    if(route==='vermietung' && width>700){
      const layout=await page.evaluate(()=>{
        const rent=document.getElementById('rentFinanceCard');
        const rates=[document.getElementById('rentInterest'),document.getElementById('rentRepayment')];
        const field=el=>el.closest('.field').getBoundingClientRect();
        const [interest,repayment]=rates.map(field);
        const fees=[document.getElementById('rentNotary'),document.getElementById('rentBroker')].map(el=>el.getBoundingClientRect());
        const option=rent.querySelector('.finance-acq-option');
        const caption=option.querySelector('.finance-check-label').getBoundingClientRect();
        const check=option.querySelector('#rentFinanceAcquisition').getBoundingClientRect();
        return {interest:{x:interest.x,y:interest.y,w:interest.width},
          repayment:{x:repayment.x,y:repayment.y,w:repayment.width},
          feeTop:fees.map(x=>x.top),
          captionCenter:caption.x+caption.width/2,checkCenter:check.x+check.width/2};
      });
      assert(Math.abs(layout.interest.w-layout.repayment.w)<3,'Interest and repayment use equal halves');
      assert(Math.abs(layout.interest.y-layout.repayment.y)<3,'Interest and repayment have one baseline');
      assert(Math.abs(layout.feeTop[0]-layout.feeTop[1])<0.51,'Notary and broker inputs align to the same pixel');
      assert(Math.abs(layout.captionCenter-layout.checkCenter)<6,'Checkbox sits centered under caption');
    }
    if(width<=700){
      const centers=await page.evaluate(id=>{
        const card=document.getElementById(id==='rentLtv'?'rentFinanceCard':'ownFinanceCard');
        const label=card.querySelector('.finance-check-label');
        const checkbox=card.querySelector('.finance-check-box input');
        const range=document.createRange();
        range.selectNodeContents(label);
        return [range.getBoundingClientRect(),checkbox.getBoundingClientRect()].map(rect=>rect.left+rect.width/2);
      },input);
      assert(Math.abs(centers[0]-centers[1])<3,'Mobile caption is centered over its checkbox: '+route);
    }
    const purchaseId=route==='vermietung'?'rentPurchase':'purchase';
    await page.locator('#'+purchaseId).fill('300000');
    await page.evaluate(({id})=>{
     const el=document.querySelector('#'+id+'~.nic-finance-percent-control input');
     const slider=el||document.getElementById(id).closest('.field').querySelector('input[type="range"]');
     slider.value='0';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    await page.waitForTimeout(100);
    const required=await page.locator('#'+equity).inputValue();
    const parse=v=>Number(v.replace(/\./g,'').replace(',','.'))||0;
    assert(parse(required)>=300000,'Zero percent financing must auto-fill at least the purchase price');
    if(route==='vermietung'){
      const before=parse(await page.locator('#'+equity).inputValue());
      const ratio=await page.locator('#'+input).inputValue();
      await page.locator('#rentNotary').fill('3');
      await page.waitForTimeout(120);
      const after=parse(await page.locator('#'+equity).inputValue());
      assert(after>before,'Changing notary costs updates automatically calculated equity');
      assert.equal(await page.locator('#'+input).inputValue(),ratio,'Changing notary does not move financing percentage');
    }
    // Once edited by the user, equity is fixed and determines the slider.
    await page.locator('#'+equity).fill('17500');
    if(route==='vermietung'){
      const check=await page.evaluate(()=>{
       const m=window.rentalCalculation();
       return {equity:Number(document.getElementById('rentEquity').value),percentage:Number(document.getElementById('rentLtv').value),
        expected:Math.round(Math.max(0,m.totalInvestment-17500)/m.financingBase*10000)/100,
        loan:m.loan,expectedLoan:m.financingBase*(Number(document.getElementById('rentLtv').value)/100)};
      });
      assert(Math.abs(check.percentage-check.expected)<0.01,'Manually fixed equity determines the financing slider');
      assert(Math.abs(check.loan-check.expectedLoan)<0.02,'Rental loan does not deduct equity a second time');
      const previous=check.percentage;
      await page.locator('#rentBroker').fill('6.00');
      await page.waitForTimeout(150);
      assert.equal(parse(await page.locator('#'+equity).inputValue()),17500,'Broker edit must preserve fixed equity');
      assert.notEqual(Number(await page.locator('#rentLtv').inputValue()),previous,'Broker edit moves slider for fixed equity');
      const updated=await page.evaluate(()=>{
       const m=window.rentalCalculation();return {loan:m.loan,expected:m.financingBase*(Number(document.getElementById('rentLtv').value)/100)};
      });
      assert(Math.abs(updated.loan-updated.expected)<0.02,'Loan remains percentage-based after broker change');
    }
    await page.evaluate(({id})=>{
      const slider=document.getElementById(id).closest('.field').querySelector('input[type="range"]');
      slider.value='99.6';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    assert.equal(Number(await page.locator('#'+input).inputValue()),100,'Slider magnetically snaps to exactly 100 percent');
    const at100=await page.evaluate(({id})=>{const m=id==='rentLtv'?window.rentalCalculation():window.model();return {total:id==='rentLtv'?m.totalInvestment:m.initialOwnUseCosts,base:m.financingBase};},{id:input});
    assert(Math.abs(parse(await page.locator('#'+equity).inputValue())-Math.max(0,at100.total-at100.base))<1,'100 percent snap recalculates equity on deliberate slider move');

    await page.evaluate(({id})=>{
     const slider=document.getElementById(id).closest('.field').querySelector('input[type="range"]');
     slider.value='80';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    const at80=await page.evaluate(({id})=>{const m=id==='rentLtv'?window.rentalCalculation():window.model();return {total:id==='rentLtv'?m.totalInvestment:m.initialOwnUseCosts,base:m.financingBase};},{id:input});
    assert(Math.abs(parse(await page.locator('#'+equity).inputValue())-Math.max(0,at80.total-at80.base*0.8))<1,'80 percent slider updates equity after manual entry');
    assert.match(await page.locator('#'+input).locator('xpath=ancestor::*[contains(concat(" ",normalize-space(@class)," ")," field ")][1]').locator('.nic-finance-equity-hint').textContent(),/Eigenkapital|mehr|weniger/,'Slider explains equity change');
    await page.evaluate(({id})=>{
     const slider=document.getElementById(id).closest('.field').querySelector('input[type="range"]');
     slider.value='120';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },{id:input});
    assert.equal(Number(await page.locator('#'+input).inputValue()),120,'120 percent reaches the original model field');

    // Cross-calculator parity: with the same project cost/base and financing
    // percentage, both modes must produce the same required-equity arithmetic.
    // A checkbox change must not preserve a stale manually fixed equity amount.
    const checkbox=page.locator('#'+(route==='vermietung'?'rentFinanceAcquisition':'financeAcquisition'));
    await page.evaluate(id=>{
      const c=document.getElementById(id);
      if(!c.checked){c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}));}
      const slider=document.getElementById(id==='rentFinanceAcquisition'?'rentLtv':'ltv').closest('.field').querySelector('input[type="range"]');
      slider.value='100';slider.dispatchEvent(new Event('input',{bubbles:true}));
    },route==='vermietung'?'rentFinanceAcquisition':'financeAcquisition');
    await page.waitForTimeout(100);
    const financed=await page.evaluate(({id,eq})=>{
      const m=id==='rentLtv'?window.rentalCalculation():window.model();
      return {total:id==='rentLtv'?m.totalInvestment:m.initialOwnUseCosts,base:m.financingBase,
        equity:Number(document.getElementById(eq).value),ratio:Number(document.getElementById(id).value)};
    },{id:input,eq:equity});
    assert(Math.abs(financed.equity-Math.max(0,financed.total-financed.base))<1,
      'Financed acquisition costs follow identical equity formula in '+route);
    assert.equal(financed.ratio,100,'Financing checkbox keeps 100 percent ratio');

    // Keyboard toggles are trusted browser actions, unlike synthetic click().
    // Dismissing the confirmation must leave all values unchanged.
    let dialogs=0;
    const dismiss=async dialog=>{dialogs++;assert.match(dialog.message(),/Kaufnebenkosten/);await dialog.dismiss();};
    page.on('dialog',dismiss);
    await checkbox.focus();
    await checkbox.press('Space');
    await page.waitForTimeout(70);
    page.off('dialog',dismiss);
    assert.equal(dialogs,1,'Unchecking financed costs requires confirmation');
    assert.equal(await checkbox.isChecked(),true,'Declining confirmation preserves financing');
    const accept=async dialog=>{dialogs++;await dialog.accept();};
    page.on('dialog',accept);
    await checkbox.press('Space');
    await page.waitForTimeout(120);
    page.off('dialog',accept);
    assert.equal(dialogs,2,'Accepting confirmation is prompted');
    assert.equal(await checkbox.isChecked(),false,'Confirmation removes acquisition financing');
    const unfinanced=await page.evaluate(({id,eq})=>{
      const m=id==='rentLtv'?window.rentalCalculation():window.model();
      return {total:id==='rentLtv'?m.totalInvestment:m.initialOwnUseCosts,base:m.financingBase,
        equity:Number(document.getElementById(eq).value),ratio:Number(document.getElementById(id).value)};
    },{id:input,eq:equity});
    assert.equal(unfinanced.ratio,100,'Disabling acquisition financing does not shift LTV');
    assert(unfinanced.base<financed.base,'Disabling acquisition financing reduces financing base');
    assert(Math.abs(unfinanced.equity-Math.max(0,unfinanced.total-unfinanced.base))<1,
      'Unfinanced acquisition costs are covered by equity in '+route);
    assert(unfinanced.equity>financed.equity,'Removing financing increases required equity');

   }
   assert.deepEqual(errors,[],'No uncaught browser errors');
   await page.close();
  }
  console.log('Financing sliders: rental and owner, 0–120 percent, manually set equity until slider movement, 100% detent, desktop/mobile passed');
 }finally{await browser.close();}
})().catch(err=>{console.error(err);process.exitCode=1;});
