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
    assert(['flex','inline-flex'].includes(actionStyle[key].display),'Unified flex alignment: '+key);
   }
   assert.equal(actionStyle.primary.bg,'rgb(180, 35, 24)','Primary restart control retains theme red');
   assert.equal(actionStyle.pdf.bg,'rgb(15, 23, 42)','PDF share retains navy');
   assert.equal(actionStyle.download.bg,'rgb(15, 23, 42)','PDF download retains navy');
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
    assert.equal(item.bg,'rgb(253, 230, 138)','Expand button background: '+JSON.stringify(item));
    assert.equal(item.color,'rgb(0, 0, 0)','Expand button color: '+JSON.stringify(item));
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
    if(width===390&&slug==='eigennutzung'){
     const fields=await page.evaluate(()=>{
      const rect=selector=>{const el=document.querySelector(selector);const r=el.getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
      return {interest:rect('.field:has(#interest)'),repayment:rect('.field:has(#repayment)'),financed:rect('.field:has(#ltv)'),duration:rect('.finance-duration-swap-v8403'),total:rect('#ownFinanceCard .finance-acq-total'),option:rect('#ownFinanceCard .finance-acq-option'),row:rect('#ownFinanceCard .finance-acq-row')};
     });
     assert(Math.abs(fields.interest.top-fields.repayment.top)<1,'Own-use mobile keeps interest and repayment together: '+JSON.stringify(fields));
     assert(fields.financed.top>fields.interest.top&&fields.financed.width>fields.interest.width,'Own-use mobile gives financed a full-width row: '+JSON.stringify(fields));
     assert(fields.duration.top>fields.financed.top&&fields.total.top>fields.duration.top,'Own-use mobile follows the desktop order through acquisition costs: '+JSON.stringify(fields));
     assert(Math.abs(fields.total.top-fields.option.top)<1&&fields.total.top>fields.duration.top,'Own-use mobile aligns acquisition total and financing toggle on one row: '+JSON.stringify(fields));
    }
    if(width===1440&&slug==='eigennutzung'){
     await page.setViewportSize({width:768,height:1024});
     const fields=await page.evaluate(()=>{
      const rect=id=>{const r=document.querySelector('.field:has(#'+id+')').getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
      return {interest:rect('interest'),repayment:rect('repayment'),financed:rect('ltv')};
     });
     assert(Math.abs(fields.interest.top-fields.repayment.top)<1&&Math.abs(fields.repayment.top-fields.financed.top)<1,
       'Own-use tablet places interest, repayment and financed on one row: '+JSON.stringify(fields));
     assert(fields.financed.left>fields.repayment.left&&fields.financed.width>0,
       'Own-use tablet places financed to the right of repayment: '+JSON.stringify(fields));
     await page.setViewportSize({width,height:900});
    }
    if(width===1440&&['eigennutzung','vermietung','fix-flip'].includes(slug)){
     const desktopSelectors=slug==='vermietung'
      ?{row:'#rentFinancingControls .finance-acq-row',total:'#rentFinancingControls .finance-acq-total',notary:'#rentFinanceCard .field:has(#rentNotary)'}
      :slug==='eigennutzung'
       ?{row:'#ownFinanceCard .finance-acq-row',total:'#ownFinanceCard .finance-acq-total',notary:'#ownFinanceCard .field:has(#notary)'}
       :{row:'#finance-acq-row-swap-v8403',total:'#finance-acq-row-swap-v8403 .finance-acq-total',notary:'#flipFinanceCard .field:has(#notary)'};
     const desktopWidths=await page.evaluate(selectors=>{
      const row=document.querySelector(selectors.row),total=document.querySelector(selectors.total),notary=document.querySelector(selectors.notary);
      if(!row||!total||!notary)return null;
      const box=el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width};};
      const option=row.querySelector('.finance-acq-option');
      return {row:box(row),total:box(total),notary:box(notary),option:option?box(option):null};
     },desktopSelectors);
     assert(desktopWidths&&desktopWidths.option,'Desktop acquisition row exists for '+slug+': '+JSON.stringify(desktopWidths));
     assert(Math.abs(desktopWidths.total.width-desktopWidths.notary.width)<2,
       'Desktop acquisition costs match Notar + Grundbuch width on '+slug+': '+JSON.stringify(desktopWidths));
     assert(Math.abs(desktopWidths.total.left-desktopWidths.notary.left)<2,
       'Desktop acquisition costs align with Notar + Grundbuch on '+slug+': '+JSON.stringify(desktopWidths));
    }
    if(width===1440&&['eigennutzung','vermietung','fix-flip'].includes(slug)){
     await page.setViewportSize({width:768,height:1024});
     const tabletSelectors=slug==='vermietung'
      ?{row:'#rentFinancingControls .finance-acq-row',total:'#rentFinancingControls .finance-acq-total',notary:'#rentFinanceCard .field:has(#rentNotary)'}
      :slug==='eigennutzung'
       ?{row:'#ownFinanceCard .finance-acq-row',total:'#ownFinanceCard .finance-acq-total',notary:'#ownFinanceCard .field:has(#notary)'}
       :{row:'#finance-acq-row-swap-v8403',total:'#finance-acq-row-swap-v8403 .finance-acq-total',notary:'#flipFinanceCard .field:has(#notary)'};
     const tabletWidths=await page.evaluate(selectors=>{
      const row=document.querySelector(selectors.row),total=document.querySelector(selectors.total),notary=document.querySelector(selectors.notary);
      if(!row||!total||!notary)return null;
      const box=el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width,top:r.top};};
      const option=row.querySelector('.finance-acq-option');
      return {row:box(row),total:box(total),notary:box(notary),option:option?box(option):null};
     },tabletSelectors);
     assert(tabletWidths&&tabletWidths.option,'Tablet acquisition row exists for '+slug+': '+JSON.stringify(tabletWidths));
     assert(Math.abs(tabletWidths.total.width-tabletWidths.notary.width)<2,
       'Tablet acquisition costs match Notar + Grundbuch width on '+slug+': '+JSON.stringify(tabletWidths));
     assert(Math.abs(tabletWidths.total.left-tabletWidths.notary.left)<2,
       'Tablet acquisition costs align with Notar + Grundbuch on '+slug+': '+JSON.stringify(tabletWidths));
     await page.setViewportSize({width,height:900});
    }
    if(width===390&&slug==='vermietung'){
     const fields=await page.evaluate(()=>{
      const rect=selector=>{const r=document.querySelector(selector).getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
      return {interest:rect('.field:has(#rentInterest)'),repayment:rect('.field:has(#rentRepayment)'),financed:rect('.field:has(#rentLtv)'),duration:rect('.field:has(#rentMonths)'),notary:rect('.field:has(#rentNotary)'),broker:rect('.field:has(#rentBroker)'),option:rect('#rentFinancingControls .finance-acq-option'),total:rect('#rentFinancingControls .finance-acq-total'),row:rect('#rentFinancingControls .finance-acq-row')};
     });
     assert(Math.abs(fields.interest.top-fields.repayment.top)<1,'Rental interest and repayment share the first mobile row: '+JSON.stringify(fields));
     assert(fields.financed.top>fields.interest.top&&fields.duration.top>fields.financed.top,'Rental financed share and duration follow interest: '+JSON.stringify(fields));
     assert(fields.notary.top>fields.duration.top&&Math.abs(fields.notary.top-fields.broker.top)<1,'Rental notary and broker follow duration on one row: '+JSON.stringify(fields));
     assert(fields.total.top>fields.broker.top&&Math.abs(fields.total.top-fields.option.top)<1,'Rental acquisition total and financing toggle form the final row: '+JSON.stringify(fields));
     assert(Math.abs(fields.total.left-fields.row.left)<1&&Math.abs(fields.option.right-fields.row.right)<1,'Rental acquisition row spans the available width');
    }
    if(width===390&&['eigennutzung','vermietung','fix-flip'].includes(slug)){
     const rowSelector=slug==='vermietung'?'#rentFinancingControls .finance-acq-row':slug==='eigennutzung'?'#ownFinanceCard .finance-acq-row':'#finance-acq-row-swap-v8403';
     const rateSelector=slug==='vermietung'?'.field:has(#rentInterest)':'.field:has(#interest)';
     const geometry=await page.evaluate(({rowSelector,rateSelector})=>{
      const row=document.querySelector(rowSelector),rate=document.querySelector(rateSelector);
      if(!row||!rate)return null;
      const box=el=>{const r=el.getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
      return {row:box(row),rate:box(rate),total:box(row.querySelector('.finance-acq-total')),option:box(row.querySelector('.finance-acq-option'))};
     },{rowSelector,rateSelector});
     assert(geometry&&geometry.total&&geometry.option,'Acquisition row and both controls exist on '+slug);
     assert(Math.abs(geometry.total.top-geometry.option.top)<1,'Acquisition total and checkbox share a row on '+slug+': '+JSON.stringify(geometry));
     assert(Math.abs(geometry.total.left-geometry.rate.left)<2&&Math.abs(geometry.total.width-geometry.rate.width)<2,
       'Acquisition total matches mobile interest field width on '+slug+': '+JSON.stringify(geometry));
     assert(Math.abs(geometry.option.right-geometry.row.right)<2,'Financing checkbox occupies right side on '+slug+': '+JSON.stringify(geometry));
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
    if(width===1440){
     await page.evaluate(()=>{
      const section=[...document.querySelectorAll('[data-nic-content-key]')].find(box=>box.querySelector('h2')?.textContent.trim()==='Wo geht das Geld hin?');
      const key=section.dataset.nicContentKey;
      NICContentSections.apply({...NICSettings.current,contentSections:{...NICSettings.current.contentSections,[key]:{visible:true,guestAllowed:true}}});
     });
     const renovation=page.locator('.cost-row').filter({hasText:'Modernisierung'});
     const total=page.locator('.cost-total').filter({hasText:'Gesamt'});
     const original=await page.locator('#reno').inputValue();
     await page.locator('#reno').fill('15000');
     await page.locator('#reno').press('Tab');
     const at15000=await total.innerText();
     assert.match(await renovation.innerText(),/15\.000/,'Manual renovation value appears in the cost breakdown');
     await page.locator('#reno').fill('20000');
     await page.locator('#reno').press('Tab');
     const at20000=await total.innerText();
     assert.notEqual(at20000,at15000,'Changing manual renovation value recalculates the overall project cost');
     await page.locator('#reno').fill(original);
     await page.locator('#reno').press('Tab');
     await page.evaluate(()=>NICContentSections.apply(NICSettings.current));
    }
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
     const rectEl=el=>{const r=el.getBoundingClientRect();return {top:r.top,left:r.left,right:r.right,width:r.width};};
     const durationField=document.querySelector('.finance-duration-swap-v8403');
     const financeGrid=durationField.closest('.quick-grid');
     const acqRow=document.getElementById('finance-acq-row-swap-v8403');
     return {interest:rect('.field:has(#interest)'),repayment:rect('.field:has(#repayment)'),financed:rect('.field:has(#ltv)'),duration:rectEl(durationField),notary:rectEl(financeGrid.querySelector('#notary').closest('.field')),buyBroker:rectEl(financeGrid.querySelector('#buyBroker').closest('.field')),option:rectEl(acqRow.querySelector('.finance-acq-option')),total:rectEl(acqRow.querySelector('.finance-acq-total')),row:rectEl(acqRow),rowStyle:{display:getComputedStyle(acqRow).display,gridTemplateColumns:getComputedStyle(acqRow).gridTemplateColumns,gridRow:getComputedStyle(acqRow).gridRow,position:getComputedStyle(acqRow).position},rowHtml:acqRow.outerHTML.slice(0,1600),parentTag:acqRow.parentElement.tagName,parentClass:acqRow.parentElement.className,parentStyle:{display:getComputedStyle(acqRow.parentElement).display,gridAutoFlow:getComputedStyle(acqRow.parentElement).gridAutoFlow,gridTemplateColumns:getComputedStyle(acqRow.parentElement).gridTemplateColumns,gridTemplateRows:getComputedStyle(acqRow.parentElement).gridTemplateRows},parentHtml:acqRow.parentElement.outerHTML.slice(0,2600)};
    });
    assert(Math.abs(fields.interest.top-fields.repayment.top)<1,'Zins and Tilgung share the first mobile row');
    assert(fields.financed.top>fields.interest.top&&fields.duration.top>fields.financed.top,'Finanzierungsdauer folgt den Finanzierungsannahmen');
    assert(fields.notary.top>fields.duration.top&&Math.abs(fields.notary.top-fields.buyBroker.top)<1,'Notar und Makler folgen auf die Laufzeit: '+JSON.stringify(fields));
    assert(Math.abs(fields.total.left-fields.row.left)<1&&Math.abs(fields.option.right-fields.row.right)<1,'Kaufnebenkosten und Mitfinanzieren füllen gemeinsam die vollständige Zeile');
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
   // Cost chart labels, amounts and totals must follow the admin 'Untertexte (px)' size.
   if(['eigennutzung','fix-flip'].includes(slug)){
    const costTypography=await page.evaluate(()=>{
     const chart=[...document.querySelectorAll('section,.card')].find(el=>el.querySelector('h2')?.textContent.trim()==='Wo geht das Geld hin?'&&el.querySelector('.cost-row'));
     if(!chart)return null;
     const rows=[...chart.querySelectorAll('.cost-row')];
     const texts=rows.flatMap(row=>[...row.querySelectorAll('*')].filter(el=>el.children.length===0&&el.textContent.trim()&&getComputedStyle(el).display!=='none'));
     const total=[...chart.querySelectorAll('*')].find(el=>el.children.length===0&&el.textContent.trim()==='Gesamt');
     return {rows:rows.length,labels:rows.map(row=>row.innerText.trim()),fonts:texts.map(el=>getComputedStyle(el).fontSize),total:total?getComputedStyle(total).fontSize:null};
    });
    const expectedCostRows=slug==='eigennutzung'?6:7;
    assert(costTypography&&costTypography.rows>=expectedCostRows,'Cost breakdown rows exist');
    assert(costTypography.fonts.length>=expectedCostRows&&costTypography.fonts.every(font=>font==='17px'),
      'Cost chart captions and amounts use Untertexte 17px: '+JSON.stringify(costTypography));
    assert.equal(costTypography.total,'17px','Cost chart overall total uses Untertexte');
    const hasSaleCostRow=costTypography.labels.some(label=>label.includes('Verkaufskosten'));
    assert.equal(hasSaleCostRow,slug==='fix-flip','Sale-cost chart row is shown only in Fix & Flip');
    if(slug==='eigennutzung'){
     const saleFieldsHidden=await page.evaluate(()=>['sellBroker','otherSaleCosts'].map(id=>{
      const field=document.getElementById(id)?.closest('.field');
      return !field||field.getClientRects().length===0;
     }));
     assert.deepEqual(saleFieldsHidden,[true,true],'Sale-cost inputs are hidden in own-use financing');
    }
   }
   for(const selector of ['.bottom-actions>.bottom-primary','.bottom-actions>.bottom-pdf']){
    assert.equal(await page.locator(selector).first().evaluate(el=>getComputedStyle(el).fontSize),'17px','Action label follows Untertexte (px)');
   }
   // Comprehensive typography coverage: every visible text node must map to
   // one of the seven Admin sizes, and Systemschrift must reach the node.
   const typographyAudit=await page.evaluate(()=>{
    const original=JSON.parse(JSON.stringify(NICSettings.current));
    const preview=JSON.parse(JSON.stringify(original));
    Object.assign(preview.layout,{font:'system',bodySize:21,subtextSize:25,
      hintSize:13,h1:40,h2:29,h3:23,h4:17});
    NICSettings.apply(preview);
    const sizes=new Set(['21px','25px','13px','40px','29px','23px','17px']);
    const failures=[],fontFailures=[];
    let examined=0;
    const bodyMappedTexts=[...document.querySelectorAll('.nic-body-font-text')]
      .filter(el=>el.textContent.trim()==='Weitere Finanzierung berücksichtigen')
      .map(el=>getComputedStyle(el).fontSize);
    const skip=new Set(['SCRIPT','STYLE','NOSCRIPT','TEMPLATE','OPTION','SVG','PATH','TITLE']);
    for(const el of document.querySelectorAll('.app *')){
     if(skip.has(el.tagName)||el.closest('svg')||el.closest('.nic-admin-open'))continue;
     if(!Array.from(el.childNodes).some(n=>n.nodeType===3&&n.textContent.trim()))continue;
     const ownText=Array.from(el.childNodes).filter(n=>n.nodeType===3).map(n=>n.textContent).join('').trim();
     if(!ownText||/^[+−×↓↑✓✔→←✕❮❯]$/.test(ownText))continue;
     const cs=getComputedStyle(el),box=el.getBoundingClientRect();
     if(cs.display==='none'||cs.visibility==='hidden'||!box.width||!box.height)continue;
     examined++;
     const info={text:ownText.slice(0,55),tag:el.tagName,id:el.id,
       cls:typeof el.className==='string'?el.className.slice(0,90):'',
       size:cs.fontSize};
     const responsiveHero=el.matches('.hero.nic-responsive-header>h1');
     const reducedReset=el.matches('.nic-clear-reno')&&
       Math.abs(parseFloat(cs.fontSize)-parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nic-body-font-size'))*.8)<.01&&
       Math.abs(box.width-38)<.1&&Math.abs(box.height-40)<.1;
     if(!sizes.has(cs.fontSize)&&!responsiveHero&&!reducedReset&&failures.length<35)failures.push(info);
     if(!cs.fontFamily.includes('Segoe UI')&&fontFailures.length<12)
      fontFailures.push({...info,font:cs.fontFamily});
    }
    NICSettings.apply(original);
    return {examined,failures,fontFailures,bodyMappedTexts};
   });
   if(typographyAudit.failures.length||typographyAudit.fontFailures.length)
    console.log('TYPOGRAPHY_AUDIT',width,slug,JSON.stringify(typographyAudit));
   assert(typographyAudit.examined>20,'No visible typography audited');
   assert.deepEqual(typographyAudit.failures,[],'All text must map to an Admin font size');
   assert.deepEqual(typographyAudit.fontFailures,[],'All text must follow Systemschrift');
   if(slug==='eigennutzung'){
    assert(typographyAudit.bodyMappedTexts.length>0,'The additional-financing title is tagged for Grundschriftgröße (px)');
    assert(typographyAudit.bodyMappedTexts.every(size=>size==='21px'),'The additional-financing title follows Grundschriftgröße (px): '+JSON.stringify(typographyAudit.bodyMappedTexts));
   }
   // Verify the real current Admin settings (not repository fallback values)
   // on portrait, small-phone, tablet and landscape viewports.
   const liveSnapshot=await page.evaluate(()=>{
    const saved=JSON.parse(JSON.stringify(NICSettings.current));
    const values=JSON.parse(JSON.stringify(saved));
    Object.assign(values.layout,{font:'system',bodySize:18,subtextSize:15,
      hintSize:14,h1:40,h2:25,h3:20,h4:14});
    NICSettings.apply(values);
    return saved;
   });
   try {
    for(const viewport of [
     {width:320,height:740},{width:390,height:844},
     {width:768,height:1024},{width:844,height:390}
    ]) {
     await page.setViewportSize(viewport);
     const result=await page.evaluate(()=>{
      const root=document.querySelector('.app');
      const targets=['.hero h1','.bottom-actions>.bottom-primary',
        '.bottom-actions>.bottom-pdf','.bottom-actions>.bottom-save'];
      const elements=targets.map(q=>root.querySelector(q)).filter(Boolean);
      const boxes=elements.map(el=>{
       const r=el.getBoundingClientRect();return {name:el.className||el.tagName,
        left:r.left,right:r.right,width:r.width};
      });
      const font=getComputedStyle(document.body).fontFamily;
      const sample=document.querySelector('.app .sub,.app .subtitle,.app .section-subtitle');
      const subSize=sample?getComputedStyle(sample).fontSize:null;
      return {pageWidth:document.documentElement.scrollWidth,viewport:innerWidth,
       bodyFont:font,subSize,boxes};
     });
     assert(result.bodyFont.includes('Segoe UI'),'Systemschrift active: '+JSON.stringify(result));
     if(result.subSize)assert.equal(result.subSize,'15px','Admin Untertexte stay at 15px');
     assert(result.pageWidth<=viewport.width+1,
       'No horizontal overflow with actual Admin font sizes: '+slug+' '+JSON.stringify({viewport,result}));
     assert(result.boxes.every(x=>x.left>=-1&&x.right<=viewport.width+1),
       'All primary controls stay visible: '+slug+' '+JSON.stringify({viewport,result}));
    }
   } finally {
    await page.evaluate(saved=>NICSettings.apply(saved),liveSnapshot);
    await page.setViewportSize({width,height:900});
   }
   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1?[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.width&&r.right>innerWidth+1}).map(e=>({tag:e.tagName,id:e.id,c:e.className,w:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).slice(0,12):[]);
   assert.deepEqual(overflow,[],'No horizontal page overflow');
   assert.equal(await page.locator('.mini').first().evaluate(e=>getComputedStyle(e).fontSize),'12px');
   const sub=page.locator('.sub,.subtitle,.card>h2+p:not(.mini)').first();if(await sub.count())assert.equal(await sub.evaluate(e=>getComputedStyle(e).fontSize),await page.evaluate(()=>NICSettings.current.layout.subtextSize+'px'));
   // Verify the user's current Admin values as a separate live preview:
   // Systemschrift and Untertexte=25px, without changing stored defaults.
   if(['eigennutzung','fix-flip'].includes(slug)){
    const savedForPreview=await page.evaluate(()=>{
     const original=JSON.parse(JSON.stringify(NICSettings.current));
     const preview=JSON.parse(JSON.stringify(original));
     preview.layout.font='system';preview.layout.subtextSize=25;
     NICSettings.apply(preview);
     return original;
    });
    const actual=await page.evaluate(()=>{
     const card=[...document.querySelectorAll('section,.card')].find(el=>el.querySelector('h2')?.textContent.trim()==='Wo geht das Geld hin?'&&el.querySelector('.cost-row'));
     const leafText=[...card.querySelectorAll('.cost-row *')].filter(el=>el.children.length===0&&el.textContent.trim()&&getComputedStyle(el).display!=='none');
     const total=[...card.querySelectorAll('*')].find(el=>el.children.length===0&&el.textContent.trim()==='Gesamt');
     return {textSizes:leafText.map(el=>getComputedStyle(el).fontSize),
       fonts:leafText.map(el=>getComputedStyle(el).fontFamily),
       totalSize:total&&getComputedStyle(total).fontSize,
       bodyFont:getComputedStyle(document.body).fontFamily};
    });
    assert(actual.textSizes.length>=7&&actual.textSizes.every(x=>x==='25px'),
      'User Admin Untertexte=25px applies to all cost labels and values: '+JSON.stringify(actual));
    assert.equal(actual.totalSize,'25px','User Admin Untertexte=25px applies to Gesamt');
    assert(actual.bodyFont.includes('Segoe UI')&&actual.fonts.every(x=>x.includes('Segoe UI')),
      'Systemschrift must be inherited by all cost texts: '+JSON.stringify(actual));
    await page.evaluate(original=>NICSettings.apply(original),savedForPreview);
   }
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
