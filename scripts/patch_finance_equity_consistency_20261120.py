"""Keep financing allocation consistent across the property calculators."""
from pathlib import Path
import sys
import re

path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=path.read_text(encoding="utf-8")

def once(old,new,label):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit(f"Finance equity consistency: {label}: expected once, got {count}")
    s=s.replace(old,new,1)

once(
    "const loan=Math.max(0,financingBase*financingShare-equityUsed);",
    "const loan=Math.max(0,financingBase*financingShare);",
    "rental loan no double deduction"
)
once(
    "const debt = isFlipFinancing ? financePlan.debt : Math.max(0,grossDebt-ownEquityInput);",
    "const debt = isFlipFinancing ? financePlan.debt : Math.max(0,grossDebt);",
    "owner loan no double deduction"
)
start=s.index("function flipFinancingPlan(")
end=s.index("function calculateFlipTargetSale(){",start)
s=s[:start]+r"""function flipFinancingPlan(p,reno,acquisitionCosts,months,requestedDebt){
  const financeAcquisition = $("financeAcquisition")?.checked ?? false;
  const annualInterest = Math.max(0,pct("interest"));
  const annualRepayment = Math.max(0,pct("repayment"));
  const holding = Math.max(0,val("holding")) * Math.max(0,months);
  const projectCostsBeforeInterest = p + reno + acquisitionCosts + holding;
  const project = debt => annuityProjection(debt,annualInterest,annualRepayment,months);
  // Use a normal-sized principal so the projection's half-cent payoff threshold
  // does not bias the interest factor for loans that amortize within the project.
  const interestFactor = project(1000000).totalInterest / 1000000;
  const netLoanFactor = 1 - interestFactor;
  const availableCapital = Math.max(0,val("ownEquityInput"));
  const netFunding = Math.max(0,projectCostsBeforeInterest - availableCapital);
  const solvable = netFunding === 0 || netLoanFactor > 0;
  const debt = netLoanFactor > 0 ? netFunding / netLoanFactor : 0;
  const projection = project(debt);
  const projectEquityNeed = Math.max(0,projectCostsBeforeInterest + projection.totalInterest - debt);
  const selectedLoan = Math.max(0,requestedDebt ?? 0);
  const equityForRequestedDebt = Math.max(0,projectCostsBeforeInterest + project(selectedLoan).totalInterest - selectedLoan);

  return {
    financeAcquisition,
    financingBase:p,
    grossDebt:debt,
    debt,
    projection,
    availableCapital,
    projectEquityNeed,
    equityShortfall:solvable ? 0 : netFunding,
    fullFinanceMode:solvable && availableCapital === 0,
    financingRatioActual:p>0 ? debt/p : 0,
    equityForRequestedDebt,
    interestFactor
  };
}

"""+s[end:]
start=s.index('  if($("financedAmountField") && $("financeFullWarning")){')
end=s.index('  $("acquisitionCostsTotal").textContent',start)
s=s[:start]+s[end:]

start=s.index('  const intFactor = annuityProjection(1,',s.index('function model('))
end=s.index('  const ownUse = ownUsePurchaseLogic',start)
s=s[:start]+r"""  const acquisitionPct = (states[stateEl.value]/100)+pct("notary")+pct("buyBroker");
  const projectBudget = Math.max(0,s*(1-pct("sellBroker"))-targetProfit-fixedOther);
  const budgetLoan = isFlipFinancing ? Math.max(0,projectBudget-financePlan.availableCapital) : 0;
  const budgetInterest = budgetLoan * (financePlan?.interestFactor ?? 0);
  const flipMaxBuy = Math.max(0,(projectBudget-budgetInterest-reno-Math.max(0,holding))/(1+acquisitionPct));
"""+s[end:]

once(
    ": Math.max(0, ownEquityInput);",
    ": Math.min(ownEquityInput, financePlan.projectEquityNeed);",
    "Fix & Flip ROI uses invested equity up to the total project costs"
)
once(
    '"100 % des verfügbaren Eigenkapitals eingesetzt"',
    'eur(m.equity)+" Eigenkapital eingesetzt"',
    "Fix & Flip actual invested equity note"
)

once(
    'const pdfFinancingRatioSuffix = pdfPercent(val("ltv"));',
    'const pdfFinancingRatioSuffix = pdfPercent(currentDealType()==="flip" ? m.financingRatioActual*100 : val("ltv"));',
    "PDF financing ratio uses actual Fix & Flip loan"
)

once(
    'Dein Eigenkapital deckt zuerst den Liquiditätsbedarf des Projekts. Nur der danach verbleibende Betrag reduziert die Kreditsumme.',
    '',
    "remove outdated Fix & Flip equity explanation"
)
once(
    '    financingRatioActual:p>0 ? debt/p : 0,',
    '    debtWithoutEquity:netLoanFactor>0 ? projectCostsBeforeInterest/netLoanFactor : null,\n'
    '    financingRatioActual:p>0 ? debt/p : 0,',
    "reference loan for the equity explanation"
)
once(
    '    equityRemaining:0,',
    '    debtWithoutEquity:isFlipFinancing ? financePlan.debtWithoutEquity : null,',
    "expose the reference loan to the Fix & Flip result"
)
start=s.index('  if($("equityCapitalNote")){')
end=s.index('  if($("equityNeedNote")',start)
s=s[:start]+r"""  if($("equityCapitalNote")){
    const isFlip = currentDealType()==="flip";
    $("equityCapitalNote").classList.toggle("show",isFlip);
    let note = "";
    if(isFlip){
      if(m.debtWithoutEquity === null){
        note = "Bei diesen Zins- und Laufzeitangaben lässt sich die Vollfinanzierung nicht berechnen.";
      }else if(m.equity > 0){
        const reduction = Math.max(0,m.debtWithoutEquity - m.debt);
        const interestSaved = Math.max(0,reduction - m.equity);
        note = "Dein Darlehen sinkt um "+eur(reduction)+". Dein Eigenkapital deckt "+
          eur(m.equity)+" der Projektkosten.";
        if(interestSaved >= 0.5){
          note += " Durch das kleinere Darlehen sparst du zusätzlich rund "+
            eur(interestSaved)+" Zinsen, die du weniger mitfinanzieren musst.";
        }
      }else{
        note = "Ohne Eigenkapital deckt das Darlehen die Projektkosten inklusive Halte- und Zinskosten.";
      }
    }
    $("equityCapitalNeed").textContent = note;
  }
"""+s[end:]

for name in ("syncComparisonOneFromDeal", "median"):
    start=s.index(f"function {name}(")
    end=s.index("\n}",start)+2
    s=s[:start]+s[end:].lstrip("\n")

once(
    '          <div class="finance-full-warning" id="financeFullWarning" hidden></div>\n',
    '',
    "remove retired financing warning"
)
s=re.sub(r"(?m)^(?:#financedAmountField\.finance-full|\.finance-full-warning)[^\n]*\n?", "", s)
s=re.sub(r"(?m)^    (?:equityForFinancing|projectReserveNeed|projectReserveInitial|projectReserveHolding|projectReserveInterest):[^\n]*\n", "", s)

once(
    '    page2Line("Eigenkapital verfügbar", pdfMoney(m.ownEquityInput), true);\n'
    '    page2Line("Projektreserve", pdfMoney(m.projectReserveNeed));\n'
    '    page2Line("Davon zur Kreditreduzierung", pdfMoney(m.equityForFinancing));',
    """    page2Line("Eigenkapital eingesetzt", pdfMoney(m.equity), true);
    if(m.debtWithoutEquity !== null && m.equity > 0){
      const loanReduction = Math.max(0,m.debtWithoutEquity - m.debt);
      page2Line("Darlehensreduzierung", pdfMoney(loanReduction));
      page2Line("Davon eingesparte Zinsen", pdfMoney(Math.max(0,loanReduction - m.equity)));
    }""",
    "align Fix & Flip PDF with the equity explanation"
)

path.write_text(s,encoding="utf-8")
print("Financing equity consistency applied")
