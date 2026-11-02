"""Render the same footer markup on all calculator pages."""
from pathlib import Path
import re
import sys

site = Path(sys.argv[1] if len(sys.argv)>1 else "_site")
pattern = re.compile(r'<footer\b[^>]*class=["\'][^"\']*\bfooter-note\b[^"\']*["\'][^>]*>.*?</footer>',re.I|re.S)
home=(site/"index.html").read_text(encoding="utf-8")
match=pattern.search(home)
if not match:
    raise SystemExit("Main calculator footer missing")
shared=match.group(0)
finance=site/"finanzierungsrechner/index.html"
html=finance.read_text(encoding="utf-8")
updated,n=pattern.subn(lambda _:shared,html,count=1)
if n!=1:
    raise SystemExit("Finance footer missing")
finance.write_text(updated,encoding="utf-8")
print("Finance footer replaced with main calculator footer markup")
