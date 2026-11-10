"""Install the one Admin-driven typography cascade after all calculator builds.

This intentionally edits public generated calculator pages only, never Admin,
print/PDF rendering, calculation formulas, or JavaScript event handlers.
"""
from pathlib import Path
import shutil, re, sys
site=Path(sys.argv[1] if len(sys.argv)>1 else "_site")
name="calculator-typography.css"
source=Path("assets")/name
if not source.is_file():
    raise SystemExit("Central typography stylesheet missing")
shutil.copyfile(source,site/name)
routes=["","budget","eigennutzung","vermietung","fix-flip","finanzierungsrechner","nebenkostenabrechnung","preise","warum-immocheck","ueber-uns","kontakt","anmelden"]
for slug in routes:
    page=site/slug/"index.html"
    if not page.is_file():raise SystemExit(f"Missing calculator: {slug}")
    html=page.read_text(encoding="utf-8")
    # Retire the older cost-chart-only stylesheet; its role lives in central CSS.
    html=re.sub(r'<link\b[^>]*href=["\'][^"\']*cost-breakdown-typography\.css[^"\']*["\'][^>]*>','',html,flags=re.I)
    html=re.sub(r'<link\b[^>]*href=["\'][^"\']*calculator-typography\.css[^"\']*["\'][^>]*>','',html,flags=re.I)
    if html.count("</head>")!=1:raise SystemExit(f"Missing unique head on {slug}")
    html=html.replace("</head>",'<link rel="stylesheet" href="/'+name+'"></head>',1)
    if html.count('href="/'+name+'"')!=1:
        raise SystemExit(f"Duplicate typography stylesheet: {slug}")
    page.write_text(html,encoding="utf-8")
# No copy of the superseded chart typography must be published.
old=site/"cost-breakdown-typography.css"
if old.exists():old.unlink()
stylesheet=(site/name).read_text(encoding="utf-8")
required=["--nic-body-font-family","--nic-body-font-size",
          "--nic-subtext-font-size","--nic-hint-font-size",
          "--nic-h1-font-size","--nic-h2-font-size",
          "--nic-h3-font-size","--nic-h4-font-size"]
assert all(name in stylesheet for name in required)
print("Admin typography consolidated for",len(routes),"calculator paths; redundant cost CSS retired.")
