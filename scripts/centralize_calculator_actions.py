"""Make the five calculators' footer actions use one authoritative CSS file.

Run after finalize_shared_layout and after any other style-generation steps.
Leave the existing buttons and their event handlers untouched.
"""
from pathlib import Path
import re
import sys
from unify_calculator_header import split

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
file_name = "calculator-actions.css"
target = re.compile(
    r"\.(?:bottom-(?:actions|primary|pdf|save|share)|save-arrow)(?![\w-])"
    r"|#(?:recalc|newCalc|share|download)(?![\w-])"
)
css = """/* Authoritative calculator action bar (all five routes).
   Only presentation is controlled here; click/PDF/reset handlers remain in JS. */
:root {
  --nic-action-height: 44px;
  --nic-action-radius: 9px;
  --nic-action-gap: 8px;
  --nic-action-primary: #af231c;
  --nic-action-secondary: #111a2e;
  --nic-action-color: #fff;
}
html body:not(.nic-admin) .bottom .bottom-actions {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  align-items: stretch !important;
  justify-content: space-between !important;
  gap: var(--nic-action-gap) !important;
  width: 100% !important;
  min-width: 0 !important;
  box-sizing: border-box !important;
}
html body:not(.nic-admin) .bottom .bottom-actions > :is(button,.bottom-primary,.bottom-pdf,.bottom-save) {
  appearance: none !important;
  -webkit-appearance: none !important;
  box-sizing: border-box !important;
  position: static !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  height: var(--nic-action-height) !important;
  min-height: var(--nic-action-height) !important;
  max-height: var(--nic-action-height) !important;
  margin: 0 !important;
  padding: 0 12px !important;
  border: 0 !important;
  border-radius: 9px !important;
  background: var(--nic-action-secondary) !important;
  color: var(--nic-action-color) !important;
  font: inherit !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  line-height: 1.15 !important;
  text-align: center !important;
  text-decoration: none !important;
  white-space: nowrap !important;
  box-shadow: none !important;
  transform: none !important;
  cursor: pointer;
}
html body:not(.nic-admin) .bottom .bottom-actions > .bottom-primary {
  background: var(--nic-action-primary) !important;
  flex: 1 1 0 !important;
  min-width: 0 !important;
  max-width: none !important;
  width: auto !important;
}
html body:not(.nic-admin) .bottom .bottom-actions > .bottom-pdf {
  background: var(--nic-action-secondary) !important;
  flex: 0 0 auto !important;
  min-width: max-content !important;
  width: auto !important;
}
html body:not(.nic-admin) .bottom .bottom-actions > .bottom-save {
  background: var(--nic-action-secondary) !important;
  flex: 0 0 52px !important;
  width: 52px !important;
  min-width: 52px !important;
  max-width: 52px !important;
  padding: 0 !important;
}
html body:not(.nic-admin) .bottom .bottom-actions .save-arrow {
  display: inline-flex !important;
  justify-content: center !important;
  align-items: center !important;
  color: inherit !important;
  font-size: 22px !important;
  font-weight: 400 !important;
  line-height: 1 !important;
  transform: none !important;
  margin: 0 !important;
}
html body:not(.nic-admin) .bottom .bottom-actions > :is(button,.bottom-primary,.bottom-pdf,.bottom-save):focus-visible {
  outline: 2px solid var(--nic-action-primary) !important;
  outline-offset: 2px !important;
}
html body:not(.nic-admin) .bottom .bottom-actions > :is(button,.bottom-primary,.bottom-pdf,.bottom-save):disabled {
  opacity: .5 !important;
  cursor: not-allowed;
}
@media (max-width: 420px) {
  html body:not(.nic-admin) .bottom .bottom-actions { gap: 6px !important; }
  html body:not(.nic-admin) .bottom .bottom-actions > :is(button,.bottom-primary,.bottom-pdf,.bottom-save) {
    font-size: 12px !important;
    padding-inline: 7px !important;
  }
  html body:not(.nic-admin) .bottom .bottom-actions > .bottom-save {
    width: 44px !important;
    min-width: 44px !important;
    max-width: 44px !important;
    flex-basis: 44px !important;
    padding: 0 !important;
  }
}
"""

paths = [site / slug / "index.html" for slug in
         ("", "budget", "eigennutzung", "vermietung", "fix-flip", "finanzierungsrechner")]
for page in paths:
    if not page.is_file():
        raise SystemExit("Missing calculator page: " + str(page))
    html = page.read_text(encoding="utf-8")
    for cls in ("bottom-actions", "bottom-primary", "bottom-pdf", "bottom-save"):
        if not re.search(r'class=["\'][^"\']*\b' + cls + r'\b', html):
            raise SystemExit(f"{page}: missing action control {cls}")

# Remove stale button-specific rules from generated stylesheets and inline CSS.
# Shared or unrelated selectors in compound rules are preserved by split().
removed = 0
for asset in site.glob("*.css"):
    if asset.name == file_name:
        continue
    content = asset.read_text(encoding="utf-8")
    cleaned, rules = split(content, target)
    if rules:
        removed += len(rules)
        asset.write_text(cleaned, encoding="utf-8")

for page in site.rglob("*.html"):
    content = page.read_text(encoding="utf-8")
    def clear_style(match):
        global removed
        cleaned, rules = split(match.group(2), target)
        removed += len(rules)
        return match.group(1) + cleaned + match.group(3)
    cleaned = re.sub(r"(<style\b[^>]*>)(.*?)(</style>)", clear_style, content,
                     flags=re.I | re.S)
    if cleaned != content:
        page.write_text(cleaned, encoding="utf-8")

(site / file_name).write_text(css, encoding="utf-8")
for page in paths:
    html = page.read_text(encoding="utf-8")
    if html.count('href="/' + file_name + '"') != 1:
        raise SystemExit(str(page) + ": expected exactly one shared action stylesheet")
    # Make the authoritative stylesheet the final head stylesheet after all
    # responsive/theme bundles, so same-specificity legacy rules cannot win.
    link_pattern = re.compile(r'<link\\b[^>]*href="/' + re.escape(file_name) + r'"[^>]*>', re.I)
    html, n = link_pattern.subn("", html)
    if n != 1 or html.count("</head>") != 1:
        raise SystemExit(str(page) + ": missing action CSS link or head")
    html = html.replace("</head>", '<link rel="stylesheet" href="/' + file_name + '"></head>', 1)
    page.write_text(html, encoding="utf-8")
    # Inline important style would win over the consolidated stylesheet.
    if re.search(r'<(?:button|a)\b[^>]*class="[^"]*bottom-(?:primary|pdf|save)[^"]*"[^>]*style="[^"]*!important',html,re.I):
        raise SystemExit(str(page) + ": action has inline !important styling")

if removed == 0:
    raise SystemExit("Legacy action CSS not found; refusing unchecked release")
print("Centralized calculator action styling. Removed",removed,"old rules. Routes:",len(paths))
