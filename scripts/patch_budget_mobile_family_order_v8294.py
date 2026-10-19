from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

script = r'''
<script id="budget-mobile-family-order-v8294">
(function(){
  const incomeIds = [
    "budgetIncomeEmployment",
    "budgetIncomePension",
    "budgetIncomeSupport",
    "budgetIncomeSide",
    "budgetIncomeRent",
    "budgetIncomeOther"
  ];

  let familyField = null;
  let originalParent = null;
  let originalNextSibling = null;

  function findFamilyField(){
    if(familyField && document.documentElement.contains(familyField)) return familyField;
    const labels = Array.from(document.querySelectorAll(".field label, label"));
    const label = labels.find(el => (el.textContent || "").trim().toLowerCase().includes("familienstatus"));
    familyField = label ? label.closest(".field") : null;
    if(familyField && !originalParent){
      originalParent = familyField.parentNode;
      originalNextSibling = familyField.nextSibling;
    }
    return familyField;
  }

  function incomeDetailFields(){
    return incomeIds
      .map(id => document.getElementById(id))
      .filter(Boolean)
      .map(el => el.closest(".field"))
      .filter(Boolean);
  }

  function isVisible(el){
    if(!el) return false;
    const style = window.getComputedStyle(el);
    return style.display !== "none" && style.visibility !== "hidden" && el.getClientRects().length > 0;
  }

  function restoreFamily(){
    const family = findFamilyField();
    if(!family || !originalParent) return;
    if(originalNextSibling && originalNextSibling.parentNode === originalParent){
      originalParent.insertBefore(family, originalNextSibling);
    }else{
      originalParent.appendChild(family);
    }
  }

  function syncMobileFamilyOrder(){
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
    if(lastDetail.parentNode){
      lastDetail.insertAdjacentElement("afterend", family);
    }
  }

  document.addEventListener("DOMContentLoaded", syncMobileFamilyOrder);
  window.addEventListener("load", syncMobileFamilyOrder);
  window.addEventListener("resize", syncMobileFamilyOrder);

  document.addEventListener("click", function(){
    setTimeout(syncMobileFamilyOrder, 0);
    setTimeout(syncMobileFamilyOrder, 120);
  });

  if(window.MutationObserver){
    const observer = new MutationObserver(function(){
      syncMobileFamilyOrder();
    });
    window.addEventListener("load", function(){
      observer.observe(document.body, {
        childList:true,
        subtree:true,
        attributes:true,
        attributeFilter:["class","style","hidden","aria-expanded"]
      });
    });
  }
})();
</script>
'''

if 'id="budget-mobile-family-order-v8294"' in s:
    raise SystemExit("V8.294 mobile family order patch already present")
if "</body>" not in s:
    raise SystemExit("body closing tag missing")

s = s.replace("</body>", script + "\n</body>", 1)
s = s.replace("V8.293", "V8.294")
for old_version in ("8.236","8.290","8.291","8.292","8.293"):
    s = s.replace(f"service-worker.js?v={old_version}", "service-worker.js?v=8.294")

required = [
    'id="budget-mobile-family-order-v8294"',
    'window.matchMedia("(max-width: 720px)")',
    '"budgetIncomeEmployment"',
    '"budgetIncomeOther"',
    'includes("familienstatus")',
    'lastDetail.insertAdjacentElement("afterend", family);',
    'restoreFamily();',
    'V8.294',
    'service-worker.js?v=8.294'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.294 verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.294 mobile household income/family-status ordering applied")
