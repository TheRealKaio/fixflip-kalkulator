/* Shared footer behavior for every calculator; calculation state stays untouched. */
(()=>{
'use strict';
const S=window.NICSettings,footer=document.querySelector('.footer-note');
if(!S||!footer)return;
function align(){
 const version=footer.querySelector('.footer-version'),cookie=footer.querySelector('#nicConsentSettings');
 if(!version||!cookie||version.closest('.nic-footer-cookie-pair'))return;
 const pair=document.createElement('span');pair.className='nic-footer-cookie-pair';cookie.before(pair);pair.append(version,cookie);
}
function refresh(s=S.current){
 if(!s)return;
 let nav=footer.querySelector('#nicSocialLinks');if(!nav){nav=document.createElement('nav');nav.id='nicSocialLinks';nav.className='nic-social-links';nav.setAttribute('aria-label','Social Media');footer.append(nav);}
 nav.replaceChildren();for(const [key,label] of S.portals){const url=s.social[key];if(!url)continue;const a=document.createElement('a');a.href=url;a.textContent=label;a.target='_blank';a.rel='noopener noreferrer';nav.append(a);}nav.hidden=!nav.childElementCount;
 align();window.NICLegal?.refresh();
}
new MutationObserver(align).observe(footer,{childList:true,subtree:true});
window.NICShell={refresh};
window.addEventListener('nic-settings-updated',()=>refresh());
window.addEventListener('storage',e=>{if(e.key===S.KEY)S.init().then(refresh).catch(console.warn);});
S.init().then(refresh).catch(()=>refresh());align();
})();
