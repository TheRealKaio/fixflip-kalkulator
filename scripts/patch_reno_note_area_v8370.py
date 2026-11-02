"""V8.370: center renovation guidance and verify zero area placeholders are absent."""

from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

html, removed = re.subn(
    r'(<input class="(?:trade-area|rent-trade-area)"[^>]*?)\s+placeholder="0"',
    r'\1',
    html,
)
if re.search(r'<input class="(?:trade-area|rent-trade-area)"[^>]*placeholder="0"', html):
    raise SystemExit("V8.370 zero placeholder remains in a renovation area field")
path.write_text(html, encoding="utf-8")

css_path = Path("assets/immocheck-brand-theme.css")
css = css_path.read_text(encoding="utf-8")
rule = "body:not(.nic-embed) .reno-note{text-align:center}"
if rule not in css:
    css = css.rstrip() + "\n\n/* Center shared renovation guidance across calculators. */\n" + rule + "\n"
    css_path.write_text(css, encoding="utf-8")
print(f"V8.370 renovation guidance centered; {removed} zero area placeholders removed")
