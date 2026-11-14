// Compare the externalized cascade with the exact same rules at their old inline positions.
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
(async()=>{
 const baselinePath=path.join(process.cwd(),'_site','.calculator-css-baseline.json');
 const baseline=fs.existsSync(baselinePath)?JSON.parse(fs.readFileSync(baselinePath,'utf8')):{};
 const browser=await chromium.launch({headless:true});
 try{
 for(const width of [320,390,1440]){
  const results=[];
  for(const inline of [true,false]){
   const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
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
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    if(key==='finance'){
     const tracks=await page.evaluate(()=>{const count=selector=>{const value=getComputedStyle(document.querySelector(selector)).gridTemplateColumns;return value.match(/\d+(?:\.\d+)?px/g)?.length||0};return {results:count('#nicFinanceModule .finance-result-grid'),scenarios:count('#nicFinanceModule .refinance-grid')}});
     assert.equal(tracks.results,width<=700?1:2,'Financing result tiles must stack on mobile at '+width+'px: '+JSON.stringify(tracks));
     assert.equal(tracks.scenarios,width<=700?1:3,'Refinancing scenarios must stack on mobile at '+width+'px: '+JSON.stringify(tracks));
    }
    snapshots.push(await page.evaluate(()=>{
     const props=['display','width','height','fontSize','fontFamily','fontWeight','lineHeight','color','backgroundColor','padding','margin','borderWidth','borderRadius','gridTemplateColumns','gap'];
     const nodes=[...document.body.querySelectorAll('*')];if(document.getElementById('nicFinanceModule')?.shadowRoot)throw Error('Finance must stay in the shared DOM');
     return nodes.filter(el=>!['STYLE','LINK','SCRIPT'].includes(el.tagName)&&el.getClientRects().length).map(el=>[el.tagName,el.id,...props.map(p=>getComputedStyle(el)[p])]);
    }));
   }
   assert.deepEqual(errors,[]);results.push(snapshots);await page.close();
  }
  assert.deepEqual(results[1],results[0],`CSS extraction must retain computed layout at ${width}px`);
  console.log(`CSS cascade equivalence passed: all five calculators at ${width}px`);
 }
 }finally{await browser.close();}
 if(fs.existsSync(baselinePath))fs.unlinkSync(baselinePath);
})().catch(error=>{console.error(error);process.exit(1);});
