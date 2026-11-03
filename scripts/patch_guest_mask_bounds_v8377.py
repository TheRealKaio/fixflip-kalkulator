"""V8.377: keep guest-only redaction masks aligned and inside cost rows."""

from pathlib import Path
import sys

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
script = (site / "content-section-access.js").read_text(encoding="utf-8")
checks = (
    "display:inline-block!important;width:fit-content!important;max-width:100%!important;",
    "background:#252525!important;border-radius:2px!important;",
    "grid-template-columns:minmax(0,1fr) max-content!important;",
    '.cost-row>strong.nic-masked-value{\n justify-self:end!important;',
)
for check in checks:
    if check not in script:
        raise SystemExit("V8.377 missing bounded guest mask rule: " + check)
if 'content:"████"' in script or '.nic-masked-value::after' in script:
    raise SystemExit("V8.377 obsolete glyph-based guest mask remains")
print("V8.377 verified: redaction masks stay aligned within cost rows")
