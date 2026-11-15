const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({serviceWorkers:'block'}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname!=='localhost')return route.fulfill(route.request().resourceType()==='script'?{contentType:'application/javascript',body:''}:{json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test',authControlsVersion:1}});
   const file=path.join(process.cwd(),'_site',u.pathname.endsWith('/')?u.pathname+'index.html':u.pathname);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png'})[path.extname(file)]||'application/octet-stream'});
  });
  for(const viewport of [{width:320,height:740},{width:390,height:844},{width:700,height:1000},{width:768,height:1024},{width:844,height:390},{width:1024,height:768},{width:1440,height:900},{width:1920,height:1080}]){
   await page.setViewportSize(viewport);await page.goto('http://localhost/');
   await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady==='ready'&&document.querySelector('#nicFooterLegal'));
   if(await page.getByRole('button',{name:'Ablehnen',exact:true}).isVisible())await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
   const portrait=viewport.width<=700&&viewport.width<viewport.height;
   for(const [social,about,contact]of [[true,true,true],[false,true,true],[true,false,true],[true,true,false],[false,false,true],[false,false,false]]){
    await page.evaluate(({social,about,contact})=>{
     const s=JSON.parse(JSON.stringify(NICSettings.current));
     s.social=Object.fromEntries(Object.keys(s.social).map(key=>[key,'']));if(social)s.social.instagram='https://example.test/instagram';
     s.content.about.metaDescription=about?'Informationen über ImmoCheck und unsere Werkzeuge.':'';
     s.meta.about={...(s.meta.about||{}),description:''};s.meta.website.description='';s.company.email=contact?'test@example.test':'';
     NICSettings.apply(s);NICShell.refresh(s);
    },{social,about,contact});
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const layout=await page.evaluate(()=>{
     const box=e=>{const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width}};
     const sections=[...document.querySelectorAll('.nic-footer-section')].map(e=>({id:e.id,hidden:e.hidden,open:e.open,box:box(e),icon:getComputedStyle(e.querySelector('.nic-footer-heading-icon')).display}));
     const legal=document.getElementById('nicFooterLegal'),footer=document.querySelector('.app>.footer-note');
     return {sections,footer:box(footer),legal:{open:legal.open,summary:getComputedStyle(legal.querySelector('summary')).display,box:box(legal),links:getComputedStyle(legal.querySelector('.footer-legal-links')).justifyContent},legalCount:document.querySelectorAll('#nicFooterLegal').length,cookies:document.querySelectorAll('#nicConsentSettings').length,legalLinks:[...legal.querySelectorAll('[data-legal-placeholder]')].map(e=>e.dataset.legalPlaceholder),overflow:document.documentElement.scrollWidth>innerWidth+1};
    });
    assert.equal(layout.legalCount,1);assert.equal(layout.cookies,1);assert.deepEqual(layout.legalLinks,['impressum','agbs','datenschutz','haftungsausschluss']);
    assert.deepEqual(layout.sections.map(s=>s.hidden),[!social,!about,!contact]);
    const visible=layout.sections.filter(s=>!s.hidden);
    assert(!layout.overflow,'Footer overflows: '+JSON.stringify({viewport,layout}));
    visible.forEach(s=>assert(s.box.left>=layout.footer.left-1&&s.box.right<=layout.footer.right+1,'Footer section exceeds container'));
    if(portrait){
     assert(layout.legal.open&&layout.legal.summary==='none');assert.equal(layout.legal.links,'center');
     visible.forEach((s,i)=>{assert(!s.open);assert.equal(s.icon,'block');if(i)assert(s.box.top>=visible[i-1].box.bottom,'Portrait sections must stack');});
     if(visible.length){const section=page.locator('#'+visible[0].id);await section.locator('summary').click();assert(await section.evaluate(e=>e.open));await section.locator('summary').click();assert(!await section.evaluate(e=>e.open));}
    }else{
     assert(!layout.legal.open&&layout.legal.summary!=='none');assert(!await page.locator('#nicConsentSettings').isVisible(),'Legal links start collapsed outside portrait');
     if(!social&&about&&contact)assert(Math.abs(visible[0].box.width/visible[1].box.width-2)<.05,'No-social layout retains the existing 2:1 column proportions');
     visible.forEach((s,i)=>{assert(s.open);assert.equal(s.icon,'none');if(i){assert(Math.abs(s.box.top-visible[0].box.top)<1,'Footer columns align');assert(s.box.left>=visible[i-1].box.right,'Footer columns overlap');}});
     const legal=page.locator('#nicFooterLegal');await legal.locator('summary').click();assert(await legal.evaluate(e=>e.open));assert(await page.locator('#nicConsentSettings').isVisible());
     await legal.locator('summary').press('Enter');assert(!await legal.evaluate(e=>e.open));
    }
   }
   // Same footer instance across all calculators and information routes.
   for(const key of ['budget','own','rent','flip','finance','settlement','prices','why','home']){
    await page.evaluate(key=>NICCalculatorNavigation.select(key),key);
    assert.equal(await page.locator('#nicFooterLegal').count(),1,'One legal footer after '+key);
    assert.equal(await page.locator('.nic-footer-heading-icon').count(),3,'Three existing heading icons after '+key);
   }
   console.log('PASS footer variants and visibility',viewport.width,viewport.height);
  }
  assert.deepEqual(errors,[]);await page.close();
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
