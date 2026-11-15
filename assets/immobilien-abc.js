/* Shared Immobilien ABC content view; no separate page shell. */
(()=>{
'use strict';
const ROOT=new URL('.',document.currentScript.src);
let entriesPromise=null;
const fetchEntries=()=>{
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
const element=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
function render(panel){
 if(!panel)return;
 panel.dataset.signature='immobilien-abc';
 panel.replaceChildren();
 const view=element('section','nic-abc');
 view.setAttribute('aria-label','Immobilien ABC');
 const lead=element('p','nic-abc-lead','Wichtige Begriffe rund um Kauf, Notar, Finanzierung, Vermietung und die ImmoCheck-Rechner – einfach erklärt und mit Beispielen.');
 const toolbar=element('div','nic-abc-toolbar');
 const label=element('label','nic-abc-search-label','Begriff suchen');
 const search=element('input','nic-abc-search');search.type='search';search.placeholder='Begriff suchen, z. B. Grundschuld …';search.autocomplete='off';search.setAttribute('aria-label','Immobilienbegriff suchen');
 label.append(search);toolbar.append(label);
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
   const example=element('div','nic-abc-example');
   example.append(element('strong','','Beispiel'),element('p','',item.example));body.append(example);
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
function showHints(){
 if(document.documentElement.dataset.nicPage==='immobilien-abc')return;
 const main=document.querySelector('.app>main.section');if(!main)return;
 const aliases={'restschuld':'restschuld','sondertilgung':'sondertilgung','eigenkapital':'eigenkapital','zinssatz':'sollzins','sollzins':'sollzins','tilgung':'tilgung','kaufnebenkosten':'kaufnebenkosten','grunderwerbsteuer':'grunderwerbsteuer','kaufpreis':'kaufpreis','hausgeld':'hausgeld','cashflow':'cashflow','kaltmiete':'kaltmiete','warmmiete':'warmmiete','mietrendite':'bruttomietrendite','kaufpreisfaktor':'kaufpreisfaktor','zinsbindung':'zinsbindung','annuität':'annuitat','budget':'haushaltsuberschuss'};
 for(const label of main.querySelectorAll('label')){
  if(label.closest('#nicContentView,#nicFinanceModule .nic-abc-tooltip')||label.querySelector('.nic-abc-help'))continue;
  const text=normalize(label.textContent).trim();
  const word=Object.keys(aliases).find(k=>text===normalize(k)||text.startsWith(normalize(k)+' ')||text.startsWith(normalize(k)+'('));
  if(!word)continue;
  const button=element('button','nic-abc-help','?');button.type='button';button.setAttribute('aria-label','Begriff '+word+' im Immobilien ABC erklären');
  button.title='Im Immobilien ABC erklären';
  button.addEventListener('click',event=>{event.preventDefault();event.stopPropagation();const id=aliases[word];window.NICCalculatorNavigation?.select('immobilien-abc',true);history.replaceState(history.state,'','/immobilien-abc/?begriff='+encodeURIComponent(id));window.NICABC.render(document.getElementById('nicContentView'));});
  label.append(' ',button);
 }
}
window.NICABC={render,showHints};
window.addEventListener('nic-route-changed',()=>requestAnimationFrame(showHints));
document.addEventListener('DOMContentLoaded',()=>requestAnimationFrame(showHints));
})();
