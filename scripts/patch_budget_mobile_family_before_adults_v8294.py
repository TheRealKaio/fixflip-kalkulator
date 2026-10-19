from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

script = r'''
<script id="budget-mobile-family-before-adults-v8294">
(function(){
  let familyField = null;
  let familyParent = null;
  let familyNextSibling = null;

  function getField(id){
    const el = document.getElementById(id);
    return el ? el.closest(".field") : null;
  }

  function rememberFamilyPosition(){
    if(familyField) return familyField;
    familyField = getField("budgetFamilyStatus");
    if(familyField){
      familyParent = familyField.parentNode;
      familyNextSibling = familyField.nextSibling;
    }
    return familyField;
  }

  function restoreDesktopPosition(){
    const family = rememberFamilyPosition();
    if(!family || !familyParent) return;
    if(familyNextSibling && familyNextSibling.parentNode === familyParent){
      familyParent.insertBefore(family, familyNextSibling);
    }else{
      familyParent.appendChild(family);
    }
  }

  function syncFamilyPosition(){
    const family = rememberFamilyPosition();
    const adults = getField("budgetAdults");
    if(!family || !adults) return;

    if(!window.matchMedia("(max-width: 720px)").matches){
      restoreDesktopPosition();
      return;
    }

    const adultsParent = adults.parentNode;
    if(!adultsParent) return;

    if(family.parentNode !== adultsParent || family.nextElementSibling !== adults){
      adultsParent.insertBefore(family, adults);
    }
  }

  document.addEventListener("DOMContentLoaded", syncFamilyPosition);
  window.addEventListener("load", syncFamilyPosition);
  window.addEventListener("resize", syncFamilyPosition);
})();
</script>
'''

if 'id="budget-mobile-family-before-adults-v8294"' in s:
    raise SystemExit("V8.294 family-before-adults patch already present")
if "</body>" not in s:
    raise SystemExit("body closing tag missing")

s = s.replace("</body>", script + "\n</body>", 1)
s = s.replace("V8.293", "V8.294")
for old_version in ("8.236","8.290","8.291","8.292","8.293"):
    s = s.replace(f"service-worker.js?v={old_version}", "service-worker.js?v=8.294")

required = [
    'id="budget-mobile-family-before-adults-v8294"',
    'getField("budgetFamilyStatus")',
    'getField("budgetAdults")',
    'window.matchMedia("(max-width: 720px)")',
    'adultsParent.insertBefore(family, adults);',
    'restoreDesktopPosition();',
    'V8.294',
    'service-worker.js?v=8.294'
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit("V8.294 verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.294 mobile Familienstatus placed directly before Anzahl Erwachsene")
