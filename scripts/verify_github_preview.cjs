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
    const pageKey=await page.locator('html').getAttribute('data-nic-page');
    const contentKey=slug===''?'welcome':pageKey;
    const header=legacySettings.content[contentKey];
    assert(header,'Admin content configuration exists for '+slug);
    assert.equal((await page.locator('#heroTitle').textContent()).replace(/\u00ad/g,''),header.headerTitle,'Configured header title: '+slug);
    assert.equal((await page.locator('#heroText').textContent()).replace(/\u00ad/g,''),header.headerDescription,'Configured header description: '+slug);
    const currentId=(await page.locator('html').getAttribute('data-calculator'));
    const portrait=width===390;
    const calculatorIds=['budget','own','rent','flip','finance'];
    const isHomepage=slug==='';
    if(isHomepage){
     const home=page.locator('#nic-home-intro .nic-home-options > .deal-type-option[data-calculator="own"]');
     assert.equal((await home.locator('strong').textContent()).trim(),'Eigenheim berechnen','Home title matches the dropdown');
     assert.equal((await home.locator('small').textContent()).trim(),'Immobilie kaufen und selbst nutzen','Home keeps its original description');
     const titles=await page.locator('#nic-home-intro .nic-home-options>a').evaluateAll(links=>{
      const options=new Map([...document.getElementById('nicMobileCalculatorSelect').options].map(option=>[option.value,option.textContent]));
      return links.map(link=>{
       const title=link.querySelector('strong'),range=document.createRange();
       range.selectNodeContents(title);
       const rect=range.getBoundingClientRect(),button=link.getBoundingClientRect();
       return {text:title.textContent,expected:options.get(link.dataset.calculator||'settlement'),fits:range.getClientRects().length===1&&rect.left>=button.left&&rect.right<=button.right};
      });
     });
     assert.equal(titles.length,6);
     for(const {text,expected,fits} of titles){assert.equal(text,expected);assert(fits,'One-line homepage title fits: '+text);}
     assert.equal(await home.locator('.nic-calculator-title-line').count(),0,'Home must not inherit two-line calculator titles');
    }else if(calculatorIds.includes(currentId)){
     const cards=page.locator('.deal-type-card .deal-type-row > .deal-type-option:not([hidden])');
     const count=await cards.count();
     assert(count>=1,'Calculator tile navigation remains in DOM');
     if(portrait){
      assert.equal(count,6,'All six calculator destinations are visible');
      const boxes=await cards.evaluateAll(tiles=>tiles.map(tile=>{
       const r=tile.getBoundingClientRect();
       return {x:r.x,y:r.y,width:r.width};
      }));
      for(let i=0;i<boxes.length;i+=2){
       assert(Math.abs(boxes[i].y-boxes[i+1].y)<1&&boxes[i].x<boxes[i+1].x,'Each portrait row has two tiles');
       assert(Math.abs(boxes[i].width-boxes[i+1].width)<1,'Portrait tile columns are equal');
       if(i)assert(boxes[i].y>boxes[i-2].y,'Portrait tile rows follow reading order');
      }
     }

     for(let i=0;i<count;i++){
      const card=cards.nth(i);
      assert.equal(await card.locator('strong > .nic-calculator-title-line').count(),2,'Every calculator title has exactly two lines: '+slug+' tile '+i);
      assert.equal(await card.locator('small').evaluate(el=>getComputedStyle(el).display),'none','Calculator tile descriptions hidden: '+slug+' tile '+i);
     }
    }
    const globalShell=page.locator('.app>.hero>.nic-global-dropdown-shell');
    assert(await globalShell.isVisible(),'Dropdown remains in header: '+slug);
    assert(await globalShell.locator('#nicMobileCalculatorTrigger').isVisible(),'Dropdown trigger visible: '+slug);
    assert.equal(await page.locator('.app>.hero>.deal-type-card').count(),0,'Calculator tiles never inside hero: '+slug);
    assert.equal(await page.locator('.app>main.section>.deal-type-card').count(),1,'Single calculator tile bar stays in content: '+slug);
    if(portrait&&!isHomepage){
     if(calculatorIds.includes(currentId)||currentId==='settlement')assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),currentId,'Current calculator selected: '+slug);
    }
    const positioning=await page.evaluate(()=>{
     const shell=document.querySelector('.app>.hero>.nic-global-dropdown-shell').getBoundingClientRect();
     const title=document.getElementById('heroTitle').getBoundingClientRect();
     return {center:shell.left+shell.width/2,heroCenter:(document.querySelector('.app>.hero').getBoundingClientRect().left+document.querySelector('.app>.hero').getBoundingClientRect().right)/2,bottom:shell.bottom,top:title.top,titleVisible:title.height>0};
    });
    assert(Math.abs(positioning.center-positioning.heroCenter)<2,'Dropdown centered: '+slug);
    if(positioning.titleVisible)assert(positioning.bottom<=positioning.top+2,'Dropdown above heading: '+slug);
    assert.equal(await page.locator('.deal-type-card').count(),1,'Exactly one calculator tile menu: '+slug);
    if(currentId==='finance'){
     const labels=page.locator('#nicFinanceModule .field label');
     assert(await labels.count()>0,'Finance labels present');
     const loan=page.locator('#nicFinanceModule [data-finance-id="loan"]');
     const loanField=loan.locator('..').locator('..');
     assert(!((await loanField.locator('label').textContent()).includes('(€)')),'Currency removed from caption');
     assert.equal((await loan.locator('..').locator('.unit').textContent()).trim(),'€','Currency inside input wrapper');
     const unitSize=await loan.locator('..').locator('.unit').evaluate(el=>({actual:getComputedStyle(el).fontSize,expected:getComputedStyle(document.documentElement).getPropertyValue('--nic-hint-font-size').trim()}));
     assert.equal(unitSize.actual,unitSize.expected,'Currency uses hint typography');
     assert.equal(await loanField.locator('label').evaluate(el=>getComputedStyle(el).fontSize),layout.bodySize+'px','Loan caption uses shared body typography');

     for(const label of await labels.all()){
      assert.equal(await label.evaluate(el=>getComputedStyle(el).justifyContent),'flex-start','Finance caption and unit align left');
     }
    }
    if(['own','flip'].includes(currentId)){
     const alignment=await page.locator('.nic-property-aligned-field').evaluateAll(fields=>fields.filter(el=>el.getBoundingClientRect().height).map(el=>{
      const label=el.querySelector(':scope > label'),control=el.querySelector(':scope > .input-wrap,:scope > .metric-box');
      return {label:label?.textContent.trim(),row:el.getBoundingClientRect().top,top:control?.getBoundingClientRect().top};
     }));
     assert(alignment.length>=4,'All four property fields found: '+JSON.stringify(alignment));
     for(let i=0;i<alignment.length;i++)for(let j=i+1;j<alignment.length;j++)if(Math.abs(alignment[i].row-alignment[j].row)<1){
      assert(Math.abs(alignment[i].top-alignment[j].top)<1,'Property inputs align: '+JSON.stringify([alignment[i],alignment[j]]));
     }
    }
    assert.equal(await page.locator('.nic-logo-link').getAttribute('href'),'http://localhost/fixflip-kalkulator/','Logo stays in preview');
    const localLinks=await page.locator('a[href]').evaluateAll(links=>links.map(a=>a.href).filter(u=>u.startsWith(location.origin)));
    assert(localLinks.every(u=>new URL(u).pathname.startsWith('/fixflip-kalkulator/')&&!new URL(u).pathname.startsWith('/fixflip-kalkulator/fixflip-kalkulator/')),'Links remain inside preview: '+slug);
   }
   // The homepage and six-tile calculator bar have distinct saved visibility rules.
   const screen=width===390?'mobile':'desktop';
   await page.goto('http://localhost/fixflip-kalkulator/',{waitUntil:'networkidle'});
   await page.evaluate(screen=>{
    const settings=JSON.parse(JSON.stringify(window.NICSettings.current));
    settings.navigationVisibility.home[screen].budget=false;
    settings.navigationVisibility.calculator[screen].budget=true;
    settings.navigationVisibility.dropdownHome[screen].dropdown=false;
    settings.navigationVisibility.dropdownOther[screen].dropdown=true;
    window.NICSettings.apply(settings);
   },screen);
   assert.equal(await page.locator('#nic-home-intro [data-calculator="budget"]').evaluate(el=>el.hidden),true,'Homepage tile independently hidden: '+screen);
   assert.equal(await page.locator('.nic-global-dropdown-shell').isVisible(),false,'Homepage dropdown independently hidden: '+screen);
   const remaining=await page.locator('#nic-home-intro .nic-home-planning .nic-home-options').evaluate(row=>{
    const tile=row.querySelector('.deal-type-option:not([hidden])');
    return {row:row.getBoundingClientRect().width,tile:tile?.getBoundingClientRect().width};
   });
   assert(remaining.tile>=remaining.row-2,'Remaining homepage tile fills freed width: '+screen);
   await page.goto('http://localhost/fixflip-kalkulator/budget/',{waitUntil:'networkidle'});
   await page.evaluate(screen=>{
    const settings=JSON.parse(JSON.stringify(window.NICSettings.current));
    settings.navigationVisibility.home[screen].budget=false;
    settings.navigationVisibility.calculator[screen].budget=true;
    settings.navigationVisibility.calculator[screen].flip=false;
    settings.navigationVisibility.dropdownHome[screen].dropdown=false;
    settings.navigationVisibility.dropdownOther[screen].dropdown=true;
    window.NICSettings.apply(settings);
   },screen);
   assert.equal(await page.locator('.deal-type-card .deal-type-option[data-calculator="budget"]').evaluate(el=>el.hidden),false,'Calculator budget tile independent of homepage: '+screen);
   assert.equal(await page.locator('.deal-type-card .deal-type-option[data-calculator="flip"]').evaluate(el=>el.hidden),true,'Calculator flip hidden independently: '+screen);
   if(screen==='desktop'){
    assert(await page.locator('.app>main.section>.deal-type-card').isVisible(),'Six-button bar stays visible with one hidden entry: '+screen);
    assert.equal(await page.locator('.deal-type-card .deal-type-row > .deal-type-option:not([hidden])').count(),5,'Other five calculator buttons remain after one is disabled: '+screen);
   }
   assert.equal(await page.locator('#nicMobileCalculatorOptions [data-value="flip"]').evaluate(el=>el.hidden),false,'Dropdown keeps Flip available despite hidden calculator bar tile: '+screen);
   assert(await page.locator('#nicMobileCalculatorTrigger').isVisible(),'Other-pages dropdown remains enabled: '+screen);
   assert.equal(await page.locator('.deal-type-card a[href*="immobilien-abc"]').count(),0,'Six-tile bar never links to Immobilien ABC: '+screen);
   assert.equal(await page.locator('#nicMobileCalculatorSelect option[value="own"]').textContent(),'Eigenheim berechnen','Dropdown own option renamed: '+screen);
   // Hiding all menu buttons must not disable any calculator or its underlying
   // radio controls. The calculator route and forms remain usable from a direct URL.
   const beforeControls=await page.locator('.deal-type-card input').count();
   await page.evaluate(screen=>{
    const config=JSON.parse(JSON.stringify(window.NICSettings.current));
    for(const section of ['home','calculator'])
     for(const key of ['budget','own','rent','flip','finance','settlement'])
      config.navigationVisibility[section][screen][key]=false;
    window.NICSettings.apply(config);
    window.NICCalculatorNavigation.select('own',true);
   },screen);
   await page.waitForFunction(()=>window.NICCalculators?.active==='own');
   assert.equal(await page.locator('.deal-type-card input').count(),beforeControls,'Menu visibility cannot remove working calculator controls: '+screen);
   assert.equal(await page.locator('html').getAttribute('data-calculator'),'own','Hidden Eigenheim menu still opens its calculator: '+screen);
   assert(await page.locator('.app>main.section').isVisible(),'Hidden menus do not remove calculator pages: '+screen);

   // A homepage tile navigates inside the same document. It must not carry
   // an oversized homepage hero into a mobile portrait calculator header.
   if(width===390){
    for(const [key,slug] of [['budget','budget'],['own','eigennutzung'],['rent','vermietung'],['flip','fix-flip'],['finance','finanzierungsrechner']]){
     await page.goto('http://localhost/fixflip-kalkulator/',{waitUntil:'networkidle'});
     await page.locator('#nic-home-intro a[data-calculator="'+key+'"]').click();
     await page.waitForURL('**/fixflip-kalkulator/'+slug+'/');
     await page.waitForFunction(k=>document.documentElement.dataset.calculator===k,key);
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     const fromHome=await page.locator('.app>.hero').evaluate(el=>el.getBoundingClientRect().height);
     await page.goto('http://localhost/fixflip-kalkulator/'+slug+'/',{waitUntil:'networkidle'});
     await page.waitForFunction(k=>document.documentElement.dataset.calculator===k,key);
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     const direct=await page.locator('.app>.hero').evaluate(el=>el.getBoundingClientRect().height);
     assert(Math.abs(fromHome-direct)<=3,'Hero height changed after homepage button: '+key+' '+JSON.stringify({fromHome,direct}));
     assert(fromHome<400,'Mobile portrait header enlarged into image panel after homepage button: '+key+' '+fromHome);
     const afterScroll=await page.evaluate(async()=>{
      const hero=document.querySelector('.app>.hero');
      scrollTo(0,500);
      window.NICHeader.refresh();
      await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
      return hero.getBoundingClientRect().height;
     });
     assert(Math.abs(afterScroll-direct)<=1,'Scrolling must not enlarge the mobile header: '+key);
    }
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
   // End-to-end: change the REAL admin checkbox, let its save finish, then
   // reload another calculator URL. Previous tests changed settings directly in JS
   // and missed the admin event/save path altogether.
   await page.locator('.admin-menu-toggle').click();
   await page.locator('#tab-layout').click();
   const checkboxSizes=await page.locator('#nicNavigationVisibilityFields input[type="checkbox"]').evaluateAll(nodes=>nodes.map(el=>{
    const box=el.getBoundingClientRect(),style=getComputedStyle(el);
    return {id:el.id,w:box.width,h:box.height,cssW:parseFloat(style.width),cssH:parseFloat(style.height)};
   }));
   assert.equal(checkboxSizes.length,28,'All 28 independent navigation checkboxes present: '+screen);
   assert(checkboxSizes.every(box=>box.cssW===20&&box.cssH===20),'Admin checkbox CSS size remains 20x20: '+screen+' '+JSON.stringify(checkboxSizes));
   assert(checkboxSizes.every(box=>box.w<=21&&box.h<=21),'Admin checkboxes never enlarge to button size: '+screen+' '+JSON.stringify(checkboxSizes));
   const visibilityBox=page.locator('#nic-navigation-calculator-'+screen+'-flip');
   assert.equal(await visibilityBox.isChecked(),true,'Calculator flip initially enabled in Admin: '+screen);
   await visibilityBox.uncheck();
   await page.waitForFunction(s=>window.NICSettings.current.navigationVisibility.calculator[s].flip===false,screen);
   await page.locator('#saveState').getByText('Lokal gespeichert').waitFor({timeout:20000});
   await page.goto('http://localhost/fixflip-kalkulator/budget/',{waitUntil:'networkidle'});
   await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady);
   const bar=page.locator('.deal-type-card .deal-type-row');
   assert.equal(await bar.locator('[data-calculator="flip"]').evaluate(e=>e.hidden),true,'Admin disabled only Flip after reload: '+screen);
   for(const key of ['budget','own','rent','finance','settlement']){
    assert.equal(await bar.locator('[data-calculator="'+key+'"]').evaluate(e=>e.hidden),false,'Admin retained '+key+' after reload: '+screen);
   }
   assert.equal(await page.locator('.deal-type-card').evaluate(e=>e.hidden),false,'One disabled checkbox cannot hide parent bar: '+screen);
   if(screen==='desktop'){
    assert(await page.locator('.app>main.section>.deal-type-card').isVisible(),'Actual six-button bar remains visible after Admin checkbox: '+screen);
    assert.equal(await bar.locator('.deal-type-option:visible').count(),5,'Exactly five calculator buttons are visibly rendered after Admin checkbox: '+screen);
    assert.equal(await bar.locator('[data-calculator="flip"]').isVisible(),false,'Only disabled Flip is visually hidden: '+screen);
   }
   assert.equal(await page.locator('#nicMobileCalculatorSelect option[value="flip"]').isEnabled(),true,'Dropdown independent from tile checkbox: '+screen);
   await page.goto('http://localhost/fixflip-kalkulator/admin.html',{waitUntil:'networkidle'});
   await page.locator('#nicAdminContent[data-ready="true"]').waitFor({timeout:20000});
   await page.locator('.admin-menu-toggle').click();
   await page.locator('#tab-layout').click();
   assert.equal(await page.locator('#nic-navigation-calculator-'+screen+'-flip').isChecked(),false,'Checkbox remains disabled after reload: '+screen);
   await page.locator('#nic-navigation-calculator-'+screen+'-flip').check();
   await page.waitForFunction(s=>window.NICSettings.current.navigationVisibility.calculator[s].flip===true,screen);
   await page.locator('#saveState').getByText('Lokal gespeichert').waitFor({timeout:20000});
   // Use the real button handler without Playwright's moving-element stability wait.
   await page.locator('.nic-admin-back').evaluate(button=>button.click());
   await page.waitForURL('http://localhost/fixflip-kalkulator/');
   await page.locator('.app > main.section').waitFor({state:'visible',timeout:15000});
   await page.waitForFunction(()=>document.documentElement.dataset.nicPage==='website',null,{timeout:15000});
   assert.equal(page.url(),'http://localhost/fixflip-kalkulator/','Admin back returns to the exact preview homepage');
   if(width===390){
    await page.goto('http://localhost/fixflip-kalkulator/budget/',{waitUntil:'networkidle'});
    await page.locator('#nicMobileCalculatorTrigger').click();
     await page.locator('#nicMobileCalculatorOptions [data-value="finance"]').click();
    await page.waitForURL('**/fixflip-kalkulator/finanzierungsrechner/');
    assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'finance','Dropdown switches to finance');
    assert.equal(await page.locator('#heroTitle').innerText(),legacySettings.content.finance.headerTitle);
    await page.goBack({waitUntil:'networkidle'});
    assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'budget','Browser back restores budget');
    const options=await page.locator('#nicMobileCalculatorSelect option:not([disabled])').evaluateAll(nodes=>nodes.map(node=>({key:node.value,label:node.textContent.trim()})));
    assert.deepEqual(options.map(o=>o.key),['budget','own','rent','flip','finance','settlement'],'Exactly five calculators followed by settlement');
    assert.equal(options[5].label,'Nebenkosten abrechnen','Final option has the agreed wording');
    await page.locator('#nicMobileCalculatorTrigger').click();
     await page.locator('#nicMobileCalculatorOptions [data-value="settlement"]').click();
    await page.waitForURL('**/fixflip-kalkulator/nebenkostenabrechnung/');
    assert.equal(await page.locator('html').getAttribute('data-calculator'),'settlement','Settlement content route activated');
    assert.equal((await page.locator('.nic-mobile-calculator-current-text').textContent()).trim(),'Nebenkosten abrechnen','Dropdown follows internal navigation');
    await page.goBack({waitUntil:'networkidle'});
    assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),'budget','Back from settlement restores calculator');
    assert.equal((await page.locator('.nic-mobile-calculator-current-text').textContent()).trim(),'Dein Budget berechnen','Dropdown follows browser back');
    // Standalone information pages do not contain calculator forms; their
    // selector must open the complete target document, not switch an empty shell.
    await page.goto('http://localhost/fixflip-kalkulator/ueber-uns/',{waitUntil:'networkidle'});
    assert(await page.locator('#nicMobileCalculatorTrigger').isVisible(),'Standalone about page has a visible picker');
    await page.locator('#nicMobileCalculatorTrigger').click();
     await page.locator('#nicMobileCalculatorOptions [data-value="finance"]').click();
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
    await page.locator('.app>main.section>.deal-type-card').waitFor({state:'attached'});
    assert(await page.locator('.app>.hero>.nic-global-dropdown-shell #nicMobileCalculatorTrigger').isVisible(),'Landscape retains the shared header dropdown');
    assert.equal(await page.locator('.app>.hero>.deal-type-card').count(),0,'Landscape calculator tiles stay outside the header');
    assert.equal(await page.locator('.app>main.section>.deal-type-card').count(),1,'Same calculator menu restored to main in landscape');
    assert(await originalMenu.evaluate(el=>el===document.querySelector('.app>main.section>.deal-type-card')),'Menu node is reused rather than replaced');
    assert.equal(await page.locator('#heroTitle').innerText(),legacySettings.content.budget.headerTitle,'Rotation retains the published budget heading');
    await page.setViewportSize({width:390,height:900});
    await page.locator('.app>.hero>.nic-global-dropdown-shell #nicMobileCalculatorTrigger').waitFor({state:'visible',timeout:10000});
    assert(await originalMenu.evaluate(el=>el===document.querySelector('.app>main.section>.deal-type-card')),'Menu stays in content area in portrait');
    for(const narrowWidth of [320,375,390,430]){
     await page.setViewportSize({width:narrowWidth,height:900});
     const dimensions=await page.locator('.app>.hero>.nic-global-dropdown-shell').evaluate(el=>{
       const green=el.querySelector('#nicMobileCalculatorTrigger').getBoundingClientRect();
       const shell=el.getBoundingClientRect(),header=el.closest('.hero').getBoundingClientRect();
       const menu=document.querySelector('.app>main.section>.deal-type-card');
       return {greenRight:green.right,limit:shell.right,headerHeight:header.height,
        menuBelowHero:menu.getBoundingClientRect().top>=header.bottom-2,
        scrollWidth:document.documentElement.scrollWidth,screenWidth:document.documentElement.clientWidth};
      });
      assert(dimensions.greenRight<=dimensions.limit+1,'Dropdown fits header at '+narrowWidth+'px');
      assert(dimensions.menuBelowHero,'Six calculator tiles below hero at '+narrowWidth+'px');
      assert(dimensions.scrollWidth<=dimensions.screenWidth+1,'No horizontal overflow at '+narrowWidth+'px');
      assert(dimensions.headerHeight>0,'Header height retained at '+narrowWidth+'px');
    }
   }
   await page.goto('http://localhost/fixflip-kalkulator/nebenkostenabrechnung/',{waitUntil:'networkidle'});
   const content = page.locator('#nicContentView');
   const settlement = content.locator(':scope > [data-settlement]');
   const manual = content.locator('[data-nic-settlement-action="manual"]');
   const upload = content.locator('[data-nic-settlement-action="upload"]');
   const exit = settlement.getByRole('button',{name:'Abrechnung verlassen'});
   await manual.waitFor({state:'visible'});
   assert.equal(await settlement.count(),0,'Settlement starts on its information page');
   await manual.click();
   await page.waitForURL('**/nebenkostenabrechnung/?modus=manuell');
   await settlement.locator('summary').filter({hasText:'1. Objekt'}).click();
   assert.equal(await settlement.locator('#entryModeState').isVisible(),false,'Manual entry omits the upload hint');
   assert.equal(await settlement.locator('iframe, .footer').count(),0,'Settlement uses the shared calculator shell');
   await settlement.locator('#wizardYear').fill('2025');
   await settlement.getByRole('button',{name:'Entwurf lokal speichern'}).click();
   await exit.click();
   await page.waitForURL('**/nebenkostenabrechnung/');
   await manual.waitFor({state:'visible'});
   assert.equal(await settlement.count(),0,'Leaving manual entry returns to the start page');
   await upload.click();
   await page.waitForURL('**/nebenkostenabrechnung/?modus=upload');
   await settlement.locator('#wegUploadButton').waitFor({state:'visible'});
   await exit.click();
   await page.waitForURL('**/nebenkostenabrechnung/');
   await upload.waitFor({state:'visible'});
   assert.equal(await settlement.count(),0,'Leaving upload returns to the start page');
   await manual.click();
   await page.waitForURL('**/nebenkostenabrechnung/?modus=manuell');
   await settlement.locator('summary').filter({hasText:'1. Objekt'}).click();
   assert.equal(await settlement.locator('#wizardYear').inputValue(),'2025','Leaving and reopening keeps the saved draft');
   await settlement.getByRole('button',{name:'1. Kontakte'}).click();
   const contacts = settlement.locator('#kontakte');
   await contacts.getByLabel('Kontaktrolle').selectOption('Mieter/in');
   await contacts.getByLabel('Vorname').fill('Mara');
   await contacts.getByLabel('Nachname / Firmenname').fill('Test');
   await contacts.getByLabel('Mietbeginn').fill('2025-01-01');
   await contacts.getByLabel('Mietende').fill('2026-10-31');
   await contacts.getByLabel('Aktiv').uncheck();
   const periods = contacts.locator('.tenant-rent-period');
   for (const [i, validFrom, coldRent, operatingCosts, heatingCosts] of [
    [0,'2025-01-01','690.50','120','80'], [1,'2025-07-01','720','135','90']
   ]) {
    if(i) await contacts.getByRole('button',{name:'Mietanpassung hinzufügen'}).click();
    const period = periods.nth(i);
    await period.getByLabel('Gültig ab').fill(validFrom);
    await period.getByLabel('Kaltmiete (€)').fill(coldRent);
    await period.getByLabel('Betriebskosten (€)').fill(operatingCosts);
    await period.getByLabel('Heizkosten (€)').fill(heatingCosts);
   }
   await contacts.getByRole('button',{name:'Kontakt übernehmen'}).click();
   await page.reload();
   await settlement.getByRole('button',{name:'1. Kontakte'}).click();
   const edit = contacts.getByRole('button',{name:'Mara · Test · Mieter/in bearbeiten'});
   await edit.click();
   assert.equal(await contacts.getByLabel('Mietbeginn').inputValue(),'2025-01-01');
   assert.equal(await contacts.getByLabel('Mietende').inputValue(),'2026-10-31');
   assert.equal(await contacts.getByLabel('Aktiv').isChecked(),false);
   assert.equal(await periods.count(),2);
   assert.equal(await periods.nth(1).getByLabel('Gültig ab').inputValue(),'2025-07-01');
   assert.equal(await periods.nth(0).getByLabel('Kaltmiete (€)').inputValue(),'690.50');
   assert.equal(await periods.nth(1).getByLabel('Betriebskosten (€)').inputValue(),'135');
   assert.equal(await periods.nth(1).getByLabel('Heizkosten (€)').inputValue(),'90');
   await contacts.getByLabel('Vorname').fill('Maria');
   await contacts.getByRole('button',{name:'Änderungen speichern'}).click();
   assert.equal(await edit.count(),0);
   assert.equal(await contacts.getByRole('button',{name:'Maria · Test · Mieter/in bearbeiten'}).count(),1);
   assert.equal(await contacts.getByText('Kontakt gespeichert.').count(),0);
   await contacts.getByRole('button',{name:'Kontakt hinzufügen'}).click();
   await contacts.getByLabel('Kontaktrolle').selectOption('Vermieter/in');
   await contacts.getByLabel('Vorname').fill('Zweiter Kontakt');
   await contacts.getByRole('button',{name:'Kontakt übernehmen'}).click();
   const removeContact = contacts.getByRole('button',{name:'Maria Test löschen'});
   page.once('dialog',dialog=>dialog.dismiss());
   await removeContact.click();
   assert.equal(await removeContact.count(),1,'Cancel leaves the contact intact');
   page.once('dialog',dialog=>dialog.accept());
   await removeContact.click();
   assert.equal(await removeContact.count(),0,'Confirm removes the contact');
   await page.reload();
   await settlement.getByRole('button',{name:'1. Kontakte'}).click();
   assert.equal(await removeContact.count(),0,'Deleted contact stays deleted after reload');
   assert.equal(await contacts.getByRole('button',{name:'Zweiter Kontakt · Vermieter/in bearbeiten'}).count(),1,'Other contacts stay available');
   await exit.click();
   await page.waitForURL('**/nebenkostenabrechnung/');
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
