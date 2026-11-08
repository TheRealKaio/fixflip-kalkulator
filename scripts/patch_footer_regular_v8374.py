"""V8.374: ensure calculator and public footer links use regular weight."""

from pathlib import Path
import sys

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
css_path = site / "statistics.css"
css = css_path.read_text(encoding="utf-8")

for selector in (".footer-legal-links a", ".public-footer a"):
    if f"{selector}{{font-weight:700" in css:
        raise SystemExit(f"V8.374 bold footer rule remains: {selector}")

index = (site / "index.html").read_text(encoding="utf-8")
if 'class="footer-version"' in index:
    raise SystemExit("Public footer version must be removed")

print("V8.374 verified: footer links use regular weight and no public version is shown")
