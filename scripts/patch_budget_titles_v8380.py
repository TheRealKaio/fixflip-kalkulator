"""V8.380: restore the budget symbol and update the three section titles."""
from pathlib import Path
import sys
path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")
header='<div class="decision go budget-financing-decision">'
if html.count(header)!=1:
    raise SystemExit("Expected one budget financing header")
html=html.replace(header,header+'\n          <div class="light" aria-hidden="true">💶</div>',1)
replacements={
 '<h2>3. Annahme zur möglichen Finanzierung</h2>':'<h2>3. Finanzierung und Nebenkosten</h2>',
 '<h2>Monatliche Belastung & Restschuld</h2>':'<h2>Monatliche Tilgung- und Restschuld</h2>',
 '<h2>Deine mögliche Finanzierung</h2>':'<h2>Wieviel Haus kann ich mir leisten?</h2>',
}
for old,new in replacements.items():
    if html.count(old)!=1:
        raise SystemExit("Expected one heading: "+old)
    html=html.replace(old,new,1)
css="""
#budgetSection .budget-financing-decision{display:grid!important;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:8px 12px;text-align:left!important}
#budgetSection .budget-financing-decision>div:not(.light){display:contents}
#budgetSection .budget-financing-decision>.light{grid-column:1;grid-row:1;width:50px;max-width:50px}
#budgetSection .budget-financing-decision h2{grid-column:2;grid-row:1;min-width:0;margin:0;text-align:left!important}
#budgetSection .budget-financing-decision p{grid-column:1 / -1;width:100%;margin:0;text-align:left!important;font-size:var(--nic-body-font-size,16px)!important}
"""
html=html.replace("</style>",css+"</style>",1)
path.write_text(html,encoding="utf-8")
print("V8.380 budget headings and financing symbol updated")
