"""Centralize expand controls without altering disclosure behavior."""
from pathlib import Path
import re, sys
site=Path(sys.argv[1] if len(sys.argv)>1 else "_site")
name="calculator-expand-controls.css"
pages=[site/p/"index.html" for p in ("","budget","eigennutzung","vermietung","fix-flip","finanzierungsrechner")]
css="""/* One visual language for the five calculators' expand/collapse controls. */
:root{
  --nic-expand-size:32px;
  --nic-expand-radius:10px;
  --nic-expand-border:#c7d8ff;
  --nic-expand-bg:#edf3ff;
  --nic-expand-ink:#2563eb;
}
body:not(.nic-admin) :is(.plus-btn,.market-check-toggle){
  box-sizing:border-box!important;
  flex:0 0 var(--nic-expand-size)!important;
  width:var(--nic-expand-size)!important;
  height:var(--nic-expand-size)!important;
  min-width:var(--nic-expand-size)!important;
  min-height:var(--nic-expand-size)!important;
  max-width:var(--nic-expand-size)!important;
  max-height:var(--nic-expand-size)!important;
  padding:0!important;
  margin:0!important;
  border:1px solid var(--nic-expand-border)!important;
  border-radius:var(--nic-expand-radius)!important;
  background:var(--nic-expand-bg)!important;
  color:var(--nic-expand-ink)!important;
  font-family:inherit!important;
  font-size:16px!important;
  font-weight:500!important;
  line-height:1!important;
  text-align:center!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  box-shadow:none!important;
  cursor:pointer;
}
body:not(.nic-admin) :is(.own-finance-card,.flip-section-card) details.advanced>summary::after{
  content:"+"!important;
  box-sizing:border-box!important;
  float:none!important;
  flex:0 0 var(--nic-expand-size)!important;
  width:var(--nic-expand-size)!important;
  height:var(--nic-expand-size)!important;
  min-width:var(--nic-expand-size)!important;
  min-height:var(--nic-expand-size)!important;
  margin:0!important;
  padding:0!important;
  border:1px solid var(--nic-expand-border)!important;
  border-radius:var(--nic-expand-radius)!important;
  background:var(--nic-expand-bg)!important;
  color:var(--nic-expand-ink)!important;
  font-family:inherit!important;
  font-size:16px!important;
  font-weight:500!important;
  line-height:1!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  box-shadow:none!important;
}
body:not(.nic-admin) :is(.own-finance-card,.flip-section-card) details.advanced[open]>summary::after{
  content:"−"!important;
}
body:not(.nic-admin) :is(.plus-btn,.market-check-toggle):focus-visible,
body:not(.nic-admin) :is(.own-finance-card,.flip-section-card) details.advanced>summary:focus-visible{
  outline:2px solid var(--nic-expand-ink);
  outline-offset:3px;
}
"""
visual={"width","height","min-width","min-height","max-width","max-height",
        "border","border-top","border-right","border-bottom","border-left",
        "border-width","border-style","border-color","border-radius",
        "background","background-color","color","font-family","font-size",
        "font-weight","line-height","padding","padding-left","padding-right",
        "padding-top","padding-bottom","margin-top","box-shadow","text-align",
        "vertical-align","float","box-sizing","align-items","justify-content",
        "flex","flex-basis","flex-grow","flex-shrink","content"}
target=re.compile(r"\.(?:plus-btn|market-check-toggle)(?![\w-])|"
                  r"\.(?:own-finance-card|flip-section-card)\s+\.advanced(?:\s*\[open\])?\s*>\s*summary::after")
rule=re.compile(r"([^{}]+)\{([^{}]*)\}",re.S)
declaration=re.compile(r"(\s*)([-\w]+)\s*:\s*([^;{}]*)(;|$)",re.S)
removed=0
def clean(value):
    def rewrite(match):
        global removed
        selector=match.group(1)
        if not target.search(selector):return match.group(0)
        if any(not target.search(s) for s in selector.split(",")):return match.group(0)
        def decl(m):
            global removed
            prop=m.group(2).lower()
            val=m.group(3).strip().lower()
            if prop in visual or (prop=="display" and val.startswith(("flex","inline-flex"))):
                removed+=1
                return ""
            return m.group(0)
        body=declaration.sub(decl,match.group(2))
        return selector+"{"+body+"}" if body.strip() else ""
    return rule.sub(rewrite,value)

for page in pages:
    if not page.is_file():raise SystemExit("Missing calculator page: "+str(page))
for path in site.glob("*.css"):
    if path.name==name:continue
    before=path.read_text(encoding="utf-8")
    after=clean(before)
    if after!=before:path.write_text(after,encoding="utf-8")
for path in site.rglob("*.html"):
    before=path.read_text(encoding="utf-8")
    after=re.sub(r"(<style\b[^>]*>)(.*?)(</style>)",
                 lambda m:m[1]+clean(m[2])+m[3],before,flags=re.S|re.I)
    if after!=before:path.write_text(after,encoding="utf-8")
if removed==0:raise SystemExit("No legacy CSS found: refuse unchecked release")
(site/name).write_text(css,encoding="utf-8")
for page in pages:
    html=page.read_text(encoding="utf-8")
    # Use the case-sensitive published route in every navigation tile.
    html=html.replace("/Finanzierungsrechner/", "/finanzierungsrechner/")
    if html.count("</head>")!=1 or name in html:
        raise SystemExit("Duplicate or missing stylesheet anchor: "+str(page))
    html=html.replace("</head>",'<link rel="stylesheet" href="/'+name+'"></head>',1)
    page.write_text(html,encoding="utf-8")
    assert html.count('href="/'+name+'"')==1
    # JavaScript sets glyph/text and aria state; no handler is removed or replaced.
    if re.search(r'<button\b[^>]*class="[^"]*(?:plus-btn|market-check-toggle)[^"]*"[^>]*style="[^"]*!important',html,re.I):
        raise SystemExit("Inline !important would override central styling: "+str(page))
print("Central expand-control CSS: removed",removed,"legacy appearance properties on",len(pages),"calculator pages")
