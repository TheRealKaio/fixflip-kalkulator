const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
  page.on('pageerror',e=>{const details=e.stack||e.message;errors.push(details);console.error('BROWSER PAGE ERROR '+width+' '+page.url()+'\\n'+details);});
  let releaseInitialSettings,documentLoads=0;
  const settingsArrival=new Promise(resolve=>{releaseInitialSettings=resolve;});
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(route.request().resourceType()==='document')documentLoads++;
   if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
   if(u.hostname!=='localhost'&&route.request().resourceType()==='script')return route.fulfill({contentType:'application/javascript',body:''});
   if(u.hostname!=='localhost'&&u.searchParams.get('r')==='settings'&&documentLoads===1){
    await settingsArrival;
    const settings=JSON.parse(JSON.stringify(require('../assets/site-settings.json')));
    settings.layout.bodySize=20;settings.layout.h1=30;
    settings.company.email='layout-test@example.com';
    return route.fulfill({status:200,json:{user:null,settings,csrf:'test'}});
   }
   if(u.hostname!=='localhost')return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
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
  assert.equal(await page.locator('.app').evaluate(el=>getComputedStyle(el).visibility),'hidden','App must not display the bundled intermediate layout while published settings are pending');
  releaseInitialSettings();
  await page.locator('.app').waitFor({state:'visible'});
  await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady==='ready');
  assert.equal(await page.evaluate(()=>NICSettings.current.layout.bodySize),20,'Published typography must be applied before reveal');
  assert.equal(await page.locator('#nicFooterEmail').textContent(),'layout-test@example.com','Footer must be populated before reveal');
  const firstVisible=await page.locator('.app').evaluate(app=>['.nic-brand-bar','.hero','.footer-note'].map(selector=>{const r=app.querySelector(selector).getBoundingClientRect();return {height:r.height,top:r.top};}));
  await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
  await page.waitForFunction(()=>document.body.dataset.calculator==='home');
  assert.deepEqual(await page.locator('.app').evaluate(app=>['.nic-brand-bar','.hero','.footer-note'].map(selector=>{const r=app.querySelector(selector).getBoundingClientRect();return {height:r.height,top:r.top};})),firstVisible,'Header/footer areas must remain stable after the first visible layout');
  const homeHeading=await page.locator('#heroTitle').innerText();
  assert((await page.evaluate(()=>window.homeHeaderWrites)).every(title=>title===homeHeading),'Calculator startup must never overwrite the homepage heading');
  assert.equal(await page.evaluate(()=>NICCalculators.active),'home','Homepage uses the shared route controller');
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
  for(const key of ['budget','finance','own','rent','flip']){
   await page.locator('#nic-home-intro a[data-calculator="'+key+'"]').click();
   await page.waitForFunction(k=>document.body.dataset.calculator===k,key);
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
  await page.waitForFunction(()=>window.NICReferenceInterest?.rate===4.09);
  assert.deepEqual(errors,[], 'Page initialization must complete without JavaScript errors');
  const origin=await page.evaluate(()=>performance.timeOrigin);
  assert.equal(await page.locator('script[src*="calculator-finance"]').count(),0,'Finance must use the shared controller bundle');
  assert.equal(await page.evaluate(()=>typeof window.NICFinanceModule),'undefined','No second finance bootstrap');
  for(const key of ['finance','own','rent','flip','budget','finance']){
   await page.locator(`.deal-type-option[data-calculator="${key}"]`).click();
   await page.waitForFunction(k=>document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
   const stickyGap=await page.locator('.nic-actions-above-footer').evaluate(el=>({position:getComputedStyle(el).position,bottom:getComputedStyle(el).bottom}));
   assert.equal(stickyGap.position,'sticky','Calculator action row remains sticky');
   assert.equal(stickyGap.bottom,'5px','Sticky calculator action row stays five pixels above the viewport edge');
   assert.equal(await page.evaluate(()=>performance.timeOrigin),origin,'calculator changes must keep same document');
   assert.equal(await page.locator('.nic-tile-active').count(),1);
   await page.waitForFunction(()=>[...document.querySelectorAll('.app>main input[placeholder],.app>main textarea[placeholder]')].every(field=>field.closest('#ownBudgetTransferCard')));
   if(key==='finance')await page.waitForFunction(()=>{const host=document.getElementById('nicFinanceModule');return !host.shadowRoot&&!host.querySelector('input[placeholder],textarea[placeholder]')});

   if(key==='own'){
    assert.equal(await page.locator('#heroTitle').innerText(),'Kannst Du Dir Dein Eigenheim leisten?');
    assert(await page.locator('#nicOwnIntro').isVisible(),'Eigenheim explanation must appear on internal navigation');
    assert((await page.locator('#nicOwnIntro').textContent()).includes('Hausgeld'),'House and apartment running costs explained');
    assert.equal(await page.locator('#result #kpiEquity').isVisible(),false,'Project-specific KPI is hidden in Eigenheim');
    assert.equal(await page.locator('#result #kpiMaxBuy').isVisible(),false,'Project purchase-price KPI is hidden in Eigenheim');
   }else assert.equal(await page.locator('#nicOwnIntro').count(),0,'Eigenheim explanation must leave other routes clean');
   if(key==='flip'){
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

   if(key==='finance'){assert(await page.locator('#nicFinanceModule [data-finance-id="loan"]').isVisible());assert((await page.locator('#heroTitle').innerText()).replace(/\u00ad/g,'').includes('Finanzierungsrechner'));}
   if(key==='rent'){
    const spacing=await page.evaluate(()=>['rentCashflowKpi','rentFactorKpi'].map(id=>{const card=document.getElementById(id);const info=card?.querySelector('.rent-kpi-info'),badge=card?.querySelector('.rent-kpi-rating');return {infoBottom:info?.getBoundingClientRect().bottom,badgeTop:badge?.getBoundingClientRect().top};}));
    for(const pair of spacing)if(pair.badgeTop!=null)assert(pair.infoBottom!=null&&pair.badgeTop>=pair.infoBottom+4,'Traffic badge has visible spacing below its info icon');
   }
   if(key==='finance'){
    const geometry=await page.locator('#nicFinanceModule').evaluate(host=>{
     const cards=[...host.querySelectorAll(':scope > .card')].map(el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};});
     const menu=document.querySelector('.deal-type-card').getBoundingClientRect();
     const grids=[...host.querySelectorAll('.grid:has(> .kpi)')].map(grid=>[...grid.children].map(el=>{const r=el.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};}));
     return {inMain:host.parentElement.matches('.app>main.section'),menu:{left:menu.left,right:menu.right},cards,grids,hasShadow:!!host.shadowRoot};
    });
    assert(geometry.inMain&&!geometry.hasShadow,'Finance must use the shared main DOM and frame');
    assert(geometry.cards.length>=2&&geometry.cards.every(card=>Math.abs(card.left-geometry.menu.left)<2&&Math.abs(card.right-geometry.menu.right)<2),'Finance cards must align with the shared calculator frame');
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
  for(const slug of ['nebenkostenabrechnung','preise','warum-immocheck']){
   const menu=page.locator('.nic-brand-bar .nic-menu-toggle');
   if(await menu.isVisible())await menu.click();
   await page.locator('[data-nic-site-nav] a[href="/'+slug+'/"]').click();
   await page.waitForURL('http://localhost/'+slug+'/');
   await page.locator(slug==='nebenkostenabrechnung'?'[data-nic-explanation=settlement]':'#nicContentView').waitFor({state:'visible'});
   assert.equal(await page.evaluate(()=>performance.timeOrigin),sharedOrigin,'Information menu must retain the document');
   assert(await headerNode.evaluate(el=>el===document.querySelector('.app>.hero')),'Header DOM must be retained');
   assert(await page.locator(slug==='nebenkostenabrechnung'?'[data-nic-explanation=settlement]':'#nicContentView').evaluate(el=>el.parentElement.matches('.app>main.section')),'Information uses the calculator main container');
   const h=await page.locator('.app>.hero').evaluate(el=>el.getBoundingClientRect().height);
   assert(Math.abs(h-standardHeader.height)<=1,'Same-document information navigation changes header height');
  }
  await page.goBack();await page.waitForURL('http://localhost/preise/');
  assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content.prices.title);
  await page.goForward();await page.waitForURL('http://localhost/warum-immocheck/');
  assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content.why.title);
  await page.goBack();await page.goBack();await page.goBack();await page.waitForURL('http://localhost/');
  assert.equal(await page.evaluate(()=>performance.timeOrigin),sharedOrigin,'Browser history returns home within the shared application');
  for(const routeName of ['preise','warum-immocheck','nebenkostenabrechnung','ueber-uns','kontakt']){
   await page.goto('http://localhost/'+routeName+'/');
   await page.locator(routeName==='nebenkostenabrechnung'?'[data-nic-explanation=settlement]':'.nic-content-card').waitFor({state:'visible'});
   if(['preise','warum-immocheck','nebenkostenabrechnung'].includes(routeName)){
    const key=({'preise':'prices','warum-immocheck':'why','nebenkostenabrechnung':'settlement'})[routeName];
    await page.waitForFunction(k=>window.NICCalculators?.active===k,key);
    assert((await page.evaluate(()=>window.homeHeaderWrites)).every(title=>title===require('../assets/site-settings.json').content[key].title),'Legacy initialization must not overwrite the information header');
    assert.equal(await page.locator('#heroTitle').innerText(),require('../assets/site-settings.json').content[key].title,'Direct content startup must preserve its heading');
    assert.equal(await page.evaluate(()=>NICCalculators.active),key,'Direct content URL must use the shared controller');
    assert(await page.locator('.deal-type-card').count(),'Direct content route retains calculator controls for shared navigation');
    assert(await page.locator('.app>.hero').isVisible(),'Standard image header missing on '+routeName);
    assert(await page.locator('.app>.hero h1').isVisible(),'Standard heading missing on '+routeName);
    assert.equal(await page.locator('.nic-content-card h1').count(),0,'Content title must not be duplicated');
    assert.equal(await page.locator('link[href*="calculator-typography"]').count(),1,'Shared typography missing on '+routeName);
    await page.waitForFunction(()=>NICSettings.ready&&document.querySelector('.hero.nic-fixed-header'));
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const header=await page.locator('.app>.hero').evaluate(el=>({height:el.getBoundingClientRect().height,background:getComputedStyle(el).backgroundImage,font:getComputedStyle(el.querySelector('h1')).fontFamily,size:getComputedStyle(el.querySelector('h1')).fontSize,logo:document.querySelector('.brand-logo').getBoundingClientRect().width}));
    for(const key of ['background','font','size','logo'])assert.equal(header[key],standardHeader[key],'Standard header '+key+' differs on '+routeName);
    assert(Math.abs(header.height-standardHeader.height)<=1,'Header height changes on '+routeName);

   }else assert(await page.locator('.nic-content-card h1').isVisible(),'Content heading missing on '+routeName);
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
  assert(await page.locator('#nicFinanceModule [data-finance-id="loan"]').isVisible(),'Direct finance must remain usable when published settings are unavailable');
  assert.deepEqual(errors,[]);
  console.log('Unified navigation passed',width,'same document, all modes, history, direct finance reload');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
