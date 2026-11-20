/* One controller and shared document layout for all five calculator tiles. */
(()=>{
'use strict';
/* FINANCE_MODULE */
/* CALCULATOR_REGISTRY */
/* EXPLANATION_MODULE */
const routes=Object.fromEntries(calculators.map(item=>[item.path,item.id]));
routes['/']='home';routes['/index.html']='home';
const contentRoutes={settlement:'/nebenkostenabrechnung/',prices:'/preise/',why:'/warum-immocheck/'};
for(const [key,path] of Object.entries(contentRoutes)){routes[path]=key;routes[path+'index.html']=key;}
function setPage(key){
 document.documentElement.dataset.nicPage=key==='home'?'website':key;
 window.dispatchEvent(new CustomEvent('nic-route-changed',{detail:document.documentElement.dataset.nicPage}));
}
const portraitHeaderCopy={
 budget:['Jetzt Budget berechnen!','Wie viel Immobilie kann ich mir leisten?'],
 own:['Jetzt Eigenheim & Eigennutzung berechnen!','Immobilie kaufen und selbst nutzen'],
 rent:['Jetzt Vermietung berechnen!','Mietwohnung als Kapitalanlage prüfen'],
 flip:['Jetzt Fix und Flip berechnen!','Kauf, Sanierung und Verkauf prüfen'],
 finance:['Jetzt Finanzierung & Restschuld berechnen!','Ermittle Rate, Zinsen und Restschuld']
};
const portraitQuery=window.matchMedia('(max-width:700px) and (orientation:portrait)');
const navigationMobileQuery=window.matchMedia('(max-width:700px)');
const navigationKeys=['budget','own','rent','flip','finance','settlement'];
function navigationAllowed(key,screen,section='calculator'){
 const v=window.NICSettings?.current?.navigationVisibility;
 return (v?.[section]?.[screen]?.[key]??v?.[screen]?.[key])!==false;
}
function updateHomepageNavigationVisibility(){
 const intro=document.getElementById('nic-home-intro');
 if(!intro)return;
 const screen=navigationMobileQuery.matches?'mobile':'desktop';
 for(const tile of intro.querySelectorAll('.nic-home-options > .deal-type-option')){
  const key=tile.dataset.calculator||(tile.hasAttribute('data-home-settlement')?'settlement':'');
  if(navigationKeys.includes(key))tile.hidden=!navigationAllowed(key,screen,'home');
 }
 for(const group of intro.querySelectorAll('.nic-home-group')){
  group.hidden=!Array.from(group.querySelectorAll('.nic-home-options > .deal-type-option')).some(tile=>!tile.hidden);
 }
}
function applyHeader(key){
 const name=key==='home'||key==='website'?'welcome':key;
 const values=window.NICSettings?.current?.content?.[name];
 if(!values)return;
 const title=document.getElementById('heroTitle'),description=document.getElementById('heroText');
 const mobile=portraitQuery.matches?portraitHeaderCopy[key]:null;
 for(const [element,text] of [[title,mobile?mobile[0]:values.headerTitle],[description,mobile?mobile[1]:values.headerDescription]]){
  if(!element)continue;
  const value=typeof text==='string'?text:'';
  if(element.textContent!==value)element.textContent=value;
  element.style.display=value?'':'none';
 }
 window.NICHeader?.refresh();
}
portraitQuery.addEventListener('change',()=>{
 const key=document.documentElement.dataset.calculator;
 if(key&&portraitHeaderCopy[key])applyHeader(key);
});
window.NICHeaderContent={apply:applyHeader};
function showContent(key,refresh=false){
 const main=document.querySelector('.app>main.section');if(!main)return;
 document.body.classList.remove('nic-home-active','nic-finance-active');
 document.body.classList.add('nic-content-active','nic-standard-header-page');
 let panel=document.getElementById('nicContentView');
 if(key==='settlement'){panel?.remove();active=key;document.documentElement.dataset.calculator=key;document.body.dataset.calculator=key;if(!refresh)setPage(key);applyHeader(key);window.NICHeader?.refresh();return;}
 if(!panel){
  panel=document.createElement('article');panel.id='nicContentView';panel.className='nic-content-card';
  const explanation=main.querySelector(':scope > .nic-explanation-card');
  if(explanation)explanation.after(panel);else main.prepend(panel);
 }
 const settings=window.NICSettings.current,c=settings.content[key];
 const signature=JSON.stringify([key,c.description,settings.company]);
 if(panel.dataset.signature!==signature){panel.replaceChildren(window.NICSettings.contentFragment(c.description,settings));panel.dataset.signature=signature;}
 active=key;document.documentElement.dataset.calculator=key;document.body.dataset.calculator=key;
 if(!refresh)setPage(key);applyHeader(key);window.NICHeader?.refresh();
}
function pushRoute(key,previousURL){
 const path=Object.keys(routes).find(p=>routes[p]===key);
 history.replaceState(history.state,'',previousURL);history.pushState({calculator:key},'',path+location.search);
 // Close native admin/legal views before rendering the destination header.
 if(new URL(previousURL).hash)window.dispatchEvent(new HashChangeEvent('hashchange',{oldURL:previousURL,newURL:location.href}));
}

window.NICCalculators=Object.freeze({
 list:Object.freeze(calculators.map(item=>Object.freeze(item))),
 get active(){return active;},
 get(id){return calculators.find(item=>item.id===id)||null;}
});
let active=null,financeHost=null,bypass=false;
function select(key,push=false){
 window.NICExplanations.show(key);

 if(key==='home'||contentRoutes[key]){
  const previousURL=location.href;
  if(push)pushRoute(key,previousURL);
  if(key==='home'){document.body.classList.remove('nic-content-active','nic-standard-header-page');document.documentElement.dataset.nicPage='website';initWelcome();setPage('home');}else showContent(key);
  if(push)window.scrollTo({top:0,left:0,behavior:'instant'});
  return;
 }
 if(!calculators.some(item=>item.id===key))throw new Error('Unknown calculator: '+key);
 if(active===key)return;
 document.body.classList.remove('nic-home-active','nic-content-active','nic-standard-header-page');
 document.documentElement.dataset.nicPage=key;
 const menu=document.querySelector('.deal-type-card');if(!menu)return;
 const y=scrollY,previousURL=location.href;
 if(key==='finance'&&!financeHost){
  const host=document.createElement('div');host.id='nicFinanceModule';host.hidden=true;(calculatorMenuAnchor||menu).after(host);
  financeHost=createFinance(host);
 }
 document.body.classList.toggle('nic-finance-active',key==='finance');
 const host=document.getElementById('nicFinanceModule');if(host)host.hidden=key!=='finance';
 bypass=true;
 try{
  // The legacy handler recognizes only budget, own, rent and flip.
  // Financing uses its own controls in the shared document; forwarding 'finance' to the
  // legacy four-calculator handler leaves its calculation state undefined.
  if(key!=='finance')window.dispatchEvent(new CustomEvent('nic-select-calculator',{detail:key}));
 }finally{bypass=false;}
 if(key==='finance'){
  document.getElementById('heroTitle').innerHTML=financeHeader[0];
  document.getElementById('heroText').textContent=financeHeader[1];
 }
 applyHeader(key);
 window.NICHeader?.refresh();
 active=key;
 document.documentElement.dataset.calculator=key;
 document.body.dataset.calculator=key;
 window.dispatchEvent(new CustomEvent('nic-calculator-changed',{detail:{id:key}}));
 if(push)pushRoute(key,previousURL);
 try{localStorage.setItem('nic_last_calculator_v1',key);}catch(_){}
 setPage(key);
 window.NICSettings?.syncCalculatorMenu(key);
 window.scrollTo({top:y,left:0,behavior:'instant'});
}
document.addEventListener('click',event=>{
 if(bypass||event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 const link=event.target.closest('a[href]');
 if(link&&document.querySelector('.deal-type-card')){
  const url=new URL(link.href,location.href),key=routes[url.pathname.toLowerCase()];
  if(url.origin===location.origin&&key&&!url.hash&&!link.download&&(!link.target||link.target==='_self')){
   event.preventDefault();select(key,true);return;
  }
 }
 const tile=event.target.closest('.deal-type-row > .deal-type-option');
 if(tile){
  const key=tile.dataset.calculator||routes[new URL(tile.dataset.href||tile.href||location.href,location.href).pathname.toLowerCase()];
  if(!key||tile.hidden)return;
  event.preventDefault();event.stopImmediatePropagation();select(key,true);return;
 }
 if(active==='finance'){
  const button=event.target.closest('.bottom button');if(!button||button.closest('#nicFinanceModule'))return;
  const id=button.classList.contains('bottom-primary')?'newCalc':button.classList.contains('bottom-save')?'download':'share';
  event.preventDefault();event.stopImmediatePropagation();financeHost.querySelector('[data-finance-id="'+id+'"]').click();
 }
},true);
window.addEventListener('popstate',()=>{const key=routes[location.pathname.toLowerCase()];if(key)select(key);});
function createSiteNavigation(){
 const links=[['/nebenkostenabrechnung/','Mieterabrechnung'],['/preise/','Preise'],['/warum-immocheck/','Warum ImmoCheck?']];
 const header=document.querySelector('.nic-brand-bar')||document.querySelector('.brand-logo-wrap')?.closest('header')||document.querySelector('header');
 if(header&&!header.querySelector('[data-nic-site-nav]')){
  const nav=document.createElement('nav');nav.dataset.nicSiteNav='';nav.setAttribute('aria-label','Hauptnavigation');
  for(const [href,label] of links){const a=document.createElement('a');a.href=href;a.textContent=label;nav.append(a);}
  nav.id='nicSiteNavigation';
  const toggle=document.createElement('button');toggle.type='button';toggle.className='nic-menu-toggle';toggle.setAttribute('aria-label','Menü öffnen');toggle.setAttribute('aria-expanded','false');toggle.setAttribute('aria-controls',nav.id);toggle.innerHTML='<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';
  function setOpen(open){toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Menü schließen':'Menü öffnen');nav.classList.toggle('is-open',open);}
  toggle.addEventListener('click',()=>setOpen(toggle.getAttribute('aria-expanded')!=='true'));
  document.addEventListener('click',event=>{if(!header.contains(event.target))setOpen(false);});
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){setOpen(false);toggle.focus();}});
  nav.addEventListener('click',event=>{if(event.target.closest('a'))setOpen(false);});
  header.append(nav,toggle);
 }
}

/* Reuse the existing calculator menu: one menu, two responsive presentations. */
let calculatorMenuAnchor=null;
function initResponsiveCalculatorMenu(){
 const main=document.querySelector('.app>main.section');
 let menu=main?.querySelector(':scope > .deal-type-card');
 const header=document.querySelector('.app>.hero');
 // Standalone content pages omit calculator forms and the original tile menu.
 // Provide the same picker once, without introducing an empty desktop card.
 const path=location.pathname.toLowerCase();
 const isHome=path==='/'||path==='/index.html'||path==='/fixflip-kalkulator/'||path==='/fixflip-kalkulator/index.html';
 if(!menu&&main&&header&&!isHome){
  menu=document.createElement('nav');
  menu.className='deal-type-card nic-standalone-calculator-menu';
  menu.setAttribute('aria-label','Rechner auswählen');
  main.prepend(menu);
 }
 // The built calculator pages do not all use the same branding wrapper.
 // Use the real shared header, with the same fallback as createSiteNavigation.
 const brand=header?.querySelector(':scope > .nic-brand-bar,:scope > .hero-top');
 if(!menu||!header){
  console.error('Calculator menu initialization failed: missing menu or header', {menu:!!menu,header:!!header});
  return;
 }
 // The six-tile bar must never include legacy links into Immobilien ABC.
 const row=menu.querySelector('.deal-type-row');
 for(const oldLink of menu.querySelectorAll('.deal-type-row a[href*="immobilien-abc"],.deal-type-row [data-href*="immobilien-abc"]'))oldLink.remove();
 // Settlement is an existing content route, not a sixth calculation engine.
 // Avoid resurrecting a tile intentionally switched off on both devices.
 function ensureSettlementTile(){
 if(row&&!row.querySelector('[data-calculator="settlement"]')&&
    (navigationAllowed('settlement','mobile','calculator')||navigationAllowed('settlement','desktop','calculator'))){
  const tile=document.createElement('a');tile.className='deal-type-option';
  tile.dataset.calculator='settlement';tile.dataset.href='/nebenkostenabrechnung/';tile.href='/nebenkostenabrechnung/';
  tile.innerHTML='<svg class="nic-menu-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg><span><strong>Nebenkosten abrechnen</strong><small>Betriebskosten erfassen und abrechnen</small></span>';
  row.append(tile);
 }
 }
 ensureSettlementTile();
 // Do not let legacy Immobilien-ABC or Sanierung entries survive in the six-tile calculator bar.
 const canonicalTileRoutes={budget:'/budget/',own:'/eigennutzung/',rent:'/vermietung/',flip:'/fix-flip/',finance:'/finanzierungsrechner/',settlement:'/nebenkostenabrechnung/'};
 const keyByPath=Object.fromEntries(Object.entries(canonicalTileRoutes).map(([key,url])=>[url,key]));
 const seenTiles=new Set();
 for(const tile of menu.querySelectorAll('.deal-type-row > .deal-type-option')){
  const heading=tile.querySelector('strong')?.textContent.trim().toLowerCase()||'';
  const path=(tile.dataset.href||tile.getAttribute('href')||'').split('?')[0];
  let key=tile.dataset.calculator;
  if(!canonicalTileRoutes[key])key=keyByPath[path];
  if(!canonicalTileRoutes[key]||heading==='sanierung'||seenTiles.has(key)){
   // Legacy labels may contain checked calculator radio inputs. Never delete
   // them when cleaning an obsolete visual navigation entry.
   if(tile.querySelector('input')){tile.hidden=true;tile.dataset.nicNavObsolete='true';}
   else tile.remove();
   continue;
  }
  seenTiles.add(key);
  tile.dataset.calculator=key;
  tile.dataset.href=canonicalTileRoutes[key];
  if(tile.tagName==='A')tile.setAttribute('href',canonicalTileRoutes[key]);
 }
 // Align the original shared calculator tiles with the central menu label.
 for(const tile of menu.querySelectorAll('.deal-type-option')){
  if(tile.dataset.calculator==='budget'||tile.dataset.href==='/budget/'){
   const heading=tile.querySelector('strong');
   if(heading?.textContent.trim()==='Budget')heading.textContent='Budgetrechner';
  }
  // Rename only visible navigation captions, never calculator routes or page titles.
  if(tile.dataset.calculator==='own'||tile.dataset.href==='/eigennutzung/'){
   const heading=tile.querySelector('strong');
   if(heading)heading.textContent='Eigenheim';
  }
 }
 if(document.getElementById('nicMobileCalculatorSelect'))return;
 calculatorMenuAnchor=document.createComment('Original calculator menu position');
 menu.after(calculatorMenuAnchor);
 const label=document.createElement('label');
 label.htmlFor='nicMobileCalculatorSelect';
 label.className='nic-mobile-calculator-label';
 label.append(document.createTextNode('Rechner auswählen '));
 const arrow=document.createElement('span');
 arrow.setAttribute('aria-hidden','true');
 arrow.textContent='→';
 label.append(arrow);
 const picker=document.createElement('select');
 picker.id='nicMobileCalculatorSelect';
 picker.className='nic-mobile-calculator-select';
 picker.setAttribute('aria-label','Rechner auswählen');
 picker.tabIndex=-1;
 picker.setAttribute('aria-hidden','true');
 for(const item of calculators){
  const option=document.createElement('option');
  option.value=item.id;
  option.textContent=item.id==='finance'?'Finanzierung & Restschuld':item.label;
  picker.append(option);
 }
 // The Mieter-Abrechnung is an existing content route, not a sixth calculator.
 const settlementOption=document.createElement('option');
 settlementOption.value='settlement';
 settlementOption.textContent='Nebenkosten abrechnen';
 picker.append(settlementOption);
 // 'Budget' is the default visible entry on information pages.
 const compact=document.createElement('div');
 compact.className='nic-mobile-calculator-controls';
 compact.append(label,picker);
 menu.append(compact);
 // Custom portrait menu: the underlying select remains the route-state source.
 const trigger=document.createElement('button');
 trigger.type='button';trigger.id='nicMobileCalculatorTrigger';
 trigger.className='nic-mobile-calculator-trigger';
 // Admin layout rules may apply a later !important button font size.
 // Inline important keeps this control bound to the live Untertexte (px) variable.
 trigger.style.setProperty('font-size','var(--nic-subtext-font-size,14px)','important');
 trigger.setAttribute('aria-label','Rechner auswählen');
 trigger.setAttribute('aria-expanded','false');
 trigger.setAttribute('aria-controls','nicMobileCalculatorOptions');
 trigger.innerHTML='<span class="nic-mobile-calculator-current"><span class="nic-mobile-calculator-current-text">Bitte Rechner wählen</span><span class="nic-mobile-calculator-chevron" aria-hidden="true"></span></span>';
 const options=document.createElement('div');
 options.id='nicMobileCalculatorOptions';options.className='nic-mobile-calculator-options';
 options.setAttribute('role','listbox');options.setAttribute('aria-label','Rechner auswählen');
 options.hidden=true;
 const icons={
  budget:'<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M7 7h10M8 11h1m3 0h1m3 0h1M8 15h1m3 0h1m3 0h1M8 19h1m3 0h1m3 0h1"/>',
  own:'<path d="M3 10.5 12 3l9 7.5V21h-6v-7H9v7H3z"/>',
  rent:'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 4 16 4 16 0V5M4 11v6c0 4 16 4 16 0v-6"/>',
  flip:'<path d="M20 7a8 8 0 0 0-14-2L3 8m0-5v5h5M4 17a8 8 0 0 0 14 2l3-3m0 5v-5h-5"/>',
  finance:'<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 4 16 4 16 0V5M4 11v6c0 4 16 4 16 0v-6"/>',
  settlement:'<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/>'
 };
 const rows=[];
 for(const option of picker.options){
  const row=document.createElement('button');row.type='button';
  row.className='nic-mobile-calculator-option';row.dataset.value=option.value;
  row.style.setProperty('font-size','var(--nic-subtext-font-size,14px)','important');
  row.setAttribute('role','option');
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
  svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('fill','none');
  svg.setAttribute('stroke','currentColor');svg.setAttribute('stroke-width','1.8');
  svg.setAttribute('stroke-linejoin','round');svg.setAttribute('stroke-linecap','round');
  svg.setAttribute('aria-hidden','true');svg.innerHTML=icons[option.value];
  const name=document.createElement('span');name.textContent=option.textContent;
  name.className='nic-mobile-calculator-option-text';
  const check=document.createElement('span');check.className='nic-mobile-calculator-check';
  check.setAttribute('aria-hidden','true');check.textContent='✓';
  row.append(svg,name,check);options.append(row);rows.push(row);
 }
 compact.append(trigger,options);
 function renderSelection(){
  const hasActive=active==='settlement'||calculators.some(item=>item.id===active);
  trigger.querySelector('.nic-mobile-calculator-current-text').textContent=hasActive
   ? picker.selectedOptions[0]?.textContent||'Bitte Rechner wählen'
   : 'Bitte Rechner wählen';
  for(const row of rows){
   const selected=row.dataset.value===picker.value;
   row.classList.toggle('is-selected',selected);
   row.setAttribute('aria-selected',String(selected));
  }
 }
 function setOpen(open,focus=false){
  const show=!!open&&!compact.hidden&&(menu.classList.contains('nic-portrait-calculator-menu')||compact.classList.contains('nic-desktop-calculator-controls'));
  options.hidden=!show;trigger.setAttribute('aria-expanded',String(show));
  if(show&&focus)(rows.find(row=>!row.hidden&&row.dataset.value===picker.value)||rows.find(row=>!row.hidden))?.focus();
 }
 trigger.addEventListener('click',()=>setOpen(options.hidden,true));
 trigger.addEventListener('keydown',e=>{
  if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();setOpen(true,true);}
 });
 options.addEventListener('click',e=>{
  const row=e.target.closest('.nic-mobile-calculator-option');if(!row||row.hidden)return;
  picker.value=row.dataset.value;renderSelection();setOpen(false);trigger.focus();
  picker.dispatchEvent(new Event('change',{bubbles:true}));
 });
 options.addEventListener('keydown',e=>{
  if(e.key==='Escape'){e.preventDefault();setOpen(false);trigger.focus();return;}
  if(e.key==='Tab'){setOpen(false);return;}
  const enabled=rows.filter(row=>!row.hidden);
  if(!enabled.length)return;
  const index=enabled.indexOf(document.activeElement);
  const n=e.key==='ArrowDown'?(index+1)%enabled.length:e.key==='ArrowUp'?(index-1+enabled.length)%enabled.length:e.key==='Home'?0:e.key==='End'?enabled.length-1:-1;
  if(n>=0){e.preventDefault();enabled[n].focus();}
 });
 document.addEventListener('pointerdown',e=>{if(!compact.contains(e.target))setOpen(false);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!options.hidden){setOpen(false);trigger.focus();}});
 const dropdownShell=document.createElement('div');
 dropdownShell.className='nic-global-dropdown-shell';
 dropdownShell.setAttribute('aria-label','Rechner-Navigation');
 function positionGlobalDropdown(){
  const title=header.querySelector(':scope > h1,#heroTitle');
  if(title)title.before(dropdownShell);
  else if(brand)brand.after(dropdownShell);
  else header.prepend(dropdownShell);
 }
 positionGlobalDropdown();
 function sync(){
  const isHome=document.body.classList.contains('nic-home-active')||location.pathname==='/'||location.pathname==='/index.html'||location.pathname==='/fixflip-kalkulator/';
  const pageKey=document.documentElement.dataset.nicPage;
  const key=active&&active!=='home'?active:pageKey&&pageKey!=='website'?pageKey:document.documentElement.dataset.calculator;
  const hiddenView=document.body.matches('.nic-admin-open,.nic-legal-open');
  const portraitCalculator=portraitQuery.matches&&!isHome&&!hiddenView;
  if(key==='settlement'||calculators.some(item=>item.id===key))picker.value=key;
  else picker.value='budget';
  if(portraitCalculator){
   if(menu.parentElement!==header){
    if(brand)brand.after(menu);
    else header.insertBefore(menu,header.querySelector(':scope > h1')||header.firstChild);
   }
   if(compact.parentElement!==menu)menu.append(compact);
   compact.classList.remove('nic-desktop-calculator-controls');
   menu.classList.add('nic-portrait-calculator-menu');
   dropdownShell.hidden=true;
  }else{
   setOpen(false);
   menu.classList.remove('nic-portrait-calculator-menu');
   menu.hidden=false;
   if(calculatorMenuAnchor?.parentNode&&menu.previousSibling!==calculatorMenuAnchor)calculatorMenuAnchor.after(menu);
   if(compact.parentElement!==dropdownShell)dropdownShell.append(compact);
   compact.classList.add('nic-desktop-calculator-controls');
   dropdownShell.hidden=false;
   if(dropdownShell.parentElement!==header)positionGlobalDropdown();
  }
  refreshNavigationVisibility();
  window.NICHeader?.refresh();
 }
 picker.addEventListener('change',()=>{
  renderSelection();
  setOpen(false);
  if(menu.classList.contains('nic-standalone-calculator-menu')){
   // Standalone information shells do not contain calculator forms.
   // Load the full calculator document rather than switching an empty shell.
   const route=Object.keys(routes).find(path=>routes[path]===picker.value);
   if(route)location.assign(route);
  }else select(picker.value,true);
 });
 function refreshNavigationVisibility(){
  ensureSettlementTile();
  const screen=navigationMobileQuery.matches?'mobile':'desktop';
  const isHome=document.body.classList.contains('nic-home-active')||location.pathname==='/'||location.pathname==='/index.html'||location.pathname==='/fixflip-kalkulator/';
  const dropdownSection=isHome?'dropdownHome':'dropdownOther';
  for(const tile of menu.querySelectorAll('.deal-type-row > .deal-type-option')){
   const key=tile.dataset.calculator;
   if(tile.dataset.nicNavObsolete==='true')continue;
   if(navigationKeys.includes(key))tile.hidden=!navigationAllowed(key,screen,'calculator');
  }
  // Dropdown destinations are independent from the separately controlled tile bar.
  for(const item of rows)item.hidden=false;
  for(const option of picker.options)option.disabled=false;
  const showDropdown=navigationAllowed('dropdown',screen,dropdownSection)&&!document.body.matches('.nic-admin-open,.nic-legal-open');
  compact.hidden=!showDropdown;
  dropdownShell.hidden=menu.classList.contains('nic-portrait-calculator-menu')||!showDropdown;
  const isPortraitMenu=menu.classList.contains('nic-portrait-calculator-menu');
  const hasVisibleTiles=Array.from(menu.querySelectorAll('.deal-type-row > .deal-type-option')).some(tile=>!tile.hidden);
  // If the mobile dropdown is off, keep the separately enabled six-button bar usable.
  menu.classList.toggle('nic-portrait-tiles-only',isPortraitMenu&&!showDropdown&&hasVisibleTiles);
  if(isPortraitMenu)menu.hidden=!showDropdown&&!hasVisibleTiles;
  else if(!isHome)menu.hidden=!hasVisibleTiles;
  renderSelection();
  updateHomepageNavigationVisibility();
  if(!showDropdown)setOpen(false);
 }
 window.NICNavigationVisibility={refresh:sync};
 navigationMobileQuery.addEventListener('change',sync);
 window.addEventListener('nic-calculator-changed',sync);
 window.addEventListener('nic-route-changed',sync);
 portraitQuery.addEventListener('change',sync);
 sync();
}

function initWelcome(){
 if(document.documentElement.dataset.nicPage!=='website')return;
 const main=document.querySelector('main.section')||document.querySelector('main'),menu=document.querySelector('.deal-type-card');
 if(!main)return;
 const title=document.getElementById('heroTitle'),text=document.getElementById('heroText');
 const settings=window.NICSettings.current,home=settings.meta.website;
 if(!/^#(?:admin(?:-|$)|account$|impressum$|agbs$|datenschutz$|haftungsausschluss$|cookie-hinweis$)/.test(location.hash)){
  let changed=false;
  if(title&&title.textContent!==settings.content.welcome.headerTitle){title.textContent=settings.content.welcome.headerTitle;changed=true;}
  if(text&&text.textContent!==settings.content.welcome.headerDescription){text.textContent=settings.content.welcome.headerDescription;changed=true;}
  applyHeader('welcome');
  window.NICSettings.applyMeta(settings,'website');if(changed)window.NICHeader?.refresh();
 }
 let intro=document.getElementById('nic-home-intro');
 if(!intro){
  const template=document.createElement('template');template.innerHTML=''/* HOME_MARKUP */;
  intro=template.content.firstElementChild;
 }
 if(intro.parentElement!==main)main.prepend(intro);
 const settlement=intro.querySelector('[data-home-settlement]');
 if(settlement){
  settlement.querySelector('strong').textContent=home.settlementButtonTitle;
  settlement.querySelector('small').textContent=home.settlementButtonText;
  if(home.settlementButtonUrl){settlement.href=home.settlementButtonUrl;settlement.removeAttribute('aria-disabled');}else{settlement.removeAttribute('href');settlement.setAttribute('aria-disabled','true');}
 }
 const content=window.NICSettings.current.content.welcome;
 const signature=JSON.stringify([content.title,content.description,settings.company]);
 if(intro.dataset.contentSignature!==signature){
  intro.querySelector('[data-home-title]').textContent=content.title;
  intro.querySelector('[data-home-description]').replaceChildren(window.NICSettings.contentFragment(content.description,settings));
  intro.dataset.contentSignature=signature;
 }

 // Copy the existing controls' content and classes; do not create a second
 // visual button system or duplicate calculator radio inputs and IDs.
 if(menu&&!intro.dataset.controlsSynced){
  for(const link of intro.querySelectorAll('a[data-calculator]')){
   const item=calculators.find(item=>item.id===link.dataset.calculator);
   const original=menu.querySelector('[data-href="'+item.path+'"]');
   if(!original)continue;
   if(!original.querySelector('.nic-menu-icon')&&link.querySelector('.nic-menu-icon'))continue;
   link.className=original.className.replace(/\b(?:nic-tile-active|current)\b/g,'').trim();
   link.dataset.href=item.path;
   link.innerHTML=original.innerHTML;
   link.querySelectorAll('input').forEach(input=>input.remove());
  }
  intro.dataset.controlsSynced='true';
 }
 document.body.classList.remove('nic-finance-active');
 document.body.classList.add('nic-home-active');
 active='home';
 document.documentElement.dataset.calculator='home';document.body.dataset.calculator='home';
 // The real calculator menu becomes visible again when a calculator opens.
 if(menu){menu.hidden=false;menu.removeAttribute('aria-hidden');}
 updateHomepageNavigationVisibility();
}
document.addEventListener('click',event=>{const button=event.target.closest('[data-nic-show-calculators]');if(!button)return;const menu=document.querySelector('.deal-type-card');if(menu){menu.hidden=false;menu.removeAttribute('aria-hidden');menu.scrollIntoView({behavior:'smooth',block:'start'});}});
window.addEventListener('nic-settings-updated',()=>{if(document.body.classList.contains('nic-home-active'))initWelcome();});
window.addEventListener('DOMContentLoaded',()=>{
 const css=document.createElement('style');css.textContent='.nic-finance-active main.section > :not(.deal-type-card):not(#nicFinanceModule):not(#nic-home-intro):not(.nic-explanation-card){display:none!important}#nicFinanceModule[hidden]{display:none!important}.deal-type-card[hidden]{display:none!important}.nic-home-intro{margin:20px 0 24px;padding:26px 30px;border:1px solid #e2e9e5;border-radius:12px;background:#f6f1e9;color:#263b3a}.nic-home-intro h2{margin:0;color:#075c55;font-size:26px}.nic-home-description{margin-top:10px;max-width:780px;line-height:1.55}.nic-home-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}.nic-home-actions a,.nic-home-actions button{display:inline-flex;min-height:44px;align-items:center;padding:10px 18px;border:1px solid #075c55;border-radius:12px;background:linear-gradient(135deg,#16867a,#075c55);color:#fff;font:inherit;font-weight:600;text-decoration:none;cursor:pointer}.nic-home-actions a{background:#fff;color:#075c55}[data-nic-site-nav]{display:flex;align-items:center;justify-content:flex-end;gap:clamp(10px,1.4vw,20px);margin-left:auto}[data-nic-site-nav] a{color:#263b3a;font-size:14px;text-decoration:none;white-space:nowrap}.nic-brand-bar:has([data-nic-site-nav]){grid-template-columns:170px minmax(0,1fr) auto}.nic-brand-bar [data-nic-site-nav]{grid-column:1/-1;grid-row:2;padding-top:9px;border-top:1px solid #e9e1d6}.nic-menu-toggle{display:none;border:1px solid #dce6e1;border-radius:10px;background:#fff;color:#075c55;font-size:22px;padding:5px 10px}@media(max-width:700px),(max-width:1024px) and (max-height:600px) and (orientation:landscape){.nic-brand-bar:has([data-nic-site-nav]){grid-template-columns:minmax(0,1fr) auto auto!important;position:relative}.nic-brand-bar a.nic-login-button{grid-column:2!important;grid-row:1!important}.nic-brand-bar .nic-brand-description{display:none!important}.nic-brand-bar [data-nic-site-nav]{display:none;position:absolute;z-index:100;top:100%;left:0;right:0;grid-column:auto;grid-row:auto;margin:0;padding:16px;background:#fff;border-top:1px solid #e2e9e5;box-shadow:0 10px 20px #263b3a18;flex-direction:column;align-items:flex-start}.nic-brand-bar [data-nic-site-nav].is-open{display:flex}.nic-brand-bar .nic-menu-toggle{display:inline-flex!important;grid-column:3!important;grid-row:1!important;align-items:center;justify-content:center;box-sizing:border-box;width:44px;height:44px;min-width:44px;padding:9px;margin:0;flex:none;cursor:pointer}.nic-brand-bar .nic-menu-toggle:focus-visible{outline:3px solid #b37b00;outline-offset:3px}.nic-home-intro{padding:22px 18px}.nic-home-actions{flex-direction:column}.nic-home-actions>*{justify-content:center}}';css.textContent+='@media(max-width:700px) and (orientation:portrait){.nic-brand-bar a.nic-login-button{box-sizing:border-box!important;width:44px!important;height:44px!important;padding:9px!important;gap:0!important}.nic-brand-bar a.nic-login-button>span{display:none!important}}';document.head.append(css);
 createSiteNavigation();
 // The shared calculator menu may be inserted after DOMContentLoaded by the
 // site build. Initialize only after the direct route has its real menu.
 function startDirectRoute(){
  const key=routes[location.pathname.toLowerCase()];
  if(key)select(key);
  initResponsiveCalculatorMenu();
 }
 window.NICSettings.init().then(startDirectRoute).catch(async error=>{
  console.error(error);
  try{
   const response=await fetch(new URL('site-settings.json',window.NICSettings.ROOT),{cache:'no-store'});
   if(!response.ok)throw new Error('Gebündelte Einstellungen konnten nicht geladen werden.');
   window.NICSettings.useFallback(await response.json());
  }catch(fallbackError){console.error(fallbackError);}
  startDirectRoute();
 });
});
window.NICContent={refresh(){if(document.body.classList.contains('nic-content-active')&&contentRoutes[active])showContent(active,true);}};
window.NICHome={refresh(){if(document.body.classList.contains('nic-home-active'))initWelcome();}};
window.NICCalculatorNavigation={select,restore(){}};
})();
