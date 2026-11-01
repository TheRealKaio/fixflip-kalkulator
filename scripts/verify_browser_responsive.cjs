const { chromium, devices } = require('playwright');
const fs = require('node:fs');
const paths = ['/budget/','/eigennutzung/','/vermietung/','/fix-flip/','/finanzierungsrechner/'];
const variants = [{ name:'desktop', viewport:{width:1440,height:900},isMobile:false }, {name:'smartphone',...devices['iPhone 13']}];
(async()=>{
 const browser=await chromium.launch({headless:true});
 const failures=[];fs.mkdirSync('tmp/browser-qa',{recursive:true});
 for(const variant of variants){
  const context=await browser.newContext(variant.name==='desktop'?{viewport:variant.viewport}:variant);
  for(const path of paths){
   const page=await context.newPage();
   const errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   const url='http://127.0.0.1:8765'+path;
   try{
    const response=await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
    if(!response || response.status()!==200)throw Error('HTTP '+response?.status());
    await page.waitForTimeout(1500);
    const result=await page.evaluate(()=>{
      const nav=document.querySelector('.nic-step-nav');
      const buttons=[...document.querySelectorAll('.nic-step-dot')];
      const visibleCards=[...document.querySelectorAll('.nic-step-enabled > .card:not(.nic-step-inactive)')];
      return {nav:!!nav,stepCount:buttons.length,visibleCards:visibleCards.length,overflow:document.documentElement.scrollWidth>innerWidth+5,overflowNodes:[...document.querySelectorAll('body *')].filter(el=>{const r=el.getBoundingClientRect();return r.width>0&&(r.right>innerWidth+5||r.left < -5)}).slice(0,12).map(el=>({tag:el.tagName,id:el.id,cls:String(el.className).slice(0,80),right:Math.round(el.getBoundingClientRect().right)})),loginLabel:!!document.querySelector('.nic-account-label')};
    });
    if(!result.nav)throw Error('Horizontal step navigation missing');
    if(path==='/budget/'&&result.stepCount!==6)throw Error('Expected 6 Budget steps; found '+result.stepCount);
    if(result.stepCount<2)throw Error('Less than 2 steps');
    if(result.overflow)throw Error('Horizontal viewport overflow: '+JSON.stringify(result.overflowNodes));
    if(!result.loginLabel)throw Error('Login label missing');
    await page.locator('.nic-step-next').evaluate(button=>button.click());
    const counter=await page.locator('.nic-step-count').innerText();
    if(!counter.includes('Schritt 2'))throw Error('Next button did not advance');
    await page.locator('.nic-step-prev').evaluate(button=>button.click());
    await page.screenshot({path:'tmp/browser-qa/'+variant.name+'-'+path.split('/')[1]+'.png',fullPage:true});
    if(errors.length)throw Error('Browser JS error: '+errors.join('; '));
    console.log('PASS',variant.name,path,JSON.stringify(result));
   }catch(e){failures.push(variant.name+' '+path+': '+e.message);console.error('FAIL',variant.name,path,e.message);
    await page.screenshot({path:'tmp/browser-qa/fail-'+variant.name+'-'+path.split('/')[1]+'.png',fullPage:true}).catch(()=>{});
   }finally{await page.close();}
  }
  await context.close();
 }
 await browser.close();
 if(failures.length){console.error(failures.join('\n'));process.exitCode=1;}
})().catch(e=>{console.error(e);process.exitCode=1;});
