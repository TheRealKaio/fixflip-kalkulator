(function(){
  'use strict';
  function apply(settings){
    if(!settings||!document.body)return;
    const loggedIn=!!window.NICAccess?.user;
    document.querySelectorAll('[data-nic-content-key]').forEach(function(box){
      const rule=settings.contentSections?.[box.dataset.nicContentKey]||{};
      box.classList.toggle('nic-content-box-hidden',rule.visible===false||(!loggedIn&&rule.guestAllowed===false));
    });
  }
  window.NICContentSections={apply};
  window.addEventListener('nic-auth-changed',function(){apply(window.NICSettings?.current);});
  window.addEventListener('nic-settings-updated',function(){apply(window.NICSettings?.current);});
  const observer=new MutationObserver(function(){apply(window.NICSettings?.current);});
  observer.observe(document.documentElement,{childList:true,subtree:true});
  apply(window.NICSettings?.current);
})();
