from pathlib import Path

path = Path("_site/index.html")
html = path.read_text(encoding="utf-8")

# Give the cost breakdown a stable hook for the guest visibility preference.
cost_heading = '<h2>Wo geht das Geld hin?</h2>'
if 'id="costsSection"' not in html:
    heading_at = html.find(cost_heading)
    if heading_at < 0:
        raise SystemExit("V8.348 cost breakdown heading missing")
    section_start = html.rfind("<section", 0, heading_at)
    if section_start < 0:
        raise SystemExit("V8.348 cost breakdown section missing")
    open_end = html.find(">", section_start)
    if open_end < 0 or open_end > heading_at:
        raise SystemExit("V8.348 cost breakdown section tag invalid")
    tag = html[section_start:open_end + 1]
    html = html[:section_start] + tag[:-1] + ' id="costsSection">' + html[open_end + 1:]

# Keep the monthly burden/rest-debt box in the page. Its visibility for guests
# is controlled by the same per-box admin settings as the other H2 boxes.
monthly_heading = "<h2>Monatliche Belastung & Restschuld</h2>"
if monthly_heading in html:
    heading_at = html.find(monthly_heading)
    section_start = html.rfind("<section", 0, heading_at)
    open_end = html.find(">", section_start)
    if section_start < 0 or open_end < 0 or open_end > heading_at:
        raise SystemExit("V8.348 budget monthly card location invalid")
    tag = html[section_start:open_end + 1]
    if 'id="budgetMonthlyBurdenSection"' not in tag:
        html = html[:section_start] + tag[:-1] + ' id="budgetMonthlyBurdenSection">' + html[open_end + 1:]

if 'id="costsSection"' not in html or monthly_heading not in html:
    raise SystemExit("V8.348 visible calculator markup check failed")
if 'id="scenarioSection"' not in html:
    raise SystemExit("V8.348 scenario section missing")

path.write_text(html, encoding="utf-8")
print("V8.348 guest-only insight hooks and budget screen cleanup applied")
