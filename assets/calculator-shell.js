/* Shared footer behavior for every calculator; calculation state stays untouched. */
(()=>{
'use strict';
const S=window.NICSettings;
const footer=document.querySelector('.app>.footer-note')||document.querySelector('.app>.nic-shared-footer')||document.querySelector('.nic-shared-footer')||document.querySelector('.footer-note');
if(!S||!footer)return;
const mobileQuery=window.matchMedia?.('(max-width:700px)')||null;
function syncDisclosureState(){
 const mobile=!!mobileQuery?.matches;
 footer.querySelectorAll('.nic-footer-section').forEach(section=>{if(!section.hidden)section.open=!mobile;});
}
if(mobileQuery?.addEventListener)mobileQuery.addEventListener('change',syncDisclosureState);
else if(mobileQuery?.addListener)mobileQuery.addListener(syncDisclosureState);
function refresh(s=S.current){
 if(!s)return;
 const socialSection=footer.querySelector('#nicFooterSocial');
 const nav=footer.querySelector('#nicSocialLinks');
 if(nav){
  nav.replaceChildren();
  for(const [key,label] of S.portals){const url=s.social?.[key];if(!url)continue;const a=document.createElement('a');a.href=url;a.textContent=label;a.target='_blank';a.rel='noopener noreferrer';nav.append(a);}
 }
 if(socialSection)socialSection.hidden=!nav?.childElementCount;
 const aboutSection=footer.querySelector('#nicFooterAboutSection');
 const about=footer.querySelector('#nicFooterAbout');
 const aboutHtml=s.content?.about?.description||'';
 if(about&&aboutHtml.trim())about.replaceChildren(S.legalFragment(aboutHtml,s));
 if(aboutSection)aboutSection.hidden=!about||!aboutHtml.trim()||!about.childNodes.length;
 const contactSection=footer.querySelector('#nicFooterContactSection');
 const email=footer.querySelector('#nicFooterEmail');
 const address=String(s.company?.email||'').trim();
 if(email){email.textContent=address;email.href=address?'mailto:'+address:'';}
 if(contactSection)contactSection.hidden=!address;
 syncDisclosureState();
 window.NICLegal?.refresh();
}
window.NICShell={refresh};
window.addEventListener('nic-settings-updated',()=>refresh());
window.addEventListener('storage',e=>{if(e.key===S.KEY)S.init().then(refresh).catch(console.warn);});
S.init().then(refresh).catch(()=>refresh());
})();
