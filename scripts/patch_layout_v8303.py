from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

# 1) Gesamte Contentbreite +10 px
old_width=".app{max-width:630px}"
new_width=".app{max-width:640px}"
if old_width not in s:
    raise SystemExit("Content width anchor missing")
s=s.replace(old_width,new_width,1)

# 2) Anfangsinvestition nicht fett
old='Modernisierung (Anfangsinvestition) <span class="hint">inkl. Puffer</span>'
new='Modernisierung <span style="font-weight:400">(Anfangsinvestition)</span> <span class="hint">inkl. Puffer</span>'
if old not in s:
    raise SystemExit("Modernisierung label anchor missing")
s=s.replace(old,new,1)

s=s.replace("V8.302","V8.303")
s=s.replace("service-worker.js?v=8.302","service-worker.js?v=8.303")

required=[
  'Modernisierung <span style="font-weight:400">(Anfangsinvestition)</span>',
  '.app{max-width:640px}',
  "V8.303",
  "service-worker.js?v=8.303"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.303 missing: "+", ".join(missing))

# Center the renovation amount field and toggle on the same horizontal line.
css = """<style id="renovation-controls-alignment">
.reno-input-row,.rent-reno-input-row{align-items:center}
.reno-input-row>.plus-btn,.rent-reno-input-row>.plus-btn{align-self:center}
</style>"""
if '</head>' not in s:
    raise SystemExit("Head anchor missing for renovation control alignment")
s=s.replace('</head>',css+'\n</head>',1)

p.write_text(s,encoding="utf-8")
print("V8.303 content width and rental label styling applied")
