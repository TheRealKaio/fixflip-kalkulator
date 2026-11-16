// Exercise the real project subpath, without allowing production backend calls.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1440,390]){
   const layout=JSON.parse(fs.readFileSync('_preview/site-settings.json','utf8')).layout;
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'}),errors=[],missing=[],backend=[];
   const legacySettings=JSON.parse(fs.readFileSync('_preview/site-settings.json','utf8'));
   legacySettings.layout.bodySize=32;legacySettings.layout.h1=60;
   const legacyJSON=JSON.stringify(legacySettings);
   await page.addInitScript(({legacyJSON})=>{
    localStorage.setItem('nic_site_settings_v1',legacyJSON);
    localStorage.setItem('nic_preview_input_preservation_test','keep-inputs');
   },{legacyJSON});
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname==='neustart-immocheck.de'&&u.pathname.startsWith('/api/')){backend.push(u.href);return route.abort();}
    if(u.hostname!=='localhost')return route.abort();
    if(!u.pathname.startsWith('/fixflip-kalkulator/')){missing.push(u.pathname);return route.fulfill({status:404,body:''});}
    let name=u.pathname.slice('/fixflip-kalkulator/'.length);if(!name||name.endsWith('/'))name+='index.html';
    const file=path.join(process.cwd(),'_preview',name);
    if(!fs.existsSync(file)){missing.push(u.pathname);return route.fulfill({status:404,body:''});}
    await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp'})[path.extname(file)]||'application/octet-stream'});
   });
   for(const slug of ['','budget/','eigennutzung/','vermietung/','fix-flip/','finanzierungsrechner/','nebenkostenabrechnung/','preise/','warum-immocheck/','immobilien-abc/','ueber-uns/','kontakt/','anmelden/']){
    await page.goto('http://localhost/fixflip-kalkulator/'+slug,{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady);
    if(await page.locator('#nicConsentDialog[open]').count())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
    assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,nofollow');
    assert(new URL(page.url()).pathname.startsWith('/fixflip-kalkulator/'),'Direct route remains in project');
    assert(await page.locator('.app > main.section').isVisible(),'Shared app visible: '+slug);
    assert.equal(await page.locator('body').evaluate(e=>parseFloat(getComputedStyle(e).zoom)||1),width>=1024?.75:1,'Preview desktop density');
    assert.equal(await page.locator('body').evaluate(e=>getComputedStyle(e).fontSize),layout.bodySize+'px','Public body size');
    const heading=await page.locator('#heroTitle').evaluate(e=>({configured:getComputedStyle(document.documentElement).getPropertyValue('--nic-h1-font-size').trim(),actual:parseFloat(getComputedStyle(e).fontSize)}));
    assert.equal(heading.configured,layout.h1+'px','Public heading setting: '+width+' '+slug);
    assert(heading.actual>0&&heading.actual<=layout.h1,'Shared responsive heading limit: '+width+' '+slug);
    const currentId=(await page.locator('html').getAttribute('data-calculator'));
    const portrait=width===390;
    const calculatorIds=['budget','own','rent','flip','finance'];
    const isHomepage=slug==='';
    const chooser=page.locator('.app>.hero>.deal-type-card.nic-portrait-calculator-menu');
    if(portrait&&!isHomepage){
     assert(await chooser.isVisible(),'Portrait selector shown for '+slug);
     if(calculatorIds.includes(currentId)||currentId==='settlement')assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),currentId,'Current calculator selected: '+slug);
     else assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'','Information route must not misrepresent its active calculator: '+slug);
     const metrics=await chooser.evaluate(el=>{
      const button=el.querySelector('.nic-mobile-calculator-label'),dropdown=el.querySelector('.nic-mobile-calculator-select');
      const a=button.getBoundingClientRect(),b=dropdown.getBoundingClientRect();
      const controls=el.querySelector('.nic-mobile-calculator-controls');
      const style=getComputedStyle(controls);
      const corners=[button,dropdown].map(node=>{const css=getComputedStyle(node);return [css.borderTopLeftRadius,css.borderTopRightRadius,css.borderBottomRightRadius,css.borderBottomLeftRadius].map(parseFloat);});
      return {gap:b.left-a.right,expectedGap:parseFloat(style.columnGap),aligned:Math.abs(a.top-b.top)<1,selectRight:b.right,containerRight:el.getBoundingClientRect().right,corners};
     });
     assert(Math.abs(metrics.gap-metrics.expectedGap)<1&&metrics.aligned,'Separate rounded selector fields align with configured gap: '+slug+' '+JSON.stringify(metrics));
     const expectedCorner=await page.evaluate(()=>parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nic-menu-radius')));
     assert(metrics.corners.every(side=>side.every(value=>Math.abs(value-expectedCorner)<0.1)),'Both selector fields must use the actual published layout corner radius: '+slug+' '+JSON.stringify(metrics));
     assert.equal(await page.locator('#nicMobileCalculatorSelect').evaluate(el=>getComputedStyle(el).appearance),'none','Custom arrow and visible rounded select shape: '+slug);
     assert(metrics.selectRight<=metrics.containerRight+1,'Selector does not overflow: '+slug);
     assert.equal(await page.locator('.app>main.section>.deal-type-card').count(),0,'Original menu moved into header: '+slug);
     assert.equal(await page.locator('.deal-type-card').count(),1,'Exactly one calculator menu: '+slug);
     assert.equal(await chooser.locator('.deal-type-row').isVisible(),false,'Old cards hidden within same mobile menu');
     if(calculatorIds.includes(currentId))assert((await page.locator('#heroTitle').innerText()).startsWith('Jetzt '),'Mobile calculator heading: '+slug);
    }else{
     assert.equal(await page.locator('.nic-mobile-calculator-controls').isVisible(),false,'No compact selector on homepage/content/desktop: '+slug);
     assert.equal(await page.locator('.deal-type-card').count(),1,'No duplicate calculator menu: '+slug);
    }
    assert.equal(await page.locator('.nic-logo-link').getAttribute('href'),'http://localhost/fixflip-kalkulator/','Logo stays in preview');
    const localLinks=await page.locator('a[href]').evaluateAll(links=>links.map(a=>a.href).filter(u=>u.startsWith(location.origin)));
    assert(localLinks.every(u=>new URL(u).pathname.startsWith('/fixflip-kalkulator/')&&!new URL(u).pathname.startsWith('/fixflip-kalkulator/fixflip-kalkulator/')),'Links remain inside preview: '+slug);
   }
   // A direct admin URL must remain in the same application with the shared hero.
   await page.goto('http://localhost/fixflip-kalkulator/admin.html',{waitUntil:'networkidle'});
   await page.waitForFunction(()=>location.pathname==='/fixflip-kalkulator/'&&location.hash.startsWith('#admin'),null,{timeout:10000}).catch(async error=>{
    throw new Error('Direct admin redirect failed: '+JSON.stringify({url:page.url(),errors})+'; '+error.message);
   });
   await page.locator('#nicAdminContent[data-ready="true"]').waitFor({timeout:20000});
   assert(await page.locator('.app > .hero').isVisible(),'Admin shares the main website header');
   assert.equal(await page.locator('iframe').count(),0,'Admin is native, not a separate iframe');
   assert.equal((await page.locator('.nic-admin-back').textContent()).trim(),'← Zurück','Admin back button retains its configured label despite CSS uppercase');
   await page.locator('.nic-admin-back').click();
   await page.waitForURL('http://localhost/fixflip-kalkulator/');
   assert(await page.locator('.app > main.section').isVisible(),'Admin back returns to homepage');
   if(width===390){
    await page.goto('http://localhost/fixflip-kalkulator/budget/',{waitUntil:'networkidle'});
    await page.locator('#nicMobileCalculatorSelect').selectOption('finance');
    await page.waitForURL('**/fixflip-kalkulator/finanzierungsrechner/');
    assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'finance','Dropdown switches to finance');
    assert.match(await page.locator('#heroTitle').innerText(),/Jetzt Finanzierung & Restschuld berechnen!/);
    await page.goBack({waitUntil:'networkidle'});
    assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'budget','Browser back restores budget');
    const options=await page.locator('#nicMobileCalculatorSelect option:not([disabled])').evaluateAll(nodes=>nodes.map(node=>({key:node.value,label:node.textContent.trim()})));
    assert.deepEqual(options.map(o=>o.key),['budget','own','rent','flip','finance','settlement'],'Exactly five calculators followed by settlement');
    assert.equal(options[5].label,'Mieter-Abrechnung','Final option has the agreed wording');
    await page.locator('#nicMobileCalculatorSelect').selectOption('settlement');
    await page.waitForURL('**/fixflip-kalkulator/nebenkostenabrechnung/');
    assert.equal(await page.locator('html').getAttribute('data-calculator'),'settlement','Settlement content route activated');
    await page.goBack({waitUntil:'networkidle'});
    assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'budget','Back from settlement restores calculator');
    // Standalone information pages do not contain calculator forms; their
    // selector must open the complete target document, not switch an empty shell.
    await page.goto('http://localhost/fixflip-kalkulator/ueber-uns/',{waitUntil:'networkidle'});
    assert(await page.locator('#nicMobileCalculatorSelect').isVisible(),'Standalone about page has a visible picker');
    await page.locator('#nicMobileCalculatorSelect').selectOption('finance');
    await page.waitForURL('**/fixflip-kalkulator/finanzierungsrechner/');
    try{
     await page.locator('#nicFinanceModule [data-finance-id="loan"]').waitFor({state:'visible',timeout:15000});
     await page.waitForFunction(()=>window.NICCalculators?.active==='finance',null,{timeout:15000});
    }catch(error){
     const diagnostic=await page.evaluate(()=>({
      route:location.pathname,page:document.documentElement.dataset.nicPage,
      active:window.NICCalculators?.active,body:document.body.className,
      financeHost:!!document.getElementById('nicFinanceModule'),
      loanField:!!document.querySelector('#nicFinanceModule [data-finance-id="loan"]')
     }));
     throw new Error('Standalone picker must load the complete finance calculator: '+JSON.stringify(diagnostic)+'; '+error.message);
    }
    await page.goto('http://localhost/fixflip-kalkulator/budget/',{waitUntil:'networkidle'});
    const originalMenu=await page.locator('.deal-type-card').elementHandle();
    await page.setViewportSize({width:844,height:390});
    assert.equal(await page.locator('.app>.hero>.deal-type-card.nic-portrait-calculator-menu').isVisible(),false,'Landscape does not show portrait selector');
    assert.equal(await page.locator('.app>main.section>.deal-type-card').count(),1,'Same calculator menu restored to main in landscape');
    assert(await originalMenu.evaluate(el=>el===document.querySelector('.app>main.section>.deal-type-card')),'Menu node is reused rather than replaced');
    assert(!(await page.locator('#heroTitle').innerText()).startsWith('Jetzt '),'Landscape restores configured title');
    await page.setViewportSize({width:390,height:900});
    assert(await page.locator('.app>.hero>.deal-type-card.nic-portrait-calculator-menu').isVisible(),'Portrait selection restored on rotate');
    assert(await originalMenu.evaluate(el=>el===document.querySelector('.app>.hero>.deal-type-card')),'Same menu returns into header in portrait');
    for(const narrowWidth of [320,375,390,430]){
     await page.setViewportSize({width:narrowWidth,height:900});
     const dimensions=await page.locator('.app>.hero>.deal-type-card.nic-portrait-calculator-menu').evaluate(el=>{
      const green=el.querySelector('.nic-mobile-calculator-label').getBoundingClientRect();
      const white=el.querySelector('.nic-mobile-calculator-select').getBoundingClientRect();
      const container=el.getBoundingClientRect();
      const header=el.closest('.hero').getBoundingClientRect();
      const style=getComputedStyle(el.querySelector('.nic-mobile-calculator-controls'));
      return {gap:white.left-green.right,expectedGap:parseFloat(style.columnGap),topGap:white.top-green.top,right:white.right,limit:container.right,
       headerHeight:header.height,scrollWidth:document.documentElement.scrollWidth,screenWidth:document.documentElement.clientWidth};
     });
     assert(Math.abs(dimensions.gap-dimensions.expectedGap)<1&&Math.abs(dimensions.topGap)<1,'Aligned selector fields at '+narrowWidth+'px');
     assert(dimensions.right<=dimensions.limit+1,'Dropdown within header at '+narrowWidth+'px');
     assert(dimensions.scrollWidth<=dimensions.screenWidth+1,'No horizontal overflow at '+narrowWidth+'px');
     assert(dimensions.headerHeight>0,'Header height retained at '+narrowWidth+'px');
    }
   }
   await page.goto('http://localhost/fixflip-kalkulator/nebenkostenabrechnung/',{waitUntil:'networkidle'});
   const disclosure=page.locator('[data-nic-explanation] summary');
   if(await disclosure.isVisible())await disclosure.click();
   await page.locator('[data-nic-explanation] a[href="http://localhost/fixflip-kalkulator/vermietung/"]').click();
   await page.waitForURL('http://localhost/fixflip-kalkulator/vermietung/');
   await page.goto('http://localhost/fixflip-kalkulator/',{waitUntil:'networkidle'});
   const budget=page.locator('a[href="/fixflip-kalkulator/budget/"]').first();
   await budget.click();
   await page.waitForURL('**/fixflip-kalkulator/budget/');
   assert.equal(await page.locator('html').getAttribute('data-nic-page'),'budget');
   await page.locator('.nic-logo-link').click();await page.waitForURL('http://localhost/fixflip-kalkulator/');
   assert.equal(await page.locator('html').getAttribute('data-nic-page'),'website');
   assert.equal(await page.evaluate(()=>localStorage.getItem('nic_site_settings_v1')),legacyJSON,'Old settings are preserved');
   assert.equal(await page.evaluate(()=>localStorage.getItem('nic_preview_input_preservation_test')),'keep-inputs','Other browser data preserved');
   assert.deepEqual(errors,[],'No browser errors');
   assert.deepEqual(missing,[],'No missing or origin-root assets');
   assert.deepEqual(backend,[],'No production backend access');
   await page.close();
  }
  console.log('GitHub preview passed: project routes, assets, desktop/mobile, navigation/back and backend isolation.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
