const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.NIC_CHROMIUM_BIN?{executablePath:process.env.NIC_CHROMIUM_BIN,args:['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-zygote','--single-process']}: {})});
 const page=await browser.newPage({viewport:{width:1440,height:900},serviceWorkers:"block"});
 await page.route('**/backend-config.json',route=>route.fulfill({json:{enabled:true,apiUrl:'https://neustart-immocheck.de/api/index.php'}}));
 await page.route('https://neustart-immocheck.de/api/**',route=>route.fulfill({json:{user:null,csrf:'ui-test',settings:require('../assets/site-settings.json'),revision:1}}));
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});
  for(const slug of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']){
   const errors=[];const listener=e=>errors.push(e.message);page.on('pageerror',listener);
   const response=await page.goto('http://127.0.0.1:8766/'+slug+'/',{waitUntil:'domcontentloaded'});
   assert.equal(response.status(),200);await page.waitForTimeout(800);
   assert.equal(await page.locator('.nic-step-nav').count(),0,'Redesign step navigation must be absent');
   assert(await page.locator('.brand-logo').evaluate(el=>el.tagName==='IMG'&&el.complete&&el.naturalWidth===920));
   assert(await page.locator('.hero').evaluate(el=>getComputedStyle(el).backgroundImage.includes('immocheck-hero.jpg')));
   assert.equal(await page.locator('.nic-brand-bar').count(),1);
   assert.equal(await page.locator('.hero #nicAccountLink').count(),0);
   assert.equal(await page.locator('.nic-menu-icon').count(),5);
   assert(await page.locator('.deal-type-option').evaluateAll(els=>els.every(el=>Math.abs(el.getBoundingClientRect().height-78)<1)),'Existing tile height must remain 78 px');
   assert(await page.locator('.nic-brand-bar').evaluate(bar=>[...bar.children].every(el=>{const r=el.getBoundingClientRect(),b=bar.getBoundingClientRect();return r.left>=b.left-1&&r.right<=b.right+1})), 'Brand bar content must stay inside its width');
   assert.equal(await page.locator('#nicAccountLink').innerText(),'Jetzt anmelden');
   if(slug!=='finanzierungsrechner')assert(!(await page.locator('.footer-note').innerText()).includes('Der Deal Check ist eine Kalkulationshilfe'));
   assert.equal(await page.locator('.footer-version').evaluate(el=>getComputedStyle(el).color),'rgb(255, 255, 255)');
   assert(await page.locator('.footer-note').evaluate(el=>parseFloat(getComputedStyle(el).borderBottomLeftRadius)>0));
   const reject=page.getByRole('button',{name:'Ablehnen',exact:true});if(await reject.isVisible())await reject.click();
   const cookie=page.locator('#nicConsentSettings');if(await cookie.count())assert.equal(await cookie.evaluate(el=>getComputedStyle(el).color),'rgb(255, 255, 255)');
   await page.locator('#nicAccountLink').click();
   await page.locator('#nicLoginTitle').waitFor({state:'visible'});
   await page.getByRole('button',{name:'Abbrechen',exact:true}).click();
   assert.equal(await page.locator('.footer-note').evaluate(el=>getComputedStyle(el).paddingTop),'5px');
   assert(await page.evaluate(()=>{const a=document.querySelector('.app').getBoundingClientRect(),b=document.querySelector('.bottom').getBoundingClientRect();return Math.abs(a.width-b.width)<1&&Math.abs(a.left-b.left)<1}),'Action bar must align with calculator width');
   assert(await page.locator('[data-nic-calculator="finance"]').evaluate(el=>{const i=el.querySelector('.nic-menu-icon').getBoundingClientRect(),t=el.querySelector('strong').getBoundingClientRect();return Math.abs(i.top+i.height/2-t.top-t.height/2)<1}),'Finance title and symbol must be centered');
   if(slug==='budget'){
    await page.locator('#budgetNetIncome').fill('5000');
    await page.locator('#budgetExpensesToggle').evaluate(el=>el.click());
    await page.locator('#budgetApplySuggestions').evaluate(el=>el.click());
    assert.equal(await page.locator('#budgetApplySuggestions').innerText(),'Vorschläge übernehmen');
    await page.locator('#budgetFood').fill('777');
    await page.locator('[data-clear-mask="#budgetExpensesBody"]').evaluate(el=>el.click());
    assert(await page.locator('#budgetExpensesBody input').evaluateAll(els=>els.every(el=>!Number(el.value.replace(',','.')))),'Expense mask must be cleared');
    assert.equal(await page.locator('#budgetNetIncome').inputValue(),'5000');
    assert.equal(await page.locator('#budgetApplySuggestions').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(7, 92, 85)');
    if(width===1440){await page.reload({waitUntil:'domcontentloaded'});await page.waitForTimeout(800);await page.locator('#budgetExpensesToggle').evaluate(el=>el.click());assert.equal(Number(await page.locator('#budgetFood').inputValue()),0,'Cleared expenses must stay cleared after reload');}
   }
   if(['eigennutzung','fix-flip','vermietung'].includes(slug)){
    const rent=slug==='vermietung',area=rent?'#rentArea':'#area',open=rent?'#rentOpenReno':'#openReno',apply=rent?'#rentApplyTradeSuggestions':'#applyTradeSuggestions',mask=rent?'#rentRenoPanel':'#renoBackdrop';
    await page.locator(area).fill('120');
    await page.locator(open).evaluate(el=>el.click());
    await page.locator(apply).evaluate(el=>el.click());
    assert.equal(await page.locator(apply).innerText(),'Vorschläge übernehmen');
    assert.equal(await page.locator(apply).evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(7, 92, 85)');
    assert(await page.locator(mask+' input[data-trade]').evaluateAll(els=>els.some(el=>Number(el.value)>0)),'Suggestions must still apply');
    await page.locator('[data-clear-mask="'+mask+'"]').evaluate(el=>el.click());
    assert(await page.locator(mask+' input').evaluateAll(els=>els.filter(el=>!el.readOnly&&!el.disabled).every(el=>!Number(el.value.replace(',','.')))),'Renovation mask must be cleared');
    assert.equal(await page.locator(area).inputValue(),'120');
    if(slug==='eigennutzung')assert.equal(await page.locator('#ownImportBudgetValues').evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(7, 92, 85)');
    for(const id of rent?['rentResetTrades','rentSaveTrades']:['resetTrades','saveTrades'])assert.equal(await page.locator('#'+id).isVisible(),false);
    assert(await page.locator(apply).evaluate(el=>{const c=el.parentElement,r=c.getBoundingClientRect(),b=el.getBoundingClientRect(),x=c.querySelector('.nic-clear-mask').getBoundingClientRect();const h=el.closest('.reno-head')?.getBoundingClientRect();return r.width<=parseFloat(c.style.getPropertyValue('--nic-suggestion-width'))+1&&Math.abs(b.top-x.top)<1&&(!h||r.right<=h.right+1)}),'Clear control must not widen or wrap its action row');
    if(width===1440){await page.reload({waitUntil:'domcontentloaded'});await page.waitForTimeout(800);await page.locator(open).evaluate(el=>el.click());assert(await page.locator(mask+' input[data-trade]').evaluateAll(els=>els.every(el=>!Number(el.value))),'Cleared renovation amounts must stay cleared after reload');assert.equal(await page.locator(area).inputValue(),'120');}
   }
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
