(function(){
  'use strict';

  const message='Nur für registrierte Nutzer sichtbar.';

  // The access controls must work even when no other stylesheet defines them.
  const style=document.createElement('style');
  style.id='nic-content-section-access-styles';
  style.textContent=`
    [data-nic-content-key].nic-content-box-hidden{display:none!important}
    [data-nic-content-key].nic-content-box-guest-locked{
      position:relative!important;
      isolation:isolate;
    }
    [data-nic-content-key].nic-content-box-guest-locked > :not(.nic-content-box-guest-overlay){
      pointer-events:none!important;
      user-select:none!important;
    }
    [data-nic-content-key] > .nic-content-box-guest-overlay{
      position:absolute!important;
      inset:0!important;
      z-index:100!important;
      display:flex!important;
      align-items:center;
      justify-content:center;
      padding:20px;
      box-sizing:border-box;
      background:rgba(245,247,250,.84)!important;
      color:#9aa3af!important;
      font-size:var(--nic-subtext-size,14px);
      font-weight:500;
      text-align:center;
      line-height:1.5;
      cursor:not-allowed;
    }
  `;
  (document.head||document.documentElement).appendChild(style);

  function apply(settings){
    if(!settings||!document.body)return;
    const loggedIn=!!window.NICAccess?.user;
    document.querySelectorAll('[data-nic-content-key]').forEach(function(box){
      const rule=settings.contentSections?.[box.dataset.nicContentKey]||{};
      const hidden=rule.visible===false;
      const locked=!hidden&&!loggedIn&&rule.guestAllowed===false;
      box.style.setProperty('--nic-subtext-size',String(settings.layout?.subtextSize||14)+'px');
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