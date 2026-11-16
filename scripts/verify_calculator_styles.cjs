// Compare the externalized cascade with the exact same rules at their old inline positions.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const baselinePath=path.join(process.cwd(),'_site','.calculator-css-baseline.json');
 const baseline=fs.existsSync(baselinePath)?JSON.parse(fs.readFileSync(baselinePath,'utf8')):{};
 const browser=await chromium.launch({headless:true});
 try{
 for(const viewport of [{width:320,height:740},{width:390,height:844},{width:768,height:1024},{width:844,height:390},{width:1024,height:768},{width:1366,height:900},{width:1920,height:1080}]){
  const width=viewport.width;
  const results=[];
  for(const inline of [true,false]){
   const page=await browser.newPage({viewport}),errors=[];
   page.on('pageerror',error=>errors.push(error.message));
   await page.route('**/*',async route=>{
    const u=new URL(route.request().url());
    if(u.hostname==='api.statistiken.bundesbank.de')return route.fulfill({contentType:'text/csv',body:'TIME_PERIOD;OBS_VALUE\n2026-09;4,09'});
    if(u.hostname!=='localhost'&&route.request().resourceType()==='script')return route.fulfill({contentType:'application/javascript',body:''});
    if(u.hostname!=='localhost')return route.fulfill({status:200,json:{user:null,settings:require('../assets/site-settings.json'),csrf:'test'}});
    let name=u.pathname;if(name.endsWith('/'))name+='index.html';
    const file=path.join(process.cwd(),'_site',name);
    if(!fs.existsSync(file))return route.fulfill({status:404,body:''});
    let body=fs.readFileSync(file);
    if(inline&&file.endsWith('.html')){assert(/calculator-(?:shared|own|rent|flip|budget)-/.test(body.toString()),'Missing external CSS fixtures');body=Buffer.from(body.toString().replace(/<link rel="stylesheet"( id="[^"]+")? href="\/(calculator-(?:shared|own|rent|flip|budget)-[a-f0-9]{16}(?:\.[a-f0-9]{16})?\.css)">/g,(_,id,css)=>'<style'+(id||'')+'>'+(baseline[css.replace(/\.[a-f0-9]{16}\.css$/,'.css')]??fs.readFileSync(path.join(process.cwd(),'_site',css),'utf8'))+'</style>'));assert(!/href="\/calculator-(?:shared|own|rent|flip|budget)-/.test(body.toString()), 'Inline baseline reconstruction failed');}
    return route.fulfill({body,contentType:({'.html':'text/html','.css':'text/css','.js':'application/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'})[path.extname(file)]||'text/plain'});
   });
   await page.goto('http://localhost/budget/');
   await page.getByRole('button',{name:'Ablehnen',exact:true}).click();
   await page.waitForFunction(()=>window.NICReferenceInterest?.rate===4.09&&window.NICCalculators?.active==='budget');
   const snapshots=[];
   for(const key of ['budget','own','rent','flip','finance']){
    await page.evaluate(k=>window.NICCalculatorNavigation.select(k),key);
    await page.waitForFunction(k=>window.NICCalculators?.active===k&&document.body.dataset.calculator===k&&document.querySelector('.nic-tile-active')?.dataset.calculator===k,key);
    // Let legacy calculator-specific DOM updates complete before comparing
    // inline/external CSS. The comparison must inspect the same mode on both.
    await page.waitForTimeout(120);
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    if(key==='finance'){
     const tracks=await page.evaluate(()=>{const count=selector=>{const value=getComputedStyle(document.querySelector(selector)).gridTemplateColumns;return value.match(/\d+(?:\.\d+)?px/g)?.length||0};return {results:count('#nicFinanceModule .finance-result-grid'),scenarios:count('#nicFinanceModule .refinance-grid')}});
     assert.equal(tracks.results,width<=700?1:2,'Financing result tiles must stack on mobile at '+width+'px: '+JSON.stringify(tracks));
     assert.equal(tracks.scenarios,width<=700?1:3,'Refinancing scenarios must stack on mobile at '+width+'px: '+JSON.stringify(tracks));
     const labelValue=await page.evaluate(()=>[...document.querySelectorAll('#nicFinanceModule .finance-result-grid>.kpi')].map(card=>{const label=card.querySelector('span:first-child').getBoundingClientRect(),value=card.querySelector('strong').getBoundingClientRect();return {label:label.toJSON(),value:value.toJSON()}}));
     assert.equal(labelValue.length,4,'All four financing result tiles have label and value at '+width+'px');
     assert(labelValue.every(item=>item.value.top>=item.label.bottom+2),'Financing tile values have visible separation below their labels at '+width+'px: '+JSON.stringify(labelValue));
     await page.waitForFunction(()=>document.querySelector('#nicFinanceModule #nicFinance-rateChart text'));
     await page.evaluate(()=>document.documentElement.style.setProperty('--nic-subtext-font-size','18px'));
     await page.evaluate(()=>document.fonts.ready);
     await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
     const chart=await page.evaluate(()=>{const svg=document.querySelector('#nicFinanceModule #nicFinance-rateChart');return [...svg.querySelectorAll('text')].map(node=>{const box=node.getBBox();return {text:node.textContent,x:box.x,right:box.x+box.width}})});
     assert(chart.length>=5,'Rate chart axis/year labels rendered at '+width+'px');
     assert(chart.every(label=>label.x>=-0.5&&label.right<=560.5),'Rate chart labels stay inside the SVG at '+width+'px: '+JSON.stringify(chart));
    }
    snapshots.push(await page.evaluate(()=>{
     const props=['display','width','height','fontSize','fontFamily','fontWeight','lineHeight','color','backgroundColor','padding','margin','borderWidth','borderRadius','gridTemplateColumns','gap'];
     const nodes=[...document.body.querySelectorAll('[id]')];if(document.getElementById('nicFinanceModule')?.shadowRoot)throw Error('Finance must stay in the shared DOM');
     // Dynamically-rendered content can change child count and order between
     // separate page loads. Compare matching, identified elements instead.
     // Retain actual computed CSS values rather than raw stylesheet declarations.
     const stableProps=props.filter(prop=>prop!=='height');
     return Object.fromEntries(nodes.filter(el=>el.getClientRects().length&&el.id).map(el=>[el.id,[el.tagName,...stableProps.map(p=>getComputedStyle(el)[p])]]));
    }));
   }
   assert.deepEqual(errors,[]);results.push(snapshots);await page.close();
  }
  for(let mode=0;mode<5;mode++){
   const inline=results[0][mode],external=results[1][mode];
   const shared=Object.keys(inline).filter(id=>Object.hasOwn(external,id));
   assert(shared.length>=40,`CSS comparison needs broad identified-element coverage at ${width}px mode ${mode}: ${shared.length}`);
   for(const id of shared){
    assert.deepEqual(external[id],inline[id],`CSS extraction differs for #${id} at ${width}px mode ${mode}`);
   }
  }
  console.log(`CSS cascade equivalence passed: all five calculators at ${width}px`);
 }
 }finally{await browser.close();}
 if(fs.existsSync(baselinePath))fs.unlinkSync(baselinePath);
})().catch(error=>{console.error(error);process.exit(1);});
