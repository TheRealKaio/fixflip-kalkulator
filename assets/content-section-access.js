(function(){
  'use strict';

  const message='Nur für registrierte Nutzer sichtbar.';

  function apply(settings){
    if(!settings||!document.body)return;
    const loggedIn=!!window.NICAccess?.user;
    document.querySelectorAll('[data-nic-content-key]').forEach(function(box){
      const rule=settings.contentSections?.[box.dataset.nicContentKey]||{};
      const hidden=rule.visible===false;
      const locked=!hidden&&!loggedIn&&rule.guestAllowed===false;
      box.classList.toggle('nic-content-box-hidden',hidden);
      box.classList.toggle('nic-content-box-guest-locked',locked);
      box.hidden=hidden;
      box.inert=hidden;

      let overlay=box.querySelector(':scope > .nic-content-box-guest-overlay');
      if(locked){
        if(!overlay){
          overlay=document.createElement('div');
          overlay.className='nic-content-box-guest-overlay';
          overlay.setAttribute('role','note');
          overlay.setAttribute('tabindex','0');
          overlay.textContent=message;
          box.append(overlay);
        }
      }else if(overlay){
        overlay.remove();
      }

      Array.from(box.children).forEach(function(child){
        if(child!==overlay)child.inert=locked;
      });
      if(locked)box.setAttribute('aria-disabled','true');
      else box.removeAttribute('aria-disabled');
    });
  }

  window.NICContentSections={apply};
  window.addEventListener('nic-auth-changed',function(){apply(window.NICSettings?.current);});
  window.addEventListener('nic-settings-updated',function(){apply(window.NICSettings?.current);});
  const observer=new MutationObserver(function(){apply(window.NICSettings?.current);});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  apply(window.NICSettings?.current);
  const settingsApi=window.NICSettings;
  if(settingsApi?.init)settingsApi.init().then(settingsApi.apply).catch(function(error){console.warn('Zentrale Box-Einstellungen:',error.message);});
})();