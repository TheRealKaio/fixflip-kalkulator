const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({serviceWorkers:'block'});
  await page.route('**/*',async route=>{
   const u=new URL(route.request().url());
   if(u.hostname!=='localhost')return route.fulfill({json:{user:null,csrf:'test',settings:require('../assets/site-settings.json')}});
   const file=path.join(process.cwd(),'_site',u.pathname.endsWith('/')?u.pathname+'index.html':u.pathname);
   if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
   return route.fulfill({body:fs.readFileSync(file),contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.svg':'image/svg+xml','.png':'image/png'})[path.extname(file)]||'application/octet-stream'});
  });
  await page.goto('http://localhost/finanzierungsrechner/');
  await page.waitForFunction(()=>document.querySelector('[data-finance-id="rateChart"] text'));
  for(const viewport of [{width:320,height:740},{width:390,height:844},{width:844,height:390},{width:390,height:844},{width:768,height:1024},{width:1024,height:768},{width:1440,height:900},{width:1920,height:1080},{width:2560,height:1440}]){
   await page.setViewportSize(viewport);
   for(const size of [14,18,24]){
    await page.evaluate(size=>{const s=JSON.parse(JSON.stringify(NICSettings.current));s.layout.subtextSize=size;NICSettings.save(s);NICSettings.apply(s);},size);
    await page.evaluate(()=>document.fonts.ready);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    const measurements=await page.evaluate(()=>[...document.querySelectorAll('#nicFinanceModule svg.chart')].map(svg=>{
     const labels=[...svg.querySelectorAll('text')].filter(text=>getComputedStyle(text).display!=='none');
     const actual=labels.map(text=>{
      const style=getComputedStyle(text),probe=document.createElement('span');
      probe.textContent=text.textContent;probe.style.cssText='position:absolute;visibility:hidden;white-space:pre;';
      probe.style.setProperty('font-family',style.fontFamily,'important');
      probe.style.setProperty('font-size','var(--nic-subtext-font-size)','important');
      probe.style.setProperty('font-weight',style.fontWeight,'important');
      document.body.append(probe);const expected=probe.getBoundingClientRect().width;probe.remove();
      return {text:text.textContent,actual:text.getBoundingClientRect().width,expected};
     });
     const years=labels.filter(text=>/^\d{4}$/.test(text.textContent));
     return {id:svg.id,height:svg.getBoundingClientRect().height,bounds:svg.getBoundingClientRect().toJSON(),labelBounds:labels.map(text=>({text:text.textContent,...text.getBoundingClientRect().toJSON()})),actual,years:years.map(text=>({label:text.textContent,left:text.getBoundingClientRect().left,right:text.getBoundingClientRect().right})),allYears:[...svg.querySelectorAll('text')].filter(text=>/^\d{4}$/.test(text.textContent)).map(text=>text.textContent)};
    }));
    assert.equal(measurements.length,2);
    for(const chart of measurements){
     assert(chart.actual.length>=2);
     for(const text of chart.actual)assert(Math.abs(text.actual-text.expected)<1,'Rendered SVG differs from HTML subtext: '+JSON.stringify({viewport,size,chart:chart.id,...text}));
     chart.years.forEach((year,i)=>{if(i)assert(year.left>=chart.years[i-1].right+1,'Year labels overlap: '+JSON.stringify({viewport,size,chart}));});
     if(chart.allYears.length){assert.equal(chart.years[0].label,chart.allYears[0]);assert.equal(chart.years.at(-1).label,chart.allYears.at(-1));}
     if(chart.id.endsWith('rateChart')){
      if(viewport.width<=700&&viewport.height>viewport.width)assert(chart.height>=239,'Portrait chart must have at least 240px height');
      for(const label of chart.labelBounds){
       assert(label.left>=chart.bounds.left-1&&label.right<=chart.bounds.right+1,'Axis label clipped horizontally: '+JSON.stringify({viewport,size,label,chart:chart.bounds}));
       assert(label.top>=chart.bounds.top-1&&label.bottom<=chart.bounds.bottom+1,'Axis label clipped vertically: '+JSON.stringify({viewport,size,label,chart:chart.bounds}));
      }
      const differences=chart.years.slice(1).map((year,i)=>Number(year.label)-Number(chart.years[i].label));
      assert(differences.every(diff=>diff===differences[0]),'Year intervals must be uniform: '+JSON.stringify(chart.years));
      const percent=chart.labelBounds.filter(label=>label.text.includes('%'));
      const years=chart.labelBounds.filter(label=>/^\d{4}$/.test(label.text));
      assert(percent.length===5&&years.length>=2,'Expected percent and year axes');
      assert(Math.max(...percent.map(label=>label.bottom))+4<=Math.min(...years.map(label=>label.top)),'Percent and year axes need separate vertical space');
     }

    }
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow');
    console.log('PASS rendered chart typography',viewport.width,viewport.height,size);
   }
  }
  await page.close();
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
