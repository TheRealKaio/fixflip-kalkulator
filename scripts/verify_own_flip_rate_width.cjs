/* Regression: real browser measurements for interest and repayment on both calculators. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const [slug,mode] of [['eigennutzung','own'],['fix-flip','flip']]){
   for(const width of [900,1440]){
    const page=await browser.newPage({viewport:{width,height:900},serviceWorkers:'block'});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.route('**/*',async route=>{
     const u=new URL(route.request().url());
     if(u.hostname!=='localhost'){
      if(route.request().resourceType()==='script')return route.fulfill({status:200,contentType:'application/javascript',body:''});
      return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
     }
     let name=u.pathname;if(name.endsWith('/'))name+='index.html';
     const file=path.join(process.cwd(),'_site',name);
     if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
     return route.fulfill({status:200,body:fs.readFileSync(file),
      contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'text/plain'});
    });
    await page.goto('http://localhost/'+slug+'/',{waitUntil:'domcontentloaded'});
    const deny=page.getByRole('button',{name:'Ablehnen',exact:true});
    if(await deny.isVisible())await deny.click();
    await page.waitForFunction(m=>document.body.dataset.calculator===m&&window.NICCalculators?.active===m,mode,{timeout:30000});
    await page.waitForFunction(()=>{
     const a=document.getElementById('interest')?.closest('.field');
     const b=document.getElementById('repayment')?.closest('.field');
     return a&&b&&a.parentElement===b.parentElement&&a.parentElement.classList.contains('nic-balanced-finance-rates');
    },{timeout:10000});
    const result=await page.evaluate(()=>{
     const a=document.getElementById('interest'),b=document.getElementById('repayment');
     const pair=a.closest('.field').parentElement;
     const r=el=>el.getBoundingClientRect();
     const x=r(a.closest('.field')),y=r(b.closest('.field')),p=r(pair),container=r(pair.parentElement);
     return {labels:[a.closest('.field').querySelector('label')?.textContent?.trim(),b.closest('.field').querySelector('label')?.textContent?.trim()],
      widths:[x.width,y.width],top:[x.top,y.top],pairWidth:p.width,containerWidth:container.width,
      pairLeft:p.left,containerLeft:container.left,columns:getComputedStyle(pair).gridTemplateColumns};
    });
    assert(/zins/i.test(result.labels[0])&&/tilgung/i.test(result.labels[1]),'Correct named inputs: '+JSON.stringify(result));
    assert(Math.abs(result.widths[0]-result.widths[1])<2,slug+' '+width+' equal columns: '+JSON.stringify(result));
    assert(Math.abs(result.top[0]-result.top[1])<2,slug+' '+width+' same row: '+JSON.stringify(result));
    assert(Math.abs(result.pairWidth-result.containerWidth)<3,slug+' '+width+' full available width: '+JSON.stringify(result));
    assert(Math.abs(result.pairLeft-result.containerLeft)<3,slug+' '+width+' no horizontal offset: '+JSON.stringify(result));
    assert.equal(errors.length,0,slug+' '+width+' browser errors: '+errors.join('; '));
    console.log('RATE LAYOUT PASS',slug,width,JSON.stringify(result));
    await page.close();
   }
  }
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
