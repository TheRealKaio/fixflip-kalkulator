from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Modernisierungs-Hinweis optisch wie die übrigen .mini-Infotexte.
old_css='''.rental-modernization-sub{
  color:#94a3b8!important;
  font-size:calc(1em - 2px)!important;
  font-weight:400!important;
  margin-top:5px!important;
}'''
new_css='''.rental-modernization-sub{
  margin-top:5px!important;
}'''
rep(old_css,new_css,"modernization mini style")

# 2) Nicht umlagefähig: ausführliche Beispiele aus dem Info-Kreis entfernen.
rep(
'''Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet, z. B. Verwalterkosten, Instandhaltung/Instandsetzung und Zuführung zur Erhaltungsrücklage.''',
'''Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet.''',
"nonalloc tooltip reset"
)

# Beispiele stattdessen wie beim Hausgeld direkt unter das Eingabefeld setzen.
old_nonalloc='''          <div class="field">
            <label class="label-with-info"><span>Davon nicht umlagefähig</span><button type="button" class="info-dot rent-info-dot" aria-label="Info zu Davon nicht umlagefähig" data-info="Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet.">i</button></label>
            <div class="input-wrap"><input id="rentNonAlloc" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>'''
new_nonalloc='''          <div class="field">
            <label class="label-with-info"><span>Davon nicht umlagefähig</span><button type="button" class="info-dot rent-info-dot" aria-label="Info zu Davon nicht umlagefähig" data-info="Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet.">i</button></label>
            <div class="input-wrap"><input id="rentNonAlloc" inputmode="decimal" value="0"><span class="unit">€</span></div>
            <div class="mini">z. B. Verwalterkosten, Instandhaltung/Instandsetzung, Erhaltungsrücklage</div>
          </div>'''
rep(old_nonalloc,new_nonalloc,"nonalloc field hint")

# 3) Zusätzliche Instandhaltung: Richtwert nur als Vorschlag, kein automatischer Wert.
old_maint='''            <div class="mini">pro Monat · zusätzlich zum nicht umlagefähigen Hausgeld</div>'''
new_maint='''            <div class="mini">pro Monat · zusätzlich zum nicht umlagefähigen Hausgeld</div>
            <div class="mini" id="rentMaintenanceSuggestion">Vorschlag: ca. 1,00 €/m² Wohnfläche/Monat</div>'''
rep(old_maint,new_maint,"maintenance suggestion hint")

# Dynamischen Euro-Vorschlag aus der Wohnfläche anzeigen, ohne das Eingabefeld zu befüllen.
script=r'''
<script id="rental-ui-script-v8305">
(function(){
  const area=document.getElementById("rentArea");
  const target=document.getElementById("rentMaintenanceSuggestion");
  if(!area || !target) return;
  const num=v=>{
    let x=String(v??"").trim().replace(/\s/g,"");
    if(x.includes(",")&&x.includes(".")){
      x=x.lastIndexOf(",")>x.lastIndexOf(".")?x.replace(/\./g,"").replace(",","."):x.replace(/,/g,"");
    }else{
      x=x.replace(",",".");
    }
    x=x.replace(/[^0-9.-]/g,"");
    const n=Number(x);
    return Number.isFinite(n)?n:0;
  };
  const eur=n=>new Intl.NumberFormat("de-DE",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(n);
  const render=()=>{
    const sqm=Math.max(0,num(area.value));
    target.textContent=sqm>0
      ? "Vorschlag: "+eur(sqm)+" / Monat (1,00 €/m²)"
      : "Vorschlag: ca. 1,00 €/m² Wohnfläche/Monat";
  };
  area.addEventListener("input",render);
  render();
})();
</script>
'''
rep("</body>",script+"\n</body>","body script")

s=s.replace("V8.304","V8.305")
s=s.replace("service-worker.js?v=8.304","service-worker.js?v=8.305")

required=[
  'id="rental-ui-script-v8305"',
  'z. B. Verwalterkosten, Instandhaltung/Instandsetzung, Erhaltungsrücklage',
  'id="rentMaintenanceSuggestion"',
  '1,00 €/m²',
  "V8.305",
  "service-worker.js?v=8.305"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.305 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.305 rental hints and maintenance suggestion applied")
