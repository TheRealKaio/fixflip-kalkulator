from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# --- V8.258: Eigenkapital-Wasserfall für Fix & Flip --------------------------

# Fresh/default project capital starts at zero.
s=s.replace('maxEquity:"100000",','maxEquity:"0",',1)
s=s.replace('<input id="maxEquity" inputmode="decimal" value="100000">',
            '<input id="maxEquity" inputmode="decimal" value="0">',1)

# Financing input is total available equity, not an amount blindly subtracted from debt.
s=s.replace('<span id="equityInputLabel">Eigenkapital eingesetzt</span> <span class="hint" id="equityInputHint">reduziert die Kreditsumme</span>',
            '<span id="equityInputLabel">Eigenkapital</span> <span class="hint" id="equityInputHint">für Finanzierung & Projektreserve</span>',1)
s=s.replace(
    'Das eingesetzte Eigenkapital reduziert direkt die Kreditsumme. Nicht eingesetztes verfügbares Eigenkapital bleibt als Liquiditätsreserve für den Projektverlauf.',
    'Dein Eigenkapital deckt zuerst den Liquiditätsbedarf des Projekts. Nur der danach verbleibende Betrag reduziert die Kreditsumme.',
    1
)

# Add a red warning area directly to financed amount.
replace_once(
'''        <div class="field">
          <label>Finanzierte Summe <span class="hint">automatisch berechnet</span></label>
          <div class="metric-box">
            <div class="metric-value" id="financedAmount">–</div>
          </div>
        </div>''',
'''        <div class="field" id="financedAmountField">
          <label>Finanzierte Summe <span class="hint">automatisch berechnet</span></label>
          <div class="metric-box">
            <div class="metric-value" id="financedAmount">–</div>
          </div>
          <div class="finance-full-warning" id="financeFullWarning" hidden></div>
        </div>''',
    "financed amount warning markup"
)

css_anchor='.metric-box .metric-value{font-size:17px;font-weight:850;margin-top:2px}'
if css_anchor not in s:
    raise SystemExit("financed amount CSS anchor missing")
s=s.replace(
    css_anchor,
    css_anchor+'''\n#financedAmountField.finance-full .metric-box{background:#fdecec;border-color:#e8a0a0;box-shadow:0 0 0 2px rgba(232,160,160,.12)}
#financedAmountField.finance-full .metric-value{color:#b91c1c}
.finance-full-warning{margin-top:7px;padding:8px 10px;border-radius:10px;background:#fdecec;border:1px solid #e8a0a0;color:#b91c1c;font-size:11px;font-weight:800;line-height:1.4}
.finance-full-warning[hidden]{display:none}''',
    1
)

# Shared financing planner. In Fix & Flip it reserves own capital for all cash
# requirements before it uses any surplus to reduce the loan.
helper=r'''
function flipFinancingPlan(p,reno,acquisitionCosts,months){
  const financeAcquisition = $("financeAcquisition") ? $("financeAcquisition").checked : false;
  const equityInput = $("ownEquityInput") ? Math.max(0,val("ownEquityInput")) : 0;
  const availableGoal = $("maxEquity") ? Math.max(0,val("maxEquity")) : 0;
  const availableCapital = equityInput > 0 ? equityInput : availableGoal;
  const holding = Math.max(0,val("holding")) * Math.max(0,months);
  const projectInitialCosts = Math.max(0,p) + Math.max(0,reno) + Math.max(0,acquisitionCosts);
  const annualInterest = Math.max(0,pct("interest"));
  const annualRepayment = Math.max(0,pct("repayment"));
  const ltv = Math.max(0,pct("ltv"));

  // Ohne eigenes Kapital werden Kauf, NK, Sanierung, laufende Kosten und die
  // während der Projektlaufzeit anfallenden Zinsen vollständig kapitalisiert.
  if(availableCapital <= 0){
    const interestFactor = annuityProjection(1,annualInterest,annualRepayment,months).totalInterest;
    const baseBeforeInterest = projectInitialCosts + holding;
    const debt = interestFactor < 0.999999
      ? baseBeforeInterest / Math.max(0.000001,1-interestFactor)
      : baseBeforeInterest;
    const projection = annuityProjection(debt,annualInterest,annualRepayment,months);
    const projectEquityNeed = Math.max(0,projectInitialCosts + holding + projection.totalInterest - debt);
    return {
      financeAcquisition:true,
      financingBase:baseBeforeInterest,
      grossDebt:debt,
      debt,
      projection,
      availableCapital:0,
      requiredReserve:holding + projection.totalInterest,
      reserveInitial:0,
      reserveHolding:0,
      reserveInterest:0,
      equityForFinancing:0,
      projectEquityNeed,
      equityRemaining:0,
      equityShortfall:projectEquityNeed,
      fullFinanceMode:true,
      financingRatioActual:p>0 ? debt/p : 0
    };
  }

  // Mit Eigenkapital bleibt der eingestellte Finanzierungsgrad relevant.
  // Nicht finanzierte Anschaffungskosten + Haltekosten + Zinsen haben Vorrang.
  const financingBase = Math.max(0,p) + Math.max(0,reno) + (financeAcquisition ? Math.max(0,acquisitionCosts) : 0);
  const grossDebt = Math.max(0,financingBase * ltv);
  const mandatoryInitial = Math.max(0,projectInitialCosts - grossDebt);

  let debt=grossDebt;
  let projection=annuityProjection(debt,annualInterest,annualRepayment,months);
  let requiredReserve=mandatoryInitial + holding + projection.totalInterest;
  let equityForFinancing=0;

  // Zinsen hängen von der nach dem Wasserfall verbleibenden Kreditsumme ab.
  // Wenige Iterationen reichen, weil die Beziehung glatt und monoton ist.
  for(let i=0;i<20;i++){
    projection=annuityProjection(debt,annualInterest,annualRepayment,months);
    requiredReserve=mandatoryInitial + holding + projection.totalInterest;
    equityForFinancing=Math.min(grossDebt,Math.max(0,availableCapital-requiredReserve));
    const nextDebt=Math.max(0,grossDebt-equityForFinancing);
    if(Math.abs(nextDebt-debt)<0.01){
      debt=nextDebt;
      break;
    }
    debt=nextDebt;
  }

  projection=annuityProjection(debt,annualInterest,annualRepayment,months);
  requiredReserve=mandatoryInitial + holding + projection.totalInterest;
  equityForFinancing=Math.min(grossDebt,Math.max(0,availableCapital-requiredReserve));
  debt=Math.max(0,grossDebt-equityForFinancing);
  projection=annuityProjection(debt,annualInterest,annualRepayment,months);
  requiredReserve=mandatoryInitial + holding + projection.totalInterest;

  const projectEquityNeed=Math.max(0,projectInitialCosts + holding + projection.totalInterest - debt);
  const equityRemaining=Math.max(0,availableCapital-projectEquityNeed);
  const equityShortfall=Math.max(0,projectEquityNeed-availableCapital);

  return {
    financeAcquisition,
    financingBase,
    grossDebt,
    debt,
    projection,
    availableCapital,
    requiredReserve,
    reserveInitial:mandatoryInitial,
    reserveHolding:holding,
    reserveInterest:projection.totalInterest,
    equityForFinancing,
    projectEquityNeed,
    equityRemaining,
    equityShortfall,
    fullFinanceMode:false,
    financingRatioActual:p>0 ? debt/p : 0
  };
}

'''
anchor='function calculateFlipTargetSale(){'
if helper not in s:
    if anchor not in s:
        raise SystemExit("flip financing helper anchor missing")
    s=s.replace(anchor,helper+anchor,1)

# Target-sale calculation must use the same financing waterfall/interest burden.
old_target='''  const financeAcquisition = $("financeAcquisition") ? $("financeAcquisition").checked : false;
  const financingBase = p + reno + (financeAcquisition ? acquisitionCosts : 0);
  const grossDebt = financingBase * pct("ltv");
  const equityInput = $("ownEquityInput") ? Math.max(0, val("ownEquityInput")) : 0;
  const debt = Math.max(0, grossDebt - equityInput);

  const financingProjection = annuityProjection(
    debt,
    Math.max(0,pct("interest")),
    Math.max(0,pct("repayment")),
    months
  );
  const interest = financingProjection.totalInterest;
  const holding = Math.max(0, val("holding")) * months;'''
new_target='''  const financePlan = flipFinancingPlan(p,reno,acquisitionCosts,months);
  const debt = financePlan.debt;
  const interest = financePlan.projection.totalInterest;
  const holding = Math.max(0, val("holding")) * months;'''
replace_once(old_target,new_target,"target sale financing waterfall")

# Main model: keep Eigennutzung untouched; Fix & Flip gets the waterfall.
old_model='''  const acquisitionCosts = tax + notary + buyBroker;
  const financeAcquisition = $("financeAcquisition") ? $("financeAcquisition").checked : false;
  const financingBase = p + reno + (financeAcquisition ? acquisitionCosts : 0);
  const grossDebt = financingBase*pct("ltv");
  const ownEquityInput = $("ownEquityInput") ? Math.max(0, val("ownEquityInput")) : 0;
  const debt = Math.max(0, grossDebt - ownEquityInput);
  const financingProjection = annuityProjection(
    debt,
    Math.max(0,pct("interest")),
    Math.max(0,pct("repayment")),
    months
  );
  const monthlyPayment = financingProjection.initialInterest;
  const monthlyRepayment = financingProjection.initialRepayment;
  const interest = financingProjection.totalInterest;
  const repayment = financingProjection.totalRepayment;
  const holding = val("holding")*months;'''
new_model='''  const acquisitionCosts = tax + notary + buyBroker;
  const isFlipFinancing = currentDealType()==="flip";
  const financePlan = isFlipFinancing ? flipFinancingPlan(p,reno,acquisitionCosts,months) : null;
  const financeAcquisition = isFlipFinancing
    ? financePlan.financeAcquisition
    : ($("financeAcquisition") ? $("financeAcquisition").checked : false);
  const financingBase = isFlipFinancing
    ? financePlan.financingBase
    : p + reno + (financeAcquisition ? acquisitionCosts : 0);
  const grossDebt = isFlipFinancing ? financePlan.grossDebt : financingBase*pct("ltv");
  const ownEquityInput = isFlipFinancing
    ? financePlan.availableCapital
    : ($("ownEquityInput") ? Math.max(0,val("ownEquityInput")) : 0);
  const debt = isFlipFinancing ? financePlan.debt : Math.max(0,grossDebt-ownEquityInput);
  const financingProjection = isFlipFinancing
    ? financePlan.projection
    : annuityProjection(
        debt,
        Math.max(0,pct("interest")),
        Math.max(0,pct("repayment")),
        months
      );
  const monthlyPayment = financingProjection.initialInterest;
  const monthlyRepayment = financingProjection.initialRepayment;
  const interest = financingProjection.totalInterest;
  const repayment = financingProjection.totalRepayment;
  const holding = val("holding")*months;'''
replace_once(old_model,new_model,"main financing model")

old_equity='''  const equity = currentDealType()==="own"
    ? Math.max(0, initialOwnUseCosts - debt)
    : Math.max(0, total - debt);'''
new_equity='''  const equity = currentDealType()==="own"
    ? Math.max(0, initialOwnUseCosts - debt)
    : financePlan.projectEquityNeed;'''
replace_once(old_equity,new_equity,"project equity need")

# Return derived waterfall values for UI/PDF.
old_return='''    financeAcquisition,financingBase,grossDebt,ownEquityInput,debt,monthlyPayment,interest,monthlyRepayment,repayment,holding,fixedOther,total,
    profit,personalTaxRate,taxOnProfit,profitAfterTax,initialOwnUseCosts,equity,roi,margin,breakEven,safety,maxBuy,'''
new_return='''    financeAcquisition,financingBase,grossDebt,ownEquityInput,debt,monthlyPayment,interest,monthlyRepayment,repayment,holding,fixedOther,total,
    equityForFinancing:isFlipFinancing ? financePlan.equityForFinancing : ownEquityInput,
    projectReserveNeed:isFlipFinancing ? financePlan.requiredReserve : 0,
    projectReserveInitial:isFlipFinancing ? financePlan.reserveInitial : 0,
    projectReserveHolding:isFlipFinancing ? financePlan.reserveHolding : 0,
    projectReserveInterest:isFlipFinancing ? financePlan.reserveInterest : 0,
    equityRemaining:isFlipFinancing ? financePlan.equityRemaining : 0,
    equityShortfall:isFlipFinancing ? financePlan.equityShortfall : 0,
    fullFinanceMode:isFlipFinancing ? financePlan.fullFinanceMode : false,
    financingRatioActual:isFlipFinancing ? financePlan.financingRatioActual : (p>0 ? debt/p : 0),
    profit,personalTaxRate,taxOnProfit,profitAfterTax,initialOwnUseCosts,equity,roi,margin,breakEven,safety,maxBuy,'''
replace_once(old_return,new_return,"model waterfall return")

# Replace V8.257 cap behavior with mirrored input fields.
old_sync='''function syncEquityAllocationToAvailable(){
  if(currentDealType()!=="flip" || !$("ownEquityInput") || !$("maxEquity")) return false;
  const cap=Math.max(0,val("maxEquity"));
  const input=$("ownEquityInput");
  input.max=String(cap);
  const deployed=Math.max(0,val("ownEquityInput"));
  if(deployed<=cap) return false;
  input.value=String(cap);
  localStorage.setItem("ff_flip_equity_input",String(cap));
  localStorage.setItem("ff_ownEquityInput",String(cap));
  return true;
}

["ownEquityInput","maxEquity"].forEach(function(id){
  const el=$(id);
  if(!el) return;
  el.addEventListener("input",function(){
    if(syncEquityAllocationToAvailable()){
      try{ render(); }catch(_err){}
    }
  });
  el.addEventListener("change",function(){
    if(syncEquityAllocationToAvailable()){
      try{ render(); }catch(_err){}
    }
  });
});
syncEquityAllocationToAvailable();'''
new_sync='''let equityCapitalSyncing=false;
function syncEquityAllocationToAvailable(sourceId){
  if(equityCapitalSyncing || currentDealType()!=="flip" || !$("ownEquityInput") || !$("maxEquity")) return false;
  equityCapitalSyncing=true;
  const source=sourceId==="maxEquity" ? $("maxEquity") : $("ownEquityInput");
  const target=sourceId==="maxEquity" ? $("ownEquityInput") : $("maxEquity");
  const value=Math.max(0,parseLocalizedNumber(source.value,false)||0);
  target.value=String(value);
  localStorage.setItem("ff_flip_equity_input",String(value));
  localStorage.setItem("ff_ownEquityInput",String(value));
  localStorage.setItem("ff_maxEquity",String(value));
  localStorage.setItem("ff_flip_maxEquity",String(value));
  equityCapitalSyncing=false;
  return true;
}

["ownEquityInput","maxEquity"].forEach(function(id){
  const el=$(id);
  if(!el) return;
  el.addEventListener("input",function(){
    syncEquityAllocationToAvailable(id);
    try{ render(); }catch(_err){}
  });
  el.addEventListener("change",function(){
    syncEquityAllocationToAvailable(id);
    try{ render(); }catch(_err){}
  });
});'''
replace_once(old_sync,new_sync,"equity field sync")

# Migrate the old 100k default once. Do not preserve a value that was merely the previous default.
load_anchor='''  if($("ownEquityInput")){
    const initialOwn = currentDealType()==="own";
    const equitySaved = localStorage.getItem(initialOwn ? "ff_own_equity_input" : "ff_flip_equity_input");
    if(equitySaved !== null) $("ownEquityInput").value = equitySaved;
  }'''
load_new=load_anchor+'''
  if(currentDealType()==="flip" && localStorage.getItem("ff_equity_waterfall_v8258")!=="1"){
    const entered=Math.max(0,val("ownEquityInput"));
    const available=Math.max(0,val("maxEquity"));
    if(entered<=0 && available===100000){
      $("maxEquity").value="0";
      localStorage.setItem("ff_maxEquity","0");
      localStorage.setItem("ff_flip_maxEquity","0");
    }else if(entered>0){
      $("maxEquity").value=String(entered);
      localStorage.setItem("ff_maxEquity",String(entered));
      localStorage.setItem("ff_flip_maxEquity",String(entered));
    }
    localStorage.setItem("ff_equity_waterfall_v8258","1");
  }'''
replace_once(load_anchor,load_new,"equity default migration")

# Recalculate target sale when either mirrored capital field changes.
s=s.replace(
    '"financeAcquisition","ltv","ownEquityInput","interest","repayment",',
    '"financeAcquisition","ltv","ownEquityInput","maxEquity","interest","repayment",',
    1
)

# Render actual financing ratio + waterfall breakdown.
old_render='''  $("financedAmount").textContent = eur(m.debt);
  $("acquisitionCostsTotal").textContent = eur(m.tax + m.notary + m.buyBroker);'''
new_render='''  $("financedAmount").textContent = eur(m.debt);
  if($("financedAmountField") && $("financeFullWarning")){
    const warn=currentDealType()==="flip" && m.fullFinanceMode && m.p>0;
    $("financedAmountField").classList.toggle("finance-full",warn);
    $("financeFullWarning").hidden=!warn;
    if(warn){
      const ratio=new Intl.NumberFormat("de-DE",{minimumFractionDigits:0,maximumFractionDigits:1}).format(m.financingRatioActual*100);
      $("financeFullWarning").textContent="Achtung: "+ratio+" % Finanzierung – bitte Eigenkapital anpassen!";
    }
  }
  $("acquisitionCostsTotal").textContent = eur(m.tax + m.notary + m.buyBroker);'''
replace_once(old_render,new_render,"financed amount render warning")

old_breakdown='''      const available=Math.max(0,val("maxEquity"));
      const deployed=Math.max(0,m.ownEquityInput||0);
      const additional=Math.max(0,m.equity-deployed);
      const reserve=available-m.equity;
      $("equityCapitalNeed").textContent = showEquityCapitalNote
        ? " Verfügbar: "+eur(available)+" · davon Finanzierung: "+eur(deployed)+" · weiterer Projektbedarf: "+eur(additional)+" · "+(reserve>=0 ? "verbleibende Reserve: "+eur(reserve) : "Fehlbetrag: "+eur(Math.abs(reserve)))
        : "";'''
new_breakdown='''      const available=Math.max(0,m.ownEquityInput||0);
      const reserveNeed=Math.max(0,m.projectReserveNeed||0);
      const toFinance=Math.max(0,m.equityForFinancing||0);
      const remaining=Math.max(0,m.equityRemaining||0);
      const shortfall=Math.max(0,m.equityShortfall||0);
      $("equityCapitalNeed").textContent = showEquityCapitalNote
        ? " Verfügbar: "+eur(available)+" · Projektreserve: "+eur(reserveNeed)+" · davon laufende Kosten: "+eur(m.projectReserveHolding||0)+" · Zinsen: "+eur(m.projectReserveInterest||0)+" · zur Kreditreduzierung: "+eur(toFinance)+" · "+(shortfall>0 ? "Fehlbetrag: "+eur(shortfall) : "Restliquidität: "+eur(remaining))
        : "";'''
replace_once(old_breakdown,new_breakdown,"equity waterfall breakdown")

old_neednote='''  if($("equityNeedNote") && currentDealType()==="flip"){
    const reserve=Math.max(0,val("maxEquity"))-m.equity;
    $("equityNeedNote").textContent = reserve>=0
      ? "Eigenkapitalbedarf · Reserve "+eur(reserve)
      : "Eigenkapitalbedarf · Fehlbetrag "+eur(Math.abs(reserve));
  }'''
new_neednote='''  if($("equityNeedNote") && currentDealType()==="flip"){
    $("equityNeedNote").textContent = m.equityShortfall>0
      ? "Eigenkapitalbedarf · Fehlbetrag "+eur(m.equityShortfall)
      : (m.fullFinanceMode ? "vollständig fremdfinanziert" : "Eigenkapitalbedarf · Restliquidität "+eur(m.equityRemaining));
  }'''
replace_once(old_neednote,new_neednote,"equity KPI note")

# Hard capital test uses the mirrored available capital. Full-finance mode deliberately
# does not fail the capital light; its risk is shown at the financed amount.
s=s.replace(
    'const missEquity = !isOwnUse && m.equity > Math.max(0,maxEquity) + moneyTolerance;',
    'const missEquity = !isOwnUse && !m.fullFinanceMode && m.equityShortfall > moneyTolerance;',
    1
)

# PDF reflects the waterfall instead of the old "eingesetzt" semantics.
s=s.replace('page2Line("Eigenkapital eingesetzt", pdfMoney(m.ownEquityInput), true);',
            'page2Line("Eigenkapital verfügbar", pdfMoney(m.ownEquityInput), true);\n    page2Line("Projektreserve", pdfMoney(m.projectReserveNeed));\n    page2Line("Davon zur Kreditreduzierung", pdfMoney(m.equityForFinancing));',
            1)
s=s.replace('page2Line("Verbleibende Liquiditätsreserve", pdfMoney(val("maxEquity")-m.equity));',
            'page2Line("Verbleibende Liquiditätsreserve", pdfMoney(m.equityRemaining));',1)

# Version bump.
s=s.replace("V8.257","V8.258")
s=s.replace("service-worker.js?v=8.257","service-worker.js?v=8.258")

required=[
  'function flipFinancingPlan(p,reno,acquisitionCosts,months){',
  'const baseBeforeInterest = projectInitialCosts + holding;',
  'baseBeforeInterest / Math.max(0.000001,1-interestFactor)',
  'requiredReserve=mandatoryInitial + holding + projection.totalInterest;',
  'equityForFinancing=Math.min(grossDebt,Math.max(0,availableCapital-requiredReserve));',
  'projectEquityNeed',
  'fullFinanceMode:true',
  'Achtung: "+ratio+" % Finanzierung – bitte Eigenkapital anpassen!',
  'Eigenkapital</span> <span class="hint" id="equityInputHint">für Finanzierung & Projektreserve',
  'maxEquity:"0"',
  'ff_equity_waterfall_v8258',
  'const missEquity = !isOwnUse && !m.fullFinanceMode && m.equityShortfall > moneyTolerance;',
  'page2Line("Projektreserve"',
  'V8.258',
  'service-worker.js?v=8.258'
]
missing=[token for token in required if token not in s]
if missing:
    raise SystemExit("V8.258 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.258 equity waterfall applied")
