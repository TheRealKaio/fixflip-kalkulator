"""Numbered, neutral result headings and aligned financing fields (preview source)."""
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
s = path.read_text(encoding="utf-8")

# Replace the visible labels without touching their financial formulas.
labels = [
    ("Dein monatlich verfügbares Budget", "3. Dein monatlich verfügbares Budget"),
    ("Wieviel Haus kann ich mir leisten?", "4. Wieviel Haus kann ich mir leisten?"),
    ("Wo geht das Geld hin?", "5. Wo geht das Geld hin?"),
]
for original, desired in labels:
    # Change only heading content; avoid copies in SEO text and PDF.
    pattern = r"(<h[1-4]\b[^>]*>\s*)" + re.escape(original) + r"(\s*</h[1-4]>)"
    s, changed = re.subn(pattern, lambda m: m[1] + desired + m[2], s)
    if not changed:
        print("Heading not found in h1-h4:", original)

# Make owner-use and rental result titles independent from traffic-light decisions.
for original, desired in [
    ("Eigennutzung", "4. Ergebnis Eigennutzung"),
    ("Negativer monatlicher Cashflow", "4. Ergebnis Vermietung"),
    ("Positiver monatlicher Cashflow", "4. Ergebnis Vermietung"),
]:
    pattern = r"(<h2\b[^>]*>\s*)" + re.escape(original) + r"(\s*</h2>)"
    s, changed = re.subn(pattern, lambda m: m[1] + desired + m[2], s, count=1)
    if changed:
        print("Result heading updated:", desired)

# Explicitly neutralize only headings, not the actual financial outcome colors.
style = """
/* Numbered section headings use the shared h2 size and neutral text. */
#budgetSection .budget-financing-decision {
  display:block!important;
  text-align:left!important;
}
#budgetSection .budget-financing-decision > .light,
#budgetSection .budget-financing-decision .light[aria-hidden="true"] {
  display:none!important;
}
#budgetSection .budget-financing-decision > div:not(.light) {
  display:block!important;
}
#budgetSection .budget-financing-decision h2,
#budgetSection .budget-financing-decision h2 * {
  color:#111827!important;
  text-align:left!important;
  font-size:var(--nic-h2-font-size,25px)!important;
}
#budgetSection .budget-financing-decision p {
  text-align:left!important;
}
/* Finance form labels have one common baseline, independently of note text. */
#budgetAssumptionsBody .budget-grid.three > .field:not(.budget-state-field) {
  display:flex;
  flex-direction:column;
  min-width:0;
}
#budgetAssumptionsBody .budget-grid.three > .field:not(.budget-state-field) > label {
  display:flex;
  align-items:flex-end;
  min-height:36px;
  line-height:1.25;
  justify-content:flex-start;
  text-align:left;
  gap:4px;
}
#budgetAssumptionsBody .budget-grid.three > .field:not(.budget-state-field) > label .hint,
#budgetAssumptionsBody .budget-grid.three > .field:not(.budget-state-field) > label .unit {
  margin-left:0!important;
  text-align:left!important;
}
#budgetAssumptionsBody .budget-grid.three > .field:not(.budget-state-field) > .input-wrap {
  margin-top:0!important;
}
@media(max-width:700px){
  #budgetAssumptionsBody .budget-grid.three > .field:not(.budget-state-field) > label {
    min-height:0;
  }
}
"""
s=s.replace("</style>",style+"</style>",1)

# The Fix & Flip decision is a dynamic traffic-light. Keep its calculations but
# replace the decision presentation with a permanent neutral H2 on that route.
# This also handles subsequent re-renders when amounts are changed.
flip_script = r"""
<script id="nic-neutral-flip-result-heading">
(function(){
  'use strict';
  function isFlip(){
    return document.body.dataset.calculator === 'flip'
      || /\/fix-flip\/?$/.test(location.pathname)
      || (document.getElementById('flipSection') && !document.getElementById('flipSection').hidden
          && getComputedStyle(document.getElementById('flipSection')).display!=='none');
  }
  function update(){
    if(!isFlip()) return;
    const decisions=[...document.querySelectorAll('.decision')];
    const decision=decisions.find(el=>/Noch verhandeln oder prüfen|Ziel-Gewinn|Ziel-Marge|Deal prüfen|Gewinnziel/i.test(el.textContent||''))
      || decisions.find(el=>el.parentElement && /Gewinn|Marge/.test(el.parentElement.textContent||''));
    if(!decision) return;
    if(!decision.previousElementSibling?.matches('[data-nic-flip-result-heading]')){
      const title=document.createElement('h2');
      title.dataset.nicFlipResultHeading='true';
      title.textContent='4. Ergebnis Fix und Flip';
      title.style.cssText='color:#111827;text-align:left;margin:0 0 12px;font-size:var(--nic-h2-font-size,25px);font-weight:700;';
      decision.insertAdjacentElement('beforebegin',title);
    }
    decision.style.setProperty('display','none','important');
    decision.setAttribute('aria-hidden','true');
  }
  let scheduled=false;
  function schedule(){
    if(scheduled) return;
    scheduled=true;
    requestAnimationFrame(()=>{scheduled=false;update();});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',()=>{
    update();
    new MutationObserver(schedule).observe(document.querySelector('main')||document.body,{subtree:true,childList:true,characterData:true});
  },{once:true});
  else {
    update();
    new MutationObserver(schedule).observe(document.querySelector('main')||document.body,{subtree:true,childList:true,characterData:true});
  }
})();
</script>
"""
if 'nic-neutral-flip-result-heading' not in s:
    s = s.replace('</body>', flip_script + '</body>', 1)
path.write_text(s,encoding="utf-8")
print("Preview heading and input-alignment pass applied")
