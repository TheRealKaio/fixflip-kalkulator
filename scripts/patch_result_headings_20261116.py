"""Numbered, neutral result headings and aligned financing fields (preview source)."""
from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
s = path.read_text(encoding="utf-8")

# Shorten only the own-use result tile label, preserving PDF wording and formulas.
s, credit_labels = re.subn(
    r'(<div class="name">)Monatliche Kreditrate \(Zins \+ Tilgung\)(</div>\s*<div class="value" id="ownKpiMonthlyCredit")',
    r'\1Monatliche Kreditrate\2', s,
)
if credit_labels != 1:
    raise SystemExit("Expected exactly one own-use monthly credit tile title")

# Replace the visible labels without touching their financial formulas.
labels = [
    ("Dein monatlich verfügbares Budget", "3. Dein monatlich verfügbares Budget"),
    ("Wieviel Haus kann ich mir leisten?", "4. Wieviel Haus kann ich mir leisten?"),
    ("Wo geht das Geld hin?", "5. Wo geht das Geld hin?"),
    ("Monatliche Tilgung- und Restschuld", "5. Monatliche Tilgung- und Restschuld"),
    ("Szenario - Was wäre wenn?", "6. Szenario - Was wäre wenn?"),
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

# Result headings are owned by the active shared route, never by a verdict.
result_script = r"""
<script id="nic-numbered-result-headings">
(function(){
 'use strict';
 let queued=false;
 function update(){
  const key=window.NICCalculators?.active||document.documentElement.dataset.calculator||document.body.dataset.calculator;
  const titles={own:'4. Ergebnis Eigennutzung',rent:'4. Ergebnis Vermietung',flip:'4. Ergebnis Fix und Flip'};
  if(!titles[key])return;
  const main=document.querySelector('.app>main.section')||document.querySelector('main');
  if(!main)return;
  const box=key==='rent'?main.querySelector('#rentDecision'):main.querySelector('.decision:not(.budget-financing-decision):not(#rentDecision)');
  if(!box)return;
  const heading=box.querySelector('h2');
  if(!heading)return;
  if(heading.textContent!==titles[key])heading.textContent=titles[key];
  heading.style.setProperty('color','#111827','important');
  heading.style.setProperty('text-align','left','important');
  heading.style.setProperty('font-size','var(--nic-h2-font-size,25px)','important');
  box.style.setProperty('display','block','important');
  box.removeAttribute('aria-hidden');
  for(const icon of box.querySelectorAll('.light'))icon.style.setProperty('display','none','important');
  if(key==='own'){
   for(const title of main.querySelectorAll('h2'))if(/^(?:2\.\s*)?Kaufpreis-Check$/.test(title.textContent.trim())&&title.textContent!=='2. Kaufpreis-Check')title.textContent='2. Kaufpreis-Check';
  }
 }
 function schedule(){if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;update();});}
 function init(){
  update();
  new MutationObserver(schedule).observe(document.querySelector('main')||document.body,{subtree:true,childList:true,characterData:true});
  window.addEventListener('nic-calculator-changed',schedule);
  window.addEventListener('nic-route-changed',schedule);
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
</script>
"""
s=re.sub(r'<script id="nic-(?:neutral-flip-result-heading|rental-neutral-result-title|numbered-result-headings)">.*?</script>', '',s,flags=re.S)
s=s.replace('</body>',result_script+'</body>',1)

path.write_text(s,encoding="utf-8")
print("Preview heading and input-alignment pass applied")
