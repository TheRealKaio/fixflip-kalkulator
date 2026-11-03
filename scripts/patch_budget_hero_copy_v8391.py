"""V8.391: readable budget introduction with unchanged typography."""
from pathlib import Path
import sys
path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")
old="Ermittle aus Einkommen, Ausgaben, Eigenkapital und Finanzierung eine realistische Kaufpreis-Spanne."
new="Berechne, wie viel Immobilie du dir in Deutschland leisten kannst – auf Basis deines Einkommens, deiner Ausgaben, deines Eigenkapitals und deiner Finanzierung."
if old not in html:raise SystemExit("Budget hero description missing")
html=html.replace(old,new)
path.write_text(html,encoding="utf-8")
print("V8.391 budget introduction updated; typography retained")
