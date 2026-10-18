from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
.own-finance-subtitle{
  margin:6px 0 14px;
  color:#94a3b8;
  font-size:12px;
  line-height:1.45;
  font-weight:400;
}
.own-additional-finance{
  margin-top:16px;
  padding-top:16px;
  border-top:1px solid #e2e8f0;
}
.own-additional-finance h3{
  margin:0 0 10px;
  font-size:14px;
  line-height:1.3;
  color:#172033;
  font-weight:800;
}
.own-additional-finance-grid{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:8px;
}
@media(max-width:720px){
  .own-additional-finance-grid{grid-template-columns:1fr}
}
</style>
"""

js=r"""
<script>
// V8.246 Eigennutzung: weitere Finanzierung berücksichtigen
(function(){
  const financeCard=document.getElementById("ownFinanceCard");
  const financeDetails=financeCard
    ? financeCard.querySelector("details.advanced")
    : null;
  if(!financeDetails) return;

  const summary=financeDetails.querySelector(":scope > summary");
  if(!summary) return;

  let subtitle=document.getElementById("ownFinanceSubtitle");
  if(!subtitle){
    subtitle=document.createElement("p");
    subtitle.id="ownFinanceSubtitle";
    subtitle.className="own-finance-subtitle";
    subtitle.textContent="Trage hier die Bedingungen deiner Finanzierung ein.";
    summary.insertAdjacentElement("afterend",subtitle);
  }

  let additional=document.getElementById("ownAdditionalFinance");
  if(!additional){
    additional=document.createElement("div");
    additional.id="ownAdditionalFinance";
    additional.className="own-additional-finance";
    additional.innerHTML=
      '<h3>Weitere Finanzierung berücksichtigen</h3>'+
      '<div class="own-additional-finance-grid">'+
        '<div class="field">'+
          '<label>Kreditsumme</label>'+
          '<div class="input-wrap"><input id="ownAdditionalLoanAmount" inputmode="decimal" value="0"><span class="unit">€</span></div>'+
        '</div>'+
        '<div class="field">'+
          '<label>Zins p.a.</label>'+
          '<div class="input-wrap"><input id="ownAdditionalLoanInterest" inputmode="decimal" value="0.00"><span class="unit">%</span></div>'+
        '</div>'+
        '<div class="field">'+
          '<label>Tilgung p.a.</label>'+
          '<div class="input-wrap"><input id="ownAdditionalLoanRepayment" inputmode="decimal" value="0.00"><span class="unit">%</span></div>'+
        '</div>'+
      '</div>';
    // Letzte Position: direkt unterhalb der Zeile Makler beim Verkauf / weitere Verkaufskosten.
    financeDetails.appendChild(additional);
  }

  const STORAGE={
    amount:"ff_own_additional_loan_amount",
    interest:"ff_own_additional_loan_interest",
    repayment:"ff_own_additional_loan_repayment"
  };

  function ownAdditionalLoanMetrics(){
    const amount=Math.max(0,val("ownAdditionalLoanAmount"));
    const interestRate=Math.max(0,pct("ownAdditionalLoanInterest"));
    const repaymentRate=Math.max(0,pct("ownAdditionalLoanRepayment"));
    const months=Math.max(0,val("months"));
    const projection=annuityProjection(amount,interestRate,repaymentRate,months);
    return {
      amount,
      interestRate,
      repaymentRate,
      months,
      monthlyInterest:projection.initialInterest,
      monthlyRepayment:projection.initialRepayment,
      total:projection.monthlyAnnuity,
      totalInterest:projection.totalInterest,
      totalRepayment:projection.totalRepayment,
      remainingDebt:projection.remainingDebt
    };
  }
  window.ownAdditionalLoanMetrics=ownAdditionalLoanMetrics;

  // Die weitere Finanzierung wird im Eigennutzungsmodell als zusätzliche
  // Zins- und Tilgungsbelastung geführt. Die Immobilien-Kreditsumme selbst
  // bleibt bewusst unverändert.
  const baseModelAdditionalFinance=model;
  model=function(overrides={}){
    const m=baseModelAdditionalFinance(overrides);
    if(currentDealType()!=="own") return m;
    const extra=ownAdditionalLoanMetrics();
    m.monthlyPayment=(Number(m.monthlyPayment)||0)+extra.monthlyInterest;
    m.monthlyRepayment=(Number(m.monthlyRepayment)||0)+extra.monthlyRepayment;
    m.interest=(Number(m.interest)||0)+extra.totalInterest;
    m.repayment=(Number(m.repayment)||0)+extra.totalRepayment;
    m.total=(Number(m.total)||0)+extra.totalInterest;
    m.ownUseTotalInvestment=(Number(m.ownUseTotalInvestment)||0)+extra.totalInterest;
    m.additionalLoanAmount=extra.amount;
    m.additionalLoanMonthlyInterest=extra.monthlyInterest;
    m.additionalLoanMonthlyRepayment=extra.monthlyRepayment;
    m.additionalLoanInterest=extra.totalInterest;
    m.additionalLoanRepayment=extra.totalRepayment;
    m.additionalLoanRemainingDebt=extra.remainingDebt;
    return m;
  };

  function saveAdditionalLoan(){
    if(!$("ownAdditionalLoanAmount")) return;
    localStorage.setItem(STORAGE.amount,String($("ownAdditionalLoanAmount").value||"0"));
    localStorage.setItem(STORAGE.interest,String($("ownAdditionalLoanInterest").value||"0.00"));
    localStorage.setItem(STORAGE.repayment,String($("ownAdditionalLoanRepayment").value||"0.00"));
  }

  function loadAdditionalLoan(){
    const amount=localStorage.getItem(STORAGE.amount);
    const interest=localStorage.getItem(STORAGE.interest);
    const repayment=localStorage.getItem(STORAGE.repayment);
    if($("ownAdditionalLoanAmount")) $("ownAdditionalLoanAmount").value=amount===null ? "0" : amount;
    if($("ownAdditionalLoanInterest")) $("ownAdditionalLoanInterest").value=interest===null ? "0.00" : interest;
    if($("ownAdditionalLoanRepayment")) $("ownAdditionalLoanRepayment").value=repayment===null ? "0.00" : repayment;
    if(typeof initTwoDecimalPercentFields==="function") initTwoDecimalPercentFields();
  }

  function resetAdditionalLoan(){
    localStorage.removeItem(STORAGE.amount);
    localStorage.removeItem(STORAGE.interest);
    localStorage.removeItem(STORAGE.repayment);
    if($("ownAdditionalLoanAmount")) $("ownAdditionalLoanAmount").value="0";
    if($("ownAdditionalLoanInterest")) $("ownAdditionalLoanInterest").value="0.00";
    if($("ownAdditionalLoanRepayment")) $("ownAdditionalLoanRepayment").value="0.00";
  }

  function updateAdditionalLoanVisibility(){
    let own=false;
    try{ own=currentDealType()==="own"; }catch(_err){}
    subtitle.style.display=own ? "" : "none";
    additional.style.display=own ? "" : "none";
  }

  function updateAdditionalLoanOutputs(m){
    if(currentDealType()!=="own") return;
    const modelNow=m || model();
    const totalCredit=(Number(modelNow.monthlyPayment)||0)+(Number(modelNow.monthlyRepayment)||0);
    const totalMonthly=totalCredit+Math.max(0,val("holding"));

    if($("ownKpiMonthlyCredit")) $("ownKpiMonthlyCredit").textContent=eur(totalCredit);
    if($("ownKpiMonthlyTotal")) $("ownKpiMonthlyTotal").textContent=eur(totalMonthly);

    const creditKpi=$("ownKpiMonthlyCredit") ? $("ownKpiMonthlyCredit").closest(".kpi") : null;
    if(creditKpi){
      const note=creditKpi.querySelector(".note");
      if(note) note.textContent="Immobilienkredit + weitere Finanzierung";
    }
    const totalKpi=$("ownKpiMonthlyTotal") ? $("ownKpiMonthlyTotal").closest(".kpi") : null;
    if(totalKpi){
      const note=totalKpi.querySelector(".note");
      if(note) note.textContent="Kreditraten + laufende Kosten";
    }
  }

  // renderOwnHouseholdBudget erhält durch das erweiterte model() bereits
  // die kombinierte monatliche Zins- und Tilgungsbelastung.

  // Nach jedem normalen Render die kombinierten Werte ausweisen.
  if(typeof render==="function"){
    const baseRenderV8246=render;
    render=function(){
      const result=baseRenderV8246.apply(this,arguments);
      if(currentDealType()==="own") updateAdditionalLoanOutputs(model());
      return result;
    };
  }

  // Reset der Eigennutzung setzt auch die weitere Finanzierung wieder auf 0.
  if(typeof resetDealCalculatorToDefaults==="function"){
    const baseResetDealV8246=resetDealCalculatorToDefaults;
    resetDealCalculatorToDefaults=function(){
      const mode=currentDealType();
      const result=baseResetDealV8246.apply(this,arguments);
      if(mode==="own"){
        resetAdditionalLoan();
        updateAdditionalLoanOutputs(model());
      }
      return result;
    };
  }

  ["ownAdditionalLoanAmount","ownAdditionalLoanInterest","ownAdditionalLoanRepayment"].forEach(function(id){
    const el=$(id);
    if(!el) return;
    const refresh=function(){
      saveAdditionalLoan();
      try{ render(); }catch(_err){ updateAdditionalLoanOutputs(model()); }
    };
    el.addEventListener("input",refresh);
    el.addEventListener("change",refresh);
  });

  document.addEventListener("change",function(event){
    if(!event.target || event.target.name!=="dealType") return;
    setTimeout(function(){
      updateAdditionalLoanVisibility();
      if(currentDealType()==="own"){
        loadAdditionalLoan();
        updateAdditionalLoanOutputs(model());
      }
    },0);
  },true);

  loadAdditionalLoan();
  updateAdditionalLoanVisibility();
  if(currentDealType()==="own") updateAdditionalLoanOutputs(model());
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.246 HTML anchors missing")
s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

# PDF: kombinierte Monatsrate anzeigen.
old_overview='{title:"Monatliche Kreditrate (Zins + Tilgung)", value:pdfMoney(m.monthlyPayment + m.monthlyRepayment), note:"pro Monat", tone:"neutral"},'
new_overview='{title:"Monatliche Kreditrate (Zins + Tilgung)", value:pdfMoney(m.monthlyPayment + m.monthlyRepayment), note:"inkl. weiterer Finanzierung", tone:"neutral"},'
if old_overview not in s:
    raise SystemExit("V8.246 PDF overview monthly credit anchor missing")
s=s.replace(old_overview,new_overview,1)

old_section='if(!isOwnUse) page2Section("Finanzierung & Nebenkosten", 62); else section("Finanzierung & Nebenkosten", 78);'
new_section='if(!isOwnUse) page2Section("Finanzierung & Nebenkosten", 62); else section("Finanzierung & Nebenkosten", 112);'
if old_section not in s:
    raise SystemExit("V8.246 PDF finance section anchor missing")
s=s.replace(old_section,new_section,1)

old_own_finance='''    line("Eigenkapital", pdfMoney(m.ownEquityInput), true);
    lineWithSuffix("Kreditsumme", pdfFinancingRatioSuffix, pdfMoney(m.debt), true);
    line("Monatliche Zinsbelastung", pdfMoney(m.monthlyPayment));
    line("Monatliche Tilgung", pdfMoney(m.monthlyRepayment));
    lineWithSuffix("Monatlich laufende Kosten", "WEG, Energie, Versicherung etc.", pdfMoney(val("holding")), false, false, true);'''
new_own_finance='''    line("Eigenkapital", pdfMoney(m.ownEquityInput), true);
    lineWithSuffix("Kreditsumme", pdfFinancingRatioSuffix, pdfMoney(m.debt), true);
    line("Monatliche Zinsbelastung", pdfMoney(m.monthlyPayment));
    line("Monatliche Tilgung", pdfMoney(m.monthlyRepayment));
    lineWithSuffix("Monatlich laufende Kosten", "WEG, Energie, Versicherung etc.", pdfMoney(val("holding")), false, false, true);
    const additionalLoanPdf=ownAdditionalLoanMetrics();
    line("Weitere Finanzierung - Kreditsumme", pdfMoney(additionalLoanPdf.amount), true);
    line("Weitere Finanzierung - Zins p.a.", pdfPercent(val("ownAdditionalLoanInterest")));
    line("Weitere Finanzierung - Tilgung p.a.", pdfPercent(val("ownAdditionalLoanRepayment")));
    line("Weitere Finanzierung - Monatsrate", pdfMoney(additionalLoanPdf.total), true);
    line("Monatliche Gesamtbelastung", pdfMoney(m.monthlyPayment + m.monthlyRepayment + val("holding")), true);'''
if old_own_finance not in s:
    raise SystemExit("V8.246 PDF own finance detail anchor missing")
s=s.replace(old_own_finance,new_own_finance,1)

s=s.replace("V8.245","V8.246")
s=s.replace("service-worker.js?v=8.245","service-worker.js?v=8.246")

required=[
  'V8.246 Eigennutzung: weitere Finanzierung berücksichtigen',
  'Trage hier die Bedingungen deiner Finanzierung ein.',
  'Weitere Finanzierung berücksichtigen',
  'id="ownAdditionalLoanAmount"',
  'id="ownAdditionalLoanInterest"',
  'id="ownAdditionalLoanRepayment"',
  'const projection=annuityProjection(amount,interestRate,repaymentRate,months);',
  'm.interest=(Number(m.interest)||0)+extra.totalInterest;',
  'm.repayment=(Number(m.repayment)||0)+extra.totalRepayment;',
  'const baseModelAdditionalFinance=model;',
  'Weitere Finanzierung - Monatsrate',
  'Monatliche Gesamtbelastung',
  'V8.246',
  'service-worker.js?v=8.246'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.246 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.246 additional own-use financing applied")
