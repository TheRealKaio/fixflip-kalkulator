"""Audit all legacy information buttons before switching their presentation.

Build data is extracted from the already assembled calculator shell. Original
calculator scripts and their information content are retained unchanged.
"""
from pathlib import Path
from html.parser import HTMLParser
import html
import json
import re
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else "_site")
source=(site/"index.html").read_text(encoding="utf-8")
rental_patch=Path("scripts/patch_unified_info_ui_v8309.py").read_text(encoding="utf-8")

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[]
    def handle_data(self,part):self.parts.append(part)
def plain(markup):
    p=PlainText();p.feed(markup)
    return " ".join(" ".join(p.parts).split())
def attr(markup,name):
    m=re.search(r'\b'+re.escape(name)+r'="([^"]*)"',markup,re.I)
    return html.unescape(m.group(1)) if m else ""
def slug(value):
    import unicodedata
    v=unicodedata.normalize("NFD",value.lower())
    return re.sub(r"[^a-z0-9]+","-", "".join(c for c in v if not unicodedata.combining(c)).replace("ß","ss")).strip("-")
def trim(text):
    return re.sub(r"\s+"," ",text).strip()
def rental_entries():
    # These strings were supplied by the existing calculator's complete
    # rental help sheets; retain all three sections in the context payload.
    found={}
    rx=re.compile(r'"([^"\n]+)":\s*\{\s*title:\s*"([^"]+)",\s*body:\s*"([^"]+)",\s*plain:\s*"([^"]+)",\s*know:\s*"([^"]+)"\s*\}',re.S)
    for match in rx.finditer(rental_patch):
        title,head,body,simple,more=match.groups()
        if title!=head:raise SystemExit("Rental information heading mismatch: "+title)
        found[title]={"term":title,"body":body,"plain":simple,"know":more,"source":"rental-sheet-v8309"}
    if len(found)!=9:raise SystemExit(f"Expected 9 complete rental help sheets, extracted {len(found)}")
    return found

rental=rental_entries()
legacy=[]
all_buttons=0
for label in re.finditer(r"<label\b[^>]*>(.*?)</label>",source,re.S|re.I):
    markup=label.group(1)
    buttons=list(re.finditer(r"<button\b[^>]*>.*?</button>",markup,re.S|re.I))
    info=[b for b in buttons if re.search(r"\b(?:info-btn|info-dot|inline-info|rent-info-dot)\b",attr(b.group(0),"class"))]
    for button in info:
        all_buttons+=1
        title=trim(plain(markup[:button.start()]+markup[button.end():]))
        opening=button.group(0).split(">",1)[0]+">"
        legacy.append({
            "term":title,
            "dataInfo":attr(opening,"data-info"),
            "ariaLabel":attr(opening,"aria-label"),
            "className":attr(opening,"class"),
            "hasRichSheet":title in rental,
        })

(site/"immobilien-abc-legacy-audit.json").write_text(json.dumps({
    "totalInfoButtons":all_buttons,
    "labelInfoButtons":len(legacy),
    "fullRentalSheets":len(rental),
    "buttons":legacy
},ensure_ascii=False,indent=2)+"\n")
# For the public contextual info we preserve the original information as a
# separate data source even if a glossary entry is edited or deleted.
# Extract the original full four-part information object from the compiled
# Fix & Flip calculator. Unlike a data-info attribute, it contains every
# sentence shown in the original explanatory bottom sheet.
begin=source.find("const info = {")
if begin<0:
    raise SystemExit("Missing legacy Fix & Flip information map")
end=source.find("};",begin)
if end<0:raise SystemExit("Unterminated legacy information map")
part=source[begin:end]
pattern=re.compile(r'([A-Za-z][A-Za-z0-9_]*):\\s*\\{\\s*title:\\s*"([^"]+)",\\s*body:\\s*"([^"]+)",\\s*plain:\\s*"([^"]+)",\\s*know:\\s*"([^"]+)"\\s*\\}',re.S)
full=list(pattern.finditer(part))
if len(full)!=20:
    raise SystemExit(f"Expected 20 complete Fix & Flip information sheets; found {len(full)}")
by_key={item["dataInfo"]:item["term"] for item in legacy if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*",item["dataInfo"])}
context=list(rental.values())
seen={entry["term"].casefold() for entry in context}
for match in full:
    key,title,body,simple,more=match.groups()
    name=by_key.get(key)
    if not name:
        # KPI information is attached to the visible .name element rather
        # than a field label. Never infer the term from the script key.
        pat=r'<button\\b[^>]*data-info="'+re.escape(key)+r'"[^>]*>[^<]*</button>\\s*<div class="name"[^>]*>([^<]+)</div>'
        label=re.search(pat,source,re.S)
        if not label:raise SystemExit("Cannot match legacy KPI information: "+key)
        name=trim(html.unescape(label.group(1)))
    if not name:raise SystemExit("Blank legacy information title for "+key)
    if name.casefold() in seen:raise SystemExit("Duplicate legacy information term: "+name)
    category=("Immobilienkauf" if key=="acquisitionCosts" else
              "Finanzierung" if key in ("interestRate","repaymentRate","financingRatio","financeAcquisitionCosts") else
              "Rechner & Kennzahlen")
    context.append({"term":name,"key":key,"body":body,"plain":simple,"know":more,
                    "category":category,"source":"legacy-info-map"})
    seen.add(name.casefold())
# Preserve older inline tooltip text when no richer information sheet exists.
for button in legacy:
    term=button["term"].strip()
    detail=button["dataInfo"].strip()
    if not term or term.casefold() in seen or len(detail)<40 or re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*",detail):
        continue
    category="Immobilienkauf" if "Kaufnebenkosten" in term else "Finanzierung"
    context.append({"term":term,"body":detail,"plain":"","know":"",
                    "category":category,"source":"field-data-info"})
    seen.add(term.casefold())
(site/"immobilien-abc-context.json").write_text(json.dumps(context,ensure_ascii=False,indent=2)+"\n")
print(f"Legacy info audit: {all_buttons} info controls in labels; {len(rental)} complete structured rental sheets preserved")
for entry in legacy:
    print("Legacy info field:", json.dumps({
        "term":entry["term"],"key":entry["dataInfo"],
        "source":entry["ariaLabel"],"rich":entry["hasRichSheet"]
    },ensure_ascii=False))

