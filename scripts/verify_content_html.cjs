// Real Admin input/save/reload and public FAQ rendering, isolated from production.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const source=fs.readFileSync('scripts/fixtures/content-html-faq.html','utf8');
  assert(source.length>12000);
  for(const width of [390,1440]){
   const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'});
   const errors=[],external=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.origin!=='http://localhost'){if(u.hostname==='invalid.example'||u.pathname.startsWith('/api/'))external.push(u.href);return route.abort();}
    if(!u.pathname.startsWith('/fixflip-kalkulator/'))return route.fulfill({status:404,body:'Outside project'});
    let name=u.pathname.slice('/fixflip-kalkulator/'.length);if(!name||name.endsWith('/'))name+='index.html';
    const file=path.join('_preview',name);
    if(!fs.existsSync(file))return route.fulfill({status:404,body:'Missing preview asset'});
    await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.json':'application/json','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp'})[path.extname(file)]||'application/octet-stream'});
   });
   await page.goto('http://localhost/fixflip-kalkulator/',{waitUntil:'networkidle'});
   if(await page.locator('#nicConsentDialog[open]').count())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
   await page.goto('http://localhost/fixflip-kalkulator/admin.html',{waitUntil:'networkidle'});
   await page.waitForFunction(()=>location.hash.startsWith('#admin'),null,{timeout:10000});
   await page.locator('#nicAdminContent[data-ready="true"]').waitFor({timeout:20000}).catch(async error=>{throw new Error('Admin setup: '+JSON.stringify({url:page.url(),errors,body:await page.locator('body').getAttribute('class')})+' '+error.message);});
   if(await page.locator('#nicConsentDialog[open]').count())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
   await page.evaluate(()=>window.NICAdminUI.select('content'));
   assert.equal(await page.locator('#nicAdminContent [role=tab]').count(),8);
   assert.equal(await page.locator('#nicAdminContent .admin-page[open]').count(),0);
   const own=page.locator('[data-admin-page="own"]');
   await own.locator('summary').click();
   const title=own.getByLabel('Meta-Titel',{exact:true});
   assert.equal(await title.count(),1);
   await title.fill('Eigenheim Test');
   await own.getByRole('checkbox',{name:'Von Suchmaschinen ausschließen'}).check();
   assert(await own.locator('.admin-page-noindex').isVisible());
   await own.locator('summary').click();
   await page.locator('[data-admin-page="why"] > summary').click();
   const editor=page.locator('[id$="content-why-description"]');
   await editor.waitFor({state:'visible'});
   assert.equal(await editor.getAttribute('maxlength'),'100000');
   await editor.fill(source);
   assert.equal(await editor.inputValue(),source,'Paste keeps full long HTML');
   await editor.evaluate(el=>el.setSelectionRange(el.value.length,el.value.length));
   const why=page.locator('[data-admin-page="why"]');
   await why.getByLabel('Abschnittstitel (optional)').fill('Ein Titel <mit Zeichen>');
   await why.getByRole('button',{name:'2 Spalten',exact:true}).click();
   await editor.evaluate(el=>el.setSelectionRange(el.value.length,el.value.length));
   await why.getByRole('button',{name:'3 Spalten',exact:true}).click();
   const editedSource=await editor.inputValue();
   assert(editedSource.startsWith(source),'Insertion preserves the existing content');
   async function verifyColumns(container){
    const sections=container.locator('.nic-content-section');
    assert.equal(await sections.count(),2);
    assert.equal(await sections.first().locator('h3').textContent(),'Ein Titel <mit Zeichen>');
    assert.equal(await sections.last().locator('h3').count(),0);
    for(const count of [2,3]){
     const grid=container.locator('.nic-content-columns-'+count);
     assert.equal(await grid.locator(':scope > div').count(),count);
     assert.equal(await grid.evaluate(el=>getComputedStyle(el).gridTemplateColumns.split(' ').length),width>700?count:1);
    }
   }
   const preview=page.locator('[id$="content-why-body-preview"]');
   await verifyColumns(preview);
   assert.equal(await preview.locator('details.imc-faq-item').count(),10,'All ten FAQ previews');
   await preview.locator('details.imc-faq-item summary').first().click();
   assert(await preview.locator('.imc-faq-answer').first().isVisible(),'Native FAQ opens');
   await page.locator('[id$="content-why-headerTitle"]').fill('Mein Titel aus dem Adminbereich');
   await page.locator('[id$="content-why-headerDescription"]').fill('Meine Kurzbeschreibung aus dem Adminbereich');
   await page.locator('[id$="saveSettings"]').click();
   await page.waitForFunction(source=>window.NICSettings.current.content.why.description===source,editedSource);
   await page.goto('http://localhost/fixflip-kalkulator/warum-immocheck/',{waitUntil:'networkidle'});
   const content=page.locator('#nicContentView');
   await verifyColumns(content);
   await content.locator('section.imc-content').waitFor({state:'visible'});
   assert.equal(await page.locator('#heroTitle').textContent(),'Mein Titel aus dem Adminbereich');
   assert.equal(await page.locator('#heroText').textContent(),'Meine Kurzbeschreibung aus dem Adminbereich');
   assert.equal(await page.evaluate(()=>window.NICSettings.current.content.why.description),editedSource,'Save/reload is lossless');
   assert.equal(await page.evaluate(()=>window.NICSettings.current.content.own.seoTitle),'Eigenheim Test');
   assert.equal(await page.evaluate(()=>window.NICSettings.current.seoIndexing.own),false);
   assert.equal(await content.locator('details.imc-faq-item').count(),10);
   assert(await content.locator('.imc-faq-note').isVisible(),'End sentinel visible after >12k characters');
   const first=content.locator('details.imc-faq-item').first();
   assert.equal(await first.getAttribute('open'),null);
   await first.locator('summary').click();
   assert(await first.locator('.imc-faq-answer').isVisible());
   assert.equal(await first.locator('summary').evaluate(el=>getComputedStyle(el).display),'flex','Embedded CSS applied');
   const pseudo=await first.locator('summary').evaluate(el=>getComputedStyle(el,'::after').content);
   assert(pseudo.includes('−'),'Open FAQ CSS applied');
   assert.equal(await page.locator('body').evaluate(el=>getComputedStyle(el).getPropertyValue('--nic-content-css-leak').trim()),'','CSS cannot affect body');
   const security=await page.evaluate(()=>{
    const host=document.createElement('div');
    host.append(window.NICSettings.contentFragment('<section><unknown>Erhalten</unknown><script>window.nicContentUnsafe=1</script><img src=x onerror="window.nicContentUnsafe=2"><a href="javascript:alert(1)" onclick="alert(1)">Link</a></section>',window.NICSettings.current));
    return {text:host.textContent,script:host.querySelectorAll('script,img,[onclick],a[href]').length};
   });
   assert(security.text.includes('Erhalten'));assert.equal(security.script,0);
   // About Us must use the saved Admin description, not stale build-time HTML.
   await page.goto('http://localhost/fixflip-kalkulator/ueber-uns/',{waitUntil:'networkidle'});
   const about=page.locator('main.nic-content-main > article.nic-content-card > div');
   await about.waitFor({state:'visible'});
   await page.evaluate(()=>{
    const s=JSON.parse(JSON.stringify(window.NICSettings.current));
    s.content.about.description='<h2>Über uns – aus dem Admin</h2><p>Aktualisierter Inhalt aus den Einstellungen.</p>';
    window.NICSettings.save(s);
    window.dispatchEvent(new Event('nic-settings-updated'));
   });
   assert.equal(await about.locator('h2').textContent(),'Über uns – aus dem Admin');
   assert((await about.innerText()).includes('Aktualisierter Inhalt aus den Einstellungen.'));
   await page.reload({waitUntil:'networkidle'});
   assert.equal(await page.locator('main.nic-content-main > article.nic-content-card h2').textContent(),'Über uns – aus dem Admin','About Us keeps saved Admin content after reload');
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
   await page.close();
  }
  console.log('Long Content HTML passed: Admin paste/save/reload, 10 native FAQs, scoped CSS, no truncation or unsafe execution.');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
