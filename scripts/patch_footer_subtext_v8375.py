"""V8.375: link all site footer text to the central subtext size setting."""

from pathlib import Path
import sys

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
settings = (site / "site-settings.js").read_text(encoding="utf-8")
expected = "body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer),body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) *{font-size:${l.subtextSize}px!important;line-height:1.5}"
if settings.count(expected) != 1:
    raise SystemExit("V8.375 footer-to-subtext typography mapping is missing or duplicated")
body_rule = next((line for line in settings.splitlines() if "font-size:${l.bodySize}px!important" in line and "footer-note" in line), "")
if body_rule:
    raise SystemExit("V8.375 footer text still uses the base font size")
print("V8.375 verified: calculator and public footer text follows subtext size")
