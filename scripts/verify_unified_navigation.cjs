const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
   if(u.hostname!=='localhost'&&route.request().resourceType()==='script')return route.fulfill({contentType:'application/javascript',body:''});
   if(u.hostname!=='localhost')return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
   let name=u.pathname;if(name.endsWith('/'))name+='index.html';
   const file=path.join(process.cwd(),'_site',name);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   await route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'})[path.extname(file)]||'text/plain'});
  });
  await page.goto('http://localhost/budget/');
  await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
  await page.waitForFunction(()=>window.NICCalculatorNavigation&&window.NICSettings.current);
  await page.waitForFunction(()=>window.NICReferenceInterest?.rate===4.09);
  const origin=await page.evaluate(()=>performance.timeOrigin);
  for(const key of ['finance','own','rent','flip','budget','finance']){
   await page.locator(`.deal-type-option[data-calculator="${key}"]`).click();
   await page.waitForFunction(k=>document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
   assert.equal(await page.evaluate(()=>performance.timeOrigin),origin,'calculator changes must keep same document');
   assert.equal(await page.locator('.nic-tile-active').count(),1);
   if(key==='finance'){assert(await page.locator('#nicFinanceModule #loan').isVisible());assert((await page.locator('#heroTitle').innerText()).replace(/\u00ad/g,'').includes('Finanzierungsrechner'));}
  }
  await page.evaluate(async()=>{
   const root=document.getElementById('nicFinanceModule').shadowRoot,input=root.getElementById('interest');
   for(const id of ['interest','budgetInterest','rentInterest'])if(Number(document.getElementById(id).value)!==4.09)throw Error('Shared reference missing: '+id);
   if(Number(input.value)!==4.09)throw Error('Finance must share the reference rate');
   input.value='5.25';input.dispatchEvent(new Event('input',{bubbles:true}));
   await initializeReferenceInterest();
   if(Number(input.value)!==5.25)throw Error('Manual finance rate overwritten');
  });
  await page.goBack();await page.waitForFunction(()=>!document.body.classList.contains('nic-finance-active'));
  await page.goForward();await page.waitForFunction(()=>document.body.classList.contains('nic-finance-active'));
  await page.reload();await page.waitForSelector('#nicFinanceModule #loan');
  assert.equal(await page.locator('.nic-tile-active').getAttribute('data-calculator'),'finance');
  await page.evaluate(()=>{const root=document.getElementById('nicFinanceModule').shadowRoot;root.getElementById('newCalc').click();if(Number(root.getElementById('interest').value)!==4.09)throw Error('Finance reset must use shared reference');});
  await page.evaluate(()=>{
   const root=document.getElementById('nicFinanceModule').shadowRoot;
   const box=root.querySelector('[data-nic-content-key]');
   if(!box)throw Error('Finance access rules missing');
   const settings=NICSettings.current;
   settings.contentSections[box.dataset.nicContentKey]={visible:false,guestAllowed:false};
   NICContentSections.apply(settings);
   if(!box.hidden||!box.inert)throw Error('Hidden finance content must stay inaccessible');
  });
  assert.deepEqual(errors,[]);
  console.log('Unified navigation passed',width,'same document, all modes, history, direct finance reload');
  await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
