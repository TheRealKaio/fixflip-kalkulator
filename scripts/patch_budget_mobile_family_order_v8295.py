from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

old = '''    const lastDetail = visibleDetails[visibleDetails.length - 1];
    if(lastDetail.parentNode){
      lastDetail.insertAdjacentElement("afterend", family);
    }'''
new = '''    const lastDetail = visibleDetails[visibleDetails.length - 1];

    // Familienstatus bleibt immer im ursprünglichen Haupt-Container.
    // Falls die Einkommensfelder in einem inneren Aufklapp-Container liegen,
    // wird dessen oberster Block als Anker verwendet.
    let anchor = lastDetail;
    while(anchor && anchor.parentNode && anchor.parentNode !== originalParent){
      anchor = anchor.parentNode;
    }

    if(anchor && anchor.parentNode === originalParent){
      originalParent.insertBefore(family, anchor.nextSibling);
    }else{
      restoreFamily();
    }'''

if old not in s:
    raise SystemExit("V8.295 mobile family-order anchor missing")
s = s.replace(old, new, 1)

s = s.replace('id="budget-mobile-family-order-v8294"', 'id="budget-mobile-family-order-v8295"', 1)
s = s.replace("V8.294", "V8.295")
for old_version in ("8.236","8.290","8.291","8.292","8.293","8.294"):
    s = s.replace(f"service-worker.js?v={old_version}", "service-worker.js?v=8.295")

required = [
    'id="budget-mobile-family-order-v8295"',
    'while(anchor && anchor.parentNode && anchor.parentNode !== originalParent)',
    'originalParent.insertBefore(family, anchor.nextSibling);',
    'restoreFamily();',
    'V8.295',
    'service-worker.js?v=8.295'
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit("V8.295 verification failed: " + ", ".join(missing))

if 'lastDetail.insertAdjacentElement("afterend", family);' in s:
    raise SystemExit("V8.295 old nested-container move still present")

path.write_text(s, encoding="utf-8")
print("V8.295 mobile family-status ordering hardened")
