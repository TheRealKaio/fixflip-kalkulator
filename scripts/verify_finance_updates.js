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
const html=fs.readFileSync(site+'/finanzierungsrechner/index.html','utf8'),from=html.indexOf('function calculate(){'),to=html.indexOf('\nfunction drawRates',from),els={};const $=id=>els[id]??=( {textContent:'',innerHTML:''} );
let values={loan:300000,interest:4,repay:2,extra:5,years:10};const fmt=new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2});
const ctx={$: $,values:()=>values,money:x=>fmt.format(x),euro:x=>fmt.format(x),pct:x=>x+' %',grid:()=>'',line:()=>'',drawRates(){},localStorage:{setItem(){}},F:'test',Math};vm.createContext(ctx);vm.runInContext(html.slice(from,to),ctx);vm.runInContext('calculate()',ctx);
assert($('monthlyInterestValue').textContent.includes(fmt.format(1000)));assert($('monthlyRepaymentValue').textContent.includes(fmt.format(500)));assert($('annualExtraAmount').textContent.includes(fmt.format(15000)));assert(html.includes('Finanzierung neu kalkulieren'));assert(!html.includes('svg text{font:11px'));assert.equal($('rate').textContent,fmt.format(1500));
values={loan:0,interest:4,repay:2,extra:5,years:10};vm.runInContext('calculate()',ctx);for(const id of ['monthlyInterestValue','monthlyRepaymentValue','annualExtraAmount'])assert($(id).textContent.includes(fmt.format(0)));
assert(html.includes('Mtl. Kreditrate inkl. Tilgung'));assert(!html.includes('annualExtraValue'));assert(html.includes('<strong id="annualExtraAmount"'));assert(html.includes('<strong id="monthlyInterestValue"'));assert(html.includes('<strong id="monthlyRepaymentValue"'));assert(!html.includes('class="action-bar"'));assert(html.includes('data-nic-page="finance"'));assert(html.includes('Finanzierungsrechner: Rate &amp; Restschuld'));
const config=JSON.parse(fs.readFileSync(site+'/site-settings.json'));assert(config.meta.finance.title);assert(config.meta.finance.description);
for(const path of ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner'])assert(fs.readFileSync(site+'/'+path+'/index.html','utf8').includes('/calculator-actions.'));
console.log('Finance updates passed: first visit/remembered selection/deep links; initial monthly interest/repayment/annual extra and zero loan; static finance metadata and shared action CSS.');
