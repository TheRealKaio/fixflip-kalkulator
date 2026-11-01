"""Presentation-only pass after route creation; calculator scripts stay untouched."""
from pathlib import Path
import re
import sys
def run(site):
    for page in Path(site).rglob('*.html'):
        source=page.read_text()
        scripts=re.findall(r"<script\b[^>]*>.*?</script>",source,flags=re.S)
        source=re.sub(r'<svg class="brand-logo".*?</svg>|<img class="brand-logo"[^>]*>',r'<img class="brand-logo" src="/header-logo.png" width="920" height="307" alt="Neustart ImmoCheck – Haus mit vier Fenstern und gelber Welle">',source,flags=re.S)
        source=re.sub(r'<link[^>]*rel="(?:shortcut )?icon"[^>]*>', '', source)
        source=source.replace('</head>','<link rel="icon" type="image/svg+xml" href="/icon.svg"><link rel="icon" type="image/png" sizes="64x64" href="/favicon-64.png"></head>',1)
        if 'rel="apple-touch-icon"' not in source:
            source=source.replace('</head>','<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"></head>',1)
        assert scripts==re.findall(r"<script\b[^>]*>.*?</script>",source,flags=re.S), f"Calculator script changed: {page}"
        page.write_text(source)
if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv)>1 else '_site')
