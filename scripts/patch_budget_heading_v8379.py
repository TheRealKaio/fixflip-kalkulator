"""V8.379: simplify the budget financing heading and expense total."""
from pathlib import Path
import sys
path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")
old="      <section class=\"card\">\n        <div class=\"decision go budget-financing-decision\">\n          <div class=\"light\" aria-hidden=\"true\">💶</div>\n          <div>\n            <h2>Deine mögliche Finanzierung</h2>\n            <p>Aus deinem Budget, Eigenkapital und den Finanzierungsannahmen ergibt sich hier deine mögliche Finanzierung.</p>\n          </div>\n        </div>\n        <div class=\"budget-result-grid\">"
new="      <section class=\"card\">\n        <div class=\"decision go budget-financing-decision\">\n          <div>\n            <h2>Deine mögliche Finanzierung</h2>\n            <p>Aus deinem Budget, Eigenkapital und den Finanzierungsannahmen ergibt sich hier deine mögliche Finanzierung.</p>\n          </div>\n        </div>\n        <div class=\"budget-result-grid\">"
if html.count(old)!=1:
    raise SystemExit("Expected one budget financing header")
html=html.replace(old,new,1)
css="/* Budget result header and expense total. */\n#budgetExpensesSection .budget-summary-row.total:has(#budgetExpensesTotal){border-top:0!important}\n#budgetSection .budget-financing-decision{display:block!important;text-align:left!important}\n#budgetSection .budget-financing-decision>div{width:100%;max-width:100%;min-width:0}\n#budgetSection .budget-financing-decision h2{ text-align:left!important }\n#budgetSection .budget-financing-decision p{width:100%;max-width:none!important;text-align:left!important;font-size:var(--nic-body-font-size,16px)!important;line-height:1.5!important}\n"
html=html.replace("</style>",css+"</style>",1)
path.write_text(html,encoding="utf-8")
print("V8.379 budget financing heading simplified")
