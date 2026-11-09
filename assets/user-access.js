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
 const panel=document.getElementById('panel-users');if(!panel||!config?.enabled||user?.role!=='admin')return;
 const old=panel.querySelector('[data-access-pending]');if(old)old.textContent='Zentrale Nutzerverwaltung aktiv. Gespeicherte Regeln gelten für alle Besucher.';
 const card=element('div',null,{class:'form-card'});card.append(element('h3','Benutzerverwaltung'));
 const who=element('p','Angemeldet als '+user.first_name+' '+user.last_name+' ('+user.email+')');card.append(who);
 const out=element('button','Abmelden',{type:'button'});out.addEventListener('click',async()=>{try{await logout();}catch(e){message(e.message);}});card.append(out);
 const search=element('input',null,{type:'search',placeholder:'Name oder E-Mail filtern','aria-label':'Benutzer filtern'}),list=element('div'),status=element('p',null,{role:'status'}),more=element('button','Weitere Benutzer laden',{type:'button'});card.append(search,status,list,more);panel.append(card);
 let page=0,rows=[];
 function render(){list.replaceChildren();const q=search.value.trim().toLowerCase();for(const row of rows){if(![row.first_name,row.last_name,row.email].join(' ').toLowerCase().includes(q))continue;const item=element('div',null,{class:'nic-user-row'});item.append(element('strong',row.first_name+' '+row.last_name),element('p',row.email+' · '+(row.role==='admin'?'Administrator':'Benutzer')+' · '+(row.status==='blocked'?'Gesperrt':row.verified_at?'Aktiv':'E-Mail noch nicht bestätigt')));
 for(const [action,title]of [[row.status==='blocked'?'unblock':'block',row.status==='blocked'?'Freigeben':'Sperren'],['delete','Löschen']]){const button=element('button',title,{type:'button'});button.disabled=row.id===user.id;button.addEventListener('click',async()=>{if(!confirm(row.email+' wirklich '+title.toLowerCase()+'?'+(action==='delete'?' Das Konto und seine Sitzungen werden endgültig gelöscht.':'')))return;button.disabled=true;try{await api('user-action',{id:row.id,action});page=0;rows=[];await load();}catch(error){status.textContent=error.message;button.disabled=false;}});item.append(button);}list.append(item);}}
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
.nic-user-row{padding:14px 0;border-bottom:1px solid #e2e8f0;overflow-wrap:anywhere}
@media(max-width:480px){.nic-auth-dialog{padding:20px}.nic-auth-dialog .nic-auth-actions{grid-auto-flow:row;grid-template-columns:1fr}}
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
