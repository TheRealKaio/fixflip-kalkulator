from html.parser import HTMLParser
from pathlib import Path
import html
import json
import re
import unicodedata

SITE = Path("_site")
ORDER = ["budget", "own", "rent", "flip", "finance"]
LABELS = {
    "budget": "Budget",
    "own": "Eigennutzung",
    "rent": "Vermietung",
    "flip": "Fix & Flip",
    "finance": "Finanzierungsrechner",
}


def slug(value):
    value = value.lower().replace("&", " und ")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:70] or "box"


class CardParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_offsets = [0]
        for match in re.finditer("\n", source):
            self.line_offsets.append(match.end())
        self.stack = []
        self.heading = None
        self.cards = []

    def source_offset(self):
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        cls = attrs.get("class", "").split()
        item = {"tag": tag, "class": cls, "id": attrs.get("id", ""), "start": self.source_offset(), "heading": ""}
        self.stack.append(item)
        if tag == "h2":
            self.heading = {"text": [], "stack": list(self.stack)}

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        if self.heading is not None:
            self.heading["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "h2" and self.heading is not None:
            title = re.sub(r"\s+", " ", " ".join(self.heading["text"])).strip()
            card = next((item for item in reversed(self.heading["stack"][:-1])
                         if item["tag"] in ("section", "div", "article")
                         and "card" in item["class"]
                         and not ({"menu", "deal-type-card"} & set(item["class"]))), None)
            if card and title and not any(x in card["class"] for x in ("nic-admin", "legal-editor-card")):
                card["ancestor_ids"] = [item["id"] for item in self.heading["stack"] if item["id"]]
                card["ancestor_classes"] = [item["class"] for item in self.heading["stack"]]
                card["heading"] = title
                self.cards.append(card)
            self.heading = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                self.stack = self.stack[:i]
                break


def route_for(page, source):
    match = re.search(r'<html\b[^>]*\bdata-nic-page="(budget|own|rent|flip|finance)"', source)
    if match:
        return match.group(1)
    if "finanzierungsrechner" in page.parts:
        return "finance"
    if page == SITE / "index.html":
        return "budget"
    return None


catalog = {}
for page in SITE.rglob("*.html"):
    source = page.read_text(encoding="utf-8")
    route = route_for(page, source)
    if route not in ORDER:
        continue
    parser = CardParser(source)
    parser.feed(source)
    used = {}
    edits = []
    for card in parser.cards:
        is_root = page == SITE / "index.html"
        if is_root and "budgetSection" not in card.get("ancestor_ids", []):
            continue
        # Own-use reveals this card at runtime; its initial mode-hidden class is not an access rule.
        own_price_check = route == "own" and card["id"] == "ownMarketCheckSection"
        if not is_root and not own_price_check and any("mode-hidden" in classes for classes in card.get("ancestor_classes", [])):
            continue
        if route != "flip" and any("flip-section-card" in classes for classes in card.get("ancestor_classes", [])):
            continue
        # Boxes hidden for another calculator are already excluded above.
        title_slug = slug(card["heading"])
        # Keep the original identity when the public heading is renamed.
        aliases = {
            "wieviel-haus-kann-ich-mir-leisten": "deine-mogliche-finanzierung",
            "3-was-kostet-eine-immobilie": "3-annahme-zur-moglichen-finanzierung",
            "3-finanzierung-und-nebenkosten": "3-annahme-zur-moglichen-finanzierung",
            "monatliche-tilgung-und-restschuld": "monatliche-belastung-und-restschuld",
        }
        if route == "budget":
            title_slug = aliases.get(title_slug, title_slug)
        used[title_slug] = used.get(title_slug, 0) + 1
        suffix = "" if used[title_slug] == 1 else f"-{used[title_slug]}"
        key = f"{route}.{title_slug}{suffix}"
        display_title = "2. Kaufpreis-Check" if own_price_check else card["heading"]
        if card["id"] == "result":
            display_title = "Ergebnis und Einschätzung"
        catalog.setdefault(key, {"key": key, "title": display_title, "calculator": route, "calculatorLabel": LABELS[route], "order": len(catalog)})
        start = card["start"]
        end = source.find(">", start)
        opening = source[start:end + 1]
        if "data-nic-content-key=" not in opening:
            edits.append((start, end + 1, opening[:-1] + f' data-nic-content-key="{html.escape(key, quote=True)}">'))
    for start, end, replacement in reversed(edits):
        source = source[:start] + replacement + source[end:]
    page.write_text(source, encoding="utf-8")

# This own-use card is created by patch_own_sections_v8245 at runtime from a details/summary.
# Its identity must exist in the admin catalog before any browser executes that transformation.
finance_key = "own.finanzierung-und-nebenkosten"
price_order = catalog.get("own.kaufpreis-check", {}).get("order", len(catalog))
catalog.setdefault(finance_key, {
    "key": finance_key, "title": "3. Finanzierung und Nebenkosten",
    "calculator": "own", "calculatorLabel": LABELS["own"], "order": price_order + 0.5,
})

ordered = sorted(catalog.values(), key=lambda item: (ORDER.index(item["calculator"]), item["order"]))
for item in ordered:
    item.pop("order", None)
(SITE / "content-sections.json").write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(SITE / "content-section-access.js").write_text(Path("assets/content-section-access.js").read_text(encoding="utf-8"), encoding="utf-8")

for page in SITE.rglob("*.html"):
    source = page.read_text(encoding="utf-8")
    if route_for(page, source) not in ORDER:
        continue
    # Fail closed before JS and database access rules have loaded: no first-paint flash.
    prepaint = '<style id="nic-content-prepaint">html:not(.nic-content-ready) [data-nic-content-key]{visibility:hidden!important}</style>'
    if prepaint not in source:
        if "</head>" not in source:
            raise SystemExit(f"Content access head anchor missing: {page}")
        source = source.replace("</head>", prepaint + "</head>", 1)
    if route_for(page, source) == "budget":
        # The clear button is inserted dynamically. Size its actual shared parent,
        # rather than an assumed CSS class which other generated styles can override.
        width_script = """<script id="nic-budget-action-layout">
(function(){
 function arrange(){
   const green=document.getElementById('budgetApplySuggestions');
   if(!green||!green.parentElement)return;
   const group=green.parentElement;
   group.style.setProperty('display','flex','important');
   const outer=green.closest('#budgetSuggestionActions');
   if(outer){
     outer.style.setProperty('display','flex','important');
     outer.style.setProperty('justify-content','center','important');
     outer.style.setProperty('align-items','center','important');
     outer.style.setProperty('margin-left','auto','important');
     outer.style.setProperty('margin-right','auto','important');
   }
   group.style.setProperty('justify-content','center','important');
   group.style.setProperty('align-items','center','important');
   group.style.setProperty('gap','8px','important');
   group.style.setProperty('box-sizing','border-box','important');
   group.style.setProperty('width','min(100%, 520px)','important');
   group.style.setProperty('max-width','520px','important');
   group.style.setProperty('margin-left','auto','important');
   group.style.setProperty('margin-right','auto','important');
   green.style.setProperty('flex','1 1 auto','important');
   green.style.setProperty('width','auto','important');
   green.style.setProperty('min-width','0','important');
   green.style.setProperty('white-space','nowrap','important');
   Array.from(group.children).filter(el=>el!==green&&el.tagName==='BUTTON').forEach(el=>{
     el.style.setProperty('flex','0 0 36px','important');
     el.style.setProperty('width','36px','important');
   });
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',arrange,{once:true});
 else arrange();
 new MutationObserver(arrange).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>"""
        if 'id="nic-budget-action-layout"' not in source:
            source = source.replace("</body>", width_script + "</body>", 1)
    if route_for(page, source) == "budget":
        reserve_hint = """<script id="nic-reserve-hint-typography">
(function(){
  function update(){
    const size=window.NICSettings?.current?.layout?.subtextSize;
    if(!size)return;
    document.querySelectorAll('p,div,aside,small').forEach(function(el){
      if(el.children.length && Array.from(el.children).some(child=>child.textContent?.includes('Der Finanzierungsreserve wird automatisch')))return;
      if(el.textContent?.includes('Der Finanzierungsreserve wird automatisch aus dem frei verfügbaren Budget')){
        el.style.setProperty('font-size',String(size)+'px','important');
        el.style.setProperty('line-height','1.5','important');
      }
    });
  }
  window.addEventListener('nic-settings-updated',update);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',update,{once:true});else update();
  new MutationObserver(function(records){
    if(records.some(r=>Array.from(r.addedNodes).some(n=>n.nodeType===1&&n.textContent?.includes('Der Finanzierungsreserve wird automatisch'))))update();
  }).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>"""
        if 'id="nic-reserve-hint-typography"' not in source:
            source=source.replace("</body>",reserve_hint+"</body>",1)
    if route_for(page, source) in ("own", "flip"):
        # Capture before calculator listeners are installed so manual typing is not
        # immediately reset by a recalculation. Reuse the existing renovation key.
        modern_script = """<script id="nic-modernization-edit">
(function(){
  var mode=document.documentElement.getAttribute('data-nic-page');
  if(mode!=='own'&&mode!=='flip')return;
  var key='ff_'+mode+'_reno_manual_total';
  function amount(raw){
    var text=String(raw||'').trim().replace(/\\s/g,'');
    if(text.includes(','))text=text.replace(/\\./g,'').replace(',','.');
    var parsed=Number(text);
    return Number.isFinite(parsed)?Math.max(0,parsed):0;
  }
  function unlock(){
    var field=document.getElementById('reno');
    if(!field)return;
    if(field.closest('.nic-content-box-hidden,.nic-content-box-guest-locked'))return field;
    field.readOnly=false;
    field.disabled=false;
    field.removeAttribute('readonly');
    field.removeAttribute('disabled');
    return field;
  }
  document.addEventListener('input',function(event){
    if(event.target.id==='reno'){
      localStorage.setItem(key,String(amount(event.target.value)));
      // The legacy input handlers must not replace the value during typing.
      event.stopImmediatePropagation();
    }else if(event.target.matches('.trade-amount,.trade-area')){
      localStorage.removeItem(key);
    }
  },true);
  document.addEventListener('change',function(event){
    if(event.target.id==='reno')localStorage.setItem(key,String(amount(event.target.value)));
  },true);
  document.addEventListener('click',function(event){
    if(event.target.closest('#applyTradeSuggestions,#resetTrades'))localStorage.removeItem(key);
  },true);
  function ready(){
    var field=unlock();
    if(!field)return;
    var stored=localStorage.getItem(key);
    if(stored!==null)field.value=stored;
    new MutationObserver(unlock).observe(field,{attributes:true,attributeFilter:['readonly','disabled']});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});
  else ready();
})();
</script>"""
        if 'id="nic-modernization-edit"' not in source:
            source = source.replace("</head>", modern_script + "</head>", 1)
    # Visual-only normalization of zero monetary amounts. Calculators continue to
    # interpret blank fields as numeric zero; count/select/percentage fields are excluded.
    zero_script = """<script id="nic-empty-zero-amounts">
(function(){
 'use strict';
 const excluded=/adults|children|kids|persons|people|guests|count|quantity|number|units|years|months|period|term|duration|age|zins|interest|repay|tilgung|percent|pct|quote|faktor/i;
 const numberZero=/^[+-]?(?:0+(?:[.,]0+)?|[.,]0+)$/;
 function allowed(el){
   if(!(el instanceof HTMLInputElement))return false;
   if(el.disabled||el.readOnly||['hidden','checkbox','radio','range','date','email','password','search'].includes(el.type))return false;
   const wrap=el.closest('.input-wrap,.field,.budget-expense-row,.rent-field,.form-group');
   const unit=wrap?.querySelector('.unit')?.textContent?.trim()||'';
   const name=(el.id||'')+' '+(el.name||'');
   // A unit marker wins over a naming convention. Monetary inputs in Vermietung
   // often have no inputmode and are otherwise missed by the old heuristic.
   if(unit.includes('€'))return true;
   if(unit.includes('%')||/^(?:Jahre?|Monate?|Personen?|Stk\\.?|m²)$/i.test(unit))return false;
   if(/adults|children|kids|persons|people|guests|count|quantity|number|units|years|months|period|term|duration|age|zins|interest|repay|tilgung|percent|pct|quote|faktor/i.test(name))return false;
   if(!['text','number','tel'].includes(el.type))return false;
   const label=el.labels?.[0]?.textContent||wrap?.querySelector('label')?.textContent||'';
   if(/€|Euro|EUR|Miete|Kosten|Betrag|Preis|Hausgeld|Instandhaltung|Rücklage|Nebenkosten|Cashflow|Darlehen|Kredit|Eigenkapital/i.test(label))return true;
   return /income|expense|cost|price|equity|loan|reno|modern|budget|rent|miete|kauf|verkauf|cash|reserve|fee|amount|betrag|salary|saving|puffer|holding|trade/i.test(name);
 }
 function normalize(el){
   if(!allowed(el)||document.activeElement===el)return;
   if(numberZero.test(el.value.trim()))el.value='';
 }
 function sweep(){document.querySelectorAll('input').forEach(normalize);}
 document.addEventListener('input',e=>{if(allowed(e.target)&&numberZero.test(e.target.value.trim())){ /* keep editable during typing */ }},true);
 document.addEventListener('change',e=>{if(allowed(e.target)&&numberZero.test(e.target.value.trim()))e.target.value='';},false);
 document.addEventListener('focusout',e=>normalize(e.target),false);
 document.addEventListener('click',e=>{
   if(e.target.closest('button,[role=button],input[type=reset]')){
     setTimeout(sweep,0);setTimeout(sweep,80);setTimeout(sweep,350);
   }
 },true);
 const observer=new MutationObserver(records=>{
   if(records.some(r=>r.addedNodes.length))requestAnimationFrame(sweep);
 });
 observer.observe(document.body||document.documentElement,{childList:true,subtree:true});
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',sweep,{once:true});
 else sweep();
 window.addEventListener('pageshow',sweep);
 // Calculation scripts update input.value programmatically, not DOM attributes.
 // A lightweight periodic check also catches reset and restore after async renders.
 setInterval(()=>{if(!document.hidden)sweep();},700);
})();
</script>"""
    if 'id="nic-empty-zero-amounts"' not in source:
        source=source.replace("</body>",zero_script+"</body>",1)
    # Classify the actual hint in HTML during build; no DOM text walker or timing dependency.
    income_phrase = "Grundlage ist dein tatsächlich verfügbares monatliches Haushaltsnettoeinkommen."
    if income_phrase in source:
        text_pos = source.index(income_phrase)
        tag_start = source.rfind("<", 0, text_pos)
        tag_end = source.find(">", tag_start)
        tag = source[tag_start:tag_end + 1]
        if not tag.startswith("<script") and "class=" in tag:
            tag = re.sub(r'\b(sub|mini|hint)\b', '', tag)
            tag = re.sub(r'class="([^"]*)"', lambda m: 'class="' + m.group(1).strip() + ' nic-household-net-income-guidance"', tag, count=1)
            source = source[:tag_start] + tag + source[tag_end + 1:]
        else:
            raise SystemExit("Household income hint markup not safely identifiable")
    # Remove obsolete paired bottom reset/apply controls, not unrelated apply buttons.
    remove_buttons = """<script id="nic-remove-obsolete-reset-apply">
(function(){
  function removePair(){
    document.querySelectorAll('button').forEach(function(red){
      if(red.textContent.trim()!=='Auf 0 zurücksetzen')return;
      const group=red.parentElement;
      if(!group)return;
      const green=Array.from(group.children).find(function(el){
        return el.tagName==='BUTTON'&&el.textContent.trim()==='Übernehmen';
      });
      if(!green)return;
      red.remove();green.remove();
      if(!group.children.length)group.remove();
    });
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',removePair,{once:true});
  else removePair();
  new MutationObserver(function(records){
    if(records.some(r=>r.addedNodes.length))removePair();
  }).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>"""
    if 'id="nic-remove-obsolete-reset-apply"' not in source:
        source=source.replace("</body>",remove_buttons+"</body>",1)
    if "content-section-access.js" not in source:
        if "</body>" not in source:
            raise SystemExit(f"Content access body anchor missing: {page}")
        source = source.replace("</body>", '<script defer src="/content-section-access.js"></script></body>', 1)
    page.write_text(source, encoding="utf-8")

print(f"Generated controls for {len(ordered)} H2 content boxes")
