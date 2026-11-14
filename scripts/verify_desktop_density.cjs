// Regression coverage for native layout zoom and header measurements on resize.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:900},serviceWorkers:'block'}),errors=[];
  const settings=JSON.parse(fs.readFileSync('assets/site-settings.json','utf8'));
  settings.layout.bodySize=20;settings.layout.h1=30;
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
   if(u.hostname!=='localhost')return route.fulfill(route.request().resourceType()==='script'?{contentType:'application/javascript',body:''}:{json:{user:null,settings,csrf:'density-test',ready:true,ok:true}});
   let name=u.pathname;if(name.endsWith('/'))name+='index.html';
   const file=path.join(process.cwd(),'_site',name);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'application/octet-stream'});
  });
  await page.goto('http://localhost/budget/',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady);
  await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
  const measure=()=>page.evaluate(()=>{
   const hero=document.getElementById('heroTitle').closest('.hero'),box=hero.getBoundingClientRect();
   return {scale:parseFloat(getComputedStyle(document.body).zoom)||1,logo:document.querySelector('.brand-logo').getBoundingClientRect().width,
    app:document.querySelector('.app').getBoundingClientRect().width,height:box.height,
    contentBottom:Math.max(...[...hero.children].map(e=>e.getBoundingClientRect().bottom)),bottom:box.bottom,
    overflow:document.documentElement.scrollWidth>innerWidth+1,
    button:document.querySelector('.bottom-actions .bottom-primary')?.getBoundingClientRect().height};
  });
  for(const width of [1440,1920,1024,1023,844,390,1440]){
   await page.setViewportSize({width,height:900});
   await page.evaluate(()=>NICCalculatorNavigation.select('budget'));
   await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   const before=await measure(),scale=width>=1024?.75:1;
   assert.equal(before.scale,scale,'Desktop-only scale at '+width);
   assert(Math.abs(before.logo-(width>=1024?250:width<=700?176:250)*scale)<1,'Logo scales once at '+width+': '+JSON.stringify(before));
   if(width>=1024)assert(before.app<=916,'Compact desktop container');
   assert(Math.abs(before.button-44*scale)<1,'Controls scale once at '+width+': '+JSON.stringify(before));
   assert(!before.overflow,'No horizontal overflow at '+width);
   assert(before.contentBottom<=before.bottom+1,'Header contains its text at '+width);
   for(const key of ['rent','finance','why','home']){
    await page.evaluate(k=>NICCalculatorNavigation.select(k),key);
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    const after=await measure();
    assert(Math.abs(after.height-before.height)<=1,'Header stable during navigation at '+width+' '+key);
    assert(after.contentBottom<=after.bottom+1,'Header text not clipped at '+width+' '+key);
    assert(!after.overflow,'No route overflow at '+width+' '+key);
   }
   const fill=await page.locator('.app').evaluate(e=>({height:e.getBoundingClientRect().height,minHeight:getComputedStyle(e).minHeight,viewport:innerHeight,bodyMin:getComputedStyle(document.body).minHeight}));
   assert(fill.height>=fill.viewport-1,'Short pages fill the viewport at '+width+': '+JSON.stringify(fill));
  }
  await page.emulateMedia({media:'print'});
  assert.equal(await page.locator('body').evaluate(e=>parseFloat(getComputedStyle(e).zoom)||1),1,'Print is not scaled');
  await page.emulateMedia({media:'screen'});
  await page.goto('http://localhost/budget/?embed=1',{waitUntil:'networkidle'});
  assert.equal(await page.locator('body').evaluate(e=>parseFloat(getComputedStyle(e).zoom)||1),1,'Embedded calculator is not scaled');
  assert.deepEqual(errors,[]);
  console.log('Desktop 75% passed: 1024/1440/1920, mobile unchanged, resize, header stability, controls, overflow and print.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
