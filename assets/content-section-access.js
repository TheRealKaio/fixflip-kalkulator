(function(){
  'use strict';

  const message='Nur für angemeldete Nutzer sichtbar.';

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
      background:rgba(245,247,250,.72)!important;
      color:#9aa3af!important;
      font-family:var(--nic-body-font-family,inherit)!important;
      font-size:var(--nic-body-font-size,16px)!important;
      font-weight:500;
      text-align:center;
      line-height:1.5;
      cursor:not-allowed;
      flex-direction:column;
      gap:8px;
    }
    [data-nic-content-key].nic-content-box-guest-locked .nic-masked-value{
      color:transparent!important;
      text-shadow:none!important;
      position:relative!important;
    }
    [data-nic-content-key].nic-content-box-guest-locked .nic-masked-value::after{
      content:"?"!important;
      color:#94a3b8!important;
      position:absolute;
      inset:0;
      display:flex;
      align-items:center;
      justify-content:center;
      font:inherit;
    }
    html:not(.nic-content-ready) [data-nic-content-key]{
      visibility:hidden!important;
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
      box.classList.toggle('nic-content-box-hidden',hidden);
      box.classList.toggle('nic-content-box-guest-locked',locked);
      box.querySelectorAll('.value,.amount,.kpi-value,.result-value,.result-amount,.metric-value,.budget-result-value,.stat-value').forEach(function(el){el.classList.toggle('nic-masked-value',locked);});
      box.hidden=hidden;
      box.inert=hidden;

      let overlay=box.querySelector(':scope > .nic-content-box-guest-overlay');
      if(locked){
        if(!overlay){
          overlay=document.createElement('div');
          overlay.className='nic-content-box-guest-overlay';
          overlay.setAttribute('role','note');
          overlay.setAttribute('tabindex','0');
          const question=document.createElement('strong');
          question.textContent='?';
          question.style.fontSize='2.5em';
          const note=document.createElement('span');
          note.textContent=message;
          overlay.append(question,note);
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
  // React only to newly added content boxes. Overlay insertion must not recursively
  // trigger a full pass, which can cause needless DOM changes and repainting.
  let pending=false;
  const observer=new MutationObserver(function(records){
    if(pending||!records.some(function(record){return Array.from(record.addedNodes).some(function(node){return node.nodeType===1&&(node.matches?.('[data-nic-content-key]')||node.querySelector?.('[data-nic-content-key]'));});}))return;
    pending=true;
    queueMicrotask(function(){pending=false;apply(window.NICSettings?.current);});
  });
  observer.observe(document.documentElement,{childList:true,subtree:true});
  const settingsApi=window.NICSettings;
  if(settingsApi?.init){
    settingsApi.init().then(function(settings){
      settingsApi.apply(settings);
      apply(settings);
      document.documentElement.classList.add('nic-content-ready');
    }).catch(function(error){
      console.warn('Zentrale Box-Einstellungen:',error.message);
      // Do not reveal protected boxes when their access policy cannot be loaded.
    });
  }
})();