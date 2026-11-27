const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:900},hasTouch:width<=700}),errors=[];
  page.on('pageerror',e=>{const details=e.stack||e.message;errors.push(details);console.error('BROWSER PAGE ERROR '+width+' '+page.url()+'\\n'+details);});
  let releaseInitialSettings,settingsRequestCount=0,resolveSettingsRequested;
  const settingsArrival=new Promise(resolve=>{releaseInitialSettings=resolve;});
  const settingsRequested=new Promise(resolve=>{resolveSettingsRequested=resolve;});
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
   // The STRATO API is cross-origin in this local browser test. Simulate its
   // credentialed CORS response and preflight, otherwise the browser silently
   // rejects the response and the application falls back to bundled 16px settings.
   const cors={'access-control-allow-origin':'http://localhost','access-control-allow-credentials':'true','access-control-allow-methods':'GET, POST, OPTIONS','access-control-allow-headers':'X-NIC-Request, X-NIC-CSRF, Content-Type'};
   if(u.hostname!=='localhost'&&route.request().method()==='OPTIONS')return route.fulfill({status:204,headers:cors});
   if(u.hostname!=='localhost'&&route.request().resourceType()==='script')return route.fulfill({contentType:'application/javascript',body:'',headers:cors});
   if(u.hostname!=='localhost'&&u.searchParams.get('r')==='settings'){
    settingsRequestCount++;
    resolveSettingsRequested();
    await settingsArrival;
    const settings=JSON.parse(JSON.stringify(require('../assets/site-settings.json')));
    settings.layout.bodySize=20;settings.layout.h1=30;
    settings.company.email='layout-test@example.com';
    return route.fulfill({status:200,json:{user:null,settings,csrf:'test'},headers:cors});
   }
   if(u.hostname!=='localhost')return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'},headers:cors});
   let name=u.pathname;if(name.endsWith('/'))name+='index.html';
   const file=path.join(process.cwd(),'_site',name);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'text/plain'});
  });
  await page.addInitScript(()=>{
   if(!['/','/preise/','/warum-immocheck/','/nebenkostenabrechnung/'].includes(location.pathname))return;
   localStorage.setItem('ff_dealType','own');
   window.homeHeaderWrites=[];
   new MutationObserver(records=>{
    for(const record of records)if(record.target.id==='heroTitle'){
     for(const node of record.addedNodes)if(node.textContent.trim())window.homeHeaderWrites.push(node.textContent.trim());
    }
   }).observe(document,{childList:true,subtree:true});
  });
  await page.goto('http://localhost/',{waitUntil:'domcontentloaded'});
  await Promise.race([settingsRequested,new Promise((_,reject)=>setTimeout(()=>reject(new Error('The browser did not request cloud settings before the first reveal')),10000))]);
  assert.equal(await page.locator('.app').evaluate(el=>getComputedStyle(el).visibility),'hidden','App must not display the bundled intermediate layout while published settings are pending');
  releaseInitialSettings();
  await page.locator('.app').waitFor({state:'visible'});
  await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady==='ready');
  const initialState=await page.evaluate(()=>({bodySize:NICSettings.current?.layout.bodySize,ready:NICSettings.ready,published:NICSettings.published?.layout.bodySize,remoteEnabled:NICAccess?.enabled,bootstrap:!!document.getElementById('nic-published-settings'),state:document.documentElement.dataset.nicLayoutReady}));
  assert.equal(initialState.bodySize,20,'Published typography must be applied before reveal: '+JSON.stringify({initialState,settingsRequestCount}));
  assert.equal(await page.locator('#nicFooterEmail').textContent(),'layout-test@example.com','Footer must be populated before reveal');
  const firstVisible=await page.locator('.app').evaluate(app=>['.nic-brand-bar','.hero','.footer-note'].map(selector=>{const r=app.querySelector(selector).getBoundingClientRect();return {height:r.height,top:r.top};}));
  await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
  await page.waitForFunction(()=>document.body.dataset.calculator==='home');
  assert.deepEqual(await page.locator('.app').evaluate(app=>['.nic-brand-bar','.hero','.footer-note'].map(selector=>{const r=app.querySelector(selector).getBoundingClientRect();return {height:r.height,top:r.top};})),firstVisible,'Header/footer areas must remain stable after the first visible layout');
  const homeHeading=await page.locator('#heroTitle').innerText();
  assert((await page.evaluate(()=>window.homeHeaderWrites)).every(title=>title===homeHeading),'Calculator startup must never overwrite the homepage heading');
  assert.equal(await page.evaluate(()=>NICCalculators.active),'home','Homepage uses the shared route controller');
  assert.equal(await page.locator('script:not([src])').evaluateAll(nodes=>nodes.some(node=>node.textContent.includes('Explicit calculator URLs keep their'))),false,'Superseded calculator startup is removed from the final page');
  assert.equal(await page.locator('#nic-home-intro').evaluate(el=>el.parentElement.matches('.app>main.section')),true,'Homepage uses the shared content container');
  assert.equal(new URL(page.url()).pathname,'/','Bare domain must stay on the homepage');
  assert.equal(await page.locator('#nic-home-intro .nic-home-group').count(),3);
  const homeLayout=await page.locator('#nic-home-intro').evaluate(el=>{
   const rect=selector=>{const r=el.querySelector(selector).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,bottom:r.bottom};};
   return {settlement:rect('.nic-home-settlement'),planning:rect('.nic-home-planning'),property:rect('.nic-home-property'),buttons:[...el.querySelectorAll('.nic-home-options>.deal-type-option')].map(button=>{const r=button.getBoundingClientRect();return {x:r.x,y:r.y,bottom:r.bottom};})};
  });
  if(width>700){
   assert(homeLayout.settlement.x<homeLayout.planning.x,'Settlement must be on the left');
   assert(Math.abs(homeLayout.settlement.y-homeLayout.planning.y)<2,'Top groups must share one row');
   assert(homeLayout.property.y>=homeLayout.planning.bottom,'Property group must be below the top row');
  }else{
   assert(homeLayout.planning.y>=homeLayout.settlement.bottom,'Mobile groups must stack');
   assert(homeLayout.property.y>=homeLayout.planning.bottom,'Mobile property group must stack');
   homeLayout.buttons.slice(1).forEach((button,i)=>assert(button.y>=homeLayout.buttons[i].bottom-1,'Every mobile button must be below its predecessor'));
  }

  assert(await page.locator('#nic-home-intro .nic-home-copy').isVisible());
  assert.equal(await page.locator('[data-home-title]').innerText(),require('../assets/site-settings.json').content.welcome.title);
  const settlement=page.locator('[data-home-settlement]');
  assert.equal(await settlement.getAttribute('href'),'/nebenkostenabrechnung/');
  assert.equal(await settlement.locator('.nic-menu-icon').count(),1);
  assert.equal(await page.locator('#nicHomeSettlementTitle').innerText(),'Mieterabrechnung');
  assert.equal(await settlement.locator('strong').innerText(),'Nebenkosten abrechnen');
  assert.equal(await settlement.locator('small').innerText(),'Betriebskosten erfassen und versenden');
  assert((await settlement.locator('small').innerText()).length>0);
  assert.equal(homeHeading,require('../assets/site-settings.json').meta.website.homeTitle);
  if(width>700){
   const startTile=page.locator('#nic-home-intro .nic-home-options>.deal-type-option').first();
   await startTile.hover();
   await page.waitForTimeout(180);
   const feedback=await startTile.evaluate(el=>({filter:getComputedStyle(el).filter,shadow:getComputedStyle(el).boxShadow}));
   assert(feedback.filter.includes('brightness(0.94)')&&feedback.shadow!=='none','Homepage buttons show desktop hover feedback: '+JSON.stringify(feedback));
  }
  for(const key of ['budget','finance','own','rent','flip']){
   await page.locator('#nic-home-intro a[data-calculator="'+key+'"]').click();
   await page.waitForFunction(k=>document.body.dataset.calculator===k,key);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   if(['budget','own','flip'].includes(key))assert.equal(await page.evaluate(()=>currentDealType()),key,'Homepage selection retains actual calculation mode after header measurement');
   assert.equal(await page.locator('#nic-home-intro').isVisible(),false);
   await page.goBack();
   await page.waitForFunction(()=>document.body.dataset.calculator==='home');
   assert(await page.locator('#nic-home-intro').isVisible());
   assert.equal(await page.locator('[data-home-settlement] .nic-menu-icon').count(),1,'Settlement symbol survives return to homepage');
   assert.equal(await page.locator('#heroTitle').innerText(),homeHeading);
  }
  await page.reload();
  await page.waitForFunction(()=>document.body.dataset.calculator==='home');
  assert.equal(new URL(page.url()).pathname,'/','Remembered calculator must not redirect home');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Homepage overflows horizontally');
  await page.goto('http://localhost/budget/');
  await page.waitForFunction(()=>window.NICCalculatorNavigation&&window.NICSettings.current);
  await page.waitForFunction(()=>window.NICCalculators?.active==='budget'&&document.body.dataset.calculator==='budget');
  assert.equal(await page.locator('.deal-type-card .nic-abc-term').count(),0,'Immobilien ABC must not turn navigation terms into help buttons');
  await page.waitForFunction(()=>window.NICReferenceInterest?.rate===4.09);
  if(width<=700){
   try{await page.locator('#nicMobileCalculatorSelect').waitFor({state:'visible',timeout:10000});}
   catch(error){
    const diagnostic=await page.evaluate(()=>{
     const menu=document.querySelector('.deal-type-card'),picker=document.getElementById('nicMobileCalculatorSelect');
     return {route:location.pathname,active:window.NICCalculators?.active,htmlCalculator:document.documentElement.dataset.calculator,
      bodyCalculator:document.body.dataset.calculator,bodyClasses:document.body.className,
      menuParent:menu?.parentElement?.className,menuClass:menu?.className,menuHidden:menu?.hidden,
      menuDisplay:menu?getComputedStyle(menu).display:null,pickerFound:!!picker,pickerDisplay:picker?getComputedStyle(picker).display:null,
      compactDisplay:picker?.parentElement?getComputedStyle(picker.parentElement).display:null,media:matchMedia('(max-width:700px) and (orientation:portrait)').matches};
    });
    throw new Error('Portrait menu not visible after route initialization: '+JSON.stringify(diagnostic)+'; '+error.message);
   }
  }
  assert.equal(await page.locator('.deal-type-card').count(),1,'Exactly one shared calculator menu exists on the calculator route');
  if(width<=700){
   const picker=page.locator('#nicMobileCalculatorSelect');
   assert.deepEqual(await picker.locator('option:not([disabled])').evaluateAll(nodes=>nodes.map(node=>node.value)),['budget','own','rent','flip','finance','settlement'],'Mieter-Abrechnung is the final selectable mobile option');
   const corners=await picker.evaluate(el=>{const style=getComputedStyle(el);return [style.borderTopLeftRadius,style.borderTopRightRadius,style.borderBottomRightRadius,style.borderBottomLeftRadius].map(parseFloat);});
   assert(corners.every(value=>value>0),'All four dropdown corners inherit a positive layout radius');
  }
  assert.deepEqual(errors,[], 'Page initialization must complete without JavaScript errors');
  const origin=await page.evaluate(()=>performance.timeOrigin);
  assert.equal(await page.locator('script[src*="calculator-finance"]').count(),0,'Finance must use the shared controller bundle');
  assert.equal(await page.evaluate(()=>typeof window.NICFinanceModule),'undefined','No second finance bootstrap');
  for(const key of ['finance','own','rent','flip','budget','finance']){
   if(width<=700){
    const picker=page.locator('#nicMobileCalculatorSelect');
    assert(await picker.isVisible(),'Portrait dropdown must be visible before changing calculator');
    await picker.selectOption(key);
   }else{
    await page.locator(`.deal-type-option[data-calculator="${key}"]`).click();
   }
   await page.waitForFunction(k=>document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   if(['budget','own','flip'].includes(key))assert.equal(await page.evaluate(()=>currentDealType()),key,'Menu selection retains actual calculation mode after header measurement');
   if(width<=700)assert.equal(await page.locator('#nicMobileCalculatorSelect').inputValue(),key,'Portrait dropdown reflects active calculator');
   const stickyGap=await page.locator('.nic-actions-above-footer').evaluate(el=>({position:getComputedStyle(el).position,bottom:getComputedStyle(el).bottom}));
   assert.equal(stickyGap.position,width<=700?'fixed':'sticky','Calculator action row uses the expected viewport positioning');
   assert.equal(stickyGap.bottom,'5px','Sticky calculator action row stays five pixels above the viewport edge');
   assert.equal(await page.evaluate(()=>performance.timeOrigin),origin,'calculator changes must keep same document');
   assert.equal(await page.locator('.nic-tile-active').count(),1);
   await page.waitForFunction(()=>[...document.querySelectorAll('.app>main input[placeholder],.app>main textarea[placeholder]')].every(field=>field.closest('#ownBudgetTransferCard')));
   if(key==='finance')await page.waitForFunction(()=>{const host=document.getElementById('nicFinanceModule');return !host.shadowRoot&&!host.querySelector('input[placeholder],textarea[placeholder]')});

   const {headerTitle,headerDescription}=await page.evaluate(k=>NICSettings.current.content[k],key);
   assert.equal((await page.locator('#heroTitle').innerText()).replace(/\u00ad/g,''),headerTitle,'Calculator uses the published heading: '+key);
   assert.equal((await page.locator('#heroText').innerText()).replace(/\u00ad/g,''),headerDescription,'Calculator uses the published description: '+key);
   if(key==='own'){
    assert(await page.locator('#nicOwnIntro').isVisible(),'Eigenheim explanation must appear on internal navigation');
    assert((await page.locator('#nicOwnIntro').textContent()).includes('Hausgeld'),'House and apartment running costs explained');
    assert.equal(await page.locator('#result #kpiEquity').isVisible(),false,'Project-specific KPI is hidden in Eigenheim');
    assert.equal(await page.locator('#result #kpiMaxBuy').isVisible(),false,'Project purchase-price KPI is hidden in Eigenheim');
   }else assert.equal(await page.locator('#nicOwnIntro').count(),0,'Eigenheim explanation must leave other routes clean');
   if(key==='flip'){
    const kpiTerm=page.locator('#kpiProfit .name .nic-abc-term');
    await kpiTerm.waitFor({state:'visible',timeout:10000});
    assert.equal(await page.locator('#kpiProfit > .info-btn').isVisible(),false,'Old KPI info icon is hidden after rich content migration');
    const oldLocation=await page.evaluate(()=>({path:location.pathname,time:performance.timeOrigin}));
    await kpiTerm.click();
    const popup=page.locator('.nic-abc-context-dialog');
    await popup.waitFor({state:'visible'});
    const content=await popup.innerText();
    assert(content.includes('Einfach gesagt')&&content.includes('Gut zu wissen'),'Original Fix & Flip explanation paragraphs must be preserved');
    await popup.locator('.nic-abc-context-close').click();
    assert.deepEqual(await page.evaluate(()=>({path:location.pathname,time:performance.timeOrigin})),oldLocation,'KPI contextual help never changes page');
    assert.equal(await page.locator('#ownUseKpis').isVisible(),false,'Eigenheim-only result KPIs are hidden in Fix & Flip');
    assert.equal(await page.locator('#ownBudgetTransferCard').isVisible(),false,'Household budget transfer is hidden in Fix & Flip');
   }
   if(width>700){
    const grids=await page.evaluate(()=>[...document.querySelectorAll('.app>main .kpis,.app>main .budget-result-grid,#nicFinanceModule .grid:has(> .kpi)')].filter(grid=>{const r=grid.getBoundingClientRect();return r.width>0&&r.height>0}).map(grid=>{
     const cells=[...grid.children].flatMap(child=>child.classList.contains('kpi-triple')?[...child.children]:[child]).filter(cell=>!cell.classList.contains('own-budget-transfer')&&!cell.matches('#ownBudgetTransferCard')).filter(cell=>{const r=cell.getBoundingClientRect();return r.width>0&&r.height>0});
     const rows=new Map();for(const cell of cells){const top=Math.round(cell.getBoundingClientRect().top);rows.set(top,(rows.get(top)||0)+1);}
     return {id:grid.id,className:grid.className,width:grid.getBoundingClientRect().width,columns:getComputedStyle(grid).gridTemplateColumns,cells:cells.map(cell=>({text:cell.innerText.trim().slice(0,55),column:getComputedStyle(cell).gridColumn,row:getComputedStyle(cell).gridRow,style:cell.getAttribute('style')})),rows:[...rows.values()]};
    }));
    for(const grid of grids){assert(grid.rows.every(count=>count<=4),'Desktop KPI rows contain no more than four cards: '+JSON.stringify({key,grid}));if(grid.rows.length>1)assert(grid.rows.every(count=>count>1),'Desktop KPI layout avoids a lonely final card: '+JSON.stringify({key,grid}));}
   }

   if(key==='finance')assert(await page.locator('#nicFinanceModule [data-finance-id="loan"]').isVisible());
   if(key==='rent'){
    const term=page.locator('.nic-abc-term', {hasText:'Nettokaltmiete pro Monat'}).first();
    await term.waitFor({state:'visible',timeout:10000});
    const before=await page.evaluate(()=>({url:location.pathname,origin:performance.timeOrigin,inputs:document.querySelector('#rentInterest')?.value}));
    await term.click();
    const popup=page.locator('.nic-abc-context-dialog');
    await popup.waitFor({state:'visible'});
    const popupText=await popup.innerText();
    assert(popupText.includes('Einfach gesagt')&&popupText.includes('Gut zu wissen'),'Original rental explanation sections survive ABC integration');
    assert(popupText.includes('Nettokaltmiete'),'Context displays relevant ABC definition');
    await popup.locator('.nic-abc-context-close').click();
    assert.equal(await page.locator('.nic-abc-context-dialog').count(),0,'Info closes without navigation');
    assert.deepEqual(await page.evaluate(()=>({url:location.pathname,origin:performance.timeOrigin,inputs:document.querySelector('#rentInterest')?.value})),before,'ABC info preserves route, document and calculator values');
    const factor=page.locator('#rentFactorKpi .nic-abc-term');
    await factor.waitFor({state:'visible'});
    assert.equal(await page.locator('#rentFactorKpi .rent-kpi-info').isVisible(),false,'Original Kaufpreisfaktor badge is replaced by contextual title');
    await factor.click();
    const factorText=await popup.innerText();
    assert(factorText.includes('Einfach gesagt')&&factorText.includes('Gut zu wissen'),'Complete Kaufpreisfaktor help is still available');
    await popup.locator('.nic-abc-context-close').click();
    const remainingIcons=await page.locator('.app>main .info-btn[data-info]:visible, .app>main .rent-info-dot[data-info]:visible').count();
    assert.equal(remainingIcons,0,'Migrated calculator information icons must not remain visible in the rental view');
    const spacing=await page.evaluate(()=>['rentCashflowKpi','rentFactorKpi'].map(id=>{const card=document.getElementById(id);const info=card?.querySelector('.rent-kpi-info'),badge=card?.querySelector('.rent-kpi-rating');return {infoHidden:!!info?.hidden,hasTerm:!!card?.querySelector('.nic-abc-term'),infoBottom:info?.getBoundingClientRect().bottom,badgeTop:badge?.getBoundingClientRect().top};}));
    for(const pair of spacing){
     if(pair.infoHidden)assert(pair.hasTerm,'New inline glossary term replaces hidden KPI information icon');
     else if(pair.badgeTop!=null)assert(pair.infoBottom!=null&&pair.badgeTop>=pair.infoBottom+4,'Legacy badge has visible spacing below its info icon');
    }
   }
   if(key==='finance'){
    const geometry=await page.locator('#nicFinanceModule').evaluate(host=>{
     const cards=[...host.querySelectorAll(':scope > .card')].map(el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};});
     const menu=document.querySelector('.deal-type-card').getBoundingClientRect();
     const grids=[...host.querySelectorAll('.grid:has(> .kpi)')].map(grid=>[...grid.children].map(el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};}));
     return {inMain:host.parentElement.matches('.app>main.section'),menu:{left:menu.left,right:menu.right},cards,grids,hasShadow:!!host.shadowRoot};
    });
    assert(geometry.inMain&&!geometry.hasShadow,'Finance must use the shared main DOM and frame');
    assert(geometry.cards.length>=2,'Financing content must include separate cards');
    if(width>700)assert(geometry.cards.every(card=>Math.abs(card.left-geometry.menu.left)<2&&Math.abs(card.right-geometry.menu.right)<2),'Finance cards must align with the shared calculator frame');
    else assert(geometry.cards.every(card=>card.right>card.left&&card.left>=0&&card.right<=width+1),'Financing cards must stay within the portrait viewport');
    for(let i=1;i<geometry.cards.length;i++)assert(geometry.cards[i].top>=geometry.cards[i-1].bottom-1,'Finance content cards must not overlap');
    for(const grid of geometry.grids){for(let i=0;i<grid.length;i++)for(let j=i+1;j<grid.length;j++){const a=grid[i],b=grid[j];const overlap=a.left<b.right-1&&a.right>b.left+1&&a.top<b.bottom-1&&a.bottom>b.top+1;assert(!overlap,'Finance result boxes must not overlap');}}
   }
  }
  await page.evaluate(async()=>{
   const root=document.getElementById('nicFinanceModule'),input=root.querySelector('[data-finance-id="interest"]');if(root.shadowRoot)throw Error('Finance must use the shared document DOM');
   for(const id of ['interest','budgetInterest','rentInterest'])if(Number(document.getElementById(id).value)!==4.09)throw Error('Shared reference missing: '+id);
   if(Number(input.value)!==4.09)throw Error('Finance must share the reference rate');
   input.value='5.25';input.dispatchEvent(new Event('input',{bubbles:true}));
   await initializeReferenceInterest();
   if(Number(input.value)!==5.25)throw Error('Manual finance rate overwritten');
  });
  await page.goBack();await page.waitForFunction(()=>!document.body.classList.contains('nic-finance-active'));
  await page.goForward();await page.waitForFunction(()=>document.body.classList.contains('nic-finance-active'));
  await page.reload();await page.waitForSelector('#nicFinanceModule [data-finance-id="loan"]');
  assert.equal(await page.locator('.nic-tile-active').getAttribute('data-calculator'),'finance');
  await page.evaluate(()=>{const root=document.getElementById('nicFinanceModule');root.querySelector('[data-finance-id="newCalc"]').click();if(Number(root.querySelector('[data-finance-id="interest"]').value)!==4.09)throw Error('Finance reset must use shared reference');});
  await page.evaluate(()=>{
   const root=document.getElementById('nicFinanceModule');
   if(root.shadowRoot)throw Error('Finance must not create a shadow root');
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
  await page.waitForFunction(()=>!!window.NICAdminUI,null,{timeout:15000});
  // Real native-admin cascade: headings must fit inside their own grid cells.
  for(const viewport of [{width:320,height:740},{width:390,height:844},{width:844,height:390},{width:768,height:1024},{width:1440,height:900}]){
   await page.setViewportSize(viewport);
   await page.evaluate(()=>{NICAdminUI.select('users');document.documentElement.style.setProperty('--nic-body-font-size','20px');document.documentElement.style.setProperty('--nic-subtext-font-size','18px');document.documentElement.style.setProperty('--nic-hint-font-size','18px');});
   const matrix=await page.locator('#nicAdminContent .content-section-controls').evaluate(root=>{
    const header=root.querySelector('.content-section-header');const bounds=header.getBoundingClientRect();
    return {headers:[...header.children].map(el=>{const r=el.getBoundingClientRect(),range=document.createRange();range.selectNodeContents(el);return {left:r.left,right:r.right,lines:[...range.getClientRects()].map(x=>({left:x.left,right:x.right}))}}),left:bounds.left,right:bounds.right,
     labels:[...root.querySelectorAll('.content-section-row>span')].map(el=>({hyphens:getComputedStyle(el).hyphens,wordBreak:getComputedStyle(el).wordBreak})),checkboxes:[...root.querySelectorAll('input')].map(el=>el.getBoundingClientRect().width)};
   });
   for(const cell of matrix.headers)assert(cell.lines.every(r=>r.left>=cell.left-.5&&r.right<=cell.right+.5),'Admin heading overlaps another column at '+viewport.width+': '+JSON.stringify(matrix));
   assert(matrix.labels.every(el=>el.hyphens==='auto'&&el.wordBreak==='normal'),'German content labels use word/syllable wrapping');
   assert(matrix.checkboxes.every(w=>w<=20),'Compact checkboxes retained');
  }
  await page.setViewportSize({width,height:900});
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
  await page.goto('http://localhost/');
  await page.waitForFunction(()=>NICSettings.ready&&document.querySelector('.hero.nic-fixed-header'));
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const standardHeader=await page.locator('.app>.hero').evaluate(el=>({height:el.getBoundingClientRect().height,background:getComputedStyle(el).backgroundImage,font:getComputedStyle(el.querySelector('h1')).fontFamily,size:getComputedStyle(el.querySelector('h1')).fontSize,logo:document.querySelector('.brand-logo').getBoundingClientRect().width}));
  // Menu/content links use the same loaded application as calculator tiles.
  const sharedOrigin=await page.evaluate(()=>performance.timeOrigin);
  const headerNode=await page.locator('.app>.hero').elementHandle();
  let subpageHeaderHeight=null;
  for(const slug of ['immobilien-abc','preise','warum-immocheck']){
   const menu=page.locator('.nic-brand-bar .nic-menu-toggle');
   if(await menu.isVisible())await menu.click();
   await page.locator('[data-nic-site-nav] a[href="/'+slug+'/"]').click();
   await page.waitForURL('http://localhost/'+slug+'/');
   await page.locator(slug==='nebenkostenabrechnung'?'#nicContentView':'#nicContentView').waitFor({state:'visible'});
   if(slug==='immobilien-abc'){
    await page.locator('#nicContentView .nic-abc-search').waitFor({state:'visible'});
    await page.locator('#nicContentView .nic-abc-entry').first().waitFor({state:'visible'});
    const measure=await page.locator('#nicContentView').evaluate(card=>{
     const search=card.querySelector('.nic-abc-search'),area=card.querySelector('.nic-abc-toolbar'),rows=card.querySelector('.nic-abc-list');
     const rect=el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,width:r.width};};
     return {search:rect(search),toolbar:rect(area),list:rect(rows),placeholder:search.placeholder,html:search.outerHTML,style:search.getAttribute('style'),computedWidth:getComputedStyle(search).width,abcReady:!!window.NICABC,stylesheets:[...document.styleSheets].map(x=>x.href).filter(Boolean).filter(h=>h.includes('immobilien'))};
    });
    assert.equal(measure.placeholder,'Begriff suchen, z. B. Grundschuld …');
    assert(Math.abs(measure.search.left-measure.list.left)<4&&Math.abs(measure.search.right-measure.list.right)<4,
      'ABC search must span available list/content width: '+JSON.stringify(measure));
   }
   assert.equal(await page.evaluate(()=>performance.timeOrigin),sharedOrigin,'Information menu must retain the document');
   assert(await headerNode.evaluate(el=>el===document.querySelector('.app>.hero')),'Header DOM must be retained');
   assert(await page.locator(slug==='nebenkostenabrechnung'?'#nicContentView':'#nicContentView').evaluate(el=>el.parentElement.matches('.app>main.section')),'Information uses the calculator main container');
   const h=await page.locator('.app>.hero').evaluate(el=>el.getBoundingClientRect().height);
   if(width<=700){
    assert(await page.locator('#nicMobileCalculatorSelect').isVisible(),'Shared portrait selector on '+slug);
    assert(h>0&&await page.locator('#nicMobileCalculatorTrigger').isVisible(),'Subpage retains usable mobile dropdown: '+slug);
    if(subpageHeaderHeight===null)subpageHeaderHeight=h;
    else assert(Math.abs(h-subpageHeaderHeight)<=1,'Information subpages retain equal header height: '+slug);
   }else assert(h>0&&await page.locator('.nic-global-dropdown-shell').isVisible(),'Desktop content retains centered dropdown: '+slug);
  }
  await page.goBack();await page.waitForURL('http://localhost/preise/');
  assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content.prices.headerTitle);
  await page.goForward();await page.waitForURL('http://localhost/warum-immocheck/');
  assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content.why.headerTitle);
  await page.goBack();await page.goBack();await page.goBack();await page.waitForURL('http://localhost/');
  assert.equal(await page.evaluate(()=>performance.timeOrigin),sharedOrigin,'Browser history returns home within the shared application');
  await page.locator('[data-home-settlement]').click();
  await page.waitForURL('http://localhost/nebenkostenabrechnung/');
  const settlementModule=page.locator('#nicContentView > [data-settlement]');
  await settlementModule.locator('#wegUploadButton').waitFor({state:'visible'});
  assert.equal(await settlementModule.locator('iframe, header, .footer').count(),0,'Settlement uses the outer header and footer');
  assert.equal(await page.evaluate(()=>performance.timeOrigin),sharedOrigin,'Settlement opens in the shared application');
  await page.goBack();
  await page.waitForURL('http://localhost/');
  for(const routeName of ['preise','warum-immocheck','nebenkostenabrechnung','ueber-uns','kontakt']){
   await page.goto('http://localhost/'+routeName+'/');
   await page.locator(routeName==='nebenkostenabrechnung'?'#nicContentView':'.nic-content-card').waitFor({state:'visible'});
   if(['preise','warum-immocheck','nebenkostenabrechnung'].includes(routeName)){
    const key=({'preise':'prices','warum-immocheck':'why','nebenkostenabrechnung':'settlement'})[routeName];
    await page.waitForFunction(k=>window.NICCalculators?.active===k,key);
    assert((await page.evaluate(()=>window.homeHeaderWrites)).every(title=>title===require('../assets/site-settings.json').content[key].headerTitle),'Legacy initialization must not overwrite the information header');
    assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content[key].headerTitle,'Direct content startup must preserve its heading');
    assert.equal(await page.evaluate(()=>NICCalculators.active),key,'Direct content URL must use the shared controller');
    assert(await page.locator('.deal-type-card').count(),'Direct content route retains calculator controls for shared navigation');
    assert(await page.locator('.app>.hero').isVisible(),'Standard image header missing on '+routeName);
    assert(await page.locator('.app>.hero h1').isVisible(),'Standard heading missing on '+routeName);
    assert.equal(await page.locator('.nic-content-card h1').count(),0,'Content title must not be duplicated');
    if(key==='settlement'){
     const module=page.locator('#nicContentView > [data-settlement]');
     await module.locator('#startManual').click();
     await module.locator('#wizardYear').fill('2025');
     await module.locator('[data-step="4"]').click();
     await module.locator('#showPreview').click();
     await module.locator('#printPreview').waitFor({state:'visible'});
     await module.locator('#closePreview').click();
     await module.locator('#printPreview').waitFor({state:'hidden'});
    }
    assert.equal(await page.locator('link[href*="calculator-typography"]').count(),1,'Shared typography missing on '+routeName);
    await page.waitForFunction(()=>NICSettings.ready&&document.querySelector('.hero.nic-fixed-header'));
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const header=await page.locator('.app>.hero').evaluate(el=>({height:el.getBoundingClientRect().height,background:getComputedStyle(el).backgroundImage,font:getComputedStyle(el.querySelector('h1')).fontFamily,size:getComputedStyle(el.querySelector('h1')).fontSize,logo:document.querySelector('.brand-logo').getBoundingClientRect().width}));
    for(const key of ['background','font','size','logo'])assert.equal(header[key],standardHeader[key],'Standard header '+key+' differs on '+routeName);
    if(width<=700){
     assert(await page.locator('#nicMobileCalculatorSelect').isVisible(),'Shared portrait selector on direct '+routeName);
     assert(header.height>0&&await page.locator('#nicMobileCalculatorTrigger').isVisible(),'Direct content route retains mobile dropdown: '+routeName);
     assert.equal(await page.locator('.app>.hero>.nic-global-dropdown-shell').count(),1,'Direct information page uses the shared header dropdown: '+routeName);
     assert.equal(await page.locator('.app>.hero>.deal-type-card').count(),0,'Calculator tiles stay outside the header: '+routeName);
    }else assert(header.height>0&&await page.locator('.nic-global-dropdown-shell').isVisible(),'Direct content retains centered desktop dropdown: '+routeName);

   }else {
    const key=({'ueber-uns':'about','kontakt':'contact'})[routeName];
    const heroDiagnostic=await page.evaluate(()=>{const el=document.querySelector('.app>.hero');if(!el)return {exists:false,body:document.body.className,app:!!document.querySelector('.app')};const css=getComputedStyle(el),rect=el.getBoundingClientRect();return {exists:true,display:css.display,visibility:css.visibility,opacity:css.opacity,width:rect.width,height:rect.height,html:document.documentElement.outerHTML.slice(0,400),body:document.body.className,inline:el.getAttribute('style'),hidden:el.hidden};});
    assert(await page.locator('.app>.hero').isVisible(),'Shared image header missing on '+routeName+' '+JSON.stringify(heroDiagnostic));
    assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content[key].headerTitle,'Content header title differs on '+routeName);
    assert.equal(await page.locator('.nic-content-card h1').count(),0,'Content page must not duplicate header title');
   }
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
  await page.unroute('**/backend-config.json');
  await page.route('**/api/index.php?r=settings',route=>route.fulfill({status:503,json:{error:'offline fixture'}}));
  await page.goto('http://localhost/finanzierungsrechner/');
  await page.locator('.app').waitFor({state:'visible'});
  await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady==='fallback');
  await page.waitForFunction(()=>window.NICCalculators?.active==='finance');
  const financeModule=page.locator('#nicFinanceModule');
  await financeModule.waitFor({state:'visible'});
  assert.equal(await page.locator('body').getAttribute('data-calculator'),'finance','Direct finance route must be selected when published settings are unavailable');
  assert(await financeModule.locator('h2').count()>0,'Direct finance module content must be present when published settings are unavailable');
  assert.equal(await financeModule.locator('[data-finance-id="loan"]').inputValue(),'300000','Direct finance keeps the default loan input when published settings are unavailable');
  if(width<=700)await page.locator('#nicMobileCalculatorSelect').selectOption('budget');
  else await page.locator('.deal-type-card .deal-type-option[data-calculator="budget"]').click();
  await page.waitForFunction(()=>window.NICCalculators?.active==='budget'&&document.body.dataset.calculator==='budget'&&window.NICSettings.ready);
  await page.locator('#budgetNetIncome').waitFor({state:'visible'});
  await page.locator('#budgetNetIncome').fill('4000');
  const assumptionsToggle=page.locator('#budgetAssumptionsToggle');
  if(await assumptionsToggle.getAttribute('aria-expanded')!=='true')await assumptionsToggle.click();
  await page.locator('#budgetInterest').fill('6.25');
  const budgetValues=await page.evaluate(()=>{
   const amount=id=>Number((document.getElementById(id).innerText||'').replace(/[^\d]/g,''));
   const hint=document.getElementById('budgetFinanceTransferHint');
   return {loan:amount('budgetLoan'),monthlyRate:amount('budgetRate'),hintSize:getComputedStyle(hint).fontSize,hintSetting:getComputedStyle(document.documentElement).getPropertyValue('--nic-hint-font-size').trim()};
  });
  assert(budgetValues.loan>0&&budgetValues.monthlyRate>0,'Budget example must produce a rate and loan amount');
  assert.equal(budgetValues.hintSize,budgetValues.hintSetting,'Budget transfer subtitle follows central hint text (px) setting');
  const transferButton=page.locator('#budgetFinanceTransfer');
  if(width>700){
   await transferButton.hover();
   await page.waitForTimeout(180);
   const feedback=await transferButton.evaluate(el=>({filter:getComputedStyle(el).filter,shadow:getComputedStyle(el).boxShadow}));
   assert(feedback.filter.includes('brightness(0.94)')&&feedback.shadow!=='none','Budget transfer button shows desktop hover feedback: '+JSON.stringify(feedback));
   await transferButton.click();
  }else{
   await transferButton.scrollIntoViewIfNeeded();
   const box=await transferButton.boundingBox();
   await page.touchscreen.tap(box.x+box.width/2,box.y+box.height/2);
  }
  await page.waitForFunction(()=>window.NICCalculators?.active==='finance'&&document.body.dataset.calculator==='finance');
  await page.locator('#nicFinanceModule [data-finance-id="loan"]').waitFor({state:'visible'});
  await page.waitForFunction(()=>window.scrollY===0,'',{timeout:5000});
  const transferred=await page.evaluate(()=>{
   const root=document.getElementById('nicFinanceModule'),value=id=>root.querySelector('[data-finance-id="'+id+'"]').value,notice=root.querySelector('[data-finance-id="budgetTransferNotice"]');
   return {loan:Number(value('loan')),interest:Number(value('interest')),repay:Number(value('repay')),extra:Number(value('extra')),years:Number(value('years')),monthlyRate:Number(root.querySelector('[data-finance-id="rate"]').textContent.replace(/[^\d]/g,'')),noticeVisible:!!notice&&!notice.hidden&&getComputedStyle(notice).display!=='none',noticePosition:notice?getComputedStyle(notice).position:null,noticeTop:notice?.getBoundingClientRect().top,scrollY:window.scrollY};
  });
  assert.equal(transferred.loan,budgetValues.loan,'Transferred loan equals the displayed rounded budget amount: '+JSON.stringify({budgetValues,transferred}));
  assert.equal(transferred.interest,6.25,'Budget interest transfers on first activation');
  assert.equal(transferred.repay,1.5,'Budget repayment transfers on first activation');
  assert.equal(transferred.extra,0,'Transferred special repayment starts at zero');
  assert.equal(transferred.years,10,'Transferred observation period starts at ten years');
  assert.equal(transferred.monthlyRate,budgetValues.monthlyRate,'Transferred monthly rate remains fixed');
  assert(transferred.noticeVisible&&transferred.noticePosition==='fixed'&&transferred.noticeTop>=0,'Transfer confirmation remains visible at the top of financing: '+JSON.stringify(transferred));
  assert.equal(transferred.scrollY,0,'Financing opens at the top of the page');
  assert.deepEqual(errors,[]);
  console.log('Unified navigation and budget transfer passed',width,'same document, first activation, fixed rate, visible confirmation');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
