const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 fs.mkdirSync('tmp',{recursive:true});
 try{
  for(const viewport of [{width:1440,height:900},{width:390,height:844},{width:844,height:390},{width:768,height:1024}]){
   const page=await browser.newPage({viewport,serviceWorkers:'block'});
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
    if(u.hostname!=='localhost'&&route.request().resourceType()==='script')return route.fulfill({contentType:'text/javascript',body:''});
    if(u.hostname!=='localhost')return route.fulfill({json:{user:null,csrf:'fixture',settings:require('../assets/site-settings.json')}});
    let name=u.pathname;if(name.endsWith('/'))name+='index.html';
    const file=path.join(process.cwd(),'_site',name);
    if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
    return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(file)]||'application/octet-stream'});
   });
   for(const slug of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']){
    await page.goto('http://localhost/'+slug+'/',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>document.documentElement.dataset.nicLayoutReady==='ready');
    const reject=page.getByRole('button',{name:'Ablehnen',exact:true});
    if(await reject.isVisible())await reject.click();
    for(const position of ['top','footer','end']){
     await page.evaluate(position=>{
      const footer=document.querySelector('.app>.footer-note,.app>.nic-shared-footer');
      const y=position==='top'?0:position==='end'?document.documentElement.scrollHeight:footer.getBoundingClientRect().top+scrollY-innerHeight*.7;
      window.scrollTo(0,y);
     },position);
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     const actual=await page.evaluate(()=>{
      const bar=document.querySelector('.app>.bottom.nic-actions-above-footer');
      const footer=document.querySelector('.app>.footer-note,.app>.nic-shared-footer');
      const actions=bar.querySelector('.bottom-actions');
      const a=actions.getBoundingClientRect(),f=footer.getBoundingClientRect(),style=getComputedStyle(bar);
      const zoom=parseFloat(getComputedStyle(document.body).zoom)||1;
      return {gap:f.top-a.bottom,minimum:(parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nic-content-footer-gap'))||16)*zoom,
       viewportBottom:innerHeight,footerBottom:f.bottom,margin:parseFloat(style.marginBottom),position:style.position,bottom:style.bottom,barBottom:a.bottom,footerTop:f.top};
     });
     const mobile=viewport.width===390||viewport.width===844;
     assert.equal(actual.position,mobile?'fixed':'sticky');
     assert.equal(actual.bottom,'5px');
     if(mobile){
      assert(Math.abs(actual.viewportBottom-actual.barBottom-5)<1,'Mobile actions stay at the viewport bottom: '+JSON.stringify({viewport,slug,position,actual}));
      if(position==='end')assert(actual.footerBottom<actual.barBottom-48,'Footer can scroll clear of the fixed actions');
     }else{
     assert(actual.margin>=16,'Missing layout footer margin: '+JSON.stringify({viewport,slug,position,actual}));
     assert(actual.gap>=actual.minimum-.5,'Action bar touches/overlaps footer: '+JSON.stringify({viewport,slug,position,actual}));
     }
     if(position==='footer')await page.screenshot({path:'tmp/action-footer-'+viewport.width+'-'+viewport.height+'-'+slug+'.png'});
    }
    console.log('PASS action/footer gap',viewport.width,viewport.height,slug);
   }
   await page.close();
  }
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
