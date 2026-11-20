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
assert.ok(gate.includes("=== 'sanierung'"));
console.log('Navigation visibility regression PASS: 28 controls, 4 groups, legacy migration, Sanierung cleanup, fluid tiles, shared dropdown.');
