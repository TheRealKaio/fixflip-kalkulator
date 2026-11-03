from pathlib import Path
import re

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

old_sale_lines='''  (!isOwnUse ? page2Line : line)("Makler Verkauf", pdfMoney(m.sellBroker));
  (!isOwnUse ? page2Line : line)("Weitere Kosten bei Verkauf", pdfMoney(m.fixedOther));'''
new_sale_lines='''  if(!isOwnUse){
    page2Line("Makler Verkauf", pdfMoney(m.sellBroker));
    page2Line("Weitere Kosten bei Verkauf", pdfMoney(m.fixedOther));
  }'''
if old_sale_lines not in s:
    raise SystemExit("V8.249 sale-cost PDF rows anchor missing")
s=s.replace(old_sale_lines,new_sale_lines,1)

old_calculator_costs='''  const calculatorSellingCosts = m.sellBroker + m.fixedOther;
  const calculatorSellingLabel = isOwnUse ? "Verkaufskosten (nur bei Verkauf)" : "Verkaufskosten";
  const costs=[
    ["Kaufpreis",m.p],["Kaufnebenkosten",m.tax+m.notary+m.buyBroker],
    ["Sanierung inkl. Puffer",m.reno],["Zinskosten",m.interest],["Tilgung (reduziert Restschuld)",m.repayment],
    ["Laufende Kosten",m.holding],[calculatorSellingLabel,calculatorSellingCosts]
  ];'''
new_calculator_costs='''  const calculatorSellingCosts = m.sellBroker + m.fixedOther;
  const costs=[
    ["Kaufpreis",m.p],["Kaufnebenkosten",m.tax+m.notary+m.buyBroker],
    ["Sanierung inkl. Puffer",m.reno],["Zinskosten",m.interest],["Tilgung (reduziert Restschuld)",m.repayment],
    ["Laufende Kosten",m.holding]
  ];
  if(!isOwnUse) costs.push(["Verkaufskosten",calculatorSellingCosts]);'''
if old_calculator_costs not in s:
    raise SystemExit("V8.249 calculator sale-cost row anchor missing")
s=s.replace(old_calculator_costs,new_calculator_costs,1)

# The visible source label can include an explanatory suffix. Preserve that label
# for Fix & Flip and remove the row from Eigennutzung reports.
cost_rows_match=re.search(r"  const costRows = \[([\s\S]*?)\n  \];",s)
if not cost_rows_match:
    raise SystemExit("V8.249 costRows array anchor missing")
sale_row_pattern=re.compile(r'(?m)^([ \t]*)\["(Verkaufskosten(?: \(nur bei Verkauf\))?)",\s*sellingCosts\](,?)\s*$')
sale_rows=list(sale_row_pattern.finditer(cost_rows_match.group(1)))
if len(sale_rows)!=1:
    raise SystemExit("V8.249 expected one sale-cost chart row, found "+str(len(sale_rows)))
sale_label=sale_rows[0].group(2)
clean_rows=sale_row_pattern.sub("",cost_rows_match.group(1),count=1)
new_cost_rows=(
  "  const costRows = ["+clean_rows+"\n  ];"
  + '\n  if(!isOwnUse) costRows.push(["'+sale_label+'", sellingCosts]);'
)
s=s[:cost_rows_match.start()]+new_cost_rows+s[cost_rows_match.end():]

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
    'if(!isOwnUse){',
    'page2Line("Makler Verkauf", pdfMoney(m.sellBroker));',
    'page2Line("Weitere Kosten bei Verkauf", pdfMoney(m.fixedOther));',
    'if(!isOwnUse) costRows.push(["',
    'if(!isOwnUse) costs.push(["Verkaufskosten",calculatorSellingCosts]);',
    'V8.249',
    'service-worker.js?v=8.249'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.249 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.249 Eigennutzung sale-cost fields removed from calculator and PDF views")
