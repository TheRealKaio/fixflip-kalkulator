const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const site=process.argv[2]||'_site',start=fs.readFileSync('assets/calculator-start.js','utf8');
function open(path,store={},hash='',search=''){
 const replaced=[];const ctx={Object,location:{pathname:path,hash,search,replace:u=>replaced.push(u)},localStorage:{getItem:k=>store[k]??null,setItem:(k,v)=>store[k]=v}};vm.runInNewContext(start,ctx);return {replaced,store};
}
assert.deepEqual(open('/').replaced,['/finanzierungsrechner/']);
for(const [key,path]of Object.entries({budget:'/budget/',own:'/eigennutzung/',rent:'/vermietung/',flip:'/fix-flip/',finance:'/finanzierungsrechner/'})){
 const store={};assert.deepEqual(open(path,store).replaced,[]);assert.equal(store.nic_last_calculator_v1,key);assert.deepEqual(open('/',store).replaced,[path]);assert.deepEqual(open(path,store).replaced,[]);
}
assert.deepEqual(open('/',{},'#admin').replaced,[]);assert.deepEqual(open('/',{},'#datenschutz').replaced,[]);assert.deepEqual(open('/',{},'','?utm_source=test').replaced,['/finanzierungsrechner/?utm_source=test']);
const html=fs.readFileSync(site+'/finanzierungsrechner/index.html','utf8'),from=html.indexOf('function calculate(){'),to=html.indexOf('\nfunction drawRates',from),els={};const $=id=>els[id]??=( {textContent:'',innerHTML:'',value:'0',setAttribute(){}} );
let values={loan:300000,interest:4,repay:2,extra:5,years:10};const fmt=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2}),whole=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:0});
const ctx={$: $,values:()=>values,money:x=>fmt.format(x),euro:x=>whole.format(x),pct:x=>x+' %',grid:()=>'',line:()=>'',drawRates(){},localStorage:{setItem(){}},F:'test',Math,refinanceBase:null,refinanceDistance:null};vm.createContext(ctx);vm.runInContext(html.slice(from,to),ctx);vm.runInContext('calculate()',ctx);
assert($('monthlyInterestValue').textContent.includes(fmt.format(1000)));assert($('monthlyRepaymentValue').textContent.includes(fmt.format(500)));assert($('annualExtraAmount').textContent.includes(fmt.format(15000)));assert(html.includes('Finanzierung neu kalkulieren'));assert(!html.includes('svg text{font:11px'));assert.equal($('rate').textContent,whole.format(1500));
let balance=300000;for(let month=1;month<=120;month++){balance=Math.max(0,balance+balance*4/1200-1500);if(month%12===0)balance=Math.max(0,balance-15000);}
for(const [id,delta] of [['refinanceFalls',-1.5],['refinanceStays',0],['refinanceRises',2]])assert.equal($(id).textContent,whole.format(balance*(4+delta+2)/1200));
const stableScenario=$('refinanceStays').textContent;
assert.equal(Number($('refinanceChange').value),4);
for(const selected of [0,1,4,7,10,2,8,4]){
 $('refinanceChange').value=String(selected);
 vm.runInContext('calculate()',ctx);
 const falls=selected<4?selected:2.5,rises=selected>4?selected:6;
 assert.equal($('refinanceStays').textContent,stableScenario);
 assert.equal($('refinanceFalls').textContent,whole.format(balance*(falls+2)/1200));
 assert.equal($('refinanceRises').textContent,whole.format(balance*(rises+2)/1200));
 assert.equal($('refinanceFallsInterest').textContent,falls+' % Sollzins p. a.');
 assert.equal($('refinanceRisesInterest').textContent,rises+' % Sollzins p. a.');
}
for(const interest of [0,1,5,9,10]){
 values={...values,interest};vm.runInContext('calculate()',ctx);
 assert.equal(Number($('refinanceChange').value),interest);
 assert.equal($('refinanceFallsInterest').textContent,Math.max(0,interest-1.5)+' % Sollzins p. a.');
 assert.equal($('refinanceRisesInterest').textContent,Math.min(10,interest+2)+' % Sollzins p. a.');
}
values={loan:0,interest:4,repay:2,extra:5,years:10};vm.runInContext('calculate()',ctx);for(const id of ['monthlyInterestValue','monthlyRepaymentValue','annualExtraAmount'])assert($(id).textContent.includes(fmt.format(0)));for(const id of ['refinanceFalls','refinanceStays','refinanceRises'])assert.equal($(id).textContent,whole.format(0));
assert(html.includes('Mtl. Kreditrate inkl. Tilgung'));assert(!html.includes('annualExtraValue'));assert(html.includes('<strong id="annualExtraAmount"'));assert(html.includes('<strong id="monthlyInterestValue"'));assert(html.includes('<strong id="monthlyRepaymentValue"'));assert(!html.includes('class="action-bar"'));assert(html.includes('data-nic-page="finance"'));assert(html.includes('Finanzierungsrechner: Rate &amp; Restschuld'));
const admin=fs.readFileSync(site+'/admin.html','utf8');assert(admin.includes('href="/docs/README-Projektdokumentation.pdf"'));assert(fs.existsSync(site+'/docs/README-Projektdokumentation.pdf'));
assert(html.includes('.refinance-grid .kpi:nth-child(2){background:#fef3c7'));assert(html.includes('.refinance-grid .kpi:nth-child(3){background:#fee2e2'));
const config=JSON.parse(fs.readFileSync(site+'/site-settings.json'));assert(config.meta.finance.title);assert(config.meta.finance.description);
for(const path of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner'])assert(fs.readFileSync(site+'/'+path+'/index.html','utf8').includes('/calculator-actions.'));
for(const label of ['Zinssatz fällt','Zinssatz stabil','Zinssatz steigt']) assert(html.includes('<span>'+label+'</span>'),`finance scenario label missing: ${label}`);
const reportSource=fs.readFileSync('assets/pdf-reports.js','utf8');
for(const label of ['Zinssatz fällt','Zinssatz stabil','Zinssatz steigt']) assert(reportSource.includes(label),`finance report scenario label missing: ${label}`);
const docs=fs.readFileSync('docs/PROJEKTSTATUS.md','utf8');
const ordered=['## 1. Aktueller Stand','## 2. Navigation und Layoutregeln','## 3. CSS- und PDF-Regeln','## 4. Formeln und Berechnungsregeln','## 5. Standardwerte und Eingaben','## 6. Build, Tests und Veröffentlichung','## 7. Offene Aufgaben'];
const sectionPositions=ordered.map(section=>docs.indexOf(section));
assert(sectionPositions.every((position,index)=>position>=0&&(index===0||position>sectionPositions[index-1])),'project documentation sections must follow the agreed order');
assert(docs.includes('### 4.6 Anschlussfinanzierung')&&docs.includes('### 4.7 Historische Hypothekenzinsen'),'finance formulas must occupy sections 4.6 and 4.7');
console.log('Finance updates passed: first visit/remembered selection/deep links; initial monthly interest/repayment/annual extra and zero loan; static finance metadata and shared action CSS.');
