"""V8.368: calculator numeric inputs display blank instead of zero."""

from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")


def blank_zero_defaults(match):
    tag = match.group(0)
    if re.search(r'\btype\s*=\s*["\'](?:range|radio|checkbox|hidden)["\']', tag, re.I):
        return tag
    numeric = re.search(r'\btype\s*=\s*["\']number["\']', tag, re.I) or re.search(
        r'\binputmode\s*=\s*["\'](?:decimal|numeric)["\']', tag, re.I
    )
    if not numeric:
        return tag
    tag = re.sub(r'\s+value\s*=\s*(["\'])[-+]?0+(?:[.,]0+)?\1', '', tag, flags=re.I)
    tag = re.sub(r'\s+placeholder\s*=\s*(["\'])0(?:[.,]0+)?\1', '', tag, flags=re.I)
    return tag


html = re.sub(r'<input\b[^>]*>', blank_zero_defaults, html, flags=re.I)

script = '<script defer src="/blank-zero-calculator-inputs.js?v=8.368"></script>'
if script not in html:
    if "</head>" not in html:
        raise SystemExit("V8.368 target closing head tag not found")
    html = html.replace("</head>", script + "</head>", 1)

path.write_text(html, encoding="utf-8")
print("V8.368 calculator inputs now display blank for zero values")
