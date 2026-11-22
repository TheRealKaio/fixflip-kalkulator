(function(){
'use strict';
const S=window.NICSettings,$=id=>document.getElementById(id),form=$('settingsForm');let favicon='',appleTouchIcon='',websiteLogo='',sharingImage='',dirty=false,contentSectionCatalog=[],importedBase=null,mediaLibrary={};
function status(message,error=false){$('saveStatus').textContent=message;$('saveStatus').classList.toggle('error',error);}
function markDirty(){dirty=true;$('saveState').textContent='Ungespeicherte Änderungen';status(window.NICAccess?.enabled?'Noch nicht global gespeichert.':'Noch nicht im Browser gespeichert.');}
function field(parent,id,label,type='text',hint=''){
 const div=document.createElement('div');div.className='admin-field';const lab=document.createElement('label');lab.htmlFor=id;lab.textContent=label;div.append(lab);
 const input=document.createElement(type==='textarea'?'textarea':'input');input.id=id;input.name=id;if(type!=='textarea')input.type=type;input.maxLength=2000;input.placeholder='';div.append(input);
 if(hint){const small=document.createElement('span');small.className='helper';small.id=id+'-hint';input.setAttribute('aria-describedby',small.id);small.textContent=hint;div.append(small);}parent.append(div);return input;
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
const calculatorPages = ['budget', 'own', 'rent', 'flip', 'finance'];
const pageLabels = {
 budget:'Budget', own:'Eigenheim', rent:'Vermietung', flip:'Fix & Flip', finance:'Finanzierung',
 settlement:'Mieterabrechnung', website:'Startseite', prices:'Preise', why:'Warum ImmoCheck?',
 'immobilien-abc':'Immobilien ABC', about:'Über uns', contact:'Kontakt', login:'Anmelden', company:'Unternehmen (Direktlink)',
 impressum:'Impressum', agbs:'AGB', datenschutz:'Datenschutz', haftungsausschluss:'Haftungsausschluss',
 widerruf:'Widerruf', avv:'AVV', 'cookie-hinweis':'Cookie-Hinweis'
};
function buildContent(){
 const groups = [
  ['Rechner', calculatorPages],
  ['Mieterabrechnung', ['settlement']],
  ['Inhaltsseiten', ['website','prices','why','immobilien-abc','about','contact','login','company']],
  ['Rechtliche Seiten', Object.keys(S.seoRouteDefaults).filter(key =>
   !calculatorPages.includes(key) && !['admin','settlement','website','prices','why','immobilien-abc','about','contact','login','company'].includes(key))]
 ];
 for(const [label,keys] of groups){
  const group=document.createElement('section');
  group.className='admin-page-group';
  const heading=document.createElement('h3');
  heading.textContent=label;
  group.append(heading);
  for(const key of keys)buildPage(group,key);
  $('contentEditors').append(group);
 }
}
function buildPage(group,route){
 const key=route==='website'?'welcome':route;
 const defaults=S.contentPageDefaults[key];
 const legacyMeta=S.pages.find(([page])=>page===route);
 const page=document.createElement('details');
 page.className='form-card admin-page';
 page.dataset.adminPage=route;
 const summary=document.createElement('summary');
 const title=document.createElement('span');
 title.textContent=pageLabels[route]||route;
 const badge=document.createElement('span');
 badge.className='helper admin-page-noindex';
 badge.textContent='Noindex';
 badge.hidden=true;
 title.append(badge);
 summary.append(title);
 page.append(summary);
 if(defaults)buildPageContent(page,key,defaults);

 const meta=document.createElement('fieldset');
 const legend=document.createElement('legend');
 legend.textContent='Metadaten';
 meta.append(legend);
 if(legacyMeta || defaults){
  const prefix=legacyMeta&&!calculatorPages.includes(route)?'meta-'+route:'content-'+key;
  const useMetaKeys=prefix.startsWith('meta-');
  field(meta,prefix+(useMetaKeys?'-title':'-seoTitle'),'Meta-Titel','text',
   'Titel für das Suchergebnis. Rund 60 Zeichen sind ein Richtwert.').maxLength=200;
  field(meta,prefix+(useMetaKeys?'-description':'-metaDescription'),'Meta-Beschreibung','textarea',
   'Kurze Zusammenfassung für das Suchergebnis. Rund 155 Zeichen sind ein Richtwert.').maxLength=500;
  const preview=document.createElement('div'), searchTitle=document.createElement('strong'), searchText=document.createElement('p');
  preview.className='search-preview';
  searchTitle.id='search-'+route+'-title';
  searchText.id='search-'+route+'-description';
  preview.append(searchTitle,searchText);
  meta.append(preview);
 }

 const row=document.createElement('label'), input=document.createElement('input'), caption=document.createElement('span');
 row.className='admin-page-index';
 input.type='checkbox';
 input.id='seo-index-'+route;
 input.checked=!S.seoRouteDefaults[route];
 input.disabled=route==='login';
 caption.textContent='Von Suchmaschinen ausschließen';
 const hint=document.createElement('p');
 hint.className='helper';
 hint.id=input.id+'-hint';
 hint.textContent=input.disabled?'Für diese Seite ist Noindex dauerhaft gesetzt.':
  'Mit diesem Haken erhält die Seite die Anweisung „Noindex“. Die Änderung wird mit der nächsten Veröffentlichung im HTML und in der Sitemap wirksam.';
 input.setAttribute('aria-describedby',hint.id);
 row.append(caption,input);
 meta.append(row,hint);
 page.append(meta);
 if(route==='website')buildWebsiteFields(page);
 group.append(page);
}
function escapeHtml(value){return String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));}
function renderMediaLibrary(){const list=$('contentMediaList');if(!list)return;list.replaceChildren();const values=Object.values(mediaLibrary);if(!values.length){const e=document.createElement('p');e.className='helper';e.textContent='Noch keine Dateien hochgeladen.';list.append(e);}for(const item of values){const row=document.createElement('div');row.className='content-media-item';const label=document.createElement('span');label.textContent=(item.type==='pdf'?'PDF · ':'Bild · ')+item.name;const del=document.createElement('button');del.type='button';del.className='button content-media-remove';del.textContent='Datei löschen';del.addEventListener('click',()=>{if(!confirm('„'+item.name+'“ aus der Medienbibliothek löschen? Die Datei wird beim Speichern entfernt. Bereits verwendete Stellen müssen dann ebenfalls angepasst werden.'))return;delete mediaLibrary[item.id];renderMediaLibrary();$('contentMediaStatus').textContent='Datei zum Löschen vorgemerkt. Bitte global speichern.';markDirty();updatePreview();});row.append(label,del);list.append(row);}refreshMediaChoices();}
function refreshMediaChoices(){document.querySelectorAll('[data-content-media-select]').forEach(select=>{const value=select.value;select.replaceChildren();const first=document.createElement('option');first.value='';first.textContent='Medium auswählen …';select.append(first);for(const item of Object.values(mediaLibrary)){const option=document.createElement('option');option.value=item.id;option.textContent=(item.type==='pdf'?'PDF · ':'Bild · ')+item.name;select.append(option);}if(mediaLibrary[value])select.value=value;});}
function buildMediaLibraryPanel(){const panel=document.createElement('div');panel.className='form-card content-media-panel';panel.innerHTML='<h3>Medien für Content-Seiten</h3><p class="helper">Bilder und PDFs hier hochladen und anschließend im jeweiligen Contentfeld einfügen. Die Dateien werden zentral gespeichert.</p><input id="contentMediaFiles" aria-label="Bilder oder PDFs auswählen" type="file" accept="image/png,image/jpeg,image/webp,application/pdf,.pdf" multiple><p class="helper">PNG, JPG, WebP oder PDF. Dateien bis 5 MB je Datei.</p><div id="contentMediaList" class="content-media-list"></div><p id="contentMediaStatus" class="helper" role="status"></p>';const tools=$('panel-layout').querySelector('.configuration-tools');if(tools)tools.before(panel);else $('panel-layout').append(panel);$('contentMediaFiles').addEventListener('change',async e=>{try{for(const file of Array.from(e.target.files||[])){let item={id:crypto.randomUUID(),name:file.name.slice(0,120)};if(file.size>5*1024*1024)throw Error('Dateien dürfen höchstens 5 MB groß sein: '+file.name);if(file.type==='application/pdf'||/\.pdf$/i.test(file.name)){item.type='pdf';}else{if(!['image/png','image/jpeg','image/webp'].includes(file.type))throw Error('Nicht unterstütztes Format: '+file.name);item.type='image';}if(!window.NICAccess?.uploadMedia)throw Error('Für den Medienupload ist die zentrale Admin-Anmeldung erforderlich.');const uploaded=await window.NICAccess.uploadMedia(file,item.id);mediaLibrary[uploaded.id]=uploaded;}renderMediaLibrary();markDirty();updatePreview();$('contentMediaStatus').textContent='Datei(en) vorbereitet. Bitte anschließend global speichern.';}catch(err){$('contentMediaStatus').textContent=err.message;$('contentMediaStatus').classList.add('error');}finally{e.target.value='';}});}
function readMediaData(file){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(String(r.result));r.onerror=()=>reject(Error('Datei konnte nicht gelesen werden.'));r.readAsDataURL(file);});}
async function optimizeContentImage(file){if(file.size<=300000)return readMediaData(file);const url=URL.createObjectURL(file);try{const img=new Image();img.src=url;await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(Error('Bild konnte nicht gelesen werden.'));});const canvas=document.createElement('canvas'),scale=Math.min(1,1600/img.naturalWidth,1600/img.naturalHeight);canvas.width=Math.max(1,Math.round(img.naturalWidth*scale));canvas.height=Math.max(1,Math.round(img.naturalHeight*scale));const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);for(let quality=.86;quality>=.42;quality-=.08){const data=canvas.toDataURL('image/jpeg',quality);if(data.length<=420000)return data;}throw Error('Bild ist auch verkleinert noch zu groß.');}finally{URL.revokeObjectURL(url);}}
function addContentLayoutButtons(input){const tools=document.createElement('div');tools.className='content-layout-tools';const title=field(tools,input.id+'-layout-title','Abschnittstitel (optional)');title.maxLength=240;const actions=document.createElement('div');actions.className='content-layout-actions';const notice=document.createElement('span');notice.className='helper';notice.setAttribute('role','status');for(const count of [2,3]){const b=document.createElement('button');b.type='button';b.className='button content-layout-button';b.textContent=count+' Spalten';b.addEventListener('click',()=>{const start=input.selectionStart,end=input.selectionEnd,selected=input.value.slice(start,end),h=document.createElement('h3');h.textContent=title.value.trim();const titleMarkup=h.textContent?h.outerHTML+'\n':'',opening='\n<section class="nic-content-section">\n'+titleMarkup+'<div class="nic-content-columns nic-content-columns-'+count+'">\n<div>',markup=opening+(selected||'<p></p>')+'</div>\n'+'<div><p></p></div>\n'.repeat(count-1)+'</div>\n</section>\n';if(input.value.length-selected.length+markup.length>input.maxLength){notice.textContent='Der Abschnitt überschreitet das Zeichenlimit.';return;}input.setRangeText(markup,start,end,'end');const caret=start+opening.length+(selected?selected.length:3);input.focus();input.setSelectionRange(caret,caret);title.value='';notice.textContent='Abschnitt mit '+count+' Spalten eingefügt.';input.dispatchEvent(new Event('input',{bubbles:true}));});actions.append(b);}const select=document.createElement('select');select.className='content-media-select';select.dataset.contentMediaSelect='true';select.setAttribute('aria-label','Medium zum Einfügen auswählen');const insert=document.createElement('button');insert.type='button';insert.className='button content-layout-button';insert.textContent='Medium einfügen';insert.addEventListener('click',()=>{const item=mediaLibrary[select.value];if(!item){notice.textContent='Bitte zuerst ein Medium auswählen.';return;}const start=input.selectionStart,end=input.selectionEnd,markup=item.type==='image'?'\n<img src="{{media.'+item.id+'}}" alt="'+escapeHtml(item.name.replace(/\.[^.]+$/,''))+'" loading="lazy">\n':'\n<a href="{{media.'+item.id+'}}" target="_blank" rel="noopener">PDF ansehen: '+escapeHtml(item.name)+'</a>\n';if(input.value.length-(end-start)+markup.length>input.maxLength){notice.textContent='Der Eintrag überschreitet das Zeichenlimit.';return;}input.setRangeText(markup,start,end,'end');input.focus();input.dispatchEvent(new Event('input',{bubbles:true}));notice.textContent=(item.type==='image'?'Bild':'PDF-Link')+' eingefügt.';});title.addEventListener('input',event=>event.stopPropagation());actions.append(select,insert);tools.append(actions,notice);input.parentElement.before(tools);refreshMediaChoices();}
function buildPageContent(page,key,defaults){
 const card=document.createElement('fieldset');
 card.className='content-editor-card';
 card.dataset.contentPage=key;
 const legend=document.createElement('legend');
 legend.textContent='Inhalt';
 card.append(legend);
  for(const [name,label,limit,type] of [['headerTitle','Headergrafik – Titel',70,'text'],['headerDescription','Headergrafik – Kurzbeschreibung',90,'textarea']]){
   const input=field(card,'content-'+key+'-'+name,label,type,'Wird ausschließlich im Header angezeigt. Leer lassen = keine Ausgabe.');
   input.maxLength=limit;input.value=defaults[name]||'';
   const counter=document.createElement('span');counter.className='counter';counter.id=input.id+'-count';
   input.parentElement.append(counter);
   input.addEventListener('input',()=>{counter.textContent=input.value.length+' / '+limit+' Zeichen';});
   counter.textContent=input.value.length+' / '+limit+' Zeichen';
   if(type==='textarea')input.parentElement.classList.add('wide');
  }
  const title=field(card,'content-'+key+'-title','Überschrift auf der Seite','text','Überschrift im Inhaltsbereich der Seite.');title.maxLength=240;title.value=defaults.title;
  if(key==='settlement')field(card,'content-'+key+'-boxTitle','Überschrift der Contentbox','text').maxLength=240;
  if(key==='settlement'){const lower=field(card,'content-settlement-lowerDescription','Unterer Informationstext (HTML möglich)','textarea','Erscheint unter den zwei Buttons bis zum Footer. Dieser Text kann jederzeit geändert werden.');lower.maxLength=S.CONTENT_HTML_LIMIT;lower.rows=9;lower.parentElement.classList.add('wide');}
  const description=field(card,'content-'+key+'-description','Inhalt der Box (HTML möglich)','textarea','Text für den Inhaltsbereich. Du kannst HTML-Absätze, Listen und Links verwenden.');description.maxLength=S.CONTENT_HTML_LIMIT;description.value=defaults.description;description.parentElement.classList.add('wide');description.rows=18;description.spellcheck=false;
  addContentLayoutButtons(description);
  const contentCounter=document.createElement('span');contentCounter.className='counter';contentCounter.dataset.contentCounter=key;description.parentElement.append(contentCounter);
  description.addEventListener('input',()=>{contentCounter.textContent=description.value.length+' / '+S.CONTENT_HTML_LIMIT+' Zeichen';});
  const bodyPreview=document.createElement('div');
  bodyPreview.className='legal-html-preview';
  bodyPreview.id='content-'+key+'-body-preview';
  card.append(Object.assign(document.createElement('strong'),{textContent:'Textvorschau'}),bodyPreview);
  page.append(card);
}
function buildWebsiteFields(page){
 const grid=document.createElement('fieldset');
 const legend=document.createElement('legend');
 legend.textContent='Startseiten-Kacheln und Google-Tag';
 grid.append(legend);
 for(const [name,config] of Object.entries(S.homeFields)){
  if(name==='homeTitle'||name==='homeDescription')continue;
  field(grid,'meta-website-'+name,config.label).maxLength=config.max;
 }
 const tag=field(grid,'meta-website-googleTag','Google-Tag-ID','text',
  'Optional. Für eine gemeinsame Gesamtauswertung denselben GA4-Datenstream verwenden.');
 tag.pattern='(G|GT)-[A-Za-z0-9]{4,30}';
 tag.maxLength=40;
 tag.placeholder='G-XXXXXXXXXX';
 tag.title='Google-Tag-ID mit G- oder GT- eintragen, keinen Script-Code.';
 page.append(grid);
}
function updateContentPreview(s){
 for(const key of Object.keys(S.contentPageDefaults)){
  document.querySelector('[data-content-counter="'+key+'"]').textContent=
   $('content-'+key+'-description').value.length+' / '+S.CONTENT_HTML_LIMIT+' Zeichen';
  $('content-'+key+'-body-preview').replaceChildren(S.contentFragment(s.content[key].description,s));
 }
 for(const route of Object.keys(S.seoRouteDefaults)){
  const index=$('seo-index-'+route);
  if(!index)continue;
  index.closest('details').querySelector('.admin-page-noindex').hidden=!index.checked;
  if(!$('search-'+route+'-title'))continue;
  const meta=S.pageMeta(s,route);
  $('search-'+route+'-title').textContent=meta.title;
  $('search-'+route+'-description').textContent=meta.description;
 }
}
function build(){
 buildContent();
 buildMediaLibraryPanel();
 buildLegal();
 for(const [key,title] of [['websiteLogo','Webseiten-Logo'],['favicon','Favicon'],['appleTouchIcon','Apple Touch Icon'],['sharing','Vorschaubild beim Teilen']]){const target=$(key==='sharing'?'sharingText':key+'File').closest(key==='sharing'?'.form-card':'div');field(target,'alt-'+key,'Alt-Text: '+title,'text',key==='favicon'||key==='appleTouchIcon'?'Bildbeschreibung für die Vorschau. Browser- und Home-Bildschirm-Icons besitzen kein HTML-Alt-Attribut.':'Beschreibe kurz den Bildinhalt für Screenreader und unterstützte Link-Vorschauen.').maxLength=300;}

 S.companyFields.forEach(([k,label],i)=>{const type=k==='email'?'email':['additional','disputeResolution','editorialAddress','professionalRules','authority'].includes(k)?'textarea':'text';const input=field($(i<11?'companyCore':'companyExtra'),'company-'+k,label,type,k==='website'?'Domain oder vollständige Internetadresse. Das Header-Logo öffnet diese Adresse. Ohne Eintrag führt es zur Startseite.':'');if(k==='website'){input.placeholder='www.beispiel.de';input.addEventListener('change',()=>{const value=S.websiteUrl(input.value);if(input.value.trim()&&!value)input.setCustomValidity('Bitte eine gültige Internetadresse eintragen.');else input.setCustomValidity('');});input.addEventListener('input',()=>input.setCustomValidity(''));}});
 const fontDiv=document.createElement('div');fontDiv.className='admin-field';const label=document.createElement('label');label.htmlFor='layout-font';label.textContent='Schriftfamilie';const select=document.createElement('select');select.id='layout-font';
 for(const [value,title] of [['system','Systemschrift'],['arial','Arial'],['verdana','Verdana'],['georgia','Georgia'],['trebuchet','Trebuchet MS']]){const o=document.createElement('option');o.value=value;o.textContent=title;select.append(o);}fontDiv.append(label,select);$('typeFields').append(fontDiv);
 for(const [k,title] of [['bodySize','Grundschriftgröße'],['subtextSize','Untertexte'],['hintSize','Hinweistexte'],['h1','H1 – Hauptüberschrift'],['h2','H2 – Abschnitt'],['h3','H3 – Unterabschnitt'],['h4','H4 – Detailüberschrift']]){const x=field($('typeFields'),'layout-'+k,title+' (px)','number');x.min=10;x.max=72;x.step=1;}
 const radius=field($('styleFields'),'layout-cornerRadius','Eckenradius (px)','number','Bisheriger Kartenradius: 22 px.');radius.min=0;radius.max=40;radius.step=1;
 for(const [key,label,value] of [['expandBackground','Hintergrundfarbe der Plusfläche','#FDE68A'],['expandBorder','Farbe der Umrandung','#FDE68A']]){const input=field($('styleFields'),'layout-'+key,label,'text');input.pattern='#[0-9A-Fa-f]{6}';input.maxLength=7;input.placeholder=value;input.title='HEX-Code mit # und sechs Zeichen, z. B. #FDE68A';const wrap=document.createElement('div');wrap.className='color-control';input.replaceWith(wrap);const picker=document.createElement('input');picker.type='color';picker.id='color-'+key;picker.setAttribute('aria-label',label+' auswählen');wrap.append(picker,input);picker.addEventListener('input',()=>{input.value=picker.value.toUpperCase();updatePreview();markDirty();});input.addEventListener('input',()=>{if(/^#[0-9a-f]{6}$/i.test(input.value))picker.value=input.value;});}
 const glyph=field($('styleFields'),'layout-expandGlyphSize','Größe des Pluszeichens (px)','number','8–24 px.');glyph.min=8;glyph.max=24;glyph.step=0.1;
 const padding=field($('styleFields'),'layout-expandPadding','Abstand des Pluszeichens zum Rand (px)','number','Innenabstand je Seite: 0–6 px.');padding.min=0;padding.max=6;padding.step=1;
 for(const [key,label,value] of [['footerExpandBackground','Hintergrundfarbe der Plusfläche','#EDF3FF'],['footerExpandBorder','Farbe der Umrandung','#C7D8FF'],['footerExpandInk','Farbe des Pluszeichens','#2563EB']]){const input=field($('footerStyleFields'),'layout-'+key,label,'text');input.pattern='#[0-9A-Fa-f]{6}';input.maxLength=7;input.placeholder=value;input.title='HEX-Code mit # und sechs Zeichen, z. B. #2563EB';const wrap=document.createElement('div');wrap.className='color-control';input.replaceWith(wrap);const picker=document.createElement('input');picker.type='color';picker.id='color-'+key;picker.setAttribute('aria-label',label+' auswählen');wrap.append(picker,input);picker.addEventListener('input',()=>{input.value=picker.value.toUpperCase();updatePreview();markDirty();});input.addEventListener('input',()=>{if(/^#[0-9a-f]{6}$/i.test(input.value))picker.value=input.value;});}
 const footerGlyph=field($('footerStyleFields'),'layout-footerExpandGlyphSize','Größe des Pluszeichens (px)','number','8–32 px; mindestens Footer-Grundschriftgröße.');footerGlyph.min=8;footerGlyph.max=32;footerGlyph.step=1;
 const footerPadding=field($('footerStyleFields'),'layout-footerExpandPadding','Abstand des Pluszeichens zum Rand (px)','number','Innenabstand je Seite: 0–3 px.');footerPadding.min=0;footerPadding.max=3;footerPadding.step=1;
 for(const [k,title] of [['background','Container-Hintergrund'],['outerBackground','Äußerer Seitenhintergrund'],['text','Text'],['greenBackground','Grün – Hintergrund (Buttons und Footer)'],['greenText','Grün – Textfarbe (AUTO oder HEX)'],['buttonBackground','Schwarz – Hintergrund (PDF, Teilen, Download)'],['buttonText','Schwarz – Textfarbe (AUTO oder HEX)'],['redBackground','Rot – Hintergrund (Neu berechnen, X)'],['redText','Rot – Textfarbe (AUTO oder HEX)'],['highlightBackground','Highlight-Farbe – Neutral (Gelb)'],['highlightGoodBackground','Highlight-Farbe – Sehr gut (Grün)'],['highlightWarningBackground','Highlight-Farbe – Warnungen (Rot)']]){
  const input=field($('colorFields'),'layout-'+k,title,'text');input.pattern=k.endsWith('Text')?'(AUTO|#[0-9A-Fa-f]{6})':'#[0-9A-Fa-f]{6}';input.maxLength=7;input.placeholder=k.endsWith('Text')?'AUTO oder #FFFFFF':'#000000';input.title='HEX-Code mit # und sechs Zeichen, z. B. #0F172A';const wrap=document.createElement('div');wrap.className='color-control';input.replaceWith(wrap);const picker=document.createElement('input');picker.type='color';picker.id='color-'+k;picker.setAttribute('aria-label',title+' auswählen');wrap.append(picker,input);picker.addEventListener('input',()=>{input.value=picker.value.toUpperCase();updatePreview();markDirty();});input.addEventListener('input',()=>{if(/^#[0-9a-f]{6}$/i.test(input.value))picker.value=input.value;});
 }
 S.portals.forEach(([k,label])=>{const input=field($('socialFields'),'social-'+k,label,'url','Vollständige Profiladresse mit https://');input.placeholder='https://';input.pattern='https?://.+';input.title='Bitte eine vollständige Adresse mit https:// oder http:// eintragen.';input.maxLength=2000;});
}
async function buildContentSectionControls(){const response=await fetch(new URL('/content-sections.json',S.ROOT),{cache:'no-store'});if(!response.ok)throw new Error('Die Liste der H2-Boxen konnte nicht geladen werden.');contentSectionCatalog=await response.json();const root=$('contentSectionControls');root.replaceChildren();const header=document.createElement('div');header.className='content-section-header';header.innerHTML='<strong>Inhalte</strong><strong>Anzeigen</strong><strong>Nur<br>Nutzer</strong>';root.append(header);let group='';for(const item of contentSectionCatalog){if(item.calculator!==group){group=item.calculator;const title=document.createElement('h5');title.className='content-section-group';title.textContent=item.calculatorLabel;root.append(title);}const row=document.createElement('div');row.className='content-section-row';row.dataset.contentKey=item.key;const label=document.createElement('span');label.lang='de';label.textContent=item.title.replace('Haushaltsinformationen','Haushalts\u00adinfor\u00adma\u00adtionen');const visible=document.createElement('input');visible.type='checkbox';visible.id='content-visible-'+item.key;visible.setAttribute('aria-label',item.title+': anzeigen');visible.checked=true;const guest=document.createElement('input');guest.type='checkbox';guest.id='content-guest-'+item.key;guest.setAttribute('aria-label',item.title+': nur für Nutzer');guest.checked=false;row.append(label,visible,guest);root.append(row);}}
const navigationLabels={budget:'Budgetrechner',own:'Eigenheim',rent:'Vermietung',flip:'Fix und Flip',finance:'Finanzierung & Restschuld',settlement:'Nebenkosten abrechnen',dropdown:'Rechner-Dropdown'};
const navigationSectionTitles={home:'Buttonleiste auf der Startseite',calculator:'Sechsfach-Buttonleiste auf Rechnerseiten',dropdownHome:'Dropdown auf der Startseite',dropdownOther:'Dropdown auf allen anderen Seiten'};
function buildNavigationControls(){
 const root=$('nicNavigationVisibilityFields');if(!root)return;
 root.classList.add('nic-navigation-admin-fields');root.replaceChildren();
 for(const section of S.navigationSections){
  const title=document.createElement('h4');title.className='nic-navigation-admin-group';title.textContent=navigationSectionTitles[section];root.append(title);
  const header=document.createElement('div');header.className='nic-navigation-admin-row nic-navigation-admin-head';
  for(const label of ['Menüelement','Mobil','Desktop / Rest']){
   const cell=document.createElement('strong');cell.textContent=label;header.append(cell);
  }
  root.append(header);
  for(const key of section.startsWith('dropdown')?['dropdown']:S.navigationItems){
   const row=document.createElement('div');row.className='nic-navigation-admin-row';
   const name=document.createElement('span');name.textContent=navigationLabels[key];row.append(name);
   for(const screen of ['mobile','desktop']){
    const box=document.createElement('input');box.type='checkbox';box.id='nic-navigation-'+section+'-'+screen+'-'+key;
    box.setAttribute('aria-label',navigationSectionTitles[section]+' · '+navigationLabels[key]+' · '+(screen==='mobile'?'Mobil':'Desktop / Rest'));
    box.checked=true;row.append(box);
   }
   root.append(row);
  }
 }
}
function collect(){
 const raw=JSON.parse(JSON.stringify(importedBase||S.current||{version:1}));
 raw.version=1;raw.seoIndexing={...(raw.seoIndexing||{})};for(const key of Object.keys(S.seoRouteDefaults))raw.seoIndexing[key]=(key==='admin'||key==='login')?false:!$('seo-index-'+key).checked;raw.company={...(raw.company||{})};raw.layout={...(raw.layout||{})};raw.social={...(raw.social||{})};raw.meta={...(raw.meta||{})};raw.content={...(raw.content||{})};
 raw.favicon=favicon;raw.appleTouchIcon=appleTouchIcon;raw.websiteLogo=websiteLogo;raw.mediaLibrary=mediaLibrary;
 raw.navigationVisibility={};for(const section of S.navigationSections){raw.navigationVisibility[section]={};for(const screen of ['mobile','desktop']){raw.navigationVisibility[section][screen]={};for(const key of section.startsWith('dropdown')?['dropdown']:S.navigationItems)raw.navigationVisibility[section][screen][key]=$('nic-navigation-'+section+'-'+screen+'-'+key).checked;}}
 S.companyFields.forEach(([k])=>raw.company[k]=$('company-'+k).value);Object.keys(S.layoutDefaults).forEach(k=>raw.layout[k]=$('layout-'+k).value);S.portals.forEach(([k])=>raw.social[k]=$('social-'+k).value);
 S.pages.filter(([k])=>!calculatorPages.includes(k)).forEach(([k])=>raw.meta[k]={...(raw.meta[k]||{}),title:$('meta-'+k+'-title').value,description:$('meta-'+k+'-description').value,googleTag:k==='website'?$('meta-website-googleTag').value:(raw.meta[k]?.googleTag||'')});
 Object.keys(S.contentPageDefaults).forEach(k=>raw.content[k]={...(raw.content[k]||{}),headerTitle:$('content-'+k+'-headerTitle').value,headerDescription:$('content-'+k+'-headerDescription').value,title:$('content-'+k+'-title').value,description:$('content-'+k+'-description').value,...(k==='settlement'?{boxTitle:$('content-'+k+'-boxTitle').value,lowerDescription:$('content-'+k+'-lowerDescription').value}:{})});
 for(const key of Object.keys(S.contentPageDefaults)){
  if(key==='welcome')continue;
  for(const [setting,legacy] of [['seoTitle','title'],['metaDescription','description']]){
   const input=$('content-'+key+'-'+setting);
   if(!calculatorPages.includes(key)||input.value!==input.dataset.savedValue){
    raw.content[key][setting]=input.value;
    if(calculatorPages.includes(key)&&!input.value.trim())raw.meta[key][legacy]='';
   }
  }
 }

 for(const name of Object.keys(S.homeFields)){const el=$('meta-website-'+name);if(el)raw.meta.website[name]=el.value;}
 raw.imageAlts={...(raw.imageAlts||{})};Object.keys(S.imageAltDefaults).forEach(k=>raw.imageAlts[k]=$('alt-'+k).value);raw.sharing={...(raw.sharing||{}),text:$('sharingText').value,image:sharingImage};
 raw.access={...(raw.access||{})};for(const key of ['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare'])raw.access[key]=$('access-'+key).checked;
 raw.contentSections={...(raw.contentSections||{})};for(const item of contentSectionCatalog)raw.contentSections[item.key]={...(raw.contentSections[item.key]||{}),visible:$('content-visible-'+item.key).checked,guestAllowed:!$('content-guest-'+item.key).checked};
 raw.reporting={...(raw.reporting||{}),propertyId:$('statsPropertyId').value,clientId:$('statsClientId').value};raw.legal={...(raw.legal||{})};for(const key of Object.keys(S.legalLabels)){const value=$('legal-'+key).value;raw.legal[key]=value===legalDefaults[key]?(legalStored[key]||''):value;}
 raw.meta.immobilienABC=window.NICABCAdmin.serialize();
 return S.normalize(raw);
}
function fill(s){mediaLibrary={...(s.mediaLibrary||{})};renderMediaLibrary();for(const section of S.navigationSections)for(const screen of ['mobile','desktop'])for(const key of section.startsWith('dropdown')?['dropdown']:S.navigationItems)$('nic-navigation-'+section+'-'+screen+'-'+key).checked=s.navigationVisibility[section][screen][key];for(const key of Object.keys(S.seoRouteDefaults)){const index=$('seo-index-'+key);if(index)index.checked=!s.seoIndexing[key];}for(const key of ['registrationBlocked','loginBlocked','calculators','pdfDownload','pdfShare'])$('access-'+key).checked=s.access[key];for(const item of contentSectionCatalog){const rule=s.contentSections[item.key]||{};$('content-visible-'+item.key).checked=rule.visible!==false;$('content-guest-'+item.key).checked=rule.guestAllowed===false;}legalStored={...s.legal};fillLegal(s);Object.keys(S.imageAltDefaults).forEach(k=>$('alt-'+k).value=s.imageAlts[k]);S.companyFields.forEach(([k])=>$('company-'+k).value=s.company[k]||'');Object.keys(S.layoutDefaults).forEach(k=>{ $('layout-'+k).value=s.layout[k];if($('color-'+k))$('color-'+k).value=s.layout[k];});S.portals.forEach(([k])=>$('social-'+k).value=s.social[k]||'');S.pages.filter(([k])=>!calculatorPages.includes(k)).forEach(([k])=>{['title','description'].forEach(p=>$('meta-'+k+'-'+p).value=s.meta[k][p]||'');});Object.keys(S.contentPageDefaults).forEach(k=>{for(const p of ['headerTitle','headerDescription','title','description',...(k==='settlement'?['boxTitle','lowerDescription']:[])])$('content-'+k+'-'+p).value=s.content[k][p]||'';for(const p of ['headerTitle','headerDescription']){const input=$('content-'+k+'-'+p);$('content-'+k+'-'+p+'-count').textContent=input.value.length+' / '+input.maxLength+' Zeichen';}});for(const key of Object.keys(S.contentPageDefaults)){
 if(key==='welcome')continue;
 for(const [setting,legacy] of [['seoTitle','title'],['metaDescription','description']]){
  const input=$('content-'+key+'-'+setting);
  input.value=s.content[key][setting]||s.meta[key]?.[legacy]||'';
  input.dataset.savedValue=input.value;
 }
}for(const name of Object.keys(S.homeFields)){const el=$('meta-website-'+name);if(el)el.value=s.meta.website[name];}$('meta-website-googleTag').value=s.meta.website.googleTag||'';$('statsPropertyId').value=s.reporting.propertyId;$('statsClientId').value=s.reporting.clientId;sharingImage=s.sharing.image;$('sharingText').value=s.sharing.text;$('sharingFile').value='';websiteLogo=s.websiteLogo||'';$('websiteLogoPreview').src=websiteLogo||'neustart-immocheck-logo.svg';$('websiteLogoFile').value='';notifyLogo();appleTouchIcon=s.appleTouchIcon||'';$('appleTouchIconPreview').src=appleTouchIcon||'apple-touch-icon.png';$('appleTouchIconFile').value='';favicon=s.favicon;$('faviconPreview').src=favicon||'icon.svg';$('faviconFile').value='';updatePreview();}
function luminance(hex){return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);}
function contrastColor(bg,choice){if(choice!=='AUTO')return choice;return luminance(bg)>.179?'#000000':'#FFFFFF';}
function updatePreview(){
 updateSharingPreview();
      const s=collect();updateLegal(s);updateContentPreview(s);for(const k of ['websiteLogo','favicon','appleTouchIcon'])$(k+'Preview').alt=s.imageAlts[k];$('sharingPreview').setAttribute('aria-label',s.imageAlts.sharing);notifyLogo();const l=s.layout,preview=$('layoutPreview');preview.style.fontFamily=S.fonts[l.font];preview.style.fontSize=l.bodySize+'px';for(const [key,label] of [['subtextSize','Untertext unter einer Überschrift'],['hintSize','Hinweis in einem Feld oder einer Box']]){let el=$('preview-'+key);if(!el){el=document.createElement('p');el.id='preview-'+key;el.textContent=label;preview.append(el);}el.style.fontSize=l[key]+'px';}preview.style.background=l.background;preview.style.color=l.text;preview.style.borderRadius=l.cornerRadius+'px';['h1','h2','h3','h4'].forEach(k=>preview.querySelector(k).style.fontSize=l[k]+'px');$('previewButton').style.background=l.greenBackground;$('previewButton').style.color=contrastColor(l.greenBackground,l.greenText);$('previewButton').style.borderRadius=Math.round(l.cornerRadius*10/22)+'px';
 const vals=[luminance(l.greenBackground),luminance(contrastColor(l.greenBackground,l.greenText))],ratio=(Math.max(...vals)+.05)/(Math.min(...vals)+.05);$('contrastNotice').textContent='Grüne Buttons – Kontrast: '+ratio.toFixed(1).replace('.',',')+':1'+(ratio<4.5?' · Für gut lesbaren kleinen Text sind mindestens 4,5:1 empfehlenswert.':' · Gut lesbarer Kontrast.');$('contrastNotice').classList.toggle('low-contrast',ratio<4.5);
 const root=$('imprintPreview');root.replaceChildren();S.imprint(s).forEach(({label,value})=>{const h=document.createElement('h4');h.textContent=label;const p=document.createElement('p');p.textContent=value;root.append(h,p);});

}
function validForm(){try{window.NICABCAdmin.validate();}catch(err){selectTab('immobilien-abc');status(err.message,true);return false;}const invalid=Array.from(form.querySelectorAll('input,textarea,select')).find(el=>!el.checkValidity());if(invalid){const section=invalid.closest('[role=tabpanel]');if(section)selectTab(section.id.replace('panel-',''));const details=invalid.closest('details');if(details)details.open=true;invalid.reportValidity();invalid.focus();return false;}return true;}
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
function selectTab(key){if(key==='meta')key='content';document.querySelectorAll('#nicAdminContent [role=tab],body.nic-admin [role=tab]').forEach(t=>{const active=t.id==='tab-'+key;t.setAttribute('aria-selected',String(active));t.tabIndex=active?0:-1;$(t.getAttribute('aria-controls')).hidden=!active;});if($('statsReset'))$('statsReset').hidden=key!=='stats'||$('statsSource').value!=='database'||!window.NICAccess?.enabled;syncAdminMenu(key);history.replaceState(null,'',(document.getElementById('nicAdminContent')?'#admin-':'#')+key);}
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
   window.NICABCAdmin.validate();
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
   if(JSON.stringify(actual.navigationVisibility)!==JSON.stringify(requested.navigationVisibility))throw Error('Server hat die Menü-Sichtbarkeit nicht vollständig gespeichert.');
    if(actual.meta.immobilienABC!==requested.meta.immobilienABC)throw Error('Der Server hat das Immobilien ABC nicht vollständig gespeichert.');
   // Do not reset checkboxes while further changes are waiting.
   if(!accessSaveRequested){
    S.apply(actual);
    importedBase=null;
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
 // Each menu checkbox must save and apply on its own, just like content access.
 // No additional Save click is required to hide one calculator navigation tile.
 if(e.target.matches?.('[id^="content-visible-"],[id^="content-guest-"],[id^="nic-navigation-"]')){
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
$('importSettings').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>4000000)throw new Error('Datei ist zu groß (maximal 4 MB).');if(dirty&&!confirm('Ungespeicherte Änderungen durch die importierte Konfiguration ersetzen?'))return;const s=S.normalize(JSON.parse(await file.text()));importedBase=s;await window.NICABCAdmin.load(s);fill(s);markDirty();status('Importiert. Prüfe die Angaben und speichere den Entwurf lokal.');}catch(err){importedBase=null;status('Import fehlgeschlagen: '+err.message,true);}finally{e.target.value='';}});
$('discardSettings').addEventListener('click',async ()=>{if(!confirm('Lokale Einstellungen verwerfen und den veröffentlichten Stand laden?'))return;try{const restored=S.discard();await window.NICABCAdmin.load(restored);fill(restored);S.apply(S.published);dirty=false;$('saveState').textContent='Veröffentlichter Stand geladen';status('Der lokale Entwurf wurde entfernt.');}catch(err){status('Zurücksetzen fehlgeschlagen: '+err.message,true);}});
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
async function start(){window.NICABCAdmin.start(markDirty);build();buildNavigationControls();form.hidden=true;try{await buildContentSectionControls();if(window.NICAccess&&!await window.NICAccess.requireAdmin()){$('saveState').textContent='Admin-Anmeldung erforderlich';status('Bitte als Administrator anmelden und den Bereich erneut öffnen.',true);return;}form.hidden=false;const globalStats=window.NICAccess?.enabled===true;document.querySelector('[data-global-statistics]').hidden=!globalStats;if(globalStats){$('statsSource').value='database';$('statsSource').dispatchEvent(new Event('change'));}const s=await S.init();await window.NICABCAdmin.load(s);fill(s);S.apply(s);$('saveState').textContent=S.isLocal?'Lokaler Entwurf geladen':'Veröffentlichte Einstellungen geladen';if(window.NICAccess?.enabled){document.querySelector('.storage-note')?.remove();$('saveSettings').textContent='Global speichern';document.querySelector('.configuration-tools>p').textContent='Mit „Global speichern“ werden alle Änderungen direkt in der Datenbank gespeichert und für alle Besucher angewendet. Die Konfigurationsdatei enthält keine Nutzerkonten; diese sicherst du separat im Bereich „Nutzerdaten sichern“.';document.querySelector('.publish-steps').hidden=true;document.querySelector('.publish-steps+p').hidden=true;document.querySelector('#panel-legal>.helper').textContent='„Global speichern“ übernimmt alle rechtlichen Texte für alle Besucher. „Konfiguration exportieren“ erstellt eine zusätzliche Sicherung der Einstellungen, ohne Nutzerkonten.';window.NICAccess.mountUsers();}status(window.NICAccess?.enabled?'Einstellungen werden zentral in der Datenbank gespeichert.':'Änderungen gelten nach dem Speichern nur auf diesem Gerät.');['saveSettings','exportSettings','discardSettings'].forEach(id=>$(id).disabled=false);}catch(err){status(err.message,true);$('saveState').textContent='Einstellungen nicht verfügbar';}const section=location.hash.replace(/^#(?:admin-)?/,'');if(['company','content','immobilien-abc','layout','social','meta','legal','users','stats'].includes(section))selectTab(section);const note=document.querySelector('.storage-note');if(note)note.hidden=false;}
window.NICAdminUI={select:selectTab,ready:null};
window.NICAdminUI.ready=start();
})();
