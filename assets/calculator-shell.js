/* Shared footer behavior for every calculator; calculation state stays untouched. */
(()=>{
'use strict';
const S=window.NICSettings,footer=document.querySelector('.footer-note');
if(!S||!footer)return;
function refresh(s=S.current){
 if(!s)return;
 let nav=footer.querySelector('#nicSocialLinks');if(!nav){nav=document.createElement('nav');nav.id='nicSocialLinks';nav.className='nic-social-links';nav.setAttribute('aria-label','Social Media');footer.append(nav);}
 nav.replaceChildren();for(const [key,label] of S.portals){const url=s.social[key];if(!url)continue;const a=document.createElement('a');a.href=url;a.textContent=label;a.target='_blank';a.rel='noopener noreferrer';nav.append(a);}nav.hidden=!nav.childElementCount;
 window.NICLegal?.refresh();
}
window.NICShell={refresh};
window.addEventListener('nic-settings-updated',()=>refresh());
window.addEventListener('storage',e=>{if(e.key===S.KEY)S.init().then(refresh).catch(console.warn);});
S.init().then(refresh).catch(()=>refresh());
})();
