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
   // Verify the final CSS cascade, including any JavaScript-applied styling.
   const actionStyle=await page.locator('.bottom-actions').evaluate(bar=>{
    const inspect=selector=>{const el=bar.querySelector(selector);if(!el)return null;
     const c=getComputedStyle(el),r=el.getBoundingClientRect();
     return {height:r.height,width:r.width,bg:c.backgroundColor,radius:c.borderTopLeftRadius,display:c.display};
    };
    return {barWidth:bar.getBoundingClientRect().width,primary:inspect('.bottom-primary'),
      pdf:inspect('.bottom-pdf'),download:inspect('.bottom-save')};
   });
   assert(actionStyle.primary&&actionStyle.pdf&&actionStyle.download,'All footer controls present');
   for(const key of ['primary','pdf','download']){
    assert.equal(actionStyle[key].height,44,'Unified footer button height: '+key);
    assert.equal(actionStyle[key].radius,'9px','Unified footer button radius: '+key);
    assert.equal(actionStyle[key].display,'inline-flex','Unified footer button alignment: '+key);
   }
   assert.equal(actionStyle.primary.bg,'rgb(175, 35, 28)','Primary restart control retains red');
   assert.equal(actionStyle.pdf.bg,'rgb(17, 26, 46)','PDF share retains navy');
   assert.equal(actionStyle.download.bg,'rgb(17, 26, 46)','PDF download retains navy');
   assert(actionStyle.primary.width>0&&actionStyle.pdf.width>0&&actionStyle.download.width>0);
   // The shared stylesheet must win over legacy CSS and JS-applied visuals.
   const expandControls=await page.evaluate(()=>{
    const selectors=['.plus-btn','.market-check-toggle','.own-finance-card details.advanced>summary','.flip-section-card details.advanced>summary'];
    return selectors.flatMap(selector=>[...document.querySelectorAll(selector)].map(el=>{
     const pseudo=el.tagName==='SUMMARY';
     const style=getComputedStyle(el,pseudo?'::after':null);
     return {selector,width:style.width,height:style.height,bg:style.backgroundColor,
       color:style.color,border:style.borderTopColor,content:pseudo?style.content:null};
    }));
   });
   for(const item of expandControls){
    assert.equal(item.width,'32px','Expand button width: '+JSON.stringify(item));
    assert.equal(item.height,'32px','Expand button height: '+JSON.stringify(item));
    assert.equal(item.bg,'rgb(237, 243, 255)','Expand button background: '+JSON.stringify(item));
    assert.equal(item.color,'rgb(37, 99, 235)','Expand button color: '+JSON.stringify(item));
   }
   if(['eigennutzung','vermietung','fix-flip'].includes(slug)){
    const id=slug==='vermietung'?'rentFinanceAcquisition':'financeAcquisition';
    const box=page.locator('#'+id);
    const summary=page.locator('details').filter({has:box}).locator(':scope > summary');
    const wasOpen=await box.evaluate(el=>el.closest('details')?.open);
    const rentalClosed=slug==='vermietung'&&await page.locator('#rentFinanceToggle').getAttribute('aria-expanded')==='false';
    if(rentalClosed)await page.locator('#rentFinanceToggle').click();
    if(wasOpen===false)await summary.click();
    for(const viewport of [{width,height:900},{width:320,height:740},{width:844,height:390}]){
     await page.setViewportSize(viewport);
     const size=await box.evaluate(el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return {width:r.width,height:r.height,padding:s.padding};});
     assert(Math.abs(size.width-22.5)<.1&&Math.abs(size.height-22.5)<.1,'Finance checkbox stays 22.5px on '+slug+': '+JSON.stringify({viewport,size}));
     assert.equal(size.padding,'0px','Finance checkbox excludes text-input padding');
    }
    await page.setViewportSize({width,height:900});
    if(width===390&&slug==='vermietung'){
     const fields=await page.evaluate(()=>{
      const rect=selector=>{const r=document.querySelector(selector).getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
      return {interest:rect('.field:has(#rentInterest)'),repayment:rect('.field:has(#rentRepayment)'),financed:rect('.field:has(#rentLtv)'),option:rect('#rentFinancingControls .finance-acq-option'),total:rect('#rentFinancingControls .finance-acq-total')};
     });
     assert(Math.abs(fields.interest.top-fields.repayment.top)<1,'Rental interest and repayment share mobile row 1');
     assert(Math.abs(fields.financed.top-fields.option.top)<1,'Rental financed share and checkbox share mobile row 2');
     assert(fields.financed.top>fields.interest.top&&fields.total.top>fields.financed.top,'Rental acquisition total follows financing choices in row 3');
     assert(Math.abs(fields.total.left-fields.interest.left)<1&&Math.abs(fields.total.right-fields.repayment.right)<1,'Rental acquisition total spans the available width');
    }
    if(wasOpen===false)await summary.click();
    if(rentalClosed)await page.locator('#rentFinanceToggle').click();
   }
   assert.equal(await page.locator('.nic-step-nav').count(),0,'Redesign step navigation must be absent');
   await page.waitForFunction(()=>document.querySelector('.brand-logo')?.complete&&document.querySelector('.brand-logo')?.naturalWidth>0);
   assert(await page.locator('.brand-logo').evaluate(el=>el.tagName==='IMG'&&el.complete&&el.naturalWidth>0));
   assert(await page.locator('.hero').evaluate(el=>getComputedStyle(el).backgroundImage.includes('immocheck-hero.jpg')));
   assert.equal(await page.locator('.nic-brand-bar').count(),1);
   assert.equal(await page.locator('.hero #nicAccountLink').count(),0);
   assert.equal(await page.locator('.nic-menu-icon').count(),5);
   assert.equal(await page.locator('.nic-tile-active').count(),1,'Exactly one active tile on every route');
   if(slug==='fix-flip'){
    await page.evaluate(()=>{
     const section=[...document.querySelectorAll('[data-nic-content-key]')].find(box=>box.querySelector('h2')?.textContent.trim()==='Wo geht das Geld hin?');
     const key=section.dataset.nicContentKey;
     NICContentSections.apply({...NICSettings.current,contentSections:{...NICSettings.current.contentSections,[key]:{visible:true,guestAllowed:false}}});
    });
    await page.waitForFunction(()=>[...document.querySelectorAll('[data-nic-content-key]')].some(box=>box.querySelector('h2')?.textContent.trim()==='Wo geht das Geld hin?'&&box.querySelector('.cost-row .nic-masked-value')));
    const masked=await page.evaluate(()=>{
     const section=[...document.querySelectorAll('[data-nic-content-key]')].find(box=>box.querySelector('h2')?.textContent.trim()==='Wo geht das Geld hin?');
     const style=getComputedStyle(section),box=section.getBoundingClientRect();
     const contentRight=box.right-parseFloat(style.borderRightWidth)-parseFloat(style.paddingRight);
     return [...section.querySelectorAll('.cost-row .nic-masked-value')].map(el=>({
      width:el.getBoundingClientRect().width,right:el.getBoundingClientRect().right,
      rowWidth:el.closest('.cost-row').getBoundingClientRect().width,
      rowRight:el.closest('.cost-row').getBoundingClientRect().right,contentRight
     }));
    });
    assert(masked.length>0,'Guest cost values should be masked');
    assert(masked.every(x=>x.width>0&&x.width<x.rowWidth*.5&&Math.abs(x.right-x.rowRight)<=1&&x.right<=x.contentRight+1),`Masked cost values must match their text width, align to the row edge and remain inside the card: ${JSON.stringify(masked)}`);
    await page.evaluate(()=>NICContentSections.apply(NICSettings.current));
   }
   if(slug==='eigennutzung'){
    const key=await page.locator('#ownMarketCheckSection').getAttribute('data-nic-content-key');
    assert.equal(key,'own.kaufpreis-check','Purchase price check has its own stable access rule');
    const catalog=require('node:fs').readFileSync('_site/content-sections.json','utf8');
    const entry=JSON.parse(catalog).find(item=>item.key===key);
    assert.equal(entry.title,'2. Kaufpreis-Check');
    const financeKey=await page.locator('#ownFinanceCard').getAttribute('data-nic-content-key');
    assert.equal(financeKey,'own.finanzierung-und-nebenkosten');
    assert(JSON.parse(catalog).some(item=>item.key===financeKey&&item.title==='3. Finanzierung und Nebenkosten'),'Own-use finance card appears in admin catalog');
    await page.evaluate(key=>NICContentSections.apply({...NICSettings.current,contentSections:{...NICSettings.current.contentSections,[key]:{visible:false,guestAllowed:false}}}),financeKey);
    assert(await page.locator('#ownFinanceCard').isHidden(),'Admin rule hides runtime finance card');
    await page.evaluate(()=>NICContentSections.apply(NICSettings.current));
    assert.equal(await page.locator('#ownMarketCheckSection h2').evaluate(el=>getComputedStyle(el).fontSize),await page.evaluate(()=>NICSettings.current.layout.h2+'px'),'Purchase price title follows configured H2 size');
    assert(JSON.parse(catalog).some(item=>item.key==='own.noch-prufen'&&item.title==='Ergebnis und Einschätzung'),'Result status has a stable admin label');
   }
   if(width===390&&['eigennutzung','fix-flip'].includes(slug)){
    const originalOpen=await page.locator('#interest').evaluate(el=>{const d=el.closest('details');const open=d.open;d.open=true;return open;});
    const fields=await page.evaluate(()=>{
     const rect=selector=>{const r=document.querySelector(selector).getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
     return {interest:rect('.field:has(#interest)'),repayment:rect('.field:has(#repayment)'),financed:rect('.field:has(#ltv)'),option:rect('.finance-acq-option'),total:rect('.finance-acq-total')};
    });
    assert(Math.abs(fields.interest.top-fields.repayment.top)<1,'Zins and Tilgung share the first mobile row');
    assert(Math.abs(fields.financed.top-fields.option.top)<1,'Finanziert and Mitfinanzieren share the second mobile row');
    assert(fields.financed.top>fields.interest.top&&fields.total.top>fields.financed.top,'Acquisition total follows the financing choices');
    assert(Math.abs(fields.total.left-fields.interest.left)<1&&Math.abs(fields.total.right-fields.repayment.right)<1,'Acquisition total spans both mobile columns');
    assert.equal(await page.locator('#buffer').inputValue(),'','Renovation buffer starts blank');
    if(slug==='eigennutzung')assert.equal(await page.locator('#months').inputValue(),'120','Financing duration starts at 120 months');
    if(slug==='fix-flip'){
     for(const viewport of [{width:320,height:740},{width:390,height:900},{width:844,height:390}]){
      await page.setViewportSize(viewport);
      const sale=await page.evaluate(()=>{
       const rect=el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width};};
       const broker=document.getElementById('sellBroker').closest('.field');
       const other=document.getElementById('otherSaleCosts').closest('.field');
       return {broker:rect(broker),other:rect(other),row:rect(broker.closest('.sale-cost-grid')),input:rect(document.getElementById('sellBroker')),viewport:innerWidth};
      });
      for(const field of [sale.broker,sale.other]){
       assert(Math.abs(field.left-sale.row.left)<1&&Math.abs(field.right-sale.row.right)<1,'Both sale fields span the full mobile row: '+JSON.stringify(sale));
      }
      assert(sale.other.top>=sale.broker.bottom,'Sale broker and additional costs have separate mobile rows');
      assert(sale.input.width>0&&sale.input.left>=0&&sale.input.right<=sale.viewport,'Sale broker input stays inside the mobile viewport');
     }
     await page.setViewportSize({width,height:900});
    }
    await page.evaluate(()=>resetDealCalculatorToDefaults());
    assert.equal(await page.locator('#buffer').inputValue(),'','Reset keeps renovation buffer blank');
    if(slug==='eigennutzung')assert.equal(await page.locator('#months').inputValue(),'120','Reset restores financing duration to 120 months');
    await page.locator('#interest').evaluate((el,open)=>{el.closest('details').open=open;},originalOpen);
   }
   if(width===390&&slug==='budget'){
    for(const id of ['budgetIncomeToggle','budgetExpensesToggle']){
     if(await page.locator('#'+id).getAttribute('aria-expanded')==='false')await page.locator('#'+id).click();
    }
    const incomeIds=['budgetIncomeEmployment','budgetIncomePension','budgetIncomeSupport','budgetIncomeSide','budgetIncomeRent','budgetIncomeOther'];
    const expenseIds=['budgetFood','budgetMobility','budgetInsurance','budgetTelecom','budgetLeisure','budgetChildCosts','budgetExistingLoans','budgetOther'];
    const finishEdit=async(id,value)=>{
     await page.locator('#'+id).fill(value);
     await page.locator('#'+id).press('Tab');
    };
    for(const id of [...incomeIds,...expenseIds])await finishEdit(id,'0');
    const state=()=>page.evaluate(()=>({value:Number(document.getElementById('budgetRateSlider').value),label:document.getElementById('budgetRateSliderValue').textContent,available:document.getElementById('budgetAvailableResult').textContent}));
    const assertRate=async expected=>{
     const current=await state();
     assert(Math.abs(current.value-expected)<0.11,'Committed slider targets safe 35 percent: '+JSON.stringify(current)+' expected '+expected);
     assert.equal(current.label,new Intl.NumberFormat('de-DE',{maximumFractionDigits:1}).format(expected)+' %');
    };
    await finishEdit('budgetIncomeEmployment','4000');await assertRate(35);
    const before=await state();
    await page.locator('#budgetFood').fill('2400');
    assert.deepEqual(await state(),before,'Typing must not update the budget or slider before leaving the field');
    await page.locator('#budgetFood').press('Tab');await assertRate(32.5);
    await page.locator('#budgetRateSlider').evaluate(el=>{el.value='10';el.dispatchEvent(new Event('input',{bubbles:true}));});
    await finishEdit('budgetFood','2600');await assertRate(27.5);
    const beforeIncome=await state();
    await page.locator('#budgetIncomeEmployment').fill('5000');
    assert.deepEqual(await state(),beforeIncome,'Income edits remain provisional before blur');
    await page.locator('#budgetIncomeEmployment').press('Tab');await assertRate(35);
    await finishEdit('budgetIncomeEmployment','0');await assertRate(0);
    const surplus=()=>page.locator('#budgetReserveResult').innerText();
    const euro=n=>new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',minimumFractionDigits:0,maximumFractionDigits:0}).format(n);
    assert.equal(await surplus(),euro(-2600),'Monthly deficit remains signed rather than clipped to zero');
    await finishEdit('budgetFood','0');
    assert.equal(await surplus(),euro(0),'Zero monthly surplus shows an exact currency value');
    await finishEdit('budgetIncomeEmployment','4000');
    await finishEdit('budgetFood','1000,25');
    await page.locator('#budgetRateSlider').evaluate(el=>{el.value='0';el.dispatchEvent(new Event('input',{bubbles:true}));});
    assert.equal(await surplus(),euro(2699.75),'Positive surplus rounds to full euros after expenses, credit rate and financing reserve');
   }
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
   await page.evaluate(()=>{const s=JSON.parse(JSON.stringify(NICSettings.current));s.layout.font='georgia';s.layout.bodySize=20;s.layout.h2=24;s.layout.subtextSize=17;NICSettings.save(s);NICSettings.apply(s);});
   assert(await page.locator('.footer-note').evaluate(el=>getComputedStyle(el).fontSize===NICSettings.current.layout.subtextSize+'px'&&getComputedStyle(el).fontFamily.includes('Georgia')));
   assert(await page.locator('.deal-type-title').evaluate(el=>getComputedStyle(el).fontSize==='24px'));
   for(const selector of ['.bottom-actions>.bottom-primary','.bottom-actions>.bottom-pdf']){
    assert.equal(await page.locator(selector).first().evaluate(el=>getComputedStyle(el).fontSize),'17px','Action label follows Untertexte (px)');
   }
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
   const navigationTile=slug==='finanzierungsrechner'
    ? page.locator('#nicFinancingTab')
    : page.locator(`.deal-type-option[data-href="/${slug}/"]`);
   await navigationTile.click();
   await page.waitForURL('http://127.0.0.1:8766/'+slug+'/',{waitUntil:'domcontentloaded'});
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
 await page.goto('http://127.0.0.1:8766/budget/',{waitUntil:'domcontentloaded'});
 await page.locator('.footer-note').waitFor({state:'visible'});
 assert.equal(await page.locator('.footer-note').evaluate(e=>getComputedStyle(e).fontSize),'17px');
 assert.equal(await page.locator('.footer-note a').first().evaluate(e=>getComputedStyle(e).fontSize),'17px');
 console.log('PASS admin: secondary typography fields, save and reload; footer follows subtext size');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
