"""V8.371: combine the budget rate slider and guidance into one card."""

from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

guidance = '<div class="budget-rate-guidance" id="budgetRateGuidance">Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten. Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung.</div>'
boundary = "          </div>\n          " + guidance + "\n        </div>"
merged = "          " + guidance + "\n          </div>\n        </div>"
if boundary not in html:
    raise SystemExit("V8.371 budget rate slider/guidance boundary not found")
html = html.replace(boundary, merged, 1)

old_css = ".budget-rate-guidance{margin-top:8px;padding:9px 10px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;color:#52627a;font-size:11px;line-height:1.45}"
new_css = ".budget-rate-guidance{margin-top:8px;padding:0;border:0;border-radius:0;background:transparent;color:#52627a;font-size:11px;line-height:1.45}"
if old_css not in html:
    raise SystemExit("V8.371 budget rate guidance card style not found")
html = html.replace(old_css, new_css, 1)

if html.count(guidance) != 1:
    raise SystemExit("V8.371 changed the budget guidance text")
if "budget-rate-guidance{margin-top:8px;padding:9px 10px" in html:
    raise SystemExit("V8.371 separate guidance box style remains")

path.write_text(html, encoding="utf-8")
print("V8.371 budget rate guidance merged into the slider card")
