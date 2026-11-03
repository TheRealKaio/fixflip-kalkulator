"""V8.373: align the rate cards and remove the redundant inline ratio."""

from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

ratio_markup = '<span class="budget-rate-ratio" id="budgetRateRatio"></span>'
if html.count(ratio_markup) != 1:
    raise SystemExit("V8.373 expected one inline rate ratio element")
html = html.replace(ratio_markup, "", 1)

ratio_runtime = '''  if($("budgetRateRatio")){
    $("budgetRateRatio").textContent = m.net > 0
      ? "(ca. " + new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(budgetRatePct) + " % vom Haushaltsnetto)"
      : "";
  }
'''
if html.count(ratio_runtime) != 1:
    raise SystemExit("V8.373 expected one inline rate ratio renderer")
html = html.replace(ratio_runtime, "", 1)

for old_css in (
    ".budget-rate-ratio{font-size:11px;font-weight:700;color:#365b96;margin-left:4px}\n",
    ".budget-summary-row.rate-status-green .budget-rate-ratio,.budget-summary-row.rate-status-yellow .budget-rate-ratio,.budget-summary-row.rate-status-red .budget-rate-ratio{color:inherit}",
):
    if html.count(old_css) != 1:
        raise SystemExit("V8.373 expected one obsolete ratio style")
    html = html.replace(old_css, "", 1)

old_width = ".budget-rate-slider-wrap{margin-top:10px;padding:11px 12px;"
new_width = ".budget-rate-slider-wrap{margin:10px -2px 0;box-sizing:border-box;padding:11px 12px;"
if html.count(old_width) != 1:
    raise SystemExit("V8.373 slider card width rule not found")
html = html.replace(old_width, new_width, 1)

if "budgetRateRatio" in html or '(ca. " + new Intl.NumberFormat' in html:
    raise SystemExit("V8.373 redundant inline rate ratio remains")

path.write_text(html, encoding="utf-8")
print("V8.373 rate cards aligned and inline ratio removed")
