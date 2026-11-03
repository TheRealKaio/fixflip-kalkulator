"""Unify 'Wo geht das Geld hin?' cost chart text with Untertexte (px).

Presentation only: no chart values, widths, calculations, masking or JS handlers are changed.
"""
from pathlib import Path
import re
import sys

site = Path(sys.argv[1] if len(sys.argv)>1 else "_site")
asset = "cost-breakdown-typography.css"
css = """/* Central typography for the purchase/renovation/financing cost bars.
   Shares the same live setting as Untertexte (px). */
html body:not(.nic-admin) :is(.cost-row, .cost-row *,
  .cost-total, .cost-total *, .cost-summary, .cost-summary *,
  .cost-footer, .cost-footer *, .cost-grand-total, .cost-grand-total *) {
  font-size: var(--nic-subtext-font-size, 14px) !important;
}
/* Some report variants use a generic total row within the cost breakdown.
   Scope it strictly to a section that contains the cost bars. */
html body:not(.nic-admin) :is(section,.card):has(.cost-row)
:is(.total, .total *, .total-row, .total-row *, .summary-total, .summary-total *) {
  font-size: var(--nic-subtext-font-size, 14px) !important;
}
"""
# Remove only redundant typography declarations inside cost-chart rules.
# Preserve colors, layout, bar widths, spacing and all calculation-related attributes.
target = re.compile(r"\.(?:cost-row|cost-total|cost-summary|cost-footer|cost-grand-total)(?![\w-])")
font_decl = re.compile(r"(?<![-\w])font-size\s*:\s*[^;{}]+;?", re.I)
style_rule = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
removed = 0
def clean_rules(content):
    def replace(m):
        global removed
        selector, body = m.groups()
        # Do not delete typography from selectors also used by unrelated UI.
        if not target.search(selector):
            return m.group(0)
        if any(not target.search(item) for item in selector.split(",")):
            return m.group(0)
        new_body, n = font_decl.subn("", body)
        removed += n
        return selector + "{" + new_body + "}"
    return style_rule.sub(replace, content)

for path in site.glob("*.css"):
    if path.name == asset:
        continue
    original = path.read_text(encoding="utf-8")
    updated = clean_rules(original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
for page in site.rglob("*.html"):
    original = page.read_text(encoding="utf-8")
    updated = re.sub(r"(<style\b[^>]*>)(.*?)(</style>)",
                     lambda m: m[1]+clean_rules(m[2])+m[3],original,
                     flags=re.S|re.I)
    if updated != original:
        page.write_text(updated, encoding="utf-8")

(site / asset).write_text(css,encoding="utf-8")
changed = 0
for slug in ("", "budget", "eigennutzung", "vermietung", "fix-flip", "finanzierungsrechner"):
    page = site / slug / "index.html"
    if not page.is_file():
        raise SystemExit("Missing calculator page: " + str(page))
    html = page.read_text(encoding="utf-8")
    if html.count("</head>") != 1:
        raise SystemExit("Missing head: " + str(page))
    if asset in html:
        raise SystemExit("Duplicate cost typography stylesheet: "+str(page))
    html = html.replace("</head>",'<link rel="stylesheet" href="/'+asset+'"></head>',1)
    page.write_text(html,encoding="utf-8")
    changed += 1
print("Central cost breakdown typography installed on",changed,
      "calculator routes; obsolete font-size declarations removed:",removed)
