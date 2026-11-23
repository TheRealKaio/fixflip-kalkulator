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
   const settlementPage=page.locator('[data-admin-page="settlement"]');
   await settlementPage.locator(':scope > summary').click();
   await settlementPage.locator('#settlementTileCodeType').selectOption('weg');
   const tileHtml=await settlementPage.locator('#settlementTileCode').inputValue();
   // Model old copied HTML whose style block predates the shared fix.
   const savedTileHtml=tileHtml
    .replace(/font-size:var\(--nic-subtext-font-size,14px\)!important/g,'font-size:var(--nic-subtext-font-size,14px)')
    .replace(/^@media\(orientation:landscape\).*\n/m,'');
   await settlementPage.locator(':scope > summary').click();
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
   const tools=why.locator('.content-layout-tools');
   assert.equal(await tools.locator('.content-column-row').count(),1,'Column insertion has its own row');
   assert.equal(await tools.locator('.content-media-row').count(),1,'Media insertion has its own row');
   const titleInput=tools.locator('.content-column-row > .admin-field input');
   const mediaSelect=tools.locator('.content-media-row > select');
   const columnButton=tools.getByRole('button',{name:'2 Spalten',exact:true});
   const mediaButton=tools.getByRole('button',{name:'Medium einfügen',exact:true});
   const dims=await Promise.all([titleInput.evaluate(el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,bottom:r.bottom};}),mediaSelect.evaluate(el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,bottom:r.bottom};}),columnButton.evaluate(el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y};}),mediaButton.evaluate(el=>{const r=el.getBoundingClientRect();return{x:r.x,y:r.y};})]);
   if(width>=640){
    const rowWidth=await tools.locator('.content-column-row').evaluate(el=>el.getBoundingClientRect().width);
    assert(Math.abs(dims[0].width-dims[1].width)<=1,'Title input and media selector have equal widths');
    assert(Math.abs(dims[0].width/rowWidth-.5)<.03,'Each tool input takes half of the available row');
    assert(dims[2].x>dims[0].x,'Column buttons follow the title input');
    assert(dims[3].x>dims[1].x,'Media insert button follows the selector');
   }else{
    assert(dims[2].y>=dims[0].bottom,'Column buttons wrap below their input at mobile width');
    assert(dims[3].y>=dims[1].bottom,'Media insert button wraps below its selector at mobile width');
   }
   await why.getByLabel('Abschnittstitel (optional)').fill('Ein Titel <mit Zeichen>');
   await why.getByRole('button',{name:'2 Spalten',exact:true}).click();
   await editor.evaluate(el=>el.setSelectionRange(el.value.length,el.value.length));
   await why.getByRole('button',{name:'3 Spalten',exact:true}).click();
   await editor.fill((await editor.inputValue())+savedTileHtml);
   const editedSource=await editor.inputValue();
   assert(!editedSource.slice(source.length).includes('\\n'),'Column inserts use real newlines');
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
   const recovered=await page.evaluate(source=>{
    const section='<section class="nic-content-section">\\n<div class="nic-content-columns">\\n<div><p></p></div>\\n</div>\\n</section>';
    const fragment=window.NICSettings.contentFragment('<p>Einleitung.\\n</p>'+section+'\\n'+source+'\n'+source,window.NICSettings.current);
    return [fragment.querySelectorAll('.nic-copy-tile-grid').length,fragment.querySelectorAll('.nic-copy-tile').length,fragment.textContent.includes('\\n'),fragment.querySelectorAll('.nic-content-section').length];
   },tileHtml);
   assert.deepEqual(recovered,[1,2,false,0],'Legacy column leftovers disappear and adjacent tile grids combine');
   const tile=content.locator('a.nic-copy-tile');
   const icon=tile.locator('svg'), label=tile.locator('strong'), description=tile.locator('small');
   assert(await icon.locator('path[d]').count()>0,'Copied tile retains its icon paths');
   assert.equal(await label.textContent(),'WEG-Abrechnung hochladen');
   assert.equal(await description.textContent(),'Fertige Jahresabrechnung automatisch einlesen');
   async function checkTileOrientation(portrait){
    const [i,t,d]=await Promise.all([icon.boundingBox(),label.boundingBox(),description.boundingBox()]);
    assert(i&&t&&d&&i.height>0);
    if(portrait){
     assert(i.x+i.width<=t.x+1 && Math.abs(i.y+i.height/2-t.y-t.height/2)<2,'Portrait puts the icon left of the centered title');
     assert(d.y+1>=Math.max(i.y+i.height,t.y+t.height),'Portrait description below both');
    }else{
     assert(i.y+i.height<=t.y+1&&t.y+t.height<=d.y+1,'Landscape stacks icon, title and description');
    }
   }
   const [subtextSize,configuredSize]=await description.evaluate(el=>{
    const style=getComputedStyle(el);
    return [style.fontSize,style.getPropertyValue('--nic-subtext-font-size').trim()||'14px'];
   });
   assert.equal(subtextSize,configuredSize,'Previously copied tiles use the configured subtext size');
   assert.deepEqual(await tile.evaluate(el=>{
    const style=getComputedStyle(el);
    return [style.padding,style.minHeight];
   }),['12px 8px','78px'],'Saved tiles use homepage spacing');
   if(width>=900){
    await tile.scrollIntoViewIfNeeded();
    const before=await tile.boundingBox();
    await tile.hover();
    assert.equal(await tile.evaluate(el=>getComputedStyle(el).transform),'none','Saved hover CSS cannot move the tile');
    assert.deepEqual(await tile.boundingBox(),before,'Hover keeps the tile in place');
   }
   await checkTileOrientation(width<900);
   if(width===390){
    await page.setViewportSize({width:844,height:390});
    await checkTileOrientation(false);
    const [singleWidth,multipleWidth,gridWidth]=await tile.evaluate(el=>{
     const grid=el.parentElement;
     const gridWidth=grid.getBoundingClientRect().width;
     const singleWidth=el.getBoundingClientRect().width;
     const secondTile=el.cloneNode(true);
     grid.append(secondTile);
     const multipleWidth=el.getBoundingClientRect().width;
     secondTile.remove();
     return [singleWidth,multipleWidth,gridWidth];
    });
    assert(Math.abs(singleWidth-gridWidth)<=1,'A lone tile spans the grid on mobile landscape');
    assert(multipleWidth<gridWidth/2,'Two tiles retain two columns on mobile landscape');
    await page.setViewportSize({width:390,height:900});
    await checkTileOrientation(true);
   }
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
