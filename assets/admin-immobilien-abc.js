/* Admin editor for the same Immobilien ABC data rendered on the public site. */
(function(){
'use strict';
let records=[],sequence=0,notify=()=>{};
const $=id=>document.getElementById(id);
const sort=(a,b)=>a.term.localeCompare(b.term,'de',{sensitivity:'base'});
const slug=s=>s.toLocaleLowerCase('de').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ß/g,'ss').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
const original = async () => {
 const r=await fetch(new URL('immobilien-abc.json',window.NICSettings.ROOT));
 if(!r.ok)throw Error('Die ursprünglichen Immobilienbegriffe konnten nicht geladen werden.');
 return r.json();
};
const publicRows=()=>records.map(item=>({
 id:slug(item.term.trim())||item.id||'neuer-begriff',
 term:item.term.trim(),category:item.category.trim(),
 explanation:item.explanation.trim(),example:item.example.trim()
})).sort(sort);
function matches(){
 const query=($('abcAdminSearch')?.value||'').trim().toLocaleLowerCase('de');
 const filtered=records.filter(row=>[row.term,row.category,row.explanation,row.example].some(value=>value.toLocaleLowerCase('de').includes(query)));
 $('abcAdminCount').textContent=filtered.length+' Begriffe von '+records.length+' Begriffen';
 return filtered.sort(sort);
}
function render(openId='',focus=false){
 const list=$('abcAdminRows');if(!list)return;
 const fragment=document.createDocumentFragment();
 for(const row of matches()){
  const details=node('details','nic-abc-admin-record');details.dataset.editorId=row._editorId;details.open=row._editorId===openId;
  const summary=node('summary','nic-abc-admin-summary');
  const labels=node('span','nic-abc-admin-labels');
  const title=node('strong','',row.term||'Neuer Begriff');
  const topic=node('small','',row.category||'Themengebiet eintragen');
  labels.append(title,topic);
  const remove=node('button','nic-abc-admin-remove','×');
  remove.type='button';remove.title='Begriff löschen';remove.setAttribute('aria-label',(row.term||'Neuen Begriff')+' löschen');
  remove.addEventListener('click',event=>{
   event.preventDefault();event.stopPropagation();
   if(!confirm('Diesen Begriff entfernen? Erst beim Speichern wird die Löschung übernommen.'))return;
   records=records.filter(item=>item!==row);notify();render();
  });
  summary.append(labels,remove);
  const fields=node('div','nic-abc-admin-fields');
  for(const [key,caption,max,multi] of [
   ['term','Titel',140,false],['category','Themengebiet',100,false],
   ['explanation','Erklärung',4000,true],['example','Beispiel (optional)',2000,true]
  ]){
   const label=node('label','nic-abc-admin-field');
   label.append(node('span','',caption));
   const control=node(multi?'textarea':'input','');
   if(!multi)control.type='text';else control.rows=3;
   control.value=row[key]||'';control.maxLength=max;
   control.required=key!=='example';control.dataset.abcField=key;
   control.addEventListener('input',()=>{
    row[key]=control.value;
    if(key==='term')title.textContent=control.value||'Neuer Begriff';
    if(key==='category')topic.textContent=control.value||'Themengebiet eintragen';
    notify();matches();
   });
   if(key==='term')control.addEventListener('change',()=>render(row._editorId));
   label.append(control);fields.append(label);
  }
  details.append(summary,fields);fragment.append(details);
 }
 list.replaceChildren(fragment);
 if(focus&&openId)list.querySelector('[data-editor-id="'+openId+'"] [data-abc-field="term"]')?.focus();
}
async function load(settings){
 let values=null;
 const stored=settings?.meta?.immobilienABC;
 if(stored){
  try{values=JSON.parse(stored);}catch(e){throw Error('Die gespeicherten Immobilienbegriffe sind ungültig: '+e.message);}
 }
 if(values===null)values=await original();
 if(!Array.isArray(values)||values.length>500)throw Error('Ungültiger Immobilien-ABC-Datenbestand (maximal 500 Begriffe).');
 records=values.map(row=>({
  _editorId:'abc-'+(++sequence),id:String(row.id||''),
  term:String(row.term||''),category:String(row.category||''),
  explanation:String(row.explanation||''),example:String(row.example||'')
 }));
 $('abcAdminSearch').value='';
 render();
}
function validate(){
 if(records.length>500)throw Error('Das Immobilien ABC darf höchstens 500 Einträge enthalten.');
 if(new TextEncoder().encode(JSON.stringify(publicRows())).length>180000)throw Error('Das Immobilien ABC ist für die sichere Speicherung zu groß. Bitte kürze einzelne Erklärungen oder Beispiele.');
 const seen=new Set();
 for(const row of records){
  const field=(!row.term.trim()?'term':!row.category.trim()?'category':!row.explanation.trim()?'explanation':null);
  const lowered=row.term.trim().toLocaleLowerCase('de');
  const duplicate=seen.has(lowered);seen.add(lowered);
  if(field||duplicate){
   $('abcAdminSearch').value='';render(row._editorId);
   $('abcAdminRows').querySelector('[data-editor-id="'+row._editorId+'"] [data-abc-field="'+(field||'term')+'"]')?.focus();
   throw Error(duplicate?'Doppelter Immobilienbegriff: '+row.term:'Bitte Titel, Themengebiet und Erklärung ergänzen.');
  }
 }
}
function start(onDirty){
 notify=onDirty;
 $('abcAdd').addEventListener('click',()=>{
  if(records.length>=500){alert('Maximal 500 Begriffe möglich.');return;}
  const row={_editorId:'abc-'+(++sequence),id:'',term:'',category:'',explanation:'',example:''};
  records.push(row);$('abcAdminSearch').value='';notify();render(row._editorId,true);
 });
 $('abcAdminSearch').addEventListener('input',()=>render());
}
window.NICABCAdmin={start,load,validate,serialize(){return JSON.stringify(publicRows());}};
})();
