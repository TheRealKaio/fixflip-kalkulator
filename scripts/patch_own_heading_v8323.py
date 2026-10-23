from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
s = p.read_text(encoding="utf-8")
old = '$("heroTitle").innerHTML = budget ? "Wie viel Immobilie<br>kannst du dir leisten?" : "Lohnt sich<br>dieses Objekt?";'
new = '$("heroTitle").innerHTML = budget ? "Wie viel Immobilie<br>kannst du dir leisten?" : own ? "Lohnt sich<br>diese Eigentumswohnung?" : "Lohnt sich<br>dieses Objekt?";'
if s.count(old) != 1:
    raise SystemExit("V8.323 owner-use heading anchor missing or ambiguous")
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("V8.323 owner-use heading updated")
