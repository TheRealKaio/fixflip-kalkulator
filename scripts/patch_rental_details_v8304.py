from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Baujahr und Grundstücksgröße direkt unter Wohnfläche / Preis pro m².
anchor='''        <div class="quick-grid">
          <div class="field">
            <label>Wohnfläche</label>
            <div class="input-wrap"><input id="rentArea" inputmode="decimal" value="0"><span class="unit">m²</span></div>
          </div>
          <div class="field">
            <label>Preis pro m²</label>
            <div class="metric-box"><div class="metric-value" id="rentPurchaseSqm">–</div></div>
          </div>
        </div>
'''
insert=anchor+'''
        <div class="quick-grid">
          <div class="field">
            <label>Baujahr</label>
            <div class="input-wrap"><input id="rentBuildYear" inputmode="numeric" value="0"><span class="unit">Jahr</span></div>
          </div>
          <div class="field">
            <label>Grundstücksgröße</label>
            <div class="input-wrap"><input id="rentPlotArea" inputmode="decimal" value="0"><span class="unit">m²</span></div>
          </div>
        </div>
'''
rep(anchor,insert,"rental build year / plot area row")

# Persistenz / Reset der beiden neuen Felder.
rep(
'''    rentPurchase:"0",
    rentArea:"0",
    rentColdRent:"0",''',
'''    rentPurchase:"0",
    rentArea:"0",
    rentBuildYear:"0",
    rentPlotArea:"0",
    rentColdRent:"0",''',
"rental defaults"
)

# 2) Modernisierung: Infotext unter dem Feld, klein und hellgrau.
rep(
'''<label>Modernisierung <span style="font-weight:400">(Anfangsinvestition)</span> <span class="hint">inkl. Puffer</span></label>''',
'''<label>Modernisierung</label>''',
"modernization label"
)
rep(
'''<div class="rent-reno-input-row">
            <div class="input-wrap"><input id="rentRenovation" inputmode="decimal" value="0" readonly><span class="unit">€</span></div>''',
'''<div class="rent-reno-input-row">
            <div class="input-wrap"><input id="rentRenovation" inputmode="decimal" value="0" readonly><span class="unit">€</span></div>''',
"modernization input anchor"
)
# Den Infotext direkt nach der Eingabe-/Plus-Zeile ergänzen.
reno_close='''          </div>
          <div class="reno-inline-panel rent-reno-inline-panel" id="rentRenoPanel">'''
reno_new='''          </div>
          <div class="mini rental-modernization-sub">Anfangsinvestition inklusive Puffer</div>
          <div class="reno-inline-panel rent-reno-inline-panel" id="rentRenoPanel">'''
rep(reno_close,reno_new,"modernization subtitle")

# 3) Vermietungszins in dieselbe Bundesbank-Referenzzinslogik wie Budget/Fix & Flip aufnehmen.
rep(
'''  const mainManual=localStorage.getItem("ff_interest_manual")==="1";
  const budgetManual=localStorage.getItem("ff_budget_interest_manual")==="1";''',
'''  const mainManual=localStorage.getItem("ff_interest_manual")==="1";
  const budgetManual=localStorage.getItem("ff_budget_interest_manual")==="1";
  const rentalManual=localStorage.getItem("ff_rent_interest_manual")==="1";''',
"reference interest manual flags"
)
rep(
'''  if(!mainManual && $("interest")) $("interest").value=value;
  if(!budgetManual && $("budgetInterest")) $("budgetInterest").value=value;
  initializeRepaymentDefaults();''',
'''  if(!mainManual && $("interest")) $("interest").value=value;
  if(!budgetManual && $("budgetInterest")) $("budgetInterest").value=value;
  if(!rentalManual && $("rentInterest")) $("rentInterest").value=value;
  initializeRepaymentDefaults();''',
"reference interest rental assignment"
)
rep(
'''    ["interest","ff_interest_manual"],
    ["budgetInterest","ff_budget_interest_manual"],
    ["repayment","ff_repayment_manual"],''',
'''    ["interest","ff_interest_manual"],
    ["budgetInterest","ff_budget_interest_manual"],
    ["rentInterest","ff_rent_interest_manual"],
    ["repayment","ff_repayment_manual"],''',
"reference interest manual tracking"
)

# 4) Beispiele bei Hausgeld und nicht umlagefähigem Anteil.
rep(
'''<div class="mini">nicht vollständig als Eigentümerkosten angesetzt</div>''',
'''<div class="mini">z. B. Wasser, Heizung, Müllentsorgung · nicht vollständig als Eigentümerkosten angesetzt</div>''',
"housegeld examples"
)
rep(
'''Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet.''',
'''Teil des Hausgeldes, der beim Eigentümer verbleibt und deshalb den monatlichen Cashflow belastet, z. B. Verwalterkosten, Instandhaltung/Instandsetzung und Zuführung zur Erhaltungsrücklage.''',
"non-alloc examples"
)

# Neue Objektdaten auch im Vermietungs-PDF aufführen.
rep(
'''row('Wohnfläche',new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(m.area)+' m²');row('Nettokaltmiete',''',
'''row('Wohnfläche',new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(m.area)+' m²');row('Baujahr',String($r('rentBuildYear')?.value||'–'));row('Grundstücksgröße',new Intl.NumberFormat('de-DE',{maximumFractionDigits:2}).format(Math.max(0,rn('rentPlotArea')))+' m²');row('Nettokaltmiete',''',
"rental pdf property fields"
)

css=r"""
<style id="rental-ui-v8304">
.rental-modernization-sub{
  color:#94a3b8!important;
  font-size:calc(1em - 2px)!important;
  font-weight:400!important;
  margin-top:5px!important;
}
</style>
"""
rep("</head>",css+"\n</head>","head css")

s=s.replace("V8.303","V8.304")
s=s.replace("service-worker.js?v=8.303","service-worker.js?v=8.304")

required=[
  'id="rentBuildYear"',
  'id="rentPlotArea"',
  'Anfangsinvestition inklusive Puffer',
  'id="rental-ui-v8304"',
  '["rentInterest","ff_rent_interest_manual"]',
  'if(!rentalManual && $("rentInterest")) $("rentInterest").value=value;',
  'z. B. Wasser, Heizung, Müllentsorgung',
  'z. B. Verwalterkosten, Instandhaltung/Instandsetzung und Zuführung zur Erhaltungsrücklage',
  "V8.304",
  "service-worker.js?v=8.304"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.304 missing: "+", ".join(missing))

if '(Anfangsinvestition)' in s:
    raise SystemExit("V8.304 old parenthesized modernization subtitle still present")

p.write_text(s,encoding="utf-8")
print("V8.304 rental property fields, modernization hint, reference interest and cost examples applied")
