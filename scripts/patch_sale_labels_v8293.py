from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(label + " anchor missing")
    s = s.replace(old, new, 1)

replace_once(
    '<span>Erwarteter Verkaufspreis</span>',
    '<span>VK Projektziel</span>',
    "expected sale label"
)

replace_once(
    '<span>Break-even-Verkaufspreis</span>',
    '<span>VK Break-even</span>',
    "break-even label"
)

replace_once(
    '<span>Verkaufspreis nach Sanierung</span>',
    '<span>VK nach Sanierung</span>',
    "post-renovation benchmark label"
)

replace_once(
    '<label>Verkaufspreis nach Sanierung <span class="hint">automatisch kalkuliert · editierbar</span></label>',
    '<label>VK nach Sanierung <span class="hint">automatisch kalkuliert · editierbar</span></label>',
    "post-renovation field label"
)

s = s.replace("V8.292", "V8.293")
import re
s = re.sub(r'service-worker\.js\?v=8\.\d+', 'service-worker.js?v=8.293', s)

required = [
    '<span>VK Projektziel</span>',
    '<span>VK Break-even</span>',
    '<span>VK nach Sanierung</span>',
    '<label>VK nach Sanierung <span class="hint">automatisch kalkuliert · editierbar</span></label>',
    'V8.293',
    'service-worker.js?v=8.293'
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit("V8.293 verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.293 sale labels shortened")
