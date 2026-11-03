"""V8.376: keep guest-only redaction masks aligned and inside cost rows."""

from pathlib import Path
import sys

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
script = (site / "content-section-access.js").read_text(encoding="utf-8")
checks = (
    "display:inline-block!important;width:fit-content!important;max-width:100%!important;",
    'content:""!important;position:absolute;inset:1px 0;z-index:1;display:block!important;',
    "grid-template-columns:minmax(0,1fr) max-content!important;",
    '.cost-row>strong.nic-masked-value{\n justify-self:end!important;',
)
for check in checks:
    if check not in script:
        raise SystemExit("V8.376 missing bounded guest mask rule: " + check)
if 'content:"████"' in script:
    raise SystemExit("V8.376 obsolete glyph-based guest mask remains")
print("V8.376 verified: redaction masks stay aligned within cost rows")
