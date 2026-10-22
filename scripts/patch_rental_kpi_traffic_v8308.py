from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# KPI-Markup: Bewertung rechts neben dem Wert + Infozeichen oben rechts.
old_cash='''          <div class="kpi wide rent-cashflow-kpi">
            <div class="name">Monatlicher Cashflow</div>
            <div class="value" id="rentCashflowResult">–</div>
            <div class="note">nach Mietausfall, Eigentümerkosten, Zins und Tilgung · vor Steuer</div>
          </div>'''
new_cash='''          <div class="kpi wide rent-cashflow-kpi" id="rentCashflowKpi">
            <div class="name rent-kpi-name"><span>Monatlicher Cashflow</span><button type="button" class="info-dot rent-info-dot rent-kpi-info" aria-label="Info zu Monatlicher Cashflow" data-info="Der monatliche Cashflow zeigt die laufende Liquidität nach Mietausfall, nicht umlagefähigen Eigentümerkosten, Verwaltung, Instandhaltung sowie Zins und Tilgung – vor persönlicher Einkommensteuer. Ampel relativ zur Nettokaltmiete: ab +10 % sehr gut, 0 bis unter +10 % positiv, unter 0 bis -10 % angespannt, unter -10 % kritisch. Eine mögliche AfA ist kein Geldzufluss, kann aber den steuerpflichtigen Überschuss mindern und damit das Ergebnis nach Steuer verbessern. Eine mögliche Wertsteigerung der Immobilie erhöht gegebenenfalls das Vermögen, ist aber kein monatlicher Cashflow und nicht garantiert.">i</button></div>
            <div class="rent-kpi-value-row"><div class="value" id="rentCashflowResult">–</div><span class="rent-kpi-rating" id="rentCashflowRating">–</span></div>
            <div class="note">nach Mietausfall, Eigentümerkosten, Zins und Tilgung · vor Steuer</div>
          </div>'''
rep(old_cash,new_cash,"cashflow KPI")

old_factor='''          <div class="kpi">
            <div class="name">Kaufpreisfaktor</div>
            <div class="value" id="rentFactorResult">–</div>
            <div class="note">Kaufpreis ÷ Jahresnettokaltmiete</div>
          </div>'''
new_factor='''          <div class="kpi" id="rentFactorKpi">
            <div class="name rent-kpi-name"><span>Kaufpreisfaktor</span><button type="button" class="info-dot rent-info-dot rent-kpi-info" aria-label="Info zu Kaufpreisfaktor" data-info="Kaufpreisfaktor = Kaufpreis ÷ Jahresnettokaltmiete. Unter 20: sehr gut / Schnäppchen, meist über 5,0 % Bruttomietrendite. 20 bis 25: gut bis solide, etwa 4,0–5,0 %. Über 25 bis 30: mäßig / teuer, etwa 3,3–3,9 %. Über 30: schlecht / sehr teuer, meist unter 3,3 %. Ein niedriger Faktor spricht für höhere laufende Mietrendite. Lage, Zustand, Mietpotenzial, Finanzierung und Wertentwicklung müssen trotzdem separat geprüft werden.">i</button></div>
            <div class="rent-kpi-value-row"><div class="value" id="rentFactorResult">–</div><span class="rent-kpi-rating" id="rentFactorRating">–</span></div>
            <div class="note">Kaufpreis ÷ Jahresnettokaltmiete</div>
          </div>'''
rep(old_factor,new_factor,"factor KPI")

css=r'''
<style id="rental-kpi-traffic-v8308">
.rent-kpi-name{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px}
.rent-kpi-info{margin-left:auto!important;flex:0 0 18px!important}
.rent-kpi-value-row{display:flex;align-items:baseline;justify-content:space-between;gap:10px;min-width:0}
.rent-kpi-value-row .value{min-width:0}
.rent-kpi-rating{font-size:12px;font-weight:700;line-height:1.25;text-align:right;max-width:48%;padding:4px 7px;border-radius:999px;white-space:normal}
#rentCashflowKpi,#rentFactorKpi{transition:border-color .18s ease,background .18s ease}
.rent-grade-green{border-color:#86efac!important;background:#f0fdf4!important}
.rent-grade-lime{border-color:#bef264!important;background:#f7fee7!important}
.rent-grade-orange{border-color:#fdba74!important;background:#fff7ed!important}
.rent-grade-red{border-color:#fca5a5!important;background:#fef2f2!important}
.rent-grade-green .value,.rent-grade-green .rent-kpi-rating{color:#15803d!important}
.rent-grade-lime .value,.rent-grade-lime .rent-kpi-rating{color:#4d7c0f!important}
.rent-grade-orange .value,.rent-grade-orange .rent-kpi-rating{color:#c2410c!important}
.rent-grade-red .value,.rent-grade-red .rent-kpi-rating{color:#b91c1c!important}
.rent-grade-green .rent-kpi-rating{background:#dcfce7}
.rent-grade-lime .rent-kpi-rating{background:#ecfccb}
.rent-grade-orange .rent-kpi-rating{background:#ffedd5}
.rent-grade-red .rent-kpi-rating{background:#fee2e2}
@media(max-width:520px){
  .rent-kpi-value-row{align-items:flex-start}
  .rent-kpi-rating{font-size:11px;max-width:46%}
}
</style>
'''
rep("</head>",css+"\n</head>","head css")

helper=r'''
  function applyRentGrade(cardId,ratingId,grade,label){
    const card=document.getElementById(cardId);
    const rating=document.getElementById(ratingId);
    if(!card || !rating) return;
    ["rent-grade-green","rent-grade-lime","rent-grade-orange","rent-grade-red"].forEach(c=>card.classList.remove(c));
    if(grade) card.classList.add("rent-grade-"+grade);
    rating.textContent=label||"–";
  }

  function renderRentTraffic(m){
    if(m.factor===null || !Number.isFinite(m.factor)){
      applyRentGrade("rentFactorKpi","rentFactorRating","","–");
    }else if(m.factor<20){
      applyRentGrade("rentFactorKpi","rentFactorRating","green","Sehr gut / Schnäppchen");
    }else if(m.factor<=25){
      applyRentGrade("rentFactorKpi","rentFactorRating","lime","Gut bis solide");
    }else if(m.factor<=30){
      applyRentGrade("rentFactorKpi","rentFactorRating","orange","Mäßig / Teuer");
    }else{
      applyRentGrade("rentFactorKpi","rentFactorRating","red","Schlecht / Sehr teuer");
    }

    if(!(m.coldRent>0) || !Number.isFinite(m.monthlyCashflow)){
      applyRentGrade("rentCashflowKpi","rentCashflowRating","","–");
    }else{
      const ratio=m.monthlyCashflow/m.coldRent;
      if(ratio>=0.10){
        applyRentGrade("rentCashflowKpi","rentCashflowRating","green","Sehr gut");
      }else if(ratio>=0){
        applyRentGrade("rentCashflowKpi","rentCashflowRating","lime","Positiv");
      }else if(ratio>=-0.10){
        applyRentGrade("rentCashflowKpi","rentCashflowRating","orange","Angespannt");
      }else{
        applyRentGrade("rentCashflowKpi","rentCashflowRating","red","Kritisch");
      }
    }
  }

'''
rep("  function renderRent(){",helper+"  function renderRent(){","traffic helper")

old_cash_color='''    const cash=document.getElementById("rentCashflowResult");
    if(cash){
      cash.style.color=m.purchase>0 && m.coldRent>0
        ? (m.monthlyCashflow>=0 ? "#15803d" : (m.monthlyCashflow>=-100 ? "#b45309" : "#b91c1c"))
        : "";
    }

    renderDecision(m);'''
new_cash_color='''    renderRentTraffic(m);
    renderDecision(m);'''
rep(old_cash_color,new_cash_color,"old cashflow color logic")

s=s.replace("V8.307","V8.308")
s=s.replace("service-worker.js?v=8.307","service-worker.js?v=8.308")

required=[
  'id="rentCashflowRating"',
  'id="rentFactorRating"',
  'id="rental-kpi-traffic-v8308"',
  'Sehr gut / Schnäppchen',
  'Schlecht / Sehr teuer',
  'Eine mögliche AfA',
  'Eine mögliche Wertsteigerung',
  'const ratio=m.monthlyCashflow/m.coldRent;',
  'renderRentTraffic(m);',
  "V8.308",
  "service-worker.js?v=8.308"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.308 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.308 purchase-factor and cashflow traffic lights applied")
