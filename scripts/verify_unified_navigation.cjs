const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
  page.on('pageerror',e=>{const details=e.stack||e.message;errors.push(details);console.error('BROWSER PAGE ERROR '+width+' '+page.url()+'\\n'+details);});
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
   if(u.hostname!=='localhost'&&route.request().resourceType()==='script')return route.fulfill({contentType:'application/javascript',body:''});
   if(u.hostname!=='localhost')return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
   let name=u.pathname;if(name.endsWith('/'))name+='index.html';
   const file=path.join(process.cwd(),'_site',name);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'text/plain'});
  });
  await page.goto('http://localhost/budget/');
  await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
  await page.waitForFunction(()=>window.NICCalculatorNavigation&&window.NICSettings.current);
  await page.waitForFunction(()=>window.NICReferenceInterest?.rate===4.09);
  assert.deepEqual(errors,[], 'Page initialization must complete without JavaScript errors');
  const origin=await page.evaluate(()=>performance.timeOrigin);
  assert.equal(await page.locator('script[src*="calculator-finance"]').count(),0,'Finance must use the shared controller bundle');
  assert.equal(await page.evaluate(()=>typeof window.NICFinanceModule),'undefined','No second finance bootstrap');
  for(const key of ['finance','own','rent','flip','budget','finance']){
   await page.locator(`.deal-type-option[data-calculator="${key}"]`).click();
   await page.waitForFunction(k=>document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
   assert.equal(await page.evaluate(()=>performance.timeOrigin),origin,'calculator changes must keep same document');
   assert.equal(await page.locator('.nic-tile-active').count(),1);
   if(key==='finance'){assert(await page.locator('#nicFinanceModule #loan').isVisible());assert((await page.locator('#heroTitle').innerText()).replace(/\u00ad/g,'').includes('Finanzierungsrechner'));}
  }
  await page.evaluate(async()=>{
   const root=document.getElementById('nicFinanceModule').shadowRoot,input=root.getElementById('interest');
   for(const id of ['interest','budgetInterest','rentInterest'])if(Number(document.getElementById(id).value)!==4.09)throw Error('Shared reference missing: '+id);
   if(Number(input.value)!==4.09)throw Error('Finance must share the reference rate');
   input.value='5.25';input.dispatchEvent(new Event('input',{bubbles:true}));
   await initializeReferenceInterest();
   if(Number(input.value)!==5.25)throw Error('Manual finance rate overwritten');
  });
  await page.goBack();await page.waitForFunction(()=>!document.body.classList.contains('nic-finance-active'));
  await page.goForward();await page.waitForFunction(()=>document.body.classList.contains('nic-finance-active'));
  await page.reload();await page.waitForSelector('#nicFinanceModule #loan');
  assert.equal(await page.locator('.nic-tile-active').getAttribute('data-calculator'),'finance');
  await page.evaluate(()=>{const root=document.getElementById('nicFinanceModule').shadowRoot;root.getElementById('newCalc').click();if(Number(root.getElementById('interest').value)!==4.09)throw Error('Finance reset must use shared reference');});
  await page.evaluate(()=>{
   const root=document.getElementById('nicFinanceModule').shadowRoot;
   const box=root.querySelector('[data-nic-content-key]');
   if(!box)throw Error('Finance access rules missing');
   const settings=NICSettings.current;
   settings.contentSections[box.dataset.nicContentKey]={visible:false,guestAllowed:false};
   NICContentSections.apply(settings);
   if(!box.hidden||!box.inert)throw Error('Hidden finance content must stay inaccessible');
  });
  await page.route('**/backend-config.json',route=>route.fulfill({json:{enabled:false}}));
  await page.goto('http://localhost/#admin-company');
  await page.locator('#nicAdminContent #settingsForm').waitFor({state:'visible'});
  for(const viewport of width===390?[{width:390,height:844},{width:844,height:390}]:[{width:1440,height:900}]){
   await page.setViewportSize(viewport);await page.evaluate(()=>window.scrollTo(0,0));
   const toggle=page.locator('.nic-brand-bar .nic-menu-toggle');
   if(await toggle.isVisible()){
    await toggle.click();
    const geometry=await page.locator('[data-nic-site-nav]').evaluate(nav=>{
     const n=nav.getBoundingClientRect(),h=nav.closest('.nic-brand-bar').getBoundingClientRect(),a=nav.querySelector('a'),r=a.getBoundingClientRect();
     return {top:n.top,bottom:h.bottom,hit:document.elementFromPoint(r.left+r.width/2,r.top+r.height/2)?.closest('[data-nic-site-nav]')===nav};
    });
    assert(Math.abs(geometry.top-geometry.bottom)<3&&geometry.hit,'Admin header dropdown is anchored below the header and clickable: '+JSON.stringify(geometry));
    await toggle.click();
   }
   const sectionToggle=page.locator('#nicAdminContent .admin-menu-toggle');
   if(await sectionToggle.isVisible()){await sectionToggle.click();await page.locator('#nicAdminContent #tab-layout').click();assert(await page.locator('#nicAdminContent #panel-layout').isVisible());}
  }
  const toggle=page.locator('.nic-brand-bar .nic-menu-toggle');if(await toggle.isVisible())await toggle.click();
  // Check every standard legal view on desktop and mobile, not just the imprint.
  for(const legalKey of ['impressum','agbs','datenschutz','haftungsausschluss','cookie-hinweis']){
   await page.goto('http://localhost/#'+legalKey);
   await page.locator('#nicLegalPanel .nic-legal-card').waitFor({state:'visible'});
   assert.equal(await page.locator('#nicLegalPanel nav[aria-label="Rechtliche Bereiche"]').count(),0,'Duplicated legal navigation on '+legalKey);
   assert.equal(await page.locator('#nicLegalPanel').isVisible(),true,'Legal panel missing on '+legalKey);
   assert(await page.locator('.footer-legal-links a').count()>0,'Footer legal links missing on '+legalKey);
   assert.deepEqual(errors,[],'Browser errors on legal page '+legalKey);
  }
  await page.goto('http://localhost/#admin-company');
  await page.locator('#nicAdminContent #settingsForm').waitFor({state:'visible'});
  await page.locator('[data-nic-site-nav] a[href="/preise/"]').click();
  await page.waitForURL('http://localhost/preise/');
  assert(!(await page.locator('body').evaluate(el=>el.classList.contains('nic-admin-open'))),'Admin header menu navigates to the selected content page');
  // Regression-check informational routes and their real responsive header.
  for(const routeName of ['preise','warum-immocheck','nebenkostenabrechnung','ueber-uns','kontakt']){
   await page.goto('http://localhost/'+routeName+'/');
   await page.locator('.nic-content-card').waitFor({state:'visible'});
   assert(await page.locator('.nic-content-card h1').isVisible(),'Content heading missing on '+routeName);
   assert(await page.locator('.footer-legal-links a').count()>0,'Footer links missing on '+routeName);
   assert.deepEqual(errors,[],'JavaScript errors on /'+routeName+'/');
   const menuToggle=page.locator('.nic-brand-bar .nic-menu-toggle');
   if(await menuToggle.isVisible()){
    await menuToggle.click();
    assert.equal(await menuToggle.getAttribute('aria-expanded'),'true','Mobile menu did not open on '+routeName);
    assert(await page.locator('[data-nic-site-nav] a[href="/preise/"]').isVisible(),'Mobile navigation links hidden on '+routeName);
    await menuToggle.click();
    assert.equal(await menuToggle.getAttribute('aria-expanded'),'false','Mobile menu did not close on '+routeName);
   }else{
    assert(await page.locator('[data-nic-site-nav] a[href="/preise/"]').isVisible(),'Desktop navigation missing on '+routeName);
   }
  }
  assert.deepEqual(errors,[]);
  console.log('Unified navigation passed',width,'same document, all modes, history, direct finance reload');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
