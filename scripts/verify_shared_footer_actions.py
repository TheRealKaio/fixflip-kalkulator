"""Verify shared footer and action classes on the deployed calculator pages."""
from pathlib import Path
import re
import sys
from unify_finance_footer_markup import extract_footer
site=Path(sys.argv[1] if len(sys.argv)>1 else "_site")
home=(site/"index.html").read_text(encoding="utf-8")
finance=(site/"finanzierungsrechner/index.html").read_text(encoding="utf-8")
a,_,_=extract_footer(home)
b,_,_=extract_footer(finance)
if a!=b:
    raise SystemExit("Calculator footers are not identical")
for name,html in (("main",home),("financing",finance)):
    for cls in ('bottom-actions','bottom-primary','bottom-pdf','bottom-save'):
        if not re.search(r'class=["\'][^"\']*\b'+cls+r'\b',html):
            raise SystemExit(f"{name}: missing {cls}")
    if '/calculator-actions.css' not in html:
        raise SystemExit(f"{name}: shared button stylesheet missing")
print("Shared footer markup and action bar classes verified")
