from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Layout: Ort des Objekts in eigener voller Zeile.
replace_once(
'''          <div class="field">
            <label>Ort des Objekts</label>
            <div class="input-wrap">
              <select id="budgetState"></select>
            </div>
            <div class="mini" id="budgetStateTaxNote">Grunderwerbsteuer wird zu den Kaufnebenkosten addiert.</div>
          </div>''',
'''          <div class="field budget-state-field">
            <label>Ort des Objekts</label>
            <div class="input-wrap">
              <select id="budgetState"></select>
            </div>
            <div class="mini" id="budgetStateTaxNote">Grunderwerbsteuer wird zu den Kaufnebenkosten addiert.</div>
          </div>''',
"budget state full row"
)

css_anchor='.budget-grid.three{grid-template-columns:repeat(3,minmax(0,1fr))}'
if css_anchor not in s:
    raise SystemExit("budget grid CSS anchor missing")
s=s.replace(
    css_anchor,
    css_anchor+'\n#budgetAssumptionsBody .budget-state-field{grid-column:1/-1}',
    1
)

# 2) Kaufnebenkostenbereich: Notar + Grundbuch, Makler beim Kauf, automatische Summe.
old_block='''          <div class="field">
            <label>Kaufnebenkosten</label>
            <div class="input-wrap"><input id="budgetAncillaryPct" inputmode="decimal" value="12"><span class="unit">%</span></div>
            <div class="mini" id="budgetAncillaryNote">zzgl. Grunderwerbsteuer gemäß Ort des Objekts</div>
          </div>'''
new_block='''          <div class="field">
            <label>Notar + Grundbuch</label>
            <div class="input-wrap"><input id="budgetNotaryPct" inputmode="decimal" value="2.00"><span class="unit">%</span></div>
          </div>
          <div class="field">
            <label>Makler beim Kauf</label>
            <div class="input-wrap"><input id="budgetBuyBrokerPct" inputmode="decimal" value="0.00"><span class="unit">%</span></div>
          </div>
          <div class="field">
            <label>Kaufnebenkosten gesamt</label>
            <div class="input-wrap"><input id="budgetAncillaryPct" inputmode="decimal" value="7.50" readonly aria-readonly="true"><span class="unit">%</span></div>
            <div class="mini" id="budgetAncillaryNote">Grunderwerbsteuer + Notar/Grundbuch + Makler beim Kauf</div>
          </div>'''
replace_once(old_block,new_block,"budget ancillary component fields")

# 3) Neue Felder speichern; das Summenfeld bleibt aus Kompatibilitätsgründen ebenfalls erhalten.
replace_once(
'''"budgetSafetyReserve","budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetAncillaryPct","budgetExtraCostsPct"''',
'''"budgetSafetyReserve","budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetNotaryPct","budgetBuyBrokerPct","budgetAncillaryPct","budgetExtraCostsPct"''',
"budget persist component fields"
)

# 4) Rechenmodell: kein 12-%-Basiswert mehr.
old_model='''  const equity=Math.max(0,budgetVal("budgetEquity"));
  const ancillaryBasePct=Math.max(0,budgetVal("budgetAncillaryPct")/100);
  const budgetStateName=$("budgetState") && states[$("budgetState").value]!==undefined ? $("budgetState").value : "Hamburg";
  const transferTaxPct=Math.max(0,(states[budgetStateName]||0)/100);
  const ancillaryPct=ancillaryBasePct+transferTaxPct;
  const extraCostsPct=Math.max(0,budgetVal("budgetExtraCostsPct")/100);'''
new_model='''  const equity=Math.max(0,budgetVal("budgetEquity"));
  const budgetStateName=$("budgetState") && states[$("budgetState").value]!==undefined ? $("budgetState").value : "Hamburg";
  const transferTaxPct=Math.max(0,(states[budgetStateName]||0)/100);
  const notaryPct=Math.max(0,budgetVal("budgetNotaryPct")/100);
  const buyBrokerPct=Math.max(0,budgetVal("budgetBuyBrokerPct")/100);
  const ancillaryPct=transferTaxPct+notaryPct+buyBrokerPct;
  if($("budgetAncillaryPct")){
    $("budgetAncillaryPct").value=(ancillaryPct*100).toFixed(2);
  }
  const extraCostsPct=Math.max(0,budgetVal("budgetExtraCostsPct")/100);'''
replace_once(old_model,new_model,"budget ancillary sum model")

replace_once(
'''interestPct,repaymentPct,loan,loanMonthlyRate,equity,ancillaryBasePct,transferTaxPct,budgetStateName,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,''',
'''interestPct,repaymentPct,loan,loanMonthlyRate,equity,transferTaxPct,notaryPct,buyBrokerPct,budgetStateName,ancillaryPct,extraCostsPct,allIn,propertyPrice,ancillaryAmount,extraCostsAmount,''',
"budget ancillary return components"
)

# 5) Dynamischer Hinweis zeigt die vollständige Summe.
old_note='''  if($("budgetAncillaryNote")){
    $("budgetAncillaryNote").textContent=
      new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryBasePct*100)
      +" % + "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)
      +" % GrESt = "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)
      +" % gesamt";
  }'''
new_note='''  if($("budgetAncillaryNote")){
    $("budgetAncillaryNote").textContent=
      new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)
      +" % GrESt + "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.notaryPct*100)
      +" % Notar/Grundbuch + "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.buyBrokerPct*100)
      +" % Makler = "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)
      +" % gesamt";
  }'''
replace_once(old_note,new_note,"budget ancillary sum note")

# 6) Neue Komponenten reagieren wie die bisherigen Finanzierungsannahmen.
replace_once(
'''"budgetInterest","budgetRepayment","budgetEquity","budgetAncillaryPct","budgetExtraCostsPct"''',
'''"budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetNotaryPct","budgetBuyBrokerPct","budgetExtraCostsPct"''',
"budget financing assumption ids"
)

# Das automatische Summenfeld ist nicht editierbar; alter Einzel-Input-Listener entfällt.
s=s.replace(
'''if($("budgetAncillaryPct")){
  $("budgetAncillaryPct").addEventListener("input",()=>{
    if(currentDealType()==="budget") renderBudget();
  });
}
''',
'',
1
)

# 7) Reset: Hamburg + 2 % Notar + 0 % Makler; kein 12-%-Standardwert.
old_reset='''  initBudgetState();
  if($("budgetState")) $("budgetState").value="Hamburg";
  if($("budgetAncillaryPct")) $("budgetAncillaryPct").value="12.00";
  if($("budgetExtraCostsPct")) $("budgetExtraCostsPct").value="5.00";'''
new_reset='''  initBudgetState();
  if($("budgetState")) $("budgetState").value="Hamburg";
  if($("budgetNotaryPct")) $("budgetNotaryPct").value="2.00";
  if($("budgetBuyBrokerPct")) $("budgetBuyBrokerPct").value="0.00";
  if($("budgetAncillaryPct")) $("budgetAncillaryPct").value="7.50";
  if($("budgetExtraCostsPct")) $("budgetExtraCostsPct").value="5.00";'''
replace_once(old_reset,new_reset,"budget ancillary reset defaults")

# 8) PDF: Komponenten einzeln und Gesamtsumme.
old_pdf='''  line("Ort des Objekts",m.budgetStateName);
  line("Grunderwerbsteuer",new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)+" %");
  line("Zins p.a.",pdfPercent(budgetVal("budgetInterest")));
  line("Tilgung p.a.",pdfPercent(budgetVal("budgetRepayment")));
  line("Kaufnebenkosten gesamt",new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)+" %");'''
new_pdf='''  line("Ort des Objekts",m.budgetStateName);
  line("Grunderwerbsteuer",new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)+" %");
  line("Notar + Grundbuch",new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.notaryPct*100)+" %");
  line("Makler beim Kauf",new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.buyBrokerPct*100)+" %");
  line("Zins p.a.",pdfPercent(budgetVal("budgetInterest")));
  line("Tilgung p.a.",pdfPercent(budgetVal("budgetRepayment")));
  line("Kaufnebenkosten gesamt",new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)+" %");'''
replace_once(old_pdf,new_pdf,"budget PDF ancillary components")

# 9) Migration alter 12-%-Werte: neue Felder erhalten Defaults, Summe wird danach neu berechnet.
load_anchor='''  budgetChildBenefitManual=localStorage.getItem("ff_budget_childBenefitManual")==="1";'''
load_new='''  if($("budgetNotaryPct") && localStorage.getItem("ff_budget_budgetNotaryPct")===null) $("budgetNotaryPct").value="2.00";
  if($("budgetBuyBrokerPct") && localStorage.getItem("ff_budget_budgetBuyBrokerPct")===null) $("budgetBuyBrokerPct").value="0.00";
  budgetChildBenefitManual=localStorage.getItem("ff_budget_childBenefitManual")==="1";'''
replace_once(load_anchor,load_new,"budget ancillary migration defaults")

# Version bump.
s=s.replace("V8.272","V8.273")
s=s.replace("service-worker.js?v=8.272","service-worker.js?v=8.273")

required=[
    'class="field budget-state-field"',
    '#budgetAssumptionsBody .budget-state-field{grid-column:1/-1}',
    'id="budgetNotaryPct"',
    'value="2.00"',
    'id="budgetBuyBrokerPct"',
    'value="0.00"',
    'id="budgetAncillaryPct" inputmode="decimal" value="7.50" readonly',
    'const ancillaryPct=transferTaxPct+notaryPct+buyBrokerPct;',
    '$("budgetAncillaryPct").value=(ancillaryPct*100).toFixed(2);',
    'Kaufnebenkosten gesamt',
    'V8.273',
    'service-worker.js?v=8.273'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.273 verification failed: "+", ".join(missing))

if 'if($("budgetAncillaryPct")) $("budgetAncillaryPct").value="12.00";' in s:
    raise SystemExit("V8.273 old 12-percent budget ancillary default still present")

path.write_text(s,encoding="utf-8")
print("V8.273 budget ancillary components and layout applied")
