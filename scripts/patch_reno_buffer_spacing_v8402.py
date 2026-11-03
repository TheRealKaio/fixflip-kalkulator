from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

style_id = "reno-buffer-row-spacing-v8402"
if style_id in s:
    raise SystemExit("V8.402 spacing patch already present")
if 'id="renoBackdrop"' not in s or 'class="trade-row trade-row-fixed reno-buffer-row"' not in s:
    raise SystemExit("V8.402 shared renovation buffer row is missing")
if "</head>" not in s:
    raise SystemExit("V8.402 HTML head anchor missing")

style = '<style id="' + style_id + '">#renoBackdrop .reno-buffer-row{margin-top:8px!important}</style>'
s = s.replace("</head>", style + "</head>", 1)

if style not in s:
    raise SystemExit("V8.402 spacing rule verification failed")

path.write_text(s, encoding="utf-8")
print("V8.402 shared renovation buffer row uses the same 8px row gap")
