from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

old = '''  function syncMobileFamilyOrder(){
    const family = findFamilyField();
    if(!family) return;

    if(!window.matchMedia("(max-width: 720px)").matches){
      restoreFamily();
      return;
    }

    const details = incomeDetailFields();
    const visibleDetails = details.filter(isVisible);

    if(!visibleDetails.length){
      restoreFamily();
      return;
    }

    const lastDetail = visibleDetails[visibleDetails.length - 1];

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
    }
  }'''

new = '''  function syncMobileFamilyOrder(){
    const family = findFamilyField();
    const details = document.getElementById("budgetIncomeDetails");
    if(!family || !details) return;

    const isMobile = window.matchMedia("(max-width: 720px)").matches;
    const detailsOpen = isVisible(details);

    if(!isMobile || !detailsOpen){
      restoreFamily();
      return;
    }

    // Reale DOM-Struktur: budgetIncomeDetails liegt direkt hinter dem
    // zweispaltigen Grid mit Haushaltsnettoeinkommen + Familienstatus.
    // Mobil wird Familienstatus deshalb aus diesem Grid herausgenommen
    // und direkt hinter den gesamten aufgeklappten Einkommensblock gesetzt.
    if(family.previousElementSibling !== details){
      details.insertAdjacentElement("afterend", family);
    }
  }'''

if old not in s:
    raise SystemExit("V8.296 V8.295 mobile-order block missing")
s = s.replace(old, new, 1)

s = s.replace('id="budget-mobile-family-order-v8295"', 'id="budget-mobile-family-order-v8296"', 1)
s = s.replace("V8.295", "V8.296")
for old_version in ("8.236","8.290","8.291","8.292","8.293","8.294","8.295"):
    s = s.replace(f"service-worker.js?v={old_version}", "service-worker.js?v=8.296")

required = [
    'id="budget-mobile-family-order-v8296"',
    'const details = document.getElementById("budgetIncomeDetails");',
    'const detailsOpen = isVisible(details);',
    'details.insertAdjacentElement("afterend", family);',
    'family.previousElementSibling !== details',
    'restoreFamily();',
    'V8.296',
    'service-worker.js?v=8.296'
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit("V8.296 verification failed: " + ", ".join(missing))

# Alte, strukturell falsche Anchor-Logik darf nicht mehr aktiv sein.
if 'while(anchor && anchor.parentNode && anchor.parentNode !== originalParent)' in s:
    raise SystemExit("V8.296 old cross-container anchor logic still present")

path.write_text(s, encoding="utf-8")
print("V8.296 mobile family-status ordering matched to actual DOM")
