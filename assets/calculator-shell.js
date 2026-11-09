/* Shared footer behavior for every calculator; calculation state stays untouched. */
(()=>{
'use strict';
const S=window.NICSettings;
const footer=document.querySelector('.app>.footer-note')||document.querySelector('.app>.nic-shared-footer')||document.querySelector('.nic-shared-footer')||document.querySelector('.footer-note');
if(!S||!footer)return;
const mobileQuery=window.matchMedia?.('(max-width:700px)')||null;
const socialIconPaths={
 instagram:'<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="18" cy="6" r="1.2"/>',
 facebook:'<path d="M13.6 21v-8h2.7l.4-3.1h-3.1v-2c0-.9.3-1.5 1.6-1.5H17V3.6c-.7-.1-1.5-.2-2.5-.2-2.5 0-4.2 1.5-4.2 4.3v2.2H7.5V13h2.8v8z"/>',
 youtube:'<rect x="2.5" y="5" width="19" height="14" rx="4" fill="none" stroke="currentColor" stroke-width="2"/><path d="m10 8.5 6 3.5-6 3.5z"/>',
 linkedin:'<path d="M5.2 8.3a1.7 1.7 0 1 0 0-3.4 1.7 1.7 0 0 0 0 3.4ZM3.8 10h2.9v10H3.8zM9 10h2.8v1.4h.1c.4-.8 1.4-1.7 3-1.7 3.1 0 3.7 2 3.7 4.6V20h-2.9v-5.1c0-1.2 0-2.7-1.7-2.7s-2 1.3-2 2.6V20H9z"/>',
 tiktok:'<path d="M16.3 3h-3.2v12.1a2.6 2.6 0 1 1-2.2-2.6v-3.3a5.8 5.8 0 1 0 5.4 5.8V9a8.1 8.1 0 0 0 4.1 1.1V6.9A4.8 4.8 0 0 1 16.3 3Z"/>',
 pinterest:'<text x="5" y="21" font-family="Georgia,serif" font-size="23" font-weight="700">P</text>',
 x:'<path d="M18.9 2H22l-6.8 7.8L23 22h-6.1l-4.8-7-6.1 7H2.8l7.3-8.4L2 2h6.3l4.3 6.4Zm-1.1 18h1.7L7.3 3.9H5.5Z"/>',
 threads:'<path d="M12 2.2c-5.5 0-9 3.8-9 9.8s3.5 9.8 9 9.8c4.8 0 7.8-2.9 7.8-7.3 0-3.1-1.8-5.2-4.7-5.7-.5-2.1-1.8-3.2-3.7-3.2-2.4 0-4 1.8-4 4.1h2.5c0-1 .5-1.6 1.4-1.6.7 0 1.2.4 1.5 1.2-3.5.2-5.6 1.8-5.6 4.4 0 2.4 1.8 4 4.3 4 2.4 0 4.2-1.5 4.3-4.2 1 .4 1.5 1.2 1.5 2.5 0 2.9-2 4.8-5.3 4.8-4 0-6.5-2.9-6.5-7.4S8 4.7 12 4.7c2.2 0 4 .9 5.1 2.7l2.2-1.3C17.7 3.6 15.2 2.2 12 2.2Zm-.4 13.1c-1.1 0-1.8-.5-1.8-1.4 0-1.1 1-1.7 3.1-1.8v.6c0 1.7-.5 2.6-1.3 2.6Z"/>',
 xing:'<path d="M3 7h4l3.2 5.5L6.8 18H2.5l3.4-5.5Zm8.8-5h4.5l-6.2 10.7L17 22h-4.5L7.6 12.7Z"/>',
 whatsapp:'<path d="M20 11.7a8 8 0 0 1-11.8 7L4 20l1.3-4A8 8 0 1 1 20 11.7Z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 8.1c-.3-.5-.6-.5-.9-.5h-.6c-.2 0-.5.1-.7.4-.3.3-.9.9-.9 2.1s.9 2.4 1 2.5c.1.2 1.8 2.9 4.4 3.9 2.2.9 2.6.7 3.1.7.5-.1 1.6-.7 1.8-1.3.2-.6.2-1.1.1-1.2-.1-.1-.3-.2-.7-.4l-1.7-.8c-.2-.1-.4-.1-.6.2l-.8 1c-.2.2-.3.2-.6.1-.3-.1-1.2-.4-2.2-1.3-.8-.7-1.3-1.5-1.5-1.8-.2-.3 0-.4.1-.6.1-.1.3-.3.4-.5.1-.1.2-.3.3-.5.1-.2 0-.4 0-.5Z"/>'
};
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
  for(const [key,label] of S.portals){const url=s.social?.[key];if(!url)continue;const a=document.createElement('a');a.href=url;a.className='nic-social-link';a.setAttribute('aria-label',label);a.title=label;a.target='_blank';a.rel='noopener noreferrer';const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('width','40');svg.setAttribute('height','40');svg.setAttribute('aria-hidden','true');svg.setAttribute('focusable','false');svg.innerHTML=socialIconPaths[key]||'';a.append(svg);nav.append(a);}
 }
 if(socialSection)socialSection.hidden=!nav?.childElementCount;
 const aboutSection=footer.querySelector('#nicFooterAboutSection');
 const about=footer.querySelector('#nicFooterAbout');
 const aboutDescription=String(s.content?.why?.metaDescription||s.meta?.why?.description||s.meta?.website?.description||'').trim();
 if(about){about.replaceChildren();if(aboutDescription){const more=document.createElement('a');more.href=new URL('warum-immocheck/',S.ROOT).href;more.textContent='Mehr...';more.className='nic-footer-more';about.append(document.createTextNode(aboutDescription+' '),more);}}
 if(aboutSection)aboutSection.hidden=!about||!aboutDescription;
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
