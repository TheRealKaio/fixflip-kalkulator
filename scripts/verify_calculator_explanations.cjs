const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const routes={budget:'budget',own:'eigennutzung',rent:'vermietung',flip:'fix-flip',finance:'finanzierungsrechner',settlement:'nebenkostenabrechnung'};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'}),errors=[];
   let admin=false,saves=0;
   let settings=JSON.parse(fs.readFileSync('assets/site-settings.json','utf8'));
   Object.assign(settings.layout,{font:'verdana',bodySize:20,h2:24,h3:22});
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
    if(u.hostname!=='localhost'){
     if(u.searchParams.get('r')==='settings'&&route.request().method()==='POST'){
      settings=route.request().postDataJSON().settings;delete settings.content;saves++;
     }
     return route.fulfill(route.request().resourceType()==='script'?{contentType:'application/javascript',body:''}:{json:{user:admin?{id:'admin',role:'admin',email:'admin@example.test'}:null,settings,revision:saves+1,authControlsVersion:1,csrf:'explanation-test',ok:true,ready:true,users:[],rows:[]}});
    }
    let name=u.pathname;if(name.endsWith('/'))name+='index.html';
    const file=path.join(process.cwd(),'_site',name);
    if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
    return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream'});
   });
   const heights=[];
   for(const [key,slug]of Object.entries(routes)){
    const source=fs.readFileSync('_site/'+slug+'/index.html','utf8');
    if(key!=='settlement')assert(source.includes('data-nic-explanation="'+key+'"'),'Direct HTML contains complete route explanation');
    await page.goto('http://localhost/'+slug+'/',{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady);
    if(await page.locator('#nicConsentDialog[open]').count())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
    if(key==='settlement'){
     const content=page.locator('#nicContentView');
     assert(await content.isVisible(),'Settlement content page is visible');
     assert.equal(await page.locator('[data-nic-explanation]').count(),0,'Settlement has no separate explanation accordion');
     assert.equal(await content.locator('summary').filter({hasText:'Weiterlesen'}).count(),0,'Settlement is never folded under read more');
     continue;
    }
    const card=page.locator('[data-nic-explanation]');
    assert.equal(await card.count(),1,'Only the current explanation exists');
    assert.equal(await card.getAttribute('data-nic-explanation'),key);
    assert(await card.isVisible(),'Explanation visible: '+key+' at '+width);
    if(key==='settlement'){assert.equal(await page.locator('#nicContentView [data-nic-settlement-action]').count(),2,'Settlement exposes both actions');assert((await card.locator('.nic-explanation-intro').innerText()).startsWith('Erstelle die jährliche Mieterabrechnung'),'Previous product copy is the introduction');}
    assert(await card.evaluate(e=>e.parentElement.firstElementChild===e),'Explanation comes first: '+key);
    if(key==='settlement')assert(await page.locator('#nicContentView').isVisible(),'Settlement content panel visible');
    const geometry=await card.evaluate(e=>({height:e.getBoundingClientRect().height,font:getComputedStyle(e).fontFamily,body:getComputedStyle(e.querySelector('p')).fontSize,h2:getComputedStyle(e.querySelector('h2')).fontSize,h3:getComputedStyle(e.querySelector('h3')).fontSize}));
    if(key!=='settlement')heights.push(geometry.height);
    assert(/verdana/i.test(geometry.font));assert.equal(geometry.body,'20px');assert.equal(geometry.h2,'24px');assert.equal(geometry.h3,'22px');
    const title=await card.locator('h2').innerText(),intro=await card.locator('.nic-explanation-intro').innerText();
    assert.notEqual(title,await page.locator('#heroTitle').innerText(),'No duplicated hero title');
    assert.notEqual(intro,await page.locator('#heroText').innerText(),'No duplicated hero description');
    const details=card.locator('details'),summary=card.locator('summary'),rest=card.locator('.nic-explanation-rest');
    assert.equal(await card.locator('.nic-explanation-intro').count(),1,'First paragraph exists');
    assert.equal(await card.locator('.nic-explanation-teaser p').count(),1,'Second paragraph visible before disclosure');
    assert(await card.locator('.nic-explanation-intro').isVisible(),'First paragraph visible');
    assert(await card.locator('.nic-explanation-teaser p').isVisible(),'Second paragraph visible');
    if(width===390){
     assert.equal(await details.evaluate(e=>e.open),false,'Mobile starts collapsed');
     assert.equal(await summary.innerText(),'weiterlesen');assert.equal(await rest.isVisible(),false);
     if(key!=='settlement'){
      assert.equal(await card.locator('.nic-explanation-intro').isVisible(),true,'First introductory paragraph remains visible on mobile');
      const teaser=await card.evaluate(e=>{const h=e.querySelector('h2'),style=getComputedStyle(h);const siblings=[...e.parentElement.children].filter(x=>x!==e&&x.getBoundingClientRect().height&&getComputedStyle(x).display!=='none');return {height:h.getBoundingClientRect().height,line:parseFloat(style.lineHeight),clamp:style.webkitLineClamp,first:siblings.every(x=>e.getBoundingClientRect().top<=x.getBoundingClientRect().top)};});
      assert.equal(teaser.clamp,'2');assert(teaser.height<=teaser.line*2+1,'Only two title lines');assert(teaser.first,'Teaser is visually before calculator inputs');
     }
     const corner=await card.evaluate(e=>{const a=e.getBoundingClientRect(),b=e.querySelector('summary').getBoundingClientRect();return {right:a.right-b.right,bottom:a.bottom-b.bottom};});
     assert(corner.right>=0&&corner.right<30&&corner.bottom>=0&&corner.bottom<30,'Read more at bottom right');
     await summary.click();assert.equal(await details.evaluate(e=>e.open),true);assert(await rest.isVisible());
     assert(await card.locator('.nic-explanation-intro').isVisible(),'Opening preserves both teaser paragraphs');
     assert(await card.evaluate(e=>e.getBoundingClientRect().height)>geometry.height,'Open box grows naturally');
     await summary.click();assert.equal(await details.evaluate(e=>e.open),false);
     await summary.focus();await page.keyboard.press('Enter');assert.equal(await details.evaluate(e=>e.open),true,'Keyboard opens explanation');
     await page.keyboard.press('Enter');assert.equal(await details.evaluate(e=>e.open),false);
    }else{
     assert.equal(await details.evaluate(e=>e.open),false,'Desktop also starts collapsed');
     assert.equal(await summary.isVisible(),true,'Desktop read-more link is visible');
     assert.equal(await rest.isVisible(),false,'Desktop hides the remaining text');
     await summary.click();
     assert.equal(await details.evaluate(e=>e.open),true,'Desktop read-more expands the content');
     assert(await rest.isVisible());
     await summary.click();
     assert.equal(await details.evaluate(e=>e.open),false,'Desktop read-more collapses again');
    }
   }
   // Desktop cards share a measured minimum height. Mobile portrait cards are
   // content-sized so they do not reserve unnecessary space before the calculator.
   if(width!==390)assert(Math.max(...heights)-Math.min(...heights)<=1,'Equal desktop card heights at '+width+': '+heights.join(','));
   for(const key of [...Object.keys(routes),'home','why','own','budget']){
    await page.evaluate(k=>NICCalculatorNavigation.select(k),key);
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    assert.equal(await page.locator('[data-nic-explanation]').count(),routes[key]&&key!=='settlement'?1:0,'Route cleanup: '+key);
    if(routes[key]&&key!=='settlement'){
     assert.equal(await page.locator('[data-nic-explanation]').getAttribute('data-nic-explanation'),key);
     assert(await page.locator('[data-nic-explanation]').evaluate(e=>e.parentElement.firstElementChild===e),'Explanation comes first after navigation: '+key);
     assert.equal(await page.locator('[data-nic-explanation] details').evaluate(e=>e.open),false,'New route starts collapsed on every device');
    }
   }
   // Rental billing is one uninterrupted content page at every viewport.
   for(const viewport of [{width:320,height:900},{width:390,height:1200},{width:768,height:1400},{width:844,height:900},{width:1440,height:1600},{width:1920,height:1800}]){
    await page.setViewportSize(viewport);
    await page.goto('http://localhost/nebenkostenabrechnung/',{waitUntil:'networkidle'});
    await page.locator('#nicContentView').waitFor({state:'visible'});
    assert.equal(await page.locator('[data-nic-explanation]').count(),0,'Settlement has one content card');
    assert.equal(await page.locator('#nicContentView summary').filter({hasText:'Weiterlesen'}).count(),0,'No forced read-more disclosure');
    assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),'Settlement has no horizontal overflow');
   }
   await page.setViewportSize({width,height:900});
   admin=true;
   await page.goto('http://localhost/#admin-content',{waitUntil:'networkidle'});
   await page.locator('#settingsForm').waitFor({state:'visible'});
   for(const key of Object.keys(routes))assert.equal(await page.locator('#content-'+key+'-description').count(),1,'Admin editor for '+key);
   await page.locator('[data-admin-page="settlement"] > summary').click();
   await page.locator('#content-settlement-boxTitle').fill('Meine Mieterabrechnung');
   await page.locator('#content-settlement-description').fill('<p>Meine eigene Einleitung</p><details><summary>Weiterlesen …</summary><h3>Meine Details</h3><p>Weitere Informationen <a href="/vermietung/">Vermietung</a></p></details><script>window.explanationInjected=true</script>');
   await page.locator('[data-admin-page="budget"] > summary').click();
   await page.locator('#content-budget-title').fill('Mein Budgettext');
   await page.locator('#saveSettings').click();
   await page.waitForFunction(()=>NICSettings.current.content.settlement.boxTitle==='Meine Mieterabrechnung');
   assert.equal(saves,1,'Admin saves through existing settings API');
   assert(!settings.content&&settings.meta.content.settlement.boxTitle==='Meine Mieterabrechnung','Legacy API retains the content transport');
   await page.goto('http://localhost/nebenkostenabrechnung/',{waitUntil:'networkidle'});
   const edited=page.locator('#nicContentView');
   assert.equal(await edited.locator('h2').innerText(),'Meine Mieterabrechnung');
   assert((await edited.innerText()).includes('Meine eigene Einleitung'),'Edited settlement description is rendered in the single card');
   assert.equal(await page.evaluate(()=>window.explanationInjected),undefined,'Active HTML is removed');
   assert.equal(await page.locator('#nicContentView summary').filter({hasText:'Weiterlesen'}).count(),0);
   assert(await page.getByRole('heading',{name:'Meine Details'}).isVisible(),'Legacy read-more content is visible without a click');
   await page.goto('http://localhost/budget/',{waitUntil:'networkidle'});
   assert.equal(await page.locator('[data-nic-explanation] h2').innerText(),'Mein Budgettext','Another box survives save and full reload');
   assert.deepEqual(errors,[]);await page.close();
  }
  console.log('Six explanations passed: static HTML, equal sizes, admin typography, two visible paragraphs, read-more/keyboard and route cleanup.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
