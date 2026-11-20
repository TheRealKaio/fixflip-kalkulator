#!/usr/bin/env node
'use strict';
/* Regression guard for the shared six-tile navigation. No browser or network needed. */
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
const navItems=['budget','own','rent','flip','finance','settlement','dropdown'];
const snippet=settings.match(/  const navigationItems=\[[^;]+;\s*function navigationVisibility\(raw\)\{[\s\S]*?\n  \}/);
assert.ok(snippet,'Navigation default/normalization function missing');
const context=vm.createContext({});
vm.runInContext(snippet[0]+'\nthis.run=navigationVisibility;this.keys=navigationItems;',context);
assert.deepEqual(Array.from(context.keys),navItems);
for(const input of [undefined,{},null]) {
 const output=JSON.parse(JSON.stringify(context.run(input)));
 for(const scope of ['mobile','desktop'])for(const key of navItems)assert.equal(output[scope][key],true);
}
const example={mobile:{budget:false,dropdown:true},desktop:{budget:true,dropdown:false}};
const normalized=JSON.parse(JSON.stringify(context.run(example)));
assert.equal(normalized.mobile.budget,false);
assert.equal(normalized.desktop.budget,true);
assert.equal(normalized.mobile.dropdown,true);
assert.equal(normalized.desktop.dropdown,false);
assert.equal(normalized.mobile.settlement,true);
assert.ok(settings.includes('s.navigationVisibility=navigationVisibility(raw.navigationVisibility)'));
assert.ok(settings.includes('window.NICNavigationVisibility?.refresh()'));
assert.ok(adminHtml.indexOf('id="nicNavigationVisibility"')<adminHtml.indexOf('<h3>Projektdokumentation'));
assert.ok(admin.includes("for(const screen of ['mobile','desktop'])for(const key of S.navigationItems)"));
assert.ok(admin.includes("raw.navigationVisibility={mobile:{},desktop:{}}"));
assert.ok(nav.includes("tile.href='/nebenkostenabrechnung/'"));
assert.ok(nav.includes("const canonicalTileRoutes="));
assert.ok(nav.includes("window.NICNavigationVisibility={refresh:sync}"));
assert.ok(nav.includes("header.append(compact)"));
assert.ok(nav.includes('function updateHomepageNavigationVisibility()'));
assert.ok(nav.includes("if(settlement){"),'Settlement removal must not crash home initialization');
assert.ok(nav.includes('updateHomepageNavigationVisibility();'));
assert.ok(css.includes('#nic-home-intro .nic-home-group[hidden]'));
assert.ok(nav.includes("navigationMobileQuery.addEventListener('change',sync)"));
assert.ok(css.includes('.nic-desktop-calculator-controls[hidden]'));
assert.ok(backend.includes("'contentSections','navigationVisibility'"));
assert.ok(gate.includes('nic-server-menu-visibility'));
console.log('Navigation visibility regression: PASS (14 settings, six tiles, desktop/mobile, server gate).');
