from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old_anchor='''  const m = model();
  const isOwnUse = currentDealType()==="own";
  const taxRate = Math.max(0,pct("personalTax"));'''
new_anchor='''  const m = model();
  const isOwnUse = currentDealType()==="own";

  // PDF rechnet die weitere Finanzierung explizit ein. So ist der Bericht
  // unabhängig davon, ob model() zur Laufzeit bereits erweitert wurde.
  const pdfAdditionalLoan = isOwnUse && typeof ownAdditionalLoanMetrics==="function"
    ? ownAdditionalLoanMetrics()
    : {
        amount:0, monthlyInterest:0, monthlyRepayment:0, total:0,
        totalInterest:0, totalRepayment:0
      };
  const pdfModelAlreadyIncludesAdditional = isOwnUse && Object.prototype.hasOwnProperty.call(m,"additionalLoanInterest");
  const pdfMainMonthlyInterest = Math.max(
    0,
    (Number(m.monthlyPayment)||0)
      - (pdfModelAlreadyIncludesAdditional ? pdfAdditionalLoan.monthlyInterest : 0)
  );
  const pdfMainMonthlyRepayment = Math.max(
    0,
    (Number(m.monthlyRepayment)||0)
      - (pdfModelAlreadyIncludesAdditional ? pdfAdditionalLoan.monthlyRepayment : 0)
  );
  const pdfMonthlyInterestTotal = pdfMainMonthlyInterest + pdfAdditionalLoan.monthlyInterest;
  const pdfMonthlyRepaymentTotal = pdfMainMonthlyRepayment + pdfAdditionalLoan.monthlyRepayment;
  const pdfMonthlyCreditTotal = pdfMonthlyInterestTotal + pdfMonthlyRepaymentTotal;
  const pdfMonthlyTotalBurden = pdfMonthlyCreditTotal + Math.max(0,val("holding"));
  const pdfInterestCostsTotal =
    (Number(m.interest)||0)
      + (pdfModelAlreadyIncludesAdditional ? 0 : pdfAdditionalLoan.totalInterest);
  const pdfRepaymentCostsTotal =
    (Number(m.repayment)||0)
      + (pdfModelAlreadyIncludesAdditional ? 0 : pdfAdditionalLoan.totalRepayment);

  const taxRate = Math.max(0,pct("personalTax"));'''
if old_anchor not in s:
    raise SystemExit("V8.249 buildPdf model anchor missing")
s=s.replace(old_anchor,new_anchor,1)

old_overview='{title:"Monatliche Kreditrate (Zins + Tilgung)", value:pdfMoney(m.monthlyPayment + m.monthlyRepayment), note:"inkl. weiterer Finanzierung", tone:"neutral"},'
new_overview='{title:"Monatliche Kreditrate (Zins + Tilgung)", value:pdfMoney(pdfMonthlyCreditTotal), note:"inkl. weiterer Finanzierung", tone:"neutral"},'
if old_overview not in s:
    raise SystemExit("V8.249 overview anchor missing")
s=s.replace(old_overview,new_overview,1)

old_finance='''    line("Eigenkapital", pdfMoney(m.ownEquityInput), true);
    lineWithSuffix("Kreditsumme", pdfFinancingRatioSuffix, pdfMoney(m.debt), true);
    line("Monatliche Zinsbelastung", pdfMoney(m.monthlyPayment));
    line("Monatliche Tilgung", pdfMoney(m.monthlyRepayment));
    lineWithSuffix("Monatlich laufende Kosten", "WEG, Energie, Versicherung etc.", pdfMoney(val("holding")), false, false, true);
    const additionalLoanPdf=ownAdditionalLoanMetrics();
    line("Kreditsumme (Weitere Finanzierung)", pdfMoney(additionalLoanPdf.amount), true);
    line("Monatliche Zinsbelastung (Weitere Finanzierung)", pdfMoney(additionalLoanPdf.monthlyInterest));
    line("Monatliche Tilgung (Weitere Finanzierung)", pdfMoney(additionalLoanPdf.monthlyRepayment));
    line("Monatliche Gesamtbelastung", pdfMoney(m.monthlyPayment + m.monthlyRepayment + val("holding")), true);'''
new_finance='''    line("Eigenkapital", pdfMoney(m.ownEquityInput), true);
    lineWithSuffix("Kreditsumme", pdfFinancingRatioSuffix, pdfMoney(m.debt), true);
    line("Monatliche Zinsbelastung", pdfMoney(pdfMainMonthlyInterest));
    line("Monatliche Tilgung", pdfMoney(pdfMainMonthlyRepayment));
    lineWithSuffix("Monatlich laufende Kosten", "WEG, Energie, Versicherung etc.", pdfMoney(val("holding")), false, false, true);
    line("Kreditsumme (Weitere Finanzierung)", pdfMoney(pdfAdditionalLoan.amount), true);
    line("Monatliche Zinsbelastung (Weitere Finanzierung)", pdfMoney(pdfAdditionalLoan.monthlyInterest));
    line("Monatliche Tilgung (Weitere Finanzierung)", pdfMoney(pdfAdditionalLoan.monthlyRepayment));
    line("Monatliche Gesamtbelastung", pdfMoney(pdfMonthlyTotalBurden), true);'''
if old_finance not in s:
    raise SystemExit("V8.249 own finance block anchor missing")
s=s.replace(old_finance,new_finance,1)

old_costs='''  const interestCosts = m.interest;
  const repaymentCosts = m.repayment;'''
new_costs='''  const interestCosts = isOwnUse ? pdfInterestCostsTotal : m.interest;
  const repaymentCosts = isOwnUse ? pdfRepaymentCostsTotal : m.repayment;'''
if old_costs not in s:
    raise SystemExit("V8.249 cost breakdown anchor missing")
s=s.replace(old_costs,new_costs,1)

s=s.replace("V8.248","V8.249")
s=s.replace("service-worker.js?v=8.248","service-worker.js?v=8.249")

required=[
    'const pdfAdditionalLoan = isOwnUse',
    'const pdfModelAlreadyIncludesAdditional',
    'const pdfMonthlyCreditTotal = pdfMonthlyInterestTotal + pdfMonthlyRepaymentTotal;',
    'const pdfMonthlyTotalBurden = pdfMonthlyCreditTotal + Math.max(0,val("holding"));',
    'const pdfInterestCostsTotal =',
    'const pdfRepaymentCostsTotal =',
    'value:pdfMoney(pdfMonthlyCreditTotal)',
    'line("Monatliche Gesamtbelastung", pdfMoney(pdfMonthlyTotalBurden), true);',
    'const interestCosts = isOwnUse ? pdfInterestCostsTotal : m.interest;',
    'const repaymentCosts = isOwnUse ? pdfRepaymentCostsTotal : m.repayment;',
    'V8.249',
    'service-worker.js?v=8.249'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.249 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.249 explicit Eigennutzung PDF financing totals applied")
