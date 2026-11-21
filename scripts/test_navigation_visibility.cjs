#!/usr/bin/env node
'use strict';
/* Regression checks: separate homepage bar, six-tile calculator bar, per-page dropdown. */
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const read=file=>fs.readFileSync(file,'utf8');
const settings=read('assets/site-settings.js');
const nav=read('assets/unified-calculator-navigation.js');
const admin=read('assets/admin.js');
const adminHtml=read('assets/admin.html');
const backend=read('server/webspace/immocheck-private/app.php');
const gate=read('server/webspace/immocheck-web/content-gate.php');
const css=read('assets/homepage.css');
const start=settings.indexOf('  const navigationItems=');
const end=settings.indexOf('  const layoutDefaults=',start);
assert(start>=0&&end>start,'Navigation configuration must be available before layout');
const context=vm.createContext({});
vm.runInContext(settings.slice(start,end)+'\nthis.test={navigationItems,navigationSections,navigationVisibility};',context);
const {navigationItems,navigationSections,navigationVisibility}=context.test;
assert.deepEqual(Array.from(navigationItems),['budget','own','rent','flip','finance','settlement']);
assert.deepEqual(Array.from(navigationSections),['home','calculator','dropdownHome','dropdownOther']);
for(const input of [undefined,{},null]){
 const n=navigationVisibility(input);
 for(const section of navigationSections)for(const screen of ['mobile','desktop']){
  const keys=section.startsWith('dropdown')?['dropdown']:navigationItems;
  for(const key of keys)assert.equal(n[section][screen][key],true,section+' '+screen+' '+key);
 }
}
const example={home:{mobile:{budget:false},desktop:{rent:false}},
 calculator:{mobile:{budget:true},desktop:{rent:true,flip:false}},
 dropdownHome:{mobile:{dropdown:false},desktop:{dropdown:true}},
 dropdownOther:{mobile:{dropdown:true},desktop:{dropdown:false}}};
const n=navigationVisibility(example);
assert.equal(n.home.mobile.budget,false);
assert.equal(n.calculator.mobile.budget,true);
assert.equal(n.home.desktop.rent,false);
assert.equal(n.calculator.desktop.rent,true);
assert.equal(n.calculator.desktop.flip,false);
assert.equal(n.dropdownHome.mobile.dropdown,false);
assert.equal(n.dropdownOther.mobile.dropdown,true);
assert.equal(n.dropdownOther.desktop.dropdown,false);
const legacy=navigationVisibility({mobile:{budget:false,dropdown:false},desktop:{budget:true,dropdown:true}});
assert.equal(legacy.home.mobile.budget,false);
assert.equal(legacy.calculator.mobile.budget,false);
assert.equal(legacy.dropdownHome.mobile.dropdown,false);
assert.equal(legacy.dropdownOther.mobile.dropdown,false);
assert.ok(settings.includes('s.navigationVisibility=navigationVisibility(raw.navigationVisibility)'));
assert.ok(settings.includes('window.NICNavigationVisibility?.refresh()'));
assert.ok(adminHtml.indexOf('id="nicNavigationVisibility"')<adminHtml.indexOf('<h3>Projektdokumentation'));
assert.ok(admin.includes('navigationSectionTitles'));
assert.ok(admin.includes('S.navigationSections'));
assert.ok(admin.includes('raw.navigationVisibility[section][screen][key]'));
assert.ok(nav.includes("tile.href='/nebenkostenabrechnung/'"));
assert.ok(nav.includes('const canonicalTileRoutes='));
assert.ok(nav.includes("heading==='sanierung'"));
assert.ok(nav.includes("navigationAllowed(key,screen,'home')"));
assert.ok(nav.includes("navigationAllowed(key,screen,'calculator')"));
assert.ok(nav.includes("dropdownSection=isHome?'dropdownHome':'dropdownOther'"));
assert.ok(nav.includes('nic-global-dropdown-shell'));
assert.ok(nav.includes('function updateHomepageNavigationVisibility()'));
assert.ok(nav.includes('window.NICNavigationVisibility={refresh:sync}'));
assert.ok(css.includes('repeat(auto-fit,minmax('),'Remaining cards must reclaim freed space');
assert.ok(css.includes('.app>.hero>.nic-global-dropdown-shell'));
assert.ok(css.includes('white-space:nowrap!important'));
assert.ok(backend.includes("'home','calculator','dropdownHome','dropdownOther'"));
assert.ok(gate.includes('data-nic-nav-context'));
const navigationGate=gate.slice(gate.indexOf('$navVisibility ='),gate.indexOf('$output = $dom->saveHTML();'));
assert(!navigationGate.includes('$option->parentNode?->removeChild($option)'),'Menu visibility must never delete calculator radio inputs');
assert(nav.includes("if(tile.querySelector('input')){tile.hidden=true"),'Legacy cleanup must preserve controls inside hidden tiles');
assert(nav.includes("heading.textContent='Eigenheim'"),'Prerendered calculator bar must show Eigenheim');
assert(admin.includes("own:'Eigenheim'"),'Admin navigation name must match Eigenheim');
const registry=JSON.parse(read('assets/calculators.json'));
assert.equal(registry.calculators.find(item=>item.id==='own').label,'Eigenheim','Calculator registry retains its short internal label');
assert(read('assets/homepage.html').includes('<strong>Eigenheim berechnen</strong>'),'Homepage tile must match the Eigenheim dropdown entry');
assert(read('scripts/build_unified_navigation.py').includes(">Eigenheim<"),'Static calculator tiles must use Eigenheim on first load');
const titleScript=nav.match(/const calculatorTileTitles=\{([\s\S]*?)\n \};/);
assert(titleScript,'Separate two-line calculator title map is required');
for(const key of ['budget','own','rent','flip','finance','settlement']){
 assert(new RegExp(key+':\\[').test(titleScript[1]),'Missing compact label: '+key);
}
const desiredLabels={
 budget:'Dein Budget berechnen',
 own:'Eigenheim berechnen',
 rent:'Vermietung als Kapitalanlage',
 flip:'Fix und Flip Projekt',
 finance:'Finanzierung & Restschuld',
 settlement:'Nebenkosten abrechnen'
};
for(const [key,label] of Object.entries(desiredLabels)){
 const match=titleScript[1].match(new RegExp('(?:^|\\n)\\s*'+key+':\\[([^\\]]+)\\]'));
 assert(match,'Expected title segments for '+key);
 const actual=Array.from(match[1].matchAll(/'([^']+)'/g),m=>m[1]).join(' ');
 assert.equal(actual,label,'Visible navigation title for '+key);
}
assert(nav.includes("option.textContent=calculatorTileTitles[item.id]?.join(' ')||item.label;"),'Dropdown options must inherit calculator button titles');
assert(nav.includes("settlementOption.textContent=calculatorTileTitles.settlement.join(' ');"),'Settlement dropdown option must inherit button title');
assert(nav.includes("name.textContent=option.textContent;"),'Visible custom dropdown rows must mirror option labels');
assert(nav.includes("picker.selectedOptions[0]?.textContent"),'Selected dropdown caption must mirror option labels');
assert(nav.includes('formatCalculatorTiles();'),'Calculator titles must be formatted at initialisation and refresh');
assert(css.includes('Calculator pages only: compact equal-height six-tile bar'),'Compact card CSS must be scoped');
assert(css.includes('.deal-type-card > .deal-type-row > .deal-type-option small'),'Calculator descriptions must be hidden');
assert(!css.includes('#nic-home-intro .nic-home-options > .deal-type-option small'),'Homepage descriptions must be preserved');
assert(read('assets/homepage.html').includes('<small>'),'Homepage descriptions must remain present');
assert.ok(gate.includes("=== 'sanierung'"));
console.log('Navigation visibility regression PASS: 28 controls, 4 groups, legacy migration, Sanierung cleanup, fluid tiles, shared dropdown.');
