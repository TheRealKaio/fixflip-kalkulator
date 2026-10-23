(function(){
'use strict';
const S=window.NICSettings;if(!S)return;
const page=document.documentElement.dataset.nicPage||'website';
let activePage=page;
function social(s){let nav=document.getElementById('nicSocialLinks');const footer=document.querySelector('.footer-note')||document.querySelector('.public-footer');if(!footer)return;if(!nav){nav=document.createElement('nav');nav.id='nicSocialLinks';nav.setAttribute('aria-label','Social Media');nav.className='nic-social-links';footer.append(nav);}nav.replaceChildren();S.portals.forEach(([key,label])=>{const url=s.social[key];if(!url)return;const a=document.createElement('a');a.href=url;a.textContent=label;a.target='_blank';a.rel='noopener noreferrer';nav.append(a);});nav.hidden=!nav.childElementCount;}
function company(s){const root=document.getElementById('companyContent');if(!root)return;root.replaceChildren();const parts=S.imprint(s);if(!parts.length){const p=document.createElement('p');p.textContent='Die Anbieterangaben wurden noch nicht hinterlegt.';root.append(p);return;}for(const {label,value} of parts){const h=document.createElement('h2');h.textContent=label;const p=document.createElement('p');p.textContent=value;root.append(h,p);}}
function apply(){if(!S.current)return;S.apply(S.current,activePage);social(S.current);company(S.current);}
function modePage(){if(document.getElementById('dealTypeRent')?.getAttribute('aria-pressed')==='true')return 'rent';return document.querySelector('input[name="dealType"]:checked')?.value||'budget';}
function updateMode(){activePage=modePage();const path=S.pages.find(p=>p[0]===activePage)?.[2];if(path!==undefined)history.replaceState(null,'',new URL(path,S.ROOT).pathname+location.search);apply();window.NICAnalytics?.changeSection(activePage);}
function activate(key){if(key==='rent')document.getElementById('dealTypeRent')?.click();else{const id={budget:'dealTypeBudget',own:'dealTypeOwn',flip:'dealTypeFlip'}[key],el=document.getElementById(id);if(el){el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));}}}
document.querySelectorAll('[data-legal-placeholder="impressum"]').forEach(a=>a.href=new URL('impressum/',S.ROOT).href);
document.querySelectorAll('input[name="dealType"]').forEach(el=>el.addEventListener('change',()=>{if(el.checked)updateMode();}));
document.getElementById('dealTypeRent')?.addEventListener('click',updateMode);
window.addEventListener('storage',e=>{if(e.key===S.KEY)S.init().then(apply).catch(()=>{});});
window.addEventListener('pageshow',()=>{if(S.current)S.init().then(apply).catch(()=>{});});
S.init().then(()=>{if(['budget','own','rent','flip'].includes(page))activate(page);activePage=page;apply();window.NICAnalytics?.start({section:page,calculator:document.getElementById('heroTitle')?modePage():null});}).catch(err=>console.warn('Einstellungen:',err.message));
})();
