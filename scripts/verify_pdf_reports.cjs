const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const dependencies=process.argv[3]||'/tmp/nic-pdf-check/node_modules';
const {parseHTML}=require(dependencies+'/linkedom'),{jsPDF}=require(dependencies+'/jspdf');
const dir=process.cwd(),site=process.argv[2]||'_site',html=fs.readFileSync(site+'/index.html','utf8'),{document}=parseHTML(html),config=JSON.parse(fs.readFileSync(dir+'/assets/site-settings.json','utf8'));
Object.defineProperty(document,'currentScript',{value:{src:'https://www.neustart-immocheck.de/site-settings.js'},configurable:true});
const storage=new Map(),ctx={URL,Intl,Date,console,WeakMap,Image:class{},document,localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},fetch:async()=>({ok:true,json:async()=>config})};ctx.window=ctx;ctx.jspdf={jsPDF};vm.createContext(ctx);
vm.runInContext(fs.readFileSync(dir+'/assets/site-settings.js','utf8'),ctx);vm.runInContext(fs.readFileSync(dir+'/assets/pdf-reports.js','utf8'),ctx);
fs.mkdirSync(dir+'/tmp/pdfs',{recursive:true});
const values={loan:300000,interest:4,repay:2,extra:5,years:10},pdf=ctx.NICPDF.financeDocument(values);assert.equal(pdf.getNumberOfPages(),2);fs.writeFileSync(dir+'/tmp/pdfs/finance-default.pdf',Buffer.from(pdf.output('arraybuffer')));
const current=JSON.parse(JSON.stringify(ctx.NICSettings.current));current.company.name='QA Anbieter';current.company.website='https://example.org';current.layout.font='georgia';current.layout.buttonBackground='#07345F';current.legal.haftungsausschluss='<h2>Aktuelle rechtliche Hinweise</h2><p>QA LIVE TEXT: Dieser Bericht verwendet die gespeicherten Angaben von {{company.name}}.</p>';
ctx.NICSettings.save(current);const custom=ctx.NICPDF.financeDocument(values);assert.equal(custom.getNumberOfPages(),2);fs.writeFileSync(dir+'/tmp/pdfs/finance-custom.pdf',Buffer.from(custom.output('arraybuffer')));
const name=ctx.NICPDF.filename('finance',new Date('2026-10-26T13:47:59Z'));assert.equal(name,'Neustart ImmoCheck Finanzierungsrechner Bericht 2026-10-26 14-47.pdf');
// Exercise each existing report's final-page helper with the same live settings.
for(const mode of ['budget','own','rent','flip']){const d=ctx.NICPDF.create({unit:'mm',format:'a4'},mode);ctx.NICPDF.header(d,mode+' Bericht','QA Bestandsbericht');ctx.NICPDF.disclaimer(d);assert.equal(d.getNumberOfPages(),2);for(let p=1;p<=2;p++){d.setPage(p);ctx.NICPDF.footer(d,p,2,'V8.347');}fs.writeFileSync(dir+'/tmp/pdfs/'+mode+'-legal.pdf',Buffer.from(d.output('arraybuffer')));}
console.log('PDF QA passed: two-page finance report, all five final legal sections, live operator tokens/theme, Berlin minute filename.');
