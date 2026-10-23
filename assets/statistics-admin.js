(function(){
'use strict';
const C=window.NICStatsCore,$=id=>document.getElementById(id),STORAGE='nic_statistics_v1';
if(!C||!$('statsSource'))return;
const labels={budget:'Budget',own:'Eigennutzung',rent:'Vermietung',flip:'Fix & Flip'};
const metrics=[['page_view','Seitenaufrufe'],['calculator_use','Rechner-Nutzungen'],['calculate','Kalkulationen'],['pdf_download','PDF-Downloads'],['pdf_share','PDF geteilt']];
let token='',expires=0,requestSerial=0,identityPromise=null,authorizedClient='';
function counter(n){return n==null?'—':new Intl.NumberFormat('de-DE').format(n);}
function authStatus(text){$('statsAuthStatus').textContent=text;}
function source(){return $('statsSource').value;}
function drawDimension(id,values,empty='Noch keine erfassten Aufrufe.'){
 const root=$(id);root.replaceChildren();const rows=Object.entries(values||{}).sort((a,b)=>b[1]-a[1]).slice(0,10);
 if(!rows.length){const p=document.createElement('p');p.className='stats-empty';p.textContent=empty;root.append(p);return;}
 for(const [name,count] of rows){const row=document.createElement('div');row.className='stats-dimension';const span=document.createElement('span');span.textContent=name;const value=document.createElement('strong');value.textContent=counter(count);row.append(span,value);root.append(row);}
}
function render(data,notice,countries=null){
 $('statsNotice').textContent=notice;$('statsMetrics').replaceChildren();
 for(const [key,label] of metrics){const card=document.createElement('div');card.className='stats-metric';const name=document.createElement('span');name.textContent=label;const value=document.createElement('strong');value.textContent=counter(data?.events[key]);card.append(name,value);$('statsMetrics').append(card);}
 $('statsCalculatorRows').replaceChildren();
 for(const key of C.CALCULATORS){const row=document.createElement('tr'),name=document.createElement('th');name.scope='row';name.textContent=labels[key];row.append(name);for(const metric of ['calculator_use','calculate','pdf_download','pdf_share']){const cell=document.createElement('td');cell.textContent=counter(data?.calculators[key][metric]);row.append(cell);}$('statsCalculatorRows').append(row);}
 drawDimension('statsDevices',data?.devices,data?'Noch keine erfassten Aufrufe.':'Keine verbundenen Daten.');drawDimension('statsSystems',data?.systems,data?'Noch keine erfassten Aufrufe.':'Keine verbundenen Daten.');drawDimension('statsSources',data?.sources,data?'Noch keine erfassten Aufrufe.':'Keine verbundenen Daten.');drawDimension('statsCountries',countries,source()==='local'?'Länder sind in der lokalen Vorschau nicht ermittelbar. Verbinde Google Analytics für eine Länder-Auswertung.':'Noch keine Länder-Daten verfügbar.');
}
function local(){let data=C.empty();try{const s=JSON.parse(localStorage.getItem(STORAGE));if(s?.version===1&&s.days)data=s;}catch(_){}const since=data.startedAt?' Erfassung seit '+new Date(data.startedAt).toLocaleDateString('de-DE')+'.':'';render(C.summary(data,Number($('statsDays').value)),'Lokale Vorschau · nur dieser Browser nach Statistik-Zustimmung. Keine Gesamtbesucherzahlen.'+since);}
function credentials(){const property=$('statsPropertyId').value.trim(),client=$('statsClientId').value.trim();if(!/^[0-9]{1,20}$/.test(property))throw new Error('Bitte die numerische GA4-Property-ID hinterlegen.');if(!/^[0-9]+-[a-zA-Z0-9_-]+\.apps\.googleusercontent\.com$/.test(client))throw new Error('Bitte eine gültige Google-OAuth-Client-ID für eine Webanwendung hinterlegen.');return {property,client};}
function body(dimensions,onlyViews=false){return {dateRanges:[{startDate:(Number($('statsDays').value)-1)+'daysAgo',endDate:'today'}],dimensions:dimensions.map(name=>({name})),metrics:[{name:'eventCount'}],dimensionFilter:{filter:{fieldName:'eventName',inListFilter:{values:onlyViews?[C.EVENTS.page_view]:Object.values(C.EVENTS)}}},limit:'10000'};}
async function report(property,dimensions,onlyViews=false){
 const response=await fetch('https://analyticsdata.googleapis.com/v1beta/properties/'+property+':runReport',{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(body(dimensions,onlyViews))});
 const result=await response.json();if(!response.ok){if(response.status===401){token='';expires=0;}throw new Error(response.status===401?'Google-Anmeldung abgelaufen. Bitte erneut verbinden.':response.status===403?'Google hat den Zugriff abgelehnt. Prüfe Property-Leserechte und die aktivierte Analytics Data API.':'Google-Bericht nicht verfügbar: '+(result.error?.message||response.status));}if((result.rowCount||0)>10000)throw new Error('Der Bericht enthält mehr als 10.000 Zeilen. Bitte einen kürzeren Zeitraum wählen.');return result;
}
function rows(result){return (result.rows||[]).map(row=>({dimensions:(row.dimensionValues||[]).map(v=>v.value||'Unbekannt'),count:Math.max(0,Number(row.metricValues?.[0]?.value)||0)}));}
async function googleData(serial){
 const {property,client}=credentials();if(!token||Date.now()>=expires||client!==authorizedClient){render(null,'Gesamte Website · noch nicht mit Google Analytics verbunden. Hinterlege Property-ID und OAuth-Client-ID und wähle „Mit Google verbinden“.');return;}
 render(null,'Google-Berichte werden geladen …');
 const results=await Promise.allSettled([report(property,['eventName']),report(property,['pagePath','eventName']),...['deviceCategory','operatingSystem','country','sessionSourceMedium'].map(d=>report(property,[d],true))]);
 if(serial!==requestSerial||source()!=='google')return;
 const failed=results.find(r=>r.status==='rejected');if(failed)throw failed.reason;
 const [overview,calculators,devices,systems,countries,sources]=results.map(r=>r.value),data=C.blankTotals();
 const reverse=Object.fromEntries(Object.entries(C.EVENTS).map(([k,v])=>[v,k]));
 rows(overview).forEach(r=>{const event=reverse[r.dimensions[0]];if(event)data.events[event]+=r.count;});
 const paths={'budget':'budget','eigennutzung':'own','vermietung':'rent','fix-flip':'flip'};
 rows(calculators).forEach(r=>{const key=paths[r.dimensions[0].replace(/^\/+|\/+$/g,'')],event=reverse[r.dimensions[1]];if(key&&event)data.calculators[key][event]+=r.count;});
 for(const [key,result] of [['devices',devices],['systems',systems],['sources',sources]])rows(result).forEach(r=>Object.defineProperty(data[key],r.dimensions[0],{value:r.count,enumerable:true,configurable:true}));
 const countryValues={};rows(countries).forEach(r=>Object.defineProperty(countryValues,r.dimensions[0],{value:r.count,enumerable:true,configurable:true}));
 render(data,'Gesamte Website · Google Analytics · Property '+property+' · nur erfasste Nutzung mit Statistik-Zustimmung. Google-Daten können zeitversetzt erscheinen.',countryValues);
 const incomplete=results.some(r=>r.value.metadata?.subjectToThresholding||r.value.metadata?.dataLossFromOtherRow);authStatus('Verbunden · Berichte zuletzt geladen um '+new Date().toLocaleTimeString('de-DE')+(incomplete?' · Google meldet Schwellenwerte oder zusammengefasste Daten.':''));
}
async function refresh(){const serial=++requestSerial;if(source()==='local'){local();return;}try{await googleData(serial);}catch(err){if(serial===requestSerial){render(null,err.message);authStatus(err.message);}}}
function loadIdentity(){if(window.google?.accounts?.oauth2)return Promise.resolve();if(identityPromise)return identityPromise;identityPromise=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='https://accounts.google.com/gsi/client';script.async=true;script.onload=()=>resolve();script.onerror=()=>{identityPromise=null;script.remove();reject(new Error('Google-Anmeldung konnte nicht geladen werden. Prüfe Verbindung und Inhaltsblocker.'));};document.head.append(script);});return identityPromise;}
$('statsConnect').addEventListener('click',async()=>{
 try{const {client}=credentials();if(!window.google?.accounts?.oauth2){authStatus('Google-Anmeldung wird vorbereitet …');await loadIdentity();authStatus('Google-Anmeldung ist bereit. Klicke erneut auf „Mit Google verbinden“, um die Kontowahl zu öffnen.');return;}
 const tokenClient=window.google.accounts.oauth2.initTokenClient({client_id:client,scope:'https://www.googleapis.com/auth/analytics.readonly',include_granted_scopes:false,callback:response=>{
 if(response.error||!response.access_token){authStatus('Google-Verbindung wurde nicht hergestellt: '+(response.error||'Kein Zugriffstoken erhalten.'));return;}
 token=response.access_token;expires=Date.now()+Math.max(0,(Number(response.expires_in)||3600)-60)*1000;authorizedClient=client;$('statsDisconnect').hidden=false;$('statsSource').value='google';authStatus('Verbunden · ausschließlich lesender Zugriff.');refresh();},error_callback:()=>authStatus('Google-Anmeldung abgebrochen oder Popup blockiert. Du kannst es erneut versuchen.')});tokenClient.requestAccessToken({prompt:'select_account'});
 }catch(err){authStatus(err.message);$('statsConnection').open=true;}
});
$('statsDisconnect').addEventListener('click',()=>{token='';expires=0;authorizedClient='';$('statsDisconnect').hidden=true;authStatus('Verbindung auf dieser Seite getrennt. Es werden keine weiteren Berichte abgefragt.');refresh();});
['statsSource','statsDays'].forEach(id=>$(id).addEventListener('change',refresh));$('statsRefresh').addEventListener('click',refresh);
window.addEventListener('storage',e=>{if(e.key===STORAGE&&source()==='local')refresh();});window.addEventListener('nic:statistics-updated',()=>{if(source()==='local')refresh();});
refresh();
})();
