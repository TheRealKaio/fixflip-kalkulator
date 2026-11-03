from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

style_id = "reno-buffer-row-spacing-v8402"
if style_id in s:
    raise SystemExit("V8.402 spacing patch already present")
required = [
    'id="renoBackdrop"',
    'class="trade-row trade-row-fixed reno-buffer-row"',
    'id="rentRenoPanel"',
    'class="trade-row trade-row-fixed reno-buffer-row rent-reno-buffer-row"',
]
missing = [item for item in required if item not in s]
if missing:
    raise SystemExit("V8.402 renovation buffer rows missing: " + ", ".join(missing))
if "</head>" not in s:
    raise SystemExit("V8.402 HTML head anchor missing")

style = '<style id="' + style_id + '">#renoBackdrop .reno-buffer-row{margin-top:8px!important}#rentRenoPanel .rent-reno-buffer-row{margin-top:8px!important}</style>'
s = s.replace("</head>", style + "</head>", 1)

if style not in s:
    raise SystemExit("V8.402 spacing rule verification failed")

path.write_text(s, encoding="utf-8")
print("V8.402 Eigennutzung, Fix & Flip and Vermietung use the same 8px buffer row gap")
