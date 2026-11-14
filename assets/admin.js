(function(){
'use strict';
const S=window.NICSettings,$=id=>document.getElementById(id),form=$('settingsForm');let favicon='',appleTouchIcon='',websiteLogo='',sharingImage='',dirty=false,contentSectionCatalog=[];
function status(message,error=false){$('saveStatus').textContent=message;$('saveStatus').classList.toggle('error',error);}
function markDirty(){dirty=true;$('saveState').textContent='Ungespeicherte Änderungen';status(window.NICAccess?.enabled?'Noch nicht global gespeichert.':'Noch nicht im Browser gespeichert.');}
function field(parent,id,label,type='text',hint=''){
 const div=document.createElement('div');div.className='admin-field';const lab=document.createElement('label');lab.htmlFor=id;lab.textContent=label;div.append(lab);
 const input=document.createElement(type==='textarea'?'textarea':'input');input.id=id;input.name=id;if(type!=='textarea')input.type=type;input.maxLength=2000;input.placeholder='';div.append(input);
 if(hint){const small=document.createElement('span');small.className='helper';small.textContent=hint;div.append(small);}parent.append(div);return input;
}
let activeLegal='impressum',legalDefaults={},legalStored={};
function disclaimerHTML(){try{const card=window.parent.document.querySelector('#legalDisclaimerPage .legal-page-card');if(card)return [...card.children].filter(x=>x.tagName!=='H1').map(x=>x.outerHTML).join('\n');}catch(_){}return '';}
function buildLegal(){
 for(const [key,label] of Object.entries(S.legalLabels)){
  const button=document.createElement('button');button.type='button';button.textContent=label;button.dataset.legalSection=key;button.addEventListener('click',()=>showLegal(key));$('legalSections').append(button);
  const card=document.createElement('section');card.className='form-card legal-editor-card';card.id='legal-card-'+key;card.hidden=true;const h=document.createElement('h3');h.textContent=label;card.append(h);
  const published=document.createElement('details'),summary=document.createElement('summary');summary.textContent='Aktuell veröffentlichten Text anzeigen';published.append(summary);const live=document.createElement('div');live.className='legal-html-preview';live.id='legal-published-'+key;published.append(live);card.append(published);
  const draftButton=document.createElement('button');draftButton.type='button';draftButton.className='button';draftButton.textContent='Rechtstext-Entwurf in den Editor übernehmen';draftButton.hidden=!window.NICLegalDrafts?.[key];draftButton.addEventListener('click',()=>{const input=$('legal-'+key);if(input.value.trim()&&!window.confirm('Vorhandenen Text durch den Entwurf ersetzen?'))return;input.value=window.NICLegalDrafts[key];markDirty();updatePreview();input.focus();});card.append(draftButton);const input=field(card,'legal-'+key,'HTML bearbeiten','textarea');input.maxLength=100000;input.rows=15;input.spellcheck=false;input.classList.add('legal-html-input');
  const hint=document.createElement('p');hint.className='helper';hint.textContent='HTML: h1–h6, p, br, strong, em, Listen, Links und Tabellen. Blocksatz: <p style="text-align:justify">…</p>. Skripte und aktive Einbettungen werden nicht ausgeführt.';card.append(hint);
  const issues=document.createElement('p');issues.id='legal-issues-'+key;issues.className='helper legal-issues';issues.setAttribute('role','status');card.append(issues);
  const details=document.createElement('details');details.className='legal-placeholders';details.open=true;const caption=document.createElement('summary');caption.textContent='Verfügbare Platzhalter · zum Einfügen anklicken';details.append(caption);
  for(const [fieldKey,fieldLabel]of S.companyFields){const row=document.createElement('button');row.type='button';row.className='legal-placeholder';row.dataset.companyPlaceholder=fieldKey;const name=document.createElement('span');name.textContent=fieldLabel;const code=document.createElement('code');code.textContent='{{company.'+fieldKey+'}}';const value=document.createElement('span');value.className='legal-placeholder-value';row.append(name,code,value);row.addEventListener('click',()=>{input.setRangeText(code.textContent,input.selectionStart,input.selectionEnd,'end');input.focus();markDirty();updatePreview();});details.append(row);}card.append(details);
  const previewHeading=document.createElement('h4');previewHeading.textContent='Vorschau deines Entwurfs';const preview=document.createElement('div');preview.id='legal-preview-'+key;preview.className='legal-html-preview';card.append(previewHeading,preview);$('legalEditors').append(card);
 }
 showLegal(activeLegal);
}
function showLegal(key){activeLegal=key;for(const k of Object.keys(S.legalLabels)){$('legal-card-'+k).hidden=k!==key;const button=$('legalSections').querySelector('[data-legal-section="'+k+'"]');button.setAttribute('aria-pressed',String(k===key));}}
function fillLegal(s){
 for(const key of Object.keys(S.legalLabels)){
  legalDefaults[key]=S.legalSource(s,key,disclaimerHTML());
  $('legal-'+key).value=s.legal?.[key]||window.NICLegalDrafts?.[key]||legalDefaults[key];
  const published=S.published||s;$('legal-published-'+key).replaceChildren(S.legalFragment(S.legalSource(published,key,disclaimerHTML()),published));
 }
}
function updateLegal(s){for(const key of Object.keys(S.legalLabels)){const source=$('legal-'+key).value;$('legal-preview-'+key).replaceChildren(S.legalFragment(source,s));$('legal-issues-'+key).textContent=S.legalIssues(source,s).join(' · ');$('legal-card-'+key).querySelectorAll('[data-company-placeholder]').forEach(row=>row.querySelector('.legal-placeholder-value').textContent=s.company[row.dataset.companyPlaceholder]||'Noch nicht hinterlegt');}}
function buildContent(){
 for(const [key,defaults] of Object.entries(S.contentPageDefaults)){
  const card=document.createElement('section');card.className='form-card content-editor-card';card.dataset.contentPage=key;
  const heading=document.createElement('h3');heading.textContent=key==='welcome'?'Startseite · Einführung':({'settlement':'Mieterabrechnung','prices':'Preise','why':'Warum ImmoCheck','about':'Über uns · Footer','contact':'Kontakt','login':'Anmelden','budget':'Budget · Contentbox','own':'Eigenheim · Contentbox','rent':'Vermietung · Contentbox','flip':'Fix & Flip · Contentbox','finance':'Finanzierung · Contentbox'}[key]||key);card.append(heading);
  const title=field(card,'content-'+key+'-title','Seitentitel / Überschrift','text');title.maxLength=240;title.value=defaults.title;
  if(key==='settlement')field(card,'content-'+key+'-boxTitle','Überschrift der Contentbox','text').maxLength=240;
  const description=field(card,'content-'+key+'-description','Inhalt der Box (HTML möglich)','textarea','Der erste Absatz ist die Einleitung und bleibt mobil sichtbar. Weitere Absätze und Zwischenüberschriften werden mit weiterlesen geöffnet.');description.maxLength=12000;description.value=defaults.description;description.parentElement.classList.add('wide');
  const seoTitle=field(card,'content-'+key+'-seoTitle','SEO-Titel','text','Empfohlen: kurz, eindeutig und passend zum Suchinhalt.');seoTitle.maxLength=200;seoTitle.value=defaults.seoTitle;
  const meta=field(card,'content-'+key+'-metaDescription','SEO- und GEO-Beschreibung','textarea','Beschreibe klar Zielgruppe, Leistung und Nutzen. Suchmaschinen und KI-Suchsysteme können eigene Textausschnitte bilden.');meta.maxLength=500;meta.value=defaults.metaDescription;meta.parentElement.classList.add('wide');
  const preview=document.createElement('div');preview.className='search-preview';preview.id='content-'+key+'-search-preview';const searchTitle=document.createElement('strong');searchTitle.id='content-'+key+'-search-title';const searchText=document.createElement('p');searchText.id='content-'+key+'-search-description';preview.append(searchTitle,searchText);card.append(preview);
  const bodyPreview=document.createElement('div');bodyPreview.className='legal-html-preview';bodyPreview.id='content-'+key+'-body-preview';card.append(document.createElement('hr'),Object.assign(document.createElement('strong'),{textContent:'Textvorschau'}),bodyPreview);
  $('contentEditors').append(card);
 }
}
function updateContentPreview(s){for(const [key] of Object.entries(S.contentPageDefaults)){
 $('content-'+key+'-search-title').textContent=s.content[key].seoTitle;
 $('content-'+key+'-search-description').textContent=s.content[key].metaDescription;
 $('content-'+key+'-body-preview').replaceChildren(S.legalFragment(s.content[key].description,s));
}}
function build(){
 buildContent();
 buildLegal();
 for(const [key,title] of [['websiteLogo','Webseiten-Logo'],['favicon','Favicon'],['appleTouchIcon','Apple Touch Icon'],['sharing','Vorschaubild beim Teilen']]){const target=$(key==='sharing'?'sharingText':key+'File').closest(key==='sharing'?'.form-card':'div');field(target,'alt-'+key,'Alt-Text: '+title,'text',key==='favicon'||key==='appleTouchIcon'?'Bildbeschreibung für die Vorschau. Browser- und Home-Bildschirm-Icons besitzen kein HTML-Alt-Attribut.':'Beschreibe kurz den Bildinhalt für Screenreader und unterstützte Link-Vorschauen.').maxLength=300;}

 S.companyFields.forEach(([k,label],i)=>{const type=k==='email'?'email':['additional','disputeResolution','editorialAddress','professionalRules','authority'].includes(k)?'textarea':'text';const input=field($(i<11?'companyCore':'companyExtra'),'company-'+k,label,type,k==='website'?'Domain oder vollständige Internetadresse. Das Header-Logo öffnet diese Adresse. Ohne Eintrag führt es zur Startseite.':'');if(k==='website'){input.placeholder='www.beispiel.de';input.addEventListener('change',()=>{const value=S.websiteUrl(input.value);if(input.value.trim()&&!value)input.setCustomValidity('Bitte eine gültige Internetadresse eintragen.');else input.setCustomValidity('');});input.addEventListener('input',()=>input.setCustomValidity(''));}});
 const fontDiv=document.createElement('div');fontDiv.className='admin-field';const label=document.createElement('label');label.htmlFor='layout-font';label.textContent='Schriftfamilie';const select=document.createElement('select');select.id='layout-font';
 for(const [value,title] of [['system','Systemschrift'],['arial','Arial'],['verdana','Verdana'],['georgia','Georgia'],['trebuchet','Trebuchet MS']]){const o=document.createElement('option');o.value=value;o.textContent=title;select.append(o);}fontDiv.append(label,select);$('typeFields').append(fontDiv);
 for(const [k,title] of [['bodySize','Grundschriftgröße'],['subtextSize','Untertexte'],['hintSize','Hinweistexte'],['h1','H1 – Hauptüberschrift'],['h2','H2 – Abschnitt'],['h3','H3 – Unterabschnitt'],['h4','H4 – Detailüberschrift']]){const x=field($('typeFields'),'layout-'+k,title+' (px)','number');x.min=10;x.max=72;x.step=1;}
 const radius=field($('styleFields'),'layout-cornerRadius','Eckenradius (px)','number','Bisheriger Kartenradius: 22 px.');radius.min=0;radius.max=40;radius.step=1;
 for(const [k,title] of [['background','Container-Hintergrund'],['outerBackground','Äußerer Seitenhintergrund'],['text','Text'],['greenBackground','Grün – Hintergrund (Buttons und Footer)'],['greenText','Grün – Textfarbe (AUTO oder HEX)'],['buttonBackground','Schwarz – Hintergrund (PDF, Teilen, Download)'],['buttonText','Schwarz – Textfarbe (AUTO oder HEX)'],['redBackground','Rot – Hintergrund (Neu kalkulieren, X)'],['redText','Rot – Textfarbe (AUTO oder HEX)'],['highlightBackground','Highlight-Farbe – Neutral (Gelb)'],['highlightGoodBackground','Highlight-Farbe – Sehr gut (Grün)'],['highlightWarningBackground','Highlight-Farbe – Warnungen (Rot)']]){
  const input=field($('colorFields'),'layout-'+k,title,'text');input.pattern=k.endsWith('Text')?'(AUTO|#[0-9A-Fa-f]{6})':'#[0-9A-Fa-f]{6}';input.maxLength=7;input.placeholder=k.endsWith('Text')?'AUTO oder #FFFFFF':'#000000';input.title='HEX-Code mit # und sechs Zeichen, z. B. #0F172A';const wrap=document.createElement('div');wrap.className='color-control';input.replaceWith(wrap);const picker=document.createElement('input');picker.type='color';picker.id='color-'+k;picker.setAttribute('aria-label',title+' auswählen');wrap.append(picker,input);picker.addEventListener('input',()=>{input.value=picker.value.toUpperCase();updatePreview();markDirty();});input.addEventListener('input',()=>{if(/^#[0-9a-f]{6}$/i.test(input.value))picker.value=input.value;});
 }
 S.portals.forEach(([k,label])=>{const input=field($('socialFields'),'social-'+k,label,'url','Vollständige Profiladresse mit https://');input.placeholder='https://';input.pattern='https?://.+';input.title='Bitte eine vollständige Adresse mit https:// oder http:// eintragen.';input.maxLength=2000;});
 S.pages.forEach(([k,label,path])=>{
  const card=document.createElement('div');card.className='form-card';const h=document.createElement('h3');h.textContent=label;const a=document.createElement('a');a.className='meta-address';a.href=new URL(path,S.ROOT);a.target='_blank';a.rel='noopener';a.textContent=new URL(path,S.ROOT).href;card.append(h,a);const grid=document.createElement('div');grid.className='field-grid';card.append(grid);
  for(const [key,title,max,recommend] of [['title','Meta-Titel',200,'ca. 50–60 Zeichen'],['description','Meta-Description',500,'ca. 140–160 Zeichen']]){const x=field(grid,'meta-'+k+'-'+key,title,key==='description'?'textarea':'text');x.maxLength=max;x.parentElement.classList.add('wide');const counter=document.createElement('span');counter.className='counter';counter.id=x.id+'-count';counter.dataset.recommend=recommend;x.parentElement.append(counter);}
  if(k==='website'){
   for(const [name,config] of Object.entries(S.homeFields)){const input=field(grid,'meta-website-'+name,config.label,name==='homeDescription'?'textarea':'text');input.maxLength=config.max;input.parentElement.classList.add('wide');}

  const tag=field(grid,'meta-'+k+'-googleTag','Google-Tag-ID','text','Optional: G-… oder GT-… . Leer übernimmt den Tag der Webseite. Für eine gemeinsame Gesamtauswertung möglichst denselben GA4-Datenstream verwenden.');tag.pattern='(G|GT)-[A-Za-z0-9]{4,30}';tag.maxLength=40;tag.placeholder='G-XXXXXXXXXX';tag.title='Google-Tag-ID mit G- oder GT- eintragen, keinen Script-Code.';tag.parentElement.classList.add('wide');
  }
  const preview=document.createElement('div');preview.className='search-preview';const title=document.createElement('strong');title.id='search-'+k+'-title';const desc=document.createElement('p');desc.id='search-'+k+'-description';preview.append(title,desc);card.append(preview);$('metaFields').append(card);
 });
}
async function buildContentSectionControls(){const response=await fetch(new URL('/content-sections.json',S.ROOT),{cache:'no-store'});if(!response.ok)throw new Error('Die Liste der H2-Boxen konnte nicht geladen werden.');contentSectionCatalog=await response.json();const root=$('contentSectionControls');root.replaceChildren();const header=document.createElement('div');header.className='content-section-header';header.innerHTML='<strong>Inhalte</strong><strong>Anzeigen</strong><strong>Nur Nutzer</strong>';root.append(header);let group='';for(const item of contentSectionCatalog){if(item.calculator!==group){group=item.calculator;const title=document.createElement('h5');title.className='content-section-group';title.textContent=item.calculatorLabel;root.append(title);}const row=document.createElement('div');row.className='content-section-row';row.dataset.contentKey=item.key;const label=document.createElement('span');label.textContent=item.title;const visible=document.createElement('input');visible.type='checkbox';visible.id='content-visible-'+item.key;visible.setAttribute('aria-label',item.title+': anzeigen');visible.checked=true;const guest=document.createElement('input');guest.type='checkbox';guest.id='content-guest-'+item.key;guest.setAttribute('aria-label',item.title+': nur für Nutzer');guest.checked=false;row.append(label,visible,guest);root.append(row);}}
function collect(){const raw={version:1,company:{},layout:{},social:{},meta:{},content:{},favicon,appleTouchIcon,websiteLogo};S.companyFields.forEach(([k])=>raw.company[k]=$('company-'+k).value);Object.keys(S.layoutDefaults).forEach(k=>raw.layout[k]=$('layout-'+k).value);S.portals.forEach(([k])=>raw.social[k]=$('social-'+k).value);S.pages.forEach(([k])=>raw.meta[k]={title:$('meta-'+k+'-title').value,description:$('meta-'+k+'-description').value,googleTag:k==='website'?$('meta-website-googleTag').value:''});Object.keys(S.contentPageDefaults).forEach(k=>raw.content[k]={title:$('content-'+k+'-title').value,description:$('content-'+k+'-description').value,seoTitle:$('content-'+k+'-seoTitle').value,metaDescription:$('content-'+k+'-metaDescription').value,...(k==='settlement'?{boxTitle:$('content-'+k+'-boxTitle').value}:{})});for(const name of Object.keys(S.homeFields))raw.meta.website[name]=$('meta-website-'+name).value;raw.imageAlts={};Object.keys(S.imageAltDefaults).forEach(k=>raw.imageAlts[k]=$('alt-'+k).value);raw.sharing={text:$('sharingText').value,image:sharingImage};raw.access=Object.fromEntries(['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare'].map(key=>[key,$('access-'+key).checked]));raw.contentSections=Object.fromEntries(contentSectionCatalog.map(item=>[item.key,{visible:$('content-visible-'+item.key).checked,guestAllowed:!$('content-guest-'+item.key).checked}]));raw.reporting={propertyId:$('statsPropertyId').value,clientId:$('statsClientId').value};raw.legal={};for(const key of Object.keys(S.legalLabels)){const value=$('legal-'+key).value;raw.legal[key]=value===legalDefaults[key]?(legalStored[key]||''):value;}return S.normalize(raw);}
function fill(s){for(const key of ['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare'])$('access-'+key).checked=s.access[key];for(const item of contentSectionCatalog){const rule=s.contentSections[item.key]||{};$('content-visible-'+item.key).checked=rule.visible!==false;$('content-guest-'+item.key).checked=rule.guestAllowed===false;}legalStored={...s.legal};fillLegal(s);Object.keys(S.imageAltDefaults).forEach(k=>$('alt-'+k).value=s.imageAlts[k]);S.companyFields.forEach(([k])=>$('company-'+k).value=s.company[k]||'');Object.keys(S.layoutDefaults).forEach(k=>{ $('layout-'+k).value=s.layout[k];if($('color-'+k))$('color-'+k).value=s.layout[k];});S.portals.forEach(([k])=>$('social-'+k).value=s.social[k]||'');S.pages.forEach(([k])=>{['title','description'].forEach(p=>$('meta-'+k+'-'+p).value=s.meta[k][p]||'');});Object.keys(S.contentPageDefaults).forEach(k=>{for(const p of ['title','description','seoTitle','metaDescription',...(k==='settlement'?['boxTitle']:[])])$('content-'+k+'-'+p).value=s.content[k][p]||'';});for(const name of Object.keys(S.homeFields))$('meta-website-'+name).value=s.meta.website[name];$('meta-website-googleTag').value=s.meta.website.googleTag||'';$('statsPropertyId').value=s.reporting.propertyId;$('statsClientId').value=s.reporting.clientId;sharingImage=s.sharing.image;$('sharingText').value=s.sharing.text;$('sharingFile').value='';websiteLogo=s.websiteLogo||'';$('websiteLogoPreview').src=websiteLogo||'neustart-immocheck-logo.svg';$('websiteLogoFile').value='';notifyLogo();appleTouchIcon=s.appleTouchIcon||'';$('appleTouchIconPreview').src=appleTouchIcon||'apple-touch-icon.png';$('appleTouchIconFile').value='';favicon=s.favicon;$('faviconPreview').src=favicon||'icon.svg';$('faviconFile').value='';updatePreview();}
function luminance(hex){return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);}
function contrastColor(bg,choice){if(choice!=='AUTO')return choice;return luminance(bg)>.179?'#000000':'#FFFFFF';}
function updatePreview(){
 updateSharingPreview();
      const s=collect();updateLegal(s);updateContentPreview(s);for(const k of ['websiteLogo','favicon','appleTouchIcon'])$(k+'Preview').alt=s.imageAlts[k];$('sharingPreview').setAttribute('aria-label',s.imageAlts.sharing);notifyLogo();const l=s.layout,preview=$('layoutPreview');preview.style.fontFamily=S.fonts[l.font];preview.style.fontSize=l.bodySize+'px';for(const [key,label] of [['subtextSize','Untertext unter einer Überschrift'],['hintSize','Hinweis in einem Feld oder einer Box']]){let el=$('preview-'+key);if(!el){el=document.createElement('p');el.id='preview-'+key;el.textContent=label;preview.append(el);}el.style.fontSize=l[key]+'px';}preview.style.background=l.background;preview.style.color=l.text;preview.style.borderRadius=l.cornerRadius+'px';['h1','h2','h3','h4'].forEach(k=>preview.querySelector(k).style.fontSize=l[k]+'px');$('previewButton').style.background=l.greenBackground;$('previewButton').style.color=contrastColor(l.greenBackground,l.greenText);$('previewButton').style.borderRadius=Math.round(l.cornerRadius*10/22)+'px';
 const vals=[luminance(l.greenBackground),luminance(contrastColor(l.greenBackground,l.greenText))],ratio=(Math.max(...vals)+.05)/(Math.min(...vals)+.05);$('contrastNotice').textContent='Grüne Buttons – Kontrast: '+ratio.toFixed(1).replace('.',',')+':1'+(ratio<4.5?' · Für gut lesbaren kleinen Text sind mindestens 4,5:1 empfehlenswert.':' · Gut lesbarer Kontrast.');$('contrastNotice').classList.toggle('low-contrast',ratio<4.5);
 const root=$('imprintPreview');root.replaceChildren();S.imprint(s).forEach(({label,value})=>{const h=document.createElement('h4');h.textContent=label;const p=document.createElement('p');p.textContent=value;root.append(h,p);});
 S.pages.forEach(([k])=>{const meta=S.pageMeta(s,k);for(const p of ['title','description']){$('search-'+k+'-'+p).textContent=meta[p];const counter=$('meta-'+k+'-'+p+'-count');counter.textContent=$('meta-'+k+'-'+p).value.length+' Zeichen · Richtwert '+counter.dataset.recommend;}});
}
function validForm(){const invalid=Array.from(form.querySelectorAll('input,textarea,select')).find(el=>!el.checkValidity());if(invalid){const section=invalid.closest('[role=tabpanel]');if(section)selectTab(section.id.replace('panel-',''));const details=invalid.closest('details');if(details)details.open=true;invalid.reportValidity();invalid.focus();return false;}return true;}
let adminMenuButton=null;
function setAdminMenuOpen(open){
 const nav=document.querySelector('#nicAdminContent .admin-tabs,body.nic-admin .admin-tabs');
 if(!nav||!adminMenuButton)return;
 nav.classList.toggle('is-open',open);
 adminMenuButton.setAttribute('aria-expanded',String(open));
}
function syncAdminMenu(key){
 const label=$('tab-'+key)?.textContent.trim();
 const current=adminMenuButton?.querySelector('[data-active-admin-label]');
 if(current&&label)current.textContent=label;
 const wasOpen=adminMenuButton?.getAttribute('aria-expanded')==='true';
 setAdminMenuOpen(false);
 if(wasOpen)adminMenuButton.focus();
}
function selectTab(key){document.querySelectorAll('#nicAdminContent [role=tab],body.nic-admin [role=tab]').forEach(t=>{const active=t.id==='tab-'+key;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;$(t.getAttribute('aria-controls')).hidden=!active;});if($('statsReset'))$('statsReset').hidden=key!=='stats'||$('statsSource').value!=='database'||!window.NICAccess?.enabled;syncAdminMenu(key);history.replaceState(null,'',(document.getElementById('nicAdminContent')?'#admin-':'#')+key);}
form.noValidate=true;
const adminNav=document.querySelector('#nicAdminContent .admin-tabs,body.nic-admin .admin-tabs');
if(adminNav){
 adminNav.id='nicAdminNavigation';
 adminMenuButton=document.createElement('button');adminMenuButton.type='button';adminMenuButton.className='admin-menu-toggle';
 adminMenuButton.setAttribute('aria-controls',adminNav.id);adminMenuButton.setAttribute('aria-expanded','false');
 adminMenuButton.innerHTML='<span>Admin-Menü · <strong data-active-admin-label>Unternehmensdaten</strong></span><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>';
 adminNav.before(adminMenuButton);
 adminMenuButton.addEventListener('click',()=>setAdminMenuOpen(adminMenuButton.getAttribute('aria-expanded')!=='true'));
 document.addEventListener('keydown',event=>{if(event.key==='Escape'&&adminMenuButton.getAttribute('aria-expanded')==='true'){setAdminMenuOpen(false);adminMenuButton.focus();}});
 document.addEventListener('click',event=>{if(!adminNav.contains(event.target)&&!adminMenuButton.contains(event.target))setAdminMenuOpen(false);});
 adminNav.setAttribute('aria-orientation','vertical');
 setAdminMenuOpen(false);
}
const tabs=Array.from(document.querySelectorAll('#nicAdminContent [role=tab],body.nic-admin [role=tab]'));tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>selectTab(tab.id.replace('tab-','')));tab.addEventListener('keydown',e=>{let i;if(e.key==='ArrowRight'||e.key==='ArrowDown')i=(index+1)%tabs.length;else if(e.key==='ArrowLeft'||e.key==='ArrowUp')i=(index-1+tabs.length)%tabs.length;else if(e.key==='Home')i=0;else if(e.key==='End')i=tabs.length-1;else return;e.preventDefault();tabs[i].click();tabs[i].focus();});});
form.addEventListener('input',e=>{if(e.target.closest('[data-stats-filter]'))return;markDirty();updatePreview();});
// Serialize checkbox saves: a second click must never overwrite an in-flight edit.
let savingAccess=false,accessSaveRequested=false;
async function persistAccessChanges(){
 if(savingAccess){accessSaveRequested=true;return;}
 savingAccess=true;
 const button=$('saveSettings');
 button.disabled=true;
 try{
  do{
   accessSaveRequested=false;
   const requested=collect();
   const online=window.NICAccess?.enabled===true;
   status(online?'Speichere Einstellungen und Inhalte auf dem Server …':'Speichere Einstellungen lokal im Browser …');
   await S.saveGlobal(requested);
   const confirmed=online?await window.NICAccess.loadSettings():S.current;
   if(!confirmed)throw Error('Gespeicherte Einstellungen konnten nicht zurückgelesen werden.');
   const actual=S.normalize(confirmed);
   const mismatch=contentSectionCatalog.find(item=>{
    const expected=requested.contentSections[item.key];
    const found=actual.contentSections[item.key];
    return !found||found.visible!==expected.visible||found.guestAllowed!==expected.guestAllowed;
   });
   if(mismatch)throw Error('Server hat die Box „'+mismatch.title+'“ nicht übernommen.');
   if(JSON.stringify(actual.content)!==JSON.stringify(requested.content))throw Error('Server hat die Content-Texte nicht vollständig übernommen.');
   // Do not reset checkboxes while further changes are waiting.
   if(!accessSaveRequested){
    S.apply(actual);
    dirty=false;
    $('saveState').textContent=online?'Auf Server bestätigt':'Lokal gespeichert';
    status(online?'Einstellungen und Content-Texte dauerhaft gespeichert und vom Server zurückgelesen.':'Lokal im Browser gespeichert. Für alle Besucher ist eine Server-Veröffentlichung erforderlich.');
   }
  }while(accessSaveRequested);
 }catch(err){
  dirty=true;
  $('saveState').textContent='Nicht gespeichert';
  status('Server-Speicherung fehlgeschlagen: '+err.message,true);
 }finally{
  button.disabled=false;
  savingAccess=false;
 }
}
form.addEventListener('change',e=>{
 if(e.target.matches?.('[id^="content-visible-"],[id^="content-guest-"]')){
  markDirty();
  persistAccessChanges();
 }
});
form.addEventListener('submit',async e=>{
 e.preventDefault();if(!validForm())return;
 if(savingAccess){accessSaveRequested=true;return;}
 await persistAccessChanges();
});
$('exportSettings').addEventListener('click',()=>{if(!validForm())return;const blob=new Blob([JSON.stringify(collect(),null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='site-settings.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('Konfiguration exportiert. Die Veröffentlichung ist ein separater Schritt.');});
$('importSettings').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>4000000)throw new Error('Datei ist zu groß (maximal 4 MB).');if(dirty&&!confirm('Ungespeicherte Änderungen durch die importierte Konfiguration ersetzen?'))return;const s=S.normalize(JSON.parse(await file.text()));fill(s);markDirty();status('Importiert. Prüfe die Angaben und speichere den Entwurf lokal.');}catch(err){status('Import fehlgeschlagen: '+err.message,true);}finally{e.target.value='';}});
$('discardSettings').addEventListener('click',()=>{if(!confirm('Lokale Einstellungen verwerfen und den veröffentlichten Stand laden?'))return;try{fill(S.discard());S.apply(S.published);dirty=false;$('saveState').textContent='Veröffentlichter Stand geladen';status('Der lokale Entwurf wurde entfernt.');}catch(err){status('Zurücksetzen fehlgeschlagen: '+err.message,true);}});
$('faviconFile').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>2*1024*1024)throw new Error('Bitte ein Bild bis maximal 2 MB wählen.');if(!['image/png','image/jpeg','image/webp','image/x-icon','image/vnd.microsoft.icon'].includes(file.type)&&!(/\.ico$/i.test(file.name)&&!file.type))throw new Error('Bitte PNG, JPG, WebP oder ICO wählen.');const url=URL.createObjectURL(file);const img=new Image();try{await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(new Error('Das Bild konnte nicht gelesen werden.'));img.src=url;});const canvas=document.createElement('canvas');canvas.width=canvas.height=128;const ctx=canvas.getContext('2d');const size=Math.min(img.naturalWidth,img.naturalHeight);ctx.drawImage(img,(img.naturalWidth-size)/2,(img.naturalHeight-size)/2,size,size,0,0,128,128);favicon=canvas.toDataURL('image/png');$('faviconPreview').src=favicon;markDirty();status('Favicon vorbereitet. Mit „Speichern“ übernehmen.');}finally{URL.revokeObjectURL(url);}}catch(err){status(err.message,true);}finally{e.target.value='';}});
$('removeFavicon').addEventListener('click',()=>{favicon='';$('faviconPreview').src='icon.svg';$('faviconFile').value='';markDirty();});
let sharingPreviewSequence=0;
async function updateSharingPreview(){
 const sequence=++sharingPreviewSequence,canvas=$('sharingPreview'),ctx=canvas.getContext('2d'),img=new Image();
 try{
  await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=sharingImage||websiteLogo||'share-logo.png';});
  if(sequence!==sharingPreviewSequence)return;
  ctx.fillStyle='#f5f7fb';ctx.fillRect(0,0,1200,630);
  const scale=Math.min(800/img.naturalWidth,300/img.naturalHeight);const w=img.naturalWidth*scale,h=img.naturalHeight*scale;
  ctx.drawImage(img,(1200-w)/2,90+(300-h)/2,w,h);
  ctx.fillStyle='#07345f';ctx.textAlign='center';ctx.textBaseline='middle';
  const words=$('sharingText').value.trim().split(/\s+/);let lines=[],fontSize=38;
  for(;fontSize>=14;fontSize--){
   ctx.font=fontSize+'px Arial, sans-serif';lines=[];let line='';
   for(const word of words){const next=line?line+' '+word:word;if(line&&ctx.measureText(next).width>1000){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);
   if(lines.length<=3&&lines.every(x=>ctx.measureText(x).width<=1000))break;
  }
  while(lines.some(x=>ctx.measureText(x).width>1000)&&fontSize>6){fontSize--;ctx.font=fontSize+'px Arial, sans-serif';}
  lines.forEach((line,i)=>ctx.fillText(line,600,450+i*46));
  $('sharingPreviewStatus').textContent='Vorschau · 1200 × 630 Pixel · wird erst nach globaler Veröffentlichung beim Teilen verwendet.';
 }catch(_){if(sequence===sharingPreviewSequence)$('sharingPreviewStatus').textContent='Das Vorschaubild konnte nicht geladen werden.';}
}
$('sharingFile').addEventListener('change',async e=>{
 const file=e.target.files[0];if(!file)return;
 try{
  if(file.size>2*1024*1024)throw new Error('Bitte ein Bild bis maximal 2 MB wählen.');
  if(!['image/png','image/jpeg','image/webp'].includes(file.type))throw new Error('Bitte PNG, JPG oder WebP wählen.');
  const url=URL.createObjectURL(file),img=new Image();
  try{
   await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(new Error('Das Bild konnte nicht gelesen werden.'));img.src=url;});
   const canvas=document.createElement('canvas');let scale=Math.min(1,1200/img.naturalWidth,630/img.naturalHeight),value;
   do{canvas.width=Math.max(1,Math.round(img.naturalWidth*scale));canvas.height=Math.max(1,Math.round(img.naturalHeight*scale));const ctx=canvas.getContext('2d');ctx.fillStyle='#ffffff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);value=canvas.toDataURL('image/jpeg',.85);scale*=.8;}while(value.length>400000);
   sharingImage=value;updateSharingPreview();markDirty();status('Bildmotiv vorbereitet. Mit „Speichern“ übernehmen.');
  }finally{URL.revokeObjectURL(url);}
 }catch(err){status(err.message,true);}finally{e.target.value='';}
});
$('removeSharingImage').addEventListener('click',()=>{sharingImage='';$('sharingFile').value='';updateSharingPreview();markDirty();});
function notifyLogo(){S.applyLogo(websiteLogo,$('alt-websiteLogo').value,S.websiteUrl($('company-website').value));}
$('websiteLogoFile').addEventListener('change',async e=>{
 const file=e.target.files[0];if(!file)return;
 try{
  if(file.size>2*1024*1024)throw new Error('Bitte ein Bild bis maximal 2 MB wählen.');
  if(!['image/png','image/jpeg','image/webp'].includes(file.type))throw new Error('Bitte PNG, JPG oder WebP wählen.');
  const url=URL.createObjectURL(file),img=new Image();
  try{
   await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(new Error('Das Bild konnte nicht gelesen werden.'));img.src=url;});
   if(!img.naturalWidth||!img.naturalHeight)throw new Error('Das Bild hat keine gültigen Abmessungen.');
   const canvas=document.createElement('canvas');let scale=Math.min(1,900/img.naturalWidth,340/img.naturalHeight),value;
   do{canvas.width=Math.max(1,Math.round(img.naturalWidth*scale));canvas.height=Math.max(1,Math.round(img.naturalHeight*scale));canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);value=canvas.toDataURL('image/png');scale*=.8;}while(value.length>400000);
   websiteLogo=value;updateSharingPreview();$('websiteLogoPreview').src=value;notifyLogo();markDirty();status('Webseiten-Logo als Header-Vorschau vorbereitet. Mit „Speichern“ übernehmen.');
  }finally{URL.revokeObjectURL(url);}
 }catch(err){status(err.message,true);}finally{e.target.value='';}
});
$('removeWebsiteLogo').addEventListener('click',()=>{websiteLogo='';updateSharingPreview();$('websiteLogoPreview').src='neustart-immocheck-logo.svg';$('websiteLogoFile').value='';notifyLogo();markDirty();});

$('appleTouchIconFile').addEventListener('change',async e=>{
 const file=e.target.files[0];if(!file)return;
 try{
  if(file.size>2*1024*1024)throw new Error('Bitte ein Bild bis maximal 2 MB wählen.');
  if(!['image/png','image/jpeg','image/webp'].includes(file.type))throw new Error('Bitte PNG, JPG oder WebP wählen.');
  const url=URL.createObjectURL(file),img=new Image();
  try{
   await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(new Error('Das Bild konnte nicht gelesen werden.'));img.src=url;});
   const canvas=document.createElement('canvas');canvas.width=canvas.height=180;const ctx=canvas.getContext('2d');
   ctx.fillStyle='#ffffff';ctx.fillRect(0,0,180,180);const scale=Math.min(180/img.naturalWidth,180/img.naturalHeight),w=img.naturalWidth*scale,h=img.naturalHeight*scale;
   ctx.drawImage(img,(180-w)/2,(180-h)/2,w,h);appleTouchIcon=canvas.toDataURL('image/png');$('appleTouchIconPreview').src=appleTouchIcon;
   markDirty();status('Apple Touch Icon als PNG mit 180 × 180 Pixeln vorbereitet. Mit „Speichern“ übernehmen.');
  }finally{URL.revokeObjectURL(url);}
 }catch(err){status(err.message,true);}finally{e.target.value='';}
});
$('removeAppleTouchIcon').addEventListener('click',()=>{appleTouchIcon='';$('appleTouchIconPreview').src='apple-touch-icon.png';$('appleTouchIconFile').value='';markDirty();});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
async function start(){build();form.hidden=true;try{await buildContentSectionControls();if(window.NICAccess&&!await window.NICAccess.requireAdmin()){$('saveState').textContent='Admin-Anmeldung erforderlich';status('Bitte als Administrator anmelden und den Bereich erneut öffnen.',true);return;}form.hidden=false;const globalStats=window.NICAccess?.enabled===true;document.querySelector('[data-global-statistics]').hidden=!globalStats;if(globalStats){$('statsSource').value='database';$('statsSource').dispatchEvent(new Event('change'));}const s=await S.init();fill(s);S.apply(s);$('saveState').textContent=S.isLocal?'Lokaler Entwurf geladen':'Veröffentlichte Einstellungen geladen';if(window.NICAccess?.enabled){document.querySelector('.storage-note')?.remove();$('saveSettings').textContent='Global speichern';document.querySelector('.configuration-tools>p').textContent='Mit „Global speichern“ werden alle Änderungen direkt in der Datenbank gespeichert und für alle Besucher angewendet. Die Konfigurationsdatei enthält keine Nutzerkonten; diese sicherst du separat im Bereich „Nutzerdaten sichern“.';document.querySelector('.publish-steps').hidden=true;document.querySelector('.publish-steps+p').hidden=true;document.querySelector('#panel-legal>.helper').textContent='„Global speichern“ übernimmt alle rechtlichen Texte für alle Besucher. „Konfiguration exportieren“ erstellt eine zusätzliche Sicherung der Einstellungen, ohne Nutzerkonten.';window.NICAccess.mountUsers();}status(window.NICAccess?.enabled?'Einstellungen werden zentral in der Datenbank gespeichert.':'Änderungen gelten nach dem Speichern nur auf diesem Gerät.');['saveSettings','exportSettings','discardSettings'].forEach(id=>$(id).disabled=false);}catch(err){status(err.message,true);$('saveState').textContent='Einstellungen nicht verfügbar';}const section=location.hash.replace(/^#(?:admin-)?/,'');if(['company','content','layout','social','meta','legal','users','stats'].includes(section))selectTab(section);const note=document.querySelector('.storage-note');if(note)note.hidden=false;}
window.NICAdminUI={select:selectTab,ready:null};
window.NICAdminUI.ready=start();
})();
