from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

flip_tab='''        <label class="deal-type-option" for="dealTypeFlip">
          <input type="radio" name="dealType" value="flip" id="dealTypeFlip">
          <span>
            <strong>Fix und Flip</strong>
            <small>Kauf, Sanierung und Verkauf</small>
          </span>
        </label>'''

rent_tab=flip_tab+'''
        <button type="button" class="deal-type-option rent-tab-button" id="dealTypeRent" aria-pressed="false">
          <span class="rent-radio-dot" aria-hidden="true"></span>
          <span class="rent-tab-copy">
            <strong>Vermietung</strong>
            <small>Mietwohnung als Kapitalanlage prüfen</small>
          </span>
        </button>'''
replace_once(flip_tab,rent_tab,"rental tab")

rent_html=r'''
    <div id="rentSection" class="mode-hidden">
      <section class="card">
        <h2>1. Deine Mietwohnung</h2>
        <p class="sub">Trage Kaufpreis, Wohnfläche und die realistisch erzielbare Nettokaltmiete ein.</p>

        <div class="field">
          <label>Kaufpreis <span class="hint">laut Angebot</span></label>
          <div class="input-wrap"><input id="rentPurchase" inputmode="decimal" value="0"><span class="unit">€</span></div>
        </div>

        <div class="quick-grid">
          <div class="field">
            <label>Wohnfläche</label>
            <div class="input-wrap"><input id="rentArea" inputmode="decimal" value="0"><span class="unit">m²</span></div>
          </div>
          <div class="field">
            <label>Preis pro m²</label>
            <div class="metric-box"><div class="metric-value" id="rentPurchaseSqm">–</div></div>
          </div>
        </div>

        <div class="quick-grid">
          <div class="field">
            <label>Nettokaltmiete pro Monat</label>
            <div class="input-wrap"><input id="rentColdRent" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>
          <div class="field">
            <label>Nettokaltmiete pro m²</label>
            <div class="metric-box"><div class="metric-value" id="rentColdRentSqm">–</div></div>
          </div>
        </div>

        <div class="quick-grid">
          <div class="field">
            <label>Bundesland <span class="hint">Ort des Objekts</span></label>
            <select id="rentState"></select>
          </div>
          <div class="field">
            <label>Einmalige Sanierung / Renovierung</label>
            <div class="input-wrap"><input id="rentRenovation" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>2. Laufende Vermietung</h2>
        <p class="sub">Für die Rendite zählen vor allem die Kosten, die dauerhaft bei dir als Eigentümer verbleiben.</p>

        <div class="quick-grid">
          <div class="field">
            <label>Hausgeld gesamt pro Monat</label>
            <div class="input-wrap"><input id="rentHousegeld" inputmode="decimal" value="0"><span class="unit">€</span></div>
            <div class="mini">zur Orientierung · nicht vollständig als Eigentümerkosten angesetzt</div>
          </div>
          <div class="field">
            <label>Davon nicht umlagefähig</label>
            <div class="input-wrap"><input id="rentNonAlloc" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>
        </div>

        <div class="quick-grid">
          <div class="field">
            <label>Mietausfall / Leerstand</label>
            <div class="input-wrap"><input id="rentVacancy" inputmode="decimal" value="2.00"><span class="unit">%</span></div>
          </div>
          <div class="field">
            <label>Verwaltung pro Monat</label>
            <div class="input-wrap"><input id="rentManagement" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>
        </div>

        <div class="quick-grid">
          <div class="field">
            <label>Zusätzliche Instandhaltung</label>
            <div class="input-wrap"><input id="rentMaintenance" inputmode="decimal" value="0"><span class="unit">€</span></div>
            <div class="mini">pro Monat · zusätzlich zum nicht umlagefähigen Hausgeld</div>
          </div>
          <div class="field">
            <label>Sonstige Vermieterkosten</label>
            <div class="input-wrap"><input id="rentOtherCosts" inputmode="decimal" value="0"><span class="unit">€</span></div>
            <div class="mini">pro Monat</div>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>3. Finanzierung und Nebenkosten</h2>
        <p class="sub">Diese Angaben werden ausschließlich für die Vermietungsrechnung gespeichert und verwendet.</p>

        <div class="finance-rate-grid">
          <div class="field">
            <label>Eigenkapital</label>
            <div class="input-wrap"><input id="rentEquity" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>
          <div class="field">
            <label>Zins p.a.</label>
            <div class="input-wrap"><input id="rentInterest" inputmode="decimal" value="4.00"><span class="unit">%</span></div>
          </div>
          <div class="field">
            <label>Tilgung p.a.</label>
            <div class="input-wrap"><input id="rentRepayment" inputmode="decimal" value="1.50"><span class="unit">%</span></div>
          </div>
        </div>

        <div class="quick-grid">
          <div class="field">
            <label>Notar & Grundbuch</label>
            <div class="input-wrap"><input id="rentNotary" inputmode="decimal" value="2.00"><span class="unit">%</span></div>
          </div>
          <div class="field">
            <label>Makler beim Kauf</label>
            <div class="input-wrap"><input id="rentBroker" inputmode="decimal" value="0"><span class="unit">%</span></div>
          </div>
        </div>

        <div class="budget-summary rent-finance-summary">
          <div class="budget-summary-row"><span>Grunderwerbsteuer</span><strong id="rentTransferTaxResult">–</strong></div>
          <div class="budget-summary-row"><span>Kaufnebenkosten gesamt</span><strong id="rentAcquisitionCostsResult">–</strong></div>
          <div class="budget-summary-row"><span>Gesamtinvestition</span><strong id="rentTotalInvestmentResult">–</strong></div>
          <div class="budget-summary-row"><span>Darlehen</span><strong id="rentLoanResult">–</strong></div>
          <div class="budget-summary-row total"><span>Monatliche Kreditrate</span><strong id="rentDebtServiceResult">–</strong></div>
        </div>
      </section>

      <section class="card result-card">
        <div class="decision check" id="rentDecision">
          <div class="light" id="rentDecisionIcon">🏠</div>
          <div>
            <h2 id="rentDecisionTitle">Mietwohnung prüfen</h2>
            <p id="rentDecisionText">Trage Kaufpreis und Nettokaltmiete ein, um die Rentabilität zu bewerten.</p>
          </div>
        </div>

        <div class="kpis rent-kpis">
          <div class="kpi wide rent-cashflow-kpi">
            <div class="name">Monatlicher Cashflow</div>
            <div class="value" id="rentCashflowResult">–</div>
            <div class="note">nach Mietausfall, Eigentümerkosten, Zins und Tilgung · vor Steuer</div>
          </div>

          <div class="kpi">
            <div class="name">Bruttomietrendite</div>
            <div class="value" id="rentGrossYieldResult">–</div>
            <div class="note">Jahresnettokaltmiete ÷ Kaufpreis</div>
          </div>
          <div class="kpi">
            <div class="name">Nettomietrendite</div>
            <div class="value" id="rentNetYieldResult">–</div>
            <div class="note">Nettoertrag vor Finanzierung ÷ Gesamtinvestition</div>
          </div>
          <div class="kpi">
            <div class="name">Rendite auf dein Eigenkapital</div>
            <div class="value" id="rentCashOnCashResult">–</div>
            <div class="note">jährlicher Cashflow ÷ eingesetztes Eigenkapital</div>
          </div>
          <div class="kpi">
            <div class="name">Kaufpreisfaktor</div>
            <div class="value" id="rentFactorResult">–</div>
            <div class="note">Kaufpreis ÷ Jahresnettokaltmiete</div>
          </div>
          <div class="kpi">
            <div class="name">Tilgung / Vermögensaufbau</div>
            <div class="value" id="rentPrincipalResult">–</div>
            <div class="note">rechnerische Tilgung im ersten Jahr</div>
          </div>
          <div class="kpi">
            <div class="name">Break-even-Nettokaltmiete</div>
            <div class="value" id="rentBreakEvenRentResult">–</div>
            <div class="note">notwendige Monatsmiete für Cashflow 0 €</div>
          </div>
        </div>

        <div class="budget-note neutral-note rent-note">
          Hausgeld gesamt dient nur als Orientierung. Für die Renditeberechnung wird der eingetragene nicht umlagefähige Anteil angesetzt. Individuelle Einkommensteuer, Abschreibung, Mietsteigerungen und Wertentwicklung sind in dieser ersten Betrachtung nicht enthalten.
        </div>
      </section>
    </div>

'''

footer_anchor='''    <div class="footer-note">'''
if footer_anchor not in s:
    raise SystemExit("V8.299 footer anchor missing")
s=s.replace(footer_anchor,rent_html+footer_anchor,1)

style=r'''
<style id="rental-calculator-v8299">
.deal-type-row{grid-template-columns:repeat(4,minmax(0,1fr))}
.rent-tab-button{
  font:inherit;
  color:inherit;
  text-align:left;
  appearance:none;
  width:100%;
}
.rent-radio-dot{
  display:block!important;
  width:20px;
  height:20px;
  min-width:20px;
  flex:0 0 20px;
  border:1.5px solid #9aa5b4;
  border-radius:50%;
  background:#fff;
  box-sizing:border-box;
  position:relative;
}
.rent-tab-button.active{border-color:#8fb1ff;background:#eef4ff}
.rent-tab-button.active .rent-radio-dot{border-color:#2563eb}
.rent-tab-button.active .rent-radio-dot:after{
  content:"";
  position:absolute;
  inset:4px;
  border-radius:50%;
  background:#2563eb;
}
.rent-tab-copy{display:flex!important;flex-direction:column!important;min-width:0}
.deal-type-card.rent-mode-active .deal-type-option:has(input[name="dealType"]:checked){
  border-color:#d9dee7;
  background:#fbfcfe;
}
.rent-finance-summary{margin-top:12px}
.rent-cashflow-kpi{background:#f8fafc}
.rent-kpis .value{font-variant-numeric:tabular-nums}
.rent-note{margin-top:14px}
@media(max-width:720px){
  .deal-type-row{grid-template-columns:1fr 1fr}
  .deal-type-option.budget-option{grid-column:auto}
}
@media(max-width:520px){
  #rentSection .quick-grid,
  #rentSection .finance-rate-grid{grid-template-columns:1fr}
}
</style>
'''
if "</head>" not in s:
    raise SystemExit("V8.299 head anchor missing")
s=s.replace("</head>",style+"\n</head>",1)

script=r'''
<script id="rental-calculator-script-v8299">
(function(){
  const PREFIX="ff_rent_";
  const rentSection=document.getElementById("rentSection");
  const rentTab=document.getElementById("dealTypeRent");
  const dealCard=document.querySelector(".deal-type-card");
  const dealContent=document.getElementById("dealCalculatorContent");
  const budgetSection=document.getElementById("budgetSection");
  const heroTitle=document.getElementById("heroTitle");
  const heroText=document.getElementById("heroText");
  const recalc=document.getElementById("recalc");
  const sharePdf=document.getElementById("sharePdf");
  const savePdf=document.getElementById("savePdf");
  if(!rentSection || !rentTab) return;

  let rentActive=false;

  const defaults={
    rentPurchase:"0",
    rentArea:"0",
    rentColdRent:"0",
    rentState:"Hamburg",
    rentRenovation:"0",
    rentHousegeld:"0",
    rentNonAlloc:"0",
    rentVacancy:"2.00",
    rentManagement:"0",
    rentMaintenance:"0",
    rentOtherCosts:"0",
    rentEquity:"0",
    rentInterest:"4.00",
    rentRepayment:"1.50",
    rentNotary:"2.00",
    rentBroker:"0"
  };

  const fieldIds=Object.keys(defaults);

  function numberValue(id){
    const el=document.getElementById(id);
    if(!el) return 0;
    let raw=String(el.value??"").trim().replace(/\s/g,"");
    if(raw.includes(",") && raw.includes(".")){
      raw=raw.lastIndexOf(",")>raw.lastIndexOf(".")
        ? raw.replace(/\./g,"").replace(",",".")
        : raw.replace(/,/g,"");
    }else if(raw.includes(",")){
      raw=raw.replace(",",".");
    }
    raw=raw.replace(/[^0-9.-]/g,"");
    const n=Number(raw);
    return Number.isFinite(n) ? n : 0;
  }

  function pctValue(id){
    return Math.max(0,numberValue(id))/100;
  }

  function euro(n){
    return new Intl.NumberFormat("de-DE",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(Number(n)||0);
  }

  function percent(n){
    if(n===null || !Number.isFinite(n)) return "–";
    return new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(n*100)+" %";
  }

  function saveRent(){
    fieldIds.forEach(function(id){
      const el=document.getElementById(id);
      if(el) localStorage.setItem(PREFIX+id,el.value);
    });
  }

  function loadRent(){
    fieldIds.forEach(function(id){
      const el=document.getElementById(id);
      if(!el) return;
      const saved=localStorage.getItem(PREFIX+id);
      el.value=saved!==null ? saved : defaults[id];
    });
  }

  function clearRent(){
    Object.keys(localStorage).forEach(function(key){
      if(key.startsWith(PREFIX)) localStorage.removeItem(key);
    });
    fieldIds.forEach(function(id){
      const el=document.getElementById(id);
      if(el) el.value=defaults[id];
    });
    localStorage.setItem(PREFIX+"active","1");
    renderRent();
  }

  function initState(){
    const select=document.getElementById("rentState");
    if(!select || select.options.length) return;
    Object.keys(states).forEach(function(name){
      const option=document.createElement("option");
      option.value=name;
      option.textContent=name+" · "+states[name].toFixed(1).replace(".",",")+" %";
      select.appendChild(option);
    });
    select.value="Hamburg";
  }

  function rentModel(){
    const purchase=Math.max(0,numberValue("rentPurchase"));
    const area=Math.max(0,numberValue("rentArea"));
    const coldRent=Math.max(0,numberValue("rentColdRent"));
    const renovation=Math.max(0,numberValue("rentRenovation"));
    const vacancy=Math.min(0.95,Math.max(0,pctValue("rentVacancy")));
    const housegeld=Math.max(0,numberValue("rentHousegeld"));
    const nonAlloc=Math.max(0,numberValue("rentNonAlloc"));
    const management=Math.max(0,numberValue("rentManagement"));
    const maintenance=Math.max(0,numberValue("rentMaintenance"));
    const otherCosts=Math.max(0,numberValue("rentOtherCosts"));
    const equity=Math.max(0,numberValue("rentEquity"));
    const interest=Math.max(0,pctValue("rentInterest"));
    const repayment=Math.max(0,pctValue("rentRepayment"));
    const notary=Math.max(0,pctValue("rentNotary"));
    const broker=Math.max(0,pctValue("rentBroker"));
    const state=document.getElementById("rentState")?.value || "Hamburg";
    const transferRate=(states[state]||0)/100;

    const transferTax=purchase*transferRate;
    const notaryAmount=purchase*notary;
    const brokerAmount=purchase*broker;
    const acquisitionCosts=transferTax+notaryAmount+brokerAmount;
    const totalInvestment=purchase+acquisitionCosts+renovation;
    const equityUsed=Math.min(equity,totalInvestment);
    const loan=Math.max(0,totalInvestment-equityUsed);
    const monthlyInterest=loan*interest/12;
    const monthlyPrincipal=loan*repayment/12;
    const debtService=monthlyInterest+monthlyPrincipal;

    const effectiveMonthlyRent=coldRent*(1-vacancy);
    const ownerMonthlyCosts=nonAlloc+management+maintenance+otherCosts;
    const monthlyCashflow=effectiveMonthlyRent-ownerMonthlyCosts-debtService;

    const annualGrossRent=coldRent*12;
    const annualEffectiveRent=effectiveMonthlyRent*12;
    const noi=annualEffectiveRent-ownerMonthlyCosts*12;
    const grossYield=purchase>0 ? annualGrossRent/purchase : null;
    const netYield=totalInvestment>0 ? noi/totalInvestment : null;
    const cashOnCash=equityUsed>0 ? (monthlyCashflow*12)/equityUsed : null;
    const factor=annualGrossRent>0 ? purchase/annualGrossRent : null;
    const annualPrincipal=monthlyPrincipal*12;
    const breakEvenRent=(1-vacancy)>0 ? (ownerMonthlyCosts+debtService)/(1-vacancy) : null;

    return {
      purchase,area,coldRent,renovation,vacancy,housegeld,nonAlloc,management,maintenance,otherCosts,
      equity,equityUsed,interest,repayment,state,transferTax,notaryAmount,brokerAmount,acquisitionCosts,
      totalInvestment,loan,monthlyInterest,monthlyPrincipal,debtService,effectiveMonthlyRent,
      ownerMonthlyCosts,monthlyCashflow,annualGrossRent,noi,grossYield,netYield,cashOnCash,factor,
      annualPrincipal,breakEvenRent
    };
  }

  function setText(id,text){
    const el=document.getElementById(id);
    if(el) el.textContent=text;
  }

  function renderDecision(m){
    const box=document.getElementById("rentDecision");
    if(!box) return;
    box.classList.remove("go","check","stop");

    let cls="check", icon="🏠", title="Mietwohnung prüfen",
        text="Trage Kaufpreis und Nettokaltmiete ein, um die Rentabilität zu bewerten.";

    if(m.purchase>0 && m.coldRent>0){
      if(m.monthlyCashflow>=0){
        cls="go"; icon="✓"; title="Positiver monatlicher Cashflow";
        text="Die Wohnung trägt ihre laufenden Eigentümer- und Finanzierungskosten rechnerisch und erzeugt einen positiven Cashflow vor Steuer.";
      }else if(m.monthlyCashflow>=-100){
        cls="check"; icon="!"; title="Nahe am monatlichen Break-even";
        text="Der monatliche Cashflow ist leicht negativ. Prüfe Miete, nicht umlagefähige Kosten und Finanzierung besonders genau.";
      }else{
        cls="stop"; icon="×"; title="Negativer monatlicher Cashflow";
        text="Die laufenden Einnahmen decken Eigentümer- und Finanzierungskosten rechnerisch nicht vollständig.";
      }
    }

    box.classList.add(cls);
    setText("rentDecisionIcon",icon);
    setText("rentDecisionTitle",title);
    setText("rentDecisionText",text);
  }

  function renderRent(){
    const m=rentModel();

    setText("rentPurchaseSqm",m.area>0 ? euro(m.purchase/m.area)+" / m²" : "–");
    setText("rentColdRentSqm",m.area>0 ? new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.coldRent/m.area)+" €/m²" : "–");

    setText("rentTransferTaxResult",euro(m.transferTax));
    setText("rentAcquisitionCostsResult",euro(m.acquisitionCosts));
    setText("rentTotalInvestmentResult",euro(m.totalInvestment));
    setText("rentLoanResult",euro(m.loan));
    setText("rentDebtServiceResult",euro(m.debtService));

    setText("rentCashflowResult",euro(m.monthlyCashflow));
    setText("rentGrossYieldResult",percent(m.grossYield));
    setText("rentNetYieldResult",percent(m.netYield));
    setText("rentCashOnCashResult",percent(m.cashOnCash));
    setText("rentFactorResult",m.factor===null ? "–" : new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.factor)+" ×");
    setText("rentPrincipalResult",euro(m.annualPrincipal)+" / Jahr");
    setText("rentBreakEvenRentResult",m.breakEvenRent===null ? "–" : euro(m.breakEvenRent)+" / Monat");

    const cash=document.getElementById("rentCashflowResult");
    if(cash){
      cash.style.color=m.purchase>0 && m.coldRent>0
        ? (m.monthlyCashflow>=0 ? "#15803d" : (m.monthlyCashflow>=-100 ? "#b45309" : "#b91c1c"))
        : "";
    }

    renderDecision(m);
  }

  function setRentMode(active){
    rentActive=!!active;
    rentSection.classList.toggle("mode-hidden",!rentActive);
    rentTab.classList.toggle("active",rentActive);
    rentTab.setAttribute("aria-pressed",rentActive ? "true" : "false");
    if(dealCard) dealCard.classList.toggle("rent-mode-active",rentActive);

    if(rentActive){
      if(dealContent) dealContent.classList.add("mode-hidden");
      if(budgetSection) budgetSection.classList.add("mode-hidden");
      if(heroTitle) heroTitle.innerHTML="Lohnt sich<br>diese Mietwohnung?";
      if(heroText) heroText.textContent="Prüfe Miete, laufende Kosten und Finanzierung. Der Rechner zeigt dir Cashflow, Renditen und die notwendige Break-even-Miete.";
      if(recalc) recalc.textContent="Vermietung neu berechnen";
      if(sharePdf) sharePdf.style.display="none";
      if(savePdf) savePdf.style.display="none";
      localStorage.setItem(PREFIX+"active","1");
      renderRent();
    }else{
      localStorage.removeItem(PREFIX+"active");
      if(sharePdf) sharePdf.style.display="";
      if(savePdf) savePdf.style.display="";
      try{ updateDealTypeUI(); }catch(_err){}
      if(recalc) recalc.textContent=currentDealType()==="budget" ? "Budget neu berechnen" : "Deal neu berechnen";
    }
  }

  initState();
  loadRent();

  fieldIds.forEach(function(id){
    const el=document.getElementById(id);
    if(!el) return;
    ["input","change"].forEach(function(eventName){
      el.addEventListener(eventName,function(){
        saveRent();
        renderRent();
      });
    });
  });

  rentTab.addEventListener("click",function(){
    setRentMode(true);
  });

  document.querySelectorAll('input[name="dealType"]').forEach(function(input){
    input.addEventListener("change",function(){
      if(!input.checked) return;
      setRentMode(false);
    },true);
  });

  if(recalc){
    recalc.addEventListener("click",function(event){
      if(!rentActive) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      const ok=confirm("Möchtest du wirklich alle Eingaben im Vermietungs-Rechner auf die initialen Standardwerte zurücksetzen?");
      if(!ok) return;
      clearRent();
    },true);
  }

  if(localStorage.getItem(PREFIX+"active")==="1"){
    setTimeout(function(){setRentMode(true);},20);
  }else{
    renderRent();
  }
})();
</script>
'''
if "</body>" not in s:
    raise SystemExit("V8.299 body anchor missing")
s=s.replace("</body>",script+"\n</body>",1)

s=s.replace("V8.298","V8.299")
s=s.replace("service-worker.js?v=8.298","service-worker.js?v=8.299")

required=[
  'id="dealTypeRent"',
  '<strong>Vermietung</strong>',
  'id="rentSection"',
  'id="rentColdRent"',
  'id="rentNonAlloc"',
  'id="rentVacancy"',
  'id="rentEquity"',
  'id="rentCashflowResult"',
  'id="rentNetYieldResult"',
  'id="rentCashOnCashResult"',
  'id="rentFactorResult"',
  'id="rentBreakEvenRentResult"',
  'const PREFIX="ff_rent_";',
  'const monthlyCashflow=effectiveMonthlyRent-ownerMonthlyCosts-debtService;',
  'const grossYield=purchase>0 ? annualGrossRent/purchase : null;',
  'const netYield=totalInvestment>0 ? noi/totalInvestment : null;',
  'const cashOnCash=equityUsed>0 ? (monthlyCashflow*12)/equityUsed : null;',
  'const breakEvenRent=(1-vacancy)>0 ? (ownerMonthlyCosts+debtService)/(1-vacancy) : null;',
  'if(key.startsWith(PREFIX)) localStorage.removeItem(key);',
  'V8.299',
  'service-worker.js?v=8.299'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.299 rental calculator verification failed: "+", ".join(missing))

# Guard: rental fields may not reuse the deal calculator's shared IDs.
for forbidden in [
  'id="purchase"', 'id="area"', 'id="holding"', 'id="interest"', 'id="repayment"',
  'id="ownEquityInput"', 'id="state"'
]:
    rent_pos=s.find('id="rentSection"')
    rent_end=s.find('<div class="footer-note">',rent_pos)
    if forbidden in s[rent_pos:rent_end]:
        raise SystemExit("V8.299 rental calculator reuses shared field ID: "+forbidden)

path.write_text(s,encoding="utf-8")
print("V8.299 independent rental calculator added")
