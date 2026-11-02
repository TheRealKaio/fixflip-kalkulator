'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 const page=await browser.newPage({serviceWorkers:'block'});
 await page.route('**/jspdf.umd.min.js',r=>r.fulfill({path:'/tmp/nic-pdf-check/node_modules/jspdf/dist/jspdf.umd.min.js',contentType:'application/javascript'}));
 await page.route('http://127.0.0.1:8766/**',async r=>{
  let name=decodeURIComponent(new URL(r.request().url()).pathname);if(name.endsWith('/'))name+='index.html';
  const file=path.join(process.cwd(),'_site',name),ext=path.extname(file);
  if(!fs.existsSync(file))return r.fulfill({status:404,body:''});
  let body=fs.readFileSync(file);
  if(ext==='.html')body=Buffer.from(body.toString().replace('async function rentalPdf(kind){','window.NICQARental=buildRentalPdf;\nasync function rentalPdf(kind){'));
  return r.fulfill({body,contentType:({'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.svg':'image/svg+xml'})[ext]||'application/octet-stream'});
 });
 fs.mkdirSync('tmp/pdfs',{recursive:true});
 for(const slug of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']){
  await page.goto('http://127.0.0.1:8766/'+slug+'/',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.NICPDF&&window.NICSettings&&window.jspdf);
  for(const size of [16,20]){
   const pdf=await page.evaluate(async({slug,size})=>{
    const s=JSON.parse(JSON.stringify(NICSettings.current));s.layout.bodySize=size;s.layout.h2=size===16?18:24;s.layout.font=size===16?'system':'georgia';NICSettings.save(s);NICSettings.apply(s);await NICPDF.prepare();
    const doc=slug==='budget'?buildBudgetPdf():slug==='vermietung'?NICQARental():slug==='finanzierungsrechner'?NICPDF.financeDocument({loan:300000,interest:4,repay:2,extra:5,years:10}):buildPdf();
    return {pages:doc.getNumberOfPages(),data:btoa(doc.output())};
   },{slug,size});
   assert(pdf.pages>=2);fs.writeFileSync(`tmp/pdfs/${slug}-${size}.pdf`,Buffer.from(pdf.data,'base64'));console.log('PASS full report',slug,size,pdf.pages,'pages');
  }
  await page.evaluate(()=>NICSettings.discard());
 }
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
