from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

# 1) The active (later) renderTrades override must emit the mobile group classes.
old_sqm='''      out+='<div class="trade-row"><div class="trade-top"><div>'+
        '<div class="trade-name">'+t.name+'</div>+'''
new_sqm='''      out+='<div class="trade-row trade-row-sqm"><div class="trade-top"><div>'+
        '<div class="trade-name">'+t.name+'</div>+'''
if old_sqm not in s:
    raise SystemExit("V8.290 active sqm render anchor missing")
s=s.replace(old_sqm,new_sqm,1)

old_fixed='''      out+='<div class="trade-row"><div class="trade-top">'+
        '<div class="trade-copy"><div class="trade-name">'+t.name+'</div><div class="trade-basis">'+basis+'</div>+'''
new_fixed='''      out+='<div class="trade-row trade-row-fixed"><div class="trade-top">'+
        '<div class="trade-copy"><div class="trade-name">'+t.name+'</div><div class="trade-basis">'+basis+'</div>+'''
if old_fixed not in s:
    raise SystemExit("V8.290 active fixed render anchor missing")
s=s.replace(old_fixed,new_fixed,1)

# 2) Remove the obsolete proposal-application listener from the earlier implementation.
old_legacy='''    btn.textContent="Vorschlag übernehmen";
    btn.addEventListener("click",applyTradeSuggestions);

    right.appendChild(btn);'''
new_legacy='''    btn.textContent="Vorschlag übernehmen";

    right.appendChild(btn);'''
if old_legacy not in s:
    raise SystemExit("V8.290 legacy proposal click anchor missing")
s=s.replace(old_legacy,new_legacy,1)

# 3) Keep one authoritative apply handler, but do not block the auxiliary update listeners.
old_apply='''  const applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      event.stopImmediatePropagation();
      applyCurrentSuggestions();
    },true);
  }'''
new_apply='''  const applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      applyCurrentSuggestions();
    },true);
  }'''
if old_apply not in s:
    raise SystemExit("V8.290 authoritative proposal handler anchor missing")
s=s.replace(old_apply,new_apply,1)

s=s.replace("V8.289","V8.290")
s=s.replace("service-worker.js?v=8.289","service-worker.js?v=8.290")

required=[
    'class="trade-row trade-row-sqm"',
    'class="trade-row trade-row-fixed"',
    'applyButton.addEventListener("click",function(event){',
    'event.preventDefault();\n      applyCurrentSuggestions();',
    'V8.290',
    'service-worker.js?v=8.290'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.290 verification failed: "+", ".join(missing))

if 'btn.addEventListener("click",applyTradeSuggestions);' in s:
    raise SystemExit("V8.290 obsolete proposal handler still present")
if 'event.stopImmediatePropagation();\n      applyCurrentSuggestions();' in s:
    raise SystemExit("V8.290 proposal handler still blocks auxiliary updates")

path.write_text(s,encoding="utf-8")
print("V8.290 active renovation rows classified and proposal handler unified")
