/* Shared Immobilien ABC content view; no separate page shell. */
(()=>{
'use strict';
const ROOT=new URL('.',document.currentScript.src);
let entriesPromise=null;
const fetchEntries=async()=>{
 // Wait for the public STRATO settings before falling back to the bundled ABC.
 if(window.NICSettings&&!window.NICSettings.ready)await window.NICSettings.init();
 const saved=window.NICSettings?.current?.meta?.immobilienABC;
 if(saved){
  try{
   const items=JSON.parse(saved);
   if(Array.isArray(items))return Promise.resolve(items.sort((a,b)=>a.term.localeCompare(b.term,'de')));
  }catch(error){console.warn('Ungültige gespeicherte ABC-Daten:',error);}
 }
 return entriesPromise||(entriesPromise=fetch(new URL('immobilien-abc.json',ROOT)).then(r=>{if(!r.ok)throw Error('Immobilien ABC konnte nicht geladen werden');return r.json();}).then(rows=>rows.sort((a,b)=>a.term.localeCompare(b.term,'de'))).catch(e=>{entriesPromise=null;throw e;}));
};
const normalize=value=>String(value||'').toLocaleLowerCase('de').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
let contextPromise=null;
const fetchContexts=()=>contextPromise||(contextPromise=fetch(new URL('immobilien-abc-context.json',ROOT))
 .then(r=>{if(!r.ok)throw Error('Rechnererklärungen nicht verfügbar');return r.json();})
 .catch(error=>{contextPromise=null;console.warn(error);return [];}));

const element=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
function render(panel){
 if(!panel)return;
 panel.dataset.signature='immobilien-abc';
 panel.replaceChildren();
 const view=element('section','nic-abc');
 view.setAttribute('aria-label','Immobilien ABC');
 const lead=element('p','nic-abc-lead','Wichtige Begriffe rund um Kauf, Notar, Finanzierung, Vermietung und die ImmoCheck-Rechner – einfach erklärt und mit Beispielen.');
 const toolbar=element('div','nic-abc-toolbar');
 const search=element('input','nic-abc-search');search.type='search';search.style.setProperty('display','block','important');search.style.setProperty('width','100%','important');search.style.setProperty('max-width','100%','important');search.style.setProperty('min-width','0','important');search.style.boxSizing='border-box';search.placeholder='Begriff suchen, z. B. Grundschuld …';search.autocomplete='off';search.setAttribute('aria-label','Immobilienbegriff suchen');
 toolbar.append(search);
 const categories=element('div','nic-abc-filters');categories.setAttribute('role','group');categories.setAttribute('aria-label','Thema auswählen');
 const headingRow=element('div','nic-abc-heading-row');
 const heading=element('h2','nic-abc-heading','Begriffe von A bis Z');
 const count=element('p','nic-abc-count');count.setAttribute('aria-live','polite');
 headingRow.append(heading,count);
 const list=element('div','nic-abc-list');
 view.append(lead,toolbar,categories,headingRow,list);panel.append(view);
 let category='Alle',rows=[];
 const termId=new URLSearchParams(location.search).get('begriff');
 function draw(){
  const query=normalize(search.value.trim());
  const filtered=rows.filter(row=>(category==='Alle'||row.category===category)&&normalize(row.term+' '+row.explanation+' '+row.example).includes(query));
  count.textContent=filtered.length+' Begriffe von '+rows.length+' Begriffen';
  const fragment=document.createDocumentFragment();
  for(const item of filtered){
   const details=element('details','nic-abc-entry');details.id='begriff-'+item.id;
   const summary=element('summary','nic-abc-summary');
   const labelStack=element('span','nic-abc-title-stack');
   labelStack.append(element('strong','',item.term),element('small','nic-abc-subtext',item.category));
   summary.append(labelStack);
   const body=element('div','nic-abc-detail');
   body.append(element('p','',item.explanation));
   if(item.example?.trim()){
    const example=element('div','nic-abc-example');
    example.append(element('strong','','Beispiel'),element('p','',item.example));body.append(example);
   }
   details.append(summary,body);fragment.append(details);
   if(item.id===termId){details.open=true;requestAnimationFrame(()=>details.scrollIntoView({block:'center'}));}
  }
  list.replaceChildren(fragment);
  if(!filtered.length)list.append(element('p','nic-abc-empty','Keine passenden Begriffe gefunden.'));
 }
 fetchEntries().then(data=>{
  if(!panel.isConnected||!panel.contains(view))return;
  rows=data;
  for(const cat of ['Alle',...new Set(data.map(e=>e.category))]){
   const button=element('button','nic-abc-filter',cat);button.type='button';button.dataset.category=cat;
   button.setAttribute('aria-pressed',String(cat===category));
   button.addEventListener('click',()=>{category=cat;for(const btn of categories.children)btn.setAttribute('aria-pressed',String(btn.dataset.category===cat));draw();});
   categories.append(button);
  }
  if(termId){const found=rows.find(x=>x.id===termId);if(found)category='Alle';}
  draw();
 }).catch(()=>{count.textContent='';list.replaceChildren(element('p','nic-abc-empty','Die Begriffe konnten gerade nicht geladen werden. Bitte versuche es erneut.'));});
 search.addEventListener('input',draw);
}
/* Context help: retain calculator-specific content before hiding its old control. */
const aliases={'restschuld':'restschuld','sondertilgung':'sondertilgung','eigenkapital':'eigenkapital','zinssatz':'sollzins','sollzins':'sollzins','tilgung':'tilgung','kaufnebenkosten':'kaufnebenkosten','grunderwerbsteuer':'grunderwerbsteuer','kaufpreis':'kaufpreis','hausgeld':'hausgeld','cashflow':'cashflow','kaltmiete':'kaltmiete','warmmiete':'warmmiete','mietrendite':'bruttomietrendite','kaufpreisfaktor':'kaufpreisfaktor','zinsbindung':'zinsbindung','annuität':'annuitat','budget':'haushaltsuberschuss'};
let contextEntries=null,openTrigger=null,contextDialog=null;
function contextClose(){
 if(contextDialog){contextDialog.remove();contextDialog=null;}
 const prior=openTrigger;openTrigger=null;
 if(prior&&prior.isConnected)prior.focus({preventScroll:true});
}
function contextOpen(trigger,item,legacy,rich){
 contextClose();
 openTrigger=trigger;
 const wrap=element('div','nic-abc-context-backdrop');
 const dialog=element('section','nic-abc-context-dialog');
 dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-label',item.term);
 const head=element('div','nic-abc-context-head');
 const heading=element('h2','',item.term);
 const close=element('button','nic-abc-context-close','×');close.type='button';close.setAttribute('aria-label','Erklärung schließen');
 close.addEventListener('click',contextClose);head.append(heading,close);dialog.append(head);
 dialog.append(element('p','nic-abc-context-description',item.explanation));
 if(legacy&&normalize(legacy)!==normalize(item.explanation)){
  const section=element('section','nic-abc-context-additional');
  section.append(element('h3','','Zum Rechner'),element('p','',legacy));dialog.append(section);
 }
 if(rich){
  if(rich.body?.trim()&&normalize(rich.body)!==normalize(item.explanation)&&normalize(rich.body)!==normalize(legacy)){
   const calculator=element('section','nic-abc-context-additional');
   calculator.append(element('h3','','Zum Rechner'),element('p','',rich.body));dialog.append(calculator);
  }
  if(rich.plain?.trim()){
   const simple=element('section','nic-abc-context-additional');
   simple.append(element('h3','','Einfach gesagt'),element('p','',rich.plain));dialog.append(simple);
  }
  if(rich.know?.trim()){
   const know=element('section','nic-abc-context-additional');
   know.append(element('h3','','Gut zu wissen'),element('p','',rich.know));dialog.append(know);
  }
 }
 if(item.example?.trim()){
  const examples=element('details','nic-abc-context-example');
  examples.append(element('summary','','Praxisbeispiel anzeigen'),element('p','',item.example));dialog.append(examples);
 }
 wrap.append(dialog);
 wrap.addEventListener('click',event=>{if(event.target===wrap)contextClose();});
 document.body.append(wrap);contextDialog=wrap;close.focus({preventScroll:true});
}
document.addEventListener('keydown',event=>{
 if(!contextDialog)return;
 if(event.key==='Escape'){event.preventDefault();contextClose();}
 if(event.key==='Tab'){
  const controls=Array.from(contextDialog.querySelectorAll('button,summary,[tabindex="0"]'));
  if(controls.length<2)return;
  const first=controls[0],last=controls[controls.length-1];
  if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}
  else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
 }
});
function identifyLegacy(label){
 const controls=[...label.querySelectorAll('.inline-info,.info-btn,.info-dot,.rent-info-dot')];
 const control=controls.length===1?controls[0]:null;
 if(!control)return null;
 // Only consolidate content we can actually read. Do not discard script-owned
 // calculation details from legacy sheets that are not present in the DOM.
 const detail=(control.getAttribute('data-info')||control.getAttribute('data-tooltip')||'').trim();
 return {control,detail,isReference:/^[A-Za-z][A-Za-z0-9_]*$/.test(detail)};
}
function markTerm(label,item,legacy,rich){
 const walker=document.createTreeWalker(label,NodeFilter.SHOW_TEXT,{
  acceptNode(node){
   return node.parentElement?.closest('button, input, select, textarea, .nic-abc-term, .nic-abc-help, .inline-info, .info-btn, .info-dot, .rent-info-dot')
    ?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT;
  }
 });
 const textNodes=[];while(walker.nextNode())textNodes.push(walker.currentNode);
 for(const node of textNodes){
  const raw=node.textContent||'',normalized=normalize(raw);
  const word=normalize(item.term);
  const pos=normalized.indexOf(word);
  if(pos<0||!(!pos||!/[a-z0-9]/i.test(normalized[pos-1]))||(/[a-z0-9]/i.test(normalized[pos+word.length]||'')))continue;
  // normalize can alter length for composed accents; only replace a direct
  // substring when index and length agree, otherwise leave the original safe.
  const original=raw.slice(pos,pos+item.term.length);
  if(normalize(original)!==word)continue;
  const button=element('button','nic-abc-term',original);
  button.type='button';button.setAttribute('aria-label',original+' erklären');
  button.addEventListener('click',async event=>{
   event.preventDefault();event.stopPropagation();
   // Resolve the term on each opening, rather than keeping a stale editor-era object.
   try{
    const rows=await fetchEntries();
    const latest=rows.find(row=>row.id===item.id)||item;
    if(button.isConnected)contextOpen(button,latest,rich?'':(legacy?.isReference?'':legacy?.detail||''),rich);
   }catch(error){console.warn('Aktuelle ABC-Erklärung nicht verfügbar:',error);if(button.isConnected)contextOpen(button,item,rich?'':(legacy?.isReference?'':legacy?.detail||''),rich);}
  });
  const before=document.createTextNode(raw.slice(0,pos)),after=document.createTextNode(raw.slice(pos+original.length));
  node.replaceWith(before,button,after);
  // A previously visible help control can be removed only if its complete
  // textual content has been carried over. Unknown legacy controls stay.
  if(legacy&&(legacy.detail||rich)&&(!legacy.isReference||(rich&&rich.key===legacy.detail))){
   legacy.control.hidden=true;
   legacy.control.setAttribute('aria-hidden','true');
   legacy.control.style.setProperty('display','none','important');
  }
  return true;
 }
 return false;
}
let hintRunning=false;
function showHints(){
 if(hintRunning||document.documentElement.dataset.nicPage==='immobilien-abc')return;
 const main=document.querySelector('.app>main.section');if(!main)return;
 hintRunning=true;
 Promise.all([fetchEntries(),fetchContexts()]).then(([items,contexts])=>{
  if(!main.isConnected)return;
  contextEntries=items;
  const byId=new Map(items.map(x=>[x.id,x]));
  const byName=new Map(items.map(x=>[normalize(x.term),x]));
  const byContext=new Map(contexts.map(x=>[normalize(x.term),x]));
  const byContextKey=new Map(contexts.filter(x=>x.key).map(x=>[x.key,x]));
  const terms=[...items].sort((a,b)=>b.term.length-a.term.length);
  for(const label of main.querySelectorAll('label')){
   if(label.closest('#nicContentView')||label.querySelector('.nic-abc-term'))continue;
   const legacy=identifyLegacy(label);
   // Some legacy labels contain an inline help icon: only the visible field
   // name is considered a glossary match, not the icon text.
   const clone=label.cloneNode(true);
   clone.querySelectorAll('button,.nic-abc-help,.info-btn,.info-dot').forEach(x=>x.remove());
   const full=normalize(clone.textContent).trim();
   const key=Object.keys(aliases).sort((a,b)=>b.length-a.length).find(k=>full===normalize(k)||full.startsWith(normalize(k)+' ')||full.startsWith(normalize(k)+'('));
   const entry=(key&&byId.get(aliases[key]))||terms.find(x=>{
    const term=normalize(x.term);return full===term||full.startsWith(term+' ')||full.startsWith(term+'(');
   });
   if(!entry)continue;
   const rich=byContext.get(normalize(entry.term))||byContext.get(full);
   // A source key takes precedence over a similarly named generic term.
   const context=(legacy?.isReference&&byContextKey.get(legacy.detail))||rich||(key&&byContext.get(normalize(key)));
   if(markTerm(label,entry,legacy,context)){
    label.querySelectorAll('.nic-abc-help').forEach(button=>button.remove());
   }
  }
  // Existing KPI information icons use the same structured legacy sheets.
  // Attach the subtle term interaction to each KPI heading, not its value.
  for(const card of main.querySelectorAll('.kpi')){
   const control=card.querySelector(':scope > button.info-btn[data-info], :scope > .name button.rent-info-dot[data-info]');
   const name=card.querySelector(':scope > .name');
   const heading=name?.querySelector(':scope > span')||name;
   if(!control||!heading||heading.querySelector('.nic-abc-term'))continue;
   const info=byContextKey.get(control.dataset.info)||byContext.get(normalize(heading.textContent.trim()));
   const entry=info&&byName.get(normalize(info.term));
   if(!entry)continue;
   markTerm(heading,entry,{control,detail:control.dataset.info,
    isReference:/^[A-Za-z][A-Za-z0-9_]*$/.test(control.dataset.info)},info);
  }
 }).catch(error=>console.warn('Kontexthilfe konnte nicht geladen werden:',error)).finally(()=>{hintRunning=false;});
}
let hintQueued=false;
function queueHints(){
 if(hintQueued)return;hintQueued=true;
 requestAnimationFrame(()=>{hintQueued=false;showHints();});
}
const observer=new MutationObserver(changes=>{
 if(changes.some(change=>[...change.addedNodes].some(n=>n.nodeType===1&&!n.closest?.('.nic-abc-context-backdrop'))))queueHints();
});
document.addEventListener('DOMContentLoaded',()=>{
 observer.observe(document.querySelector('.app>main.section')||document.body,{childList:true,subtree:true});
 queueHints();
});

window.NICABC={render,showHints};
window.addEventListener('nic-route-changed',()=>{contextClose();queueHints();});

})();
