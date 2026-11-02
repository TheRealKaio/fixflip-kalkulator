"""V8.372: simplify the budget rate slider label, value and warning copy."""

from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

replacements = [
    (
        '<div class="budget-rate-slider-head">\n              <span>Maximal tragbare Kreditrate</span>',
        '<div class="budget-rate-slider-head">\n              <span>Anteil am Haushaltsnetto</span>',
        "slider label",
    ),
    (
        '$("budgetRateSliderValue").textContent=eur(m.monthlyRate)+" · "+new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(selectedPct)+" %";',
        '$("budgetRateSliderValue").textContent=new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(selectedPct)+" %";',
        "slider value",
    ),
    (
        'Finanzierungsreserve unterschritten · Abweichung: "+eur(bufferDeviation)+" · Finanzierungsreserve: ',
        'Finanzierungsreserve unterschritten · Finanzierungsreserve: ',
        "warning deviation",
    ),
]

for old, new, label in replacements:
    if html.count(old) != 1:
        raise SystemExit(f"V8.372 expected one {label} target, found {html.count(old)}")
    html = html.replace(old, new, 1)

for obsolete in ('Abweichung: "+eur(bufferDeviation)', 'textContent=eur(m.monthlyRate)+" · "+'):
    if obsolete in html:
        raise SystemExit("V8.372 obsolete slider text remains: " + obsolete)

path.write_text(html, encoding="utf-8")
print("V8.372 budget rate label, euro display and warning deviation updated")
