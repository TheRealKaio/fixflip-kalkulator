(function(){
'use strict';
const ROOT=new URL('.',document.currentScript.src);
let config=null,boot=null,user=null,csrf=null,revision=null,authPending=null,requestPending=false,authControlsVersion=0;
async function api(route,body,query=''){
 const url=new URL(config.apiUrl);url.searchParams.set('r',route);if(query)for(const [k,v]of new URLSearchParams(query))url.searchParams.set(k,v);
 const headers={'X-NIC-Request':'1'};if(body!==undefined){headers['Content-Type']='application/json';if(csrf)headers['X-NIC-CSRF']=csrf;}
 const response=await fetch(url,{method:body===undefined?'GET':'POST',credentials:'include',headers,body:body===undefined?undefined:JSON.stringify(body),cache:'no-store',signal:AbortSignal.timeout(['email-change-start','email-change-approve','email-change-resend','request-code'].includes(route)?60000:15000)});
 let data;try{data=await response.json();}catch(_){throw Error('Die Schnittstelle liefert keine gültige Antwort.');}
 if(!response.ok){const error=Error(data.error||'Anfrage fehlgeschlagen.');error.status=response.status;if(response.status===401){user=null;csrf=null;window.dispatchEvent(new Event('nic-auth-changed'));}throw error;}
 return data;
}
function init(){
 if(!boot)boot=(async()=>{const r=await fetch(new URL('backend-config.json',ROOT),{cache:'no-store',signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error('Verbindungseinstellungen fehlen.');config=await r.json();if(config.enabled!==true)return false;
 const url=new URL(config.apiUrl);if(url.protocol!=='https:')throw Error('Die Schnittstelle benötigt HTTPS.');
 const me=await api('me');user=me.user;csrf=me.csrf;return true;})();
 return boot;
}
function element(tag,text,attrs={}){const el=document.createElement(tag);if(text)el.textContent=text;for(const [k,v]of Object.entries(attrs))el.setAttribute(k,v);return el;}
function message(text){const el=document.getElementById('nicAccessStatus');if(el)el.textContent=text;}
function login(){
 if(authPending)return authPending;
 authPending=new Promise(resolve=>{
 const modal=element('dialog',null,{'aria-labelledby':'nicLoginTitle'});modal.className='nic-auth-dialog';
 const form=element('form');form.innerHTML='<h2 id="nicLoginTitle">Anmelden oder registrieren</h2><p>Du erhältst einen einmaligen Code per E-Mail.</p><label>E-Mail-Adresse<input type="email" name="email" autocomplete="email" maxlength="254" required></label><label class="nic-register-choice"><input type="checkbox" name="register"><span>Neues Benutzerkonto anlegen</span></label><div data-names hidden><label>Vorname<input name="first_name" autocomplete="given-name" maxlength="100"></label><label>Nachname<input name="last_name" autocomplete="family-name" maxlength="100"></label></div><div data-code hidden><label>Anmeldecode<input name="code" inputmode="numeric" pattern="[0-9]{8}" autocomplete="one-time-code" maxlength="8"></label></div><p role="status" aria-live="polite"></p><div class="nic-auth-actions"><button type="submit">Code anfordern</button><button type="button" data-close>Abbrechen</button></div>';
 let challenge=null;const status=form.querySelector('[role=status]'),submit=form.querySelector('[type=submit]'),register=form.elements.register;
 register.addEventListener('change',()=>{form.querySelector('[data-names]').hidden=!register.checked;for(const key of ['first_name','last_name'])form.elements[key].required=register.checked;});
 const finish=ok=>{modal.close();modal.remove();authPending=null;resolve(ok);};
 form.querySelector('[data-close]').addEventListener('click',()=>finish(false));modal.addEventListener('cancel',event=>{event.preventDefault();finish(false);});
 form.addEventListener('submit',async event=>{event.preventDefault();if(requestPending)return;requestPending=true;submit.disabled=true;status.textContent='Bitte warten …';try{
 if(!challenge){const r=await api('request-code',{email:form.elements.email.value,register:register.checked,first_name:form.elements.first_name.value,last_name:form.elements.last_name.value});challenge=r.challenge;status.textContent=r.message;form.querySelector('[data-code]').hidden=false;form.elements.code.required=true;form.elements.email.readOnly=true;register.disabled=true;submit.textContent='Code bestätigen';form.elements.code.focus();}
 else{const r=await api('verify-code',{challenge,code:form.elements.code.value});user=r.user;csrf=r.csrf;window.dispatchEvent(new Event('nic-auth-changed'));if(window!==window.top)window.parent.postMessage({type:'nic-auth-changed'},location.origin);finish(true);}
 }catch(error){status.textContent=error.message;}finally{requestPending=false;submit.disabled=false;}});
 modal.append(form);document.body.append(modal);modal.showModal();form.elements.email.focus();
 });return authPending;
}
async function authorize(action){
 if(!await init())return true;
 try{await api('authorize',{action});return true;}catch(error){if(error.status!==401)throw error;}
 if(!await login())return false;
 await api('authorize',{action});return true;
}
async function requireAdmin(){
 if(!await init())return true;
 const me=await api('me');user=me.user;csrf=me.csrf;
 if(!user&&!await login())return false;
 if(user?.role!=='admin'){message('Dieser Bereich ist nur für Administratoren verfügbar.');return false;}
 return true;
}
async function loadSettings(){if(!await init())return null;const data=await api('settings');revision=data.revision;authControlsVersion=data.authControlsVersion||0;return data.settings;}
async function refresh(){if(!await init())return null;try{const me=await api('me');user=me.user;csrf=me.csrf;return user;}catch(error){if(error.status===401)return null;throw error;}}
async function saveSettings(settings){if((settings.access?.registrationBlocked||settings.access?.loginBlocked)&&authControlsVersion<1)throw Error('Bitte zuerst die aktualisierte app.php auf STRATO hochladen. Die Sperren wurden nicht gespeichert.');if(!await requireAdmin())throw Error('Admin-Anmeldung erforderlich.');return api('settings',{settings,revision}).then(data=>{revision=data.revision;return data.settings;});}
async function logout(){await api('logout',{});user=null;csrf=null;window.dispatchEvent(new Event('nic-auth-changed'));const destination=new URL('.',ROOT);destination.searchParams.set('logged-out','1');window.top.location.replace(destination.href);}
async function profile(){
 if(!await init())return;
 if(!user&&!await login())return;
 location.hash=user.role==='admin'?'#admin':'#account';
}
function mountUsers(){
 const panel=document.getElementById('panel-users');if(!panel||!config?.enabled||user?.role!=='admin'||panel.querySelector('.nic-user-admin-card'))return;
 const old=panel.querySelector('[data-access-pending]');if(old)old.textContent='Zentrale Nutzerverwaltung aktiv. Gespeicherte Regeln gelten für alle Besucher.';
 const backup=element('section',null,{class:'configuration-tools nic-user-backup-tools'});backup.id='nicUserBackupTools';backup.append(element('h2','Nutzerdaten sichern'),element('p','Sichere alle Nutzerkonten als CSV mit Vorname, Nachname und E-Mail. Der Export umfasst auch unbestätigte und gesperrte Konten. Der Import legt fehlende Konten als unbestätigte Benutzer an und ändert bei vorhandenen E-Mail-Adressen nur Vor- und Nachname. Rollen, Sperren und Bestätigungsstatus bleiben erhalten.'));
 const backupRow=element('div',null,{class:'tool-row'}),backupButton=element('button','Nutzerdaten als CSV sichern',{type:'button'}),importButton=element('button','Nutzerdaten importieren',{type:'button'}),importFile=element('input',null,{type:'file',accept:'.csv,text/csv',hidden:true}),backupStatus=element('p',null,{role:'status','aria-live':'polite'});
 backupRow.append(backupButton,importButton,importFile);backup.append(backupRow,backupStatus);const settingsTools=document.querySelector('.configuration-tools');if(settingsTools)settingsTools.before(backup);
 backupButton.addEventListener('click',async()=>{backupButton.disabled=importButton.disabled=true;backupStatus.textContent='Nutzerdaten werden geladen …';try{const all=[];for(let pageNumber=0;pageNumber<=100000;pageNumber++){const data=await api('users',undefined,'page='+pageNumber);if(!Array.isArray(data.users)||typeof data.more!=='boolean')throw Error('Die Nutzerliste konnte nicht vollständig gelesen werden.');all.push(...data.users);if(!data.more)break;if(pageNumber===100000)throw Error('Der Export hat die maximale Seitenzahl überschritten.');}const csvCell=value=>{const raw=String(value??'');const safe=/^[\\t\\r ]*[-=+@]/.test(raw)?"'"+raw:raw;return '"'+safe.replace(/"/g,'""')+'"';};const rows=[['Vorname','Nachname','E-Mail'],...all.map(row=>[row.first_name,row.last_name,row.email])];const csv=rows.map(row=>row.map(csvCell).join(';')).join('\\r\\n');const blob=new Blob([String.fromCharCode(0xfeff),csv],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a'),now=new Date(),date=[now.getFullYear(),String(now.getMonth()+1).padStart(2,'0'),String(now.getDate()).padStart(2,'0')].join('-');link.href=url;link.download='nutzer-sicherung-'+date+'.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);backupStatus.textContent=all.length+' Nutzerkonten wurden als CSV gesichert.';}catch(error){backupStatus.textContent='Nutzerdaten konnten nicht gesichert werden: '+error.message;}finally{backupButton.disabled=importButton.disabled=false;}});
 function parseUserCsv(text){
  const source=text.replace(/^\\uFEFF/,'');const records=[];let row=[],cell='',quoted=false;
  for(let i=0;i<source.length;i++){const ch=source[i];if(quoted){if(ch==='"'&&source[i+1]==='"'){cell+='"';i++;}else if(ch==='"')quoted=false;else cell+=ch;}else if(ch==='"'){if(cell)throw Error('Die CSV-Datei enthält ein ungültiges Anführungszeichen.');quoted=true;}else if(ch===';'){row.push(cell);cell='';}else if(ch==='\\r'||ch==='\\n'){row.push(cell);if(row.some(value=>value.trim()))records.push(row);row=[];cell='';if(ch==='\\r'&&source[i+1]==='\\n')i++;}else cell+=ch;}
  if(quoted)throw Error('Die CSV-Datei enthält ein nicht geschlossenes Anführungszeichen.');row.push(cell);if(row.some(value=>value.trim()))records.push(row);
  if(!records.length||records[0].length!==3||records[0][0].trim()!=='Vorname'||records[0][1].trim()!=='Nachname'||records[0][2].trim()!=='E-Mail')throw Error('Bitte die unveränderte CSV-Datei aus „Nutzerdaten sichern“ auswählen.');
  const data=records.slice(1);if(!data.length)throw Error('Die CSV-Datei enthält keine Nutzerdaten.');if(data.length>2000)throw Error('Pro Import können höchstens 2.000 Nutzerkonten verarbeitet werden.');
  const emails=new Set();return data.map((values,index)=>{if(values.length!==3)throw Error('Zeile '+(index+2)+' enthält nicht genau drei Spalten.');const [first_name,last_name]=values.slice(0,2).map(value=>value.trim()),email=values[2].trim().toLowerCase();if(!first_name||!last_name||!email||first_name.length>100||last_name.length>100||email.length>254||!/^\\S+@[^\\s@]+\\.[^\\s@]+$/.test(email))throw Error('Bitte Vorname, Nachname und eine gültige E-Mail-Adresse in Zeile '+(index+2)+' prüfen.');if(emails.has(email))throw Error('Die E-Mail-Adresse '+email+' kommt mehrfach in der CSV-Datei vor.');emails.add(email);return{first_name,last_name,email};});
 }
 importButton.addEventListener('click',()=>importFile.click());
 importFile.addEventListener('change',async()=>{const file=importFile.files?.[0];if(!file)return;try{if(file.size>2000000)throw Error('Die CSV-Datei darf höchstens 2 MB groß sein.');const users=parseUserCsv(await file.text());if(!confirm(users.length+' Nutzerkonten importieren? Fehlende Konten werden als unbestätigte Benutzer angelegt. Bei vorhandenen E-Mail-Adressen werden nur Vor- und Nachname aktualisiert.'))return;backupButton.disabled=importButton.disabled=true;backupStatus.textContent='Nutzerdaten werden importiert …';const result=await api('users-import',{users});if(!Number.isInteger(result.created)||!Number.isInteger(result.updated))throw Error('Die Schnittstelle hat kein gültiges Importergebnis geliefert.');backupStatus.textContent='Import abgeschlossen: '+result.created+' neu angelegt, '+result.updated+' aktualisiert. Neue Konten müssen ihre E-Mail-Adresse bestätigen.';}catch(error){backupStatus.textContent='Nutzerdaten konnten nicht importiert werden: '+error.message;}finally{backupButton.disabled=importButton.disabled=false;importFile.value='';}});
 const card=element('div',null,{class:'form-card nic-user-admin-card'});card.append(element('h3','Benutzerverwaltung'));
 const who=element('p','Angemeldet als '+user.first_name+' '+user.last_name+' ('+user.email+')');card.append(who);
 const out=element('button','Abmelden',{type:'button',class:'nic-user-admin-action'});out.addEventListener('click',async()=>{try{await logout();}catch(e){message(e.message);}});
 const search=element('input',null,{type:'search',placeholder:'Name oder E-Mail filtern','aria-label':'Benutzer filtern'}),list=element('div'),status=element('p',null,{role:'status'}),more=element('button','Weitere Benutzer laden',{type:'button',class:'nic-user-admin-action'});const userTools=element('div',null,{class:'nic-user-admin-tools'});userTools.append(out);card.append(userTools);card.append(search,status,list,more);panel.append(card);
 let page=0,rows=[];
 function render(){list.replaceChildren();const q=search.value.trim().toLowerCase();for(const row of rows){if(![row.first_name,row.last_name,row.email].join(' ').toLowerCase().includes(q))continue;const item=element('div',null,{class:'nic-user-row'});item.append(element('strong',row.first_name+' '+row.last_name),element('p',row.email+' · '+(row.role==='admin'?'Administrator':'Benutzer')+' · '+(row.status==='blocked'?'Gesperrt':row.verified_at?'Aktiv':'E-Mail noch nicht bestätigt')));const actions=element('div',null,{class:'nic-user-actions'});
 for(const [action,title]of [[row.status==='blocked'?'unblock':'block',row.status==='blocked'?'Freigeben':'Sperren'],['delete','Löschen']]){const button=element('button',title,{type:'button',class:'nic-user-admin-action'+(action==='delete'?' nic-user-admin-action--danger':'')});button.disabled=row.id===user.id;button.addEventListener('click',async()=>{if(!confirm(row.email+' wirklich '+title.toLowerCase()+'?'+(action==='delete'?' Das Konto und seine Sitzungen werden endgültig gelöscht.':'')))return;button.disabled=true;try{await api('user-action',{id:row.id,action});page=0;rows=[];await load();}catch(error){status.textContent=error.message;button.disabled=false;}});actions.append(button);}item.append(actions);list.append(item);}}
 async function load(){more.disabled=true;try{const data=await api('users',undefined,'page='+page);rows.push(...data.users);page++;more.hidden=!data.more;status.textContent=rows.length+' Benutzer geladen.';render();}catch(error){status.textContent=error.message;}finally{more.disabled=false;}}
 search.addEventListener('input',render);more.addEventListener('click',load);load();
}
// The page's initial /me response already establishes the active account.
// Rechecking on each click can turn a valid in-memory login into a false login prompt.
document.addEventListener('click',event=>{
 const target=event.target.closest?.('#nicAccountLink,.nic-account-link');if(!target||!config?.enabled)return;
 if(event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
 event.preventDefault();event.stopImmediatePropagation();
 profile().catch(error=>alert(error.message));
},true);
window.NICAccess={init,authorize,requireAdmin,loadSettings,refresh,saveSettings,mountUsers,logout,login,saveOwn:async values=>{const r=await api('profile',values);user=r.user;return user;},deleteOwn:async()=>{const result=await api('delete-own-account',{confirm:true});user=null;csrf=null;window.dispatchEvent(new Event('nic-auth-changed'));return result;},resendEmailChange:()=>api('email-change-resend',{}),emailChangeStatus:()=>api('email-change-status'),startEmailChange:email=>api('email-change-start',{email}),approveEmailChange:token=>api('email-change-approve',{token}),finishEmailChange:async code=>{const result=await api('email-change-finish',{code});if(result.loggedOut!==true||typeof result.email!=='string')throw Error('Bitte die aktuelle app.php auf STRATO hochladen und die Seite neu laden.');user=null;csrf=null;window.dispatchEvent(new Event('nic-auth-changed'));return result;},get enabled(){return config?.enabled===true;},get user(){return user;}};
const css=element('style');css.textContent=`
.nic-auth-dialog{box-sizing:border-box;border:1px solid var(--line,#e2e8f0);border-radius:18px;padding:24px;max-width:580px;width:calc(100% - 32px);color:var(--ink,#172033);background:var(--bg,#f5f7fb);font:inherit;line-height:1.5;box-shadow:0 20px 80px #0f172a45;color-scheme:light}
.nic-auth-dialog [hidden]{display:none!important}
.nic-auth-dialog::backdrop{background:#0f172a88}
.nic-auth-dialog h2{color:inherit;margin:0 0 16px;line-height:1.25}
.nic-auth-dialog p{color:inherit;margin:0 0 16px;overflow-wrap:anywhere}
.nic-auth-dialog label{display:block;color:inherit;margin:14px 0}
.nic-auth-dialog input:not([type=checkbox]){display:block;width:100%;box-sizing:border-box;font:inherit;padding:11px 12px;border:1px solid var(--line,#cbd5e1);border-radius:10px;background:var(--bg,#f5f7fb);color:var(--ink,#172033)}
.nic-auth-dialog .nic-register-choice{display:flex;align-items:center;gap:10px;cursor:pointer}.nic-auth-dialog .nic-register-choice input[type=checkbox]{appearance:auto;-webkit-appearance:checkbox;flex:0 0 10px;width:10px;height:10px;min-width:10px;min-height:10px;padding:0;margin:0}.nic-auth-dialog .nic-register-choice span{flex:1;text-align:left}
.nic-auth-dialog input[type=checkbox]{accent-color:var(--nic-button-bg,#0f172a)}
.nic-auth-dialog input:not([type=checkbox]):focus,.nic-auth-dialog input:not([type=checkbox]):focus-visible{outline:none;box-shadow:none;border-color:#4b5563}
.nic-auth-dialog .nic-auth-actions{display:grid;grid-auto-columns:minmax(0,1fr);grid-auto-flow:column;gap:12px;margin-top:24px;align-items:stretch}
.nic-auth-dialog button,.nic-auth-dialog a.nic-auth-button,.nic-auth-dialog a.nic-auth-button:visited{appearance:none;-webkit-appearance:none;display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;min-width:0;min-height:46px;font:inherit;font-weight:700;line-height:1.35;text-align:center;text-decoration:none;text-shadow:none;padding:12px 14px;margin:0;border:1px solid var(--nic-button-bg,#0f172a);border-radius:11px;background:var(--nic-button-bg,#0f172a);color:var(--nic-button-text,#fff);cursor:pointer;white-space:normal;overflow-wrap:anywhere}
.nic-auth-dialog a.nic-admin-action{border:0}
.nic-auth-dialog :is(button,a.nic-auth-button):hover{filter:brightness(.92)}
.nic-auth-dialog :is(button,a.nic-auth-button):focus-visible{outline:3px solid var(--nic-button-bg,#0f172a);outline-offset:4px}
.nic-auth-dialog button:disabled{opacity:.65;cursor:wait}
.nic-user-row{padding:14px 0;border-bottom:1px solid #e2e8f0;overflow-wrap:anywhere}.nic-user-admin-tools{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}.nic-user-admin-card :is(.nic-user-admin-action){appearance:none;-webkit-appearance:none;display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;min-height:46px;padding:11px 18px;border:1px solid var(--nic-green-bg,#075c55);border-radius:var(--nic-control-radius,10px);background:var(--nic-green-bg,#075c55);color:var(--nic-green-text,#fff);font:700 var(--nic-body-font-size,16px)/1.35 var(--nic-body-font-family,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif);text-align:center;text-shadow:none;cursor:pointer;white-space:normal;overflow-wrap:anywhere}.nic-user-admin-card .nic-user-admin-action--danger{border-color:var(--nic-red-bg,#b42318);background:var(--nic-red-bg,#b42318);color:var(--nic-red-text,#fff)}.nic-user-admin-card .nic-user-admin-action:hover{filter:brightness(.92)}.nic-user-admin-card .nic-user-admin-action:focus-visible{outline:3px solid var(--nic-green-bg,#075c55);outline-offset:3px}.nic-user-admin-card .nic-user-admin-action--danger:focus-visible{outline-color:var(--nic-red-bg,#b42318)}.nic-user-admin-card .nic-user-admin-action:disabled{opacity:.55;cursor:not-allowed}.nic-user-actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}.nic-user-admin-card>p:first-of-type{overflow-wrap:anywhere;margin:0 0 12px}
@media(max-width:600px){.nic-user-admin-card>.nic-user-admin-action{width:100%}.nic-user-admin-tools{display:grid;grid-template-columns:1fr}.nic-user-admin-tools>.nic-user-admin-action{width:100%}.nic-user-actions>*{flex:1 1 132px}}@media(max-width:480px){.nic-auth-dialog{padding:20px}.nic-auth-dialog .nic-auth-actions{grid-auto-flow:row;grid-template-columns:1fr}}
`;document.head.append(css);
// Logout confirmation is a nonmodal notice on the calculator page.
if(typeof location!=='undefined'){
 const currentURL=new URL(location.href);
 if(currentURL.searchParams.get('logged-out')==='1'||currentURL.searchParams.get('email-changed')==='1'||currentURL.searchParams.get('account-deleted')==='1'){
  const accountDeleted=currentURL.searchParams.get('account-deleted')==='1';currentURL.searchParams.delete('account-deleted');const emailChanged=currentURL.searchParams.get('email-changed')==='1';currentURL.searchParams.delete('email-changed');currentURL.searchParams.delete('logged-out');history.replaceState(null,'',currentURL.href);
  const notice=element('div',accountDeleted?'Nutzerdaten erfolgreich gelöscht!':emailChanged?'Deine E-Mail-Adresse wurde geändert. Bitte melde dich mit der neuen Adresse an.':'Du wurdest erfolgreich abgemeldet!',{role:'status',class:'nic-logout-notice'});
  notice.style.cssText='position:fixed;top:20px;left:50%;transform:translateX(-50%);z-index:10000;max-width:calc(100% - 40px);box-sizing:border-box;padding:16px 22px;border:1px solid #cbd5e1;border-radius:12px;background:var(--bg,#fff);color:var(--ink,#172033);box-shadow:0 6px 24px #0f172a20;font:inherit;text-align:center';
  document.body.append(notice);setTimeout(()=>notice.remove(),6000);
 }
}
// Public-page gate. This controls application use, not distribution of its public source.
let gate=null,checking=false;
async function checkCalculator(){
 if(checking||!config?.enabled||document.body.classList.contains('nic-admin'))return;
 const isCalculator=!!document.querySelector('#loan,#dealTypeBudget,.deal-type-row');if(!isCalculator)return;
 checking=true;
 try{
 const data=await api('settings');
 if(data.settings.access?.calculators!==false){if(gate){gate.close();gate.remove();gate=null;}return;}
 if(user){try{await api('authorize',{action:'calculators'});if(gate){gate.close();gate.remove();gate=null;}return;}catch(error){if(error.status!==401)throw error;}}
 if(gate)return;
 gate=element('dialog',null,{'aria-label':'Anmeldung erforderlich'});gate.className='nic-auth-dialog';gate.append(element('h2','Anmeldung erforderlich'),element('p','Bitte melde dich an, um die Kalkulatoren zu nutzen.'));const button=element('button','Anmelden oder registrieren'),notice=element('p',null,{role:'status'});gate.append(button,notice);gate.addEventListener('cancel',e=>e.preventDefault());document.body.append(gate);gate.showModal();
 button.addEventListener('click',async()=>{gate.close();try{if(await authorize('calculators')){gate.remove();gate=null;return;}}catch(error){notice.textContent=error.message;}gate.showModal();});
 }finally{checking=false;}
}
init().then(enabled=>{if(!enabled)return;checkCalculator().catch(e=>console.warn('Zugangsprüfung:',e.message));if(!document.body.classList.contains('nic-admin'))setInterval(async()=>{if(document.visibilityState==='hidden')return;try{const S=window.NICSettings;if(S){const s=await S.init();S.apply(s);window.dispatchEvent(new Event('nic-settings-updated'));}await checkCalculator();}catch(error){console.warn('Zentrale Einstellungen:',error.message);}},30000);}).catch(error=>console.warn('Nutzerverwaltung:',error.message));
})();
