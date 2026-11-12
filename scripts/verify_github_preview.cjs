// Exercise the real project subpath, without allowing production backend calls.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'}),errors=[],missing=[],backend=[];
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
   for(const slug of ['','budget/','eigennutzung/','vermietung/','fix-flip/','finanzierungsrechner/','nebenkostenabrechnung/','preise/','warum-immocheck/']){
    await page.goto('http://localhost/fixflip-kalkulator/'+slug,{waitUntil:'networkidle'});
    await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady);
    if(await page.locator('#nicConsentDialog[open]').count())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
    assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,nofollow');
    assert(new URL(page.url()).pathname.startsWith('/fixflip-kalkulator/'),'Direct route remains in project');
    assert(await page.locator('.app > main.section').isVisible(),'Shared app visible: '+slug);
    const localLinks=await page.locator('a[href]').evaluateAll(links=>links.map(a=>a.href).filter(u=>u.startsWith(location.origin)));
    assert(localLinks.every(u=>new URL(u).pathname.startsWith('/fixflip-kalkulator/')),'Links remain inside preview: '+slug);
   }
   await page.goto('http://localhost/fixflip-kalkulator/',{waitUntil:'networkidle'});
   const budget=page.locator('a[href="/fixflip-kalkulator/budget/"]').first();
   await budget.click();
   await page.waitForURL('**/fixflip-kalkulator/budget/');
   assert.equal(await page.locator('html').getAttribute('data-nic-page'),'budget');
   await page.goBack();await page.waitForURL('http://localhost/fixflip-kalkulator/');
   assert.equal(await page.locator('html').getAttribute('data-nic-page'),'website');
   assert.deepEqual(errors,[],'No browser errors');
   assert.deepEqual(missing,[],'No missing or origin-root assets');
   assert.deepEqual(backend,[],'No production backend access');
   await page.close();
  }
  console.log('GitHub preview passed: project routes, assets, desktop/mobile, navigation/back and backend isolation.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
