from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

replacements = {
'''    line("Weitere Finanzierung - Kreditsumme", pdfMoney(additionalLoanPdf.amount), true);
    line("Weitere Finanzierung - Zins p.a.", pdfPercent(val("ownAdditionalLoanInterest")));
    line("Weitere Finanzierung - Tilgung p.a.", pdfPercent(val("ownAdditionalLoanRepayment")));
    line("Weitere Finanzierung - Monatsrate", pdfMoney(additionalLoanPdf.total), true);
    line("Monatliche Gesamtbelastung", pdfMoney(m.monthlyPayment + m.monthlyRepayment + val("holding")), true);''':
'''    line("Kreditsumme (Weitere Finanzierung)", pdfMoney(additionalLoanPdf.amount), true);
    line("Monatliche Zinsbelastung (Weitere Finanzierung)", pdfMoney(additionalLoanPdf.monthlyInterest));
    line("Monatliche Tilgung (Weitere Finanzierung)", pdfMoney(additionalLoanPdf.monthlyRepayment));
    line("Monatliche Gesamtbelastung", pdfMoney(m.monthlyPayment + m.monthlyRepayment + val("holding")), true);'''
}

for old,new in replacements.items():
    if old not in s:
        raise SystemExit("V8.248 PDF additional-financing anchor missing")
    s=s.replace(old,new,1)

# Versionsstand im sichtbaren Rechner, PDF und SW-Registrierung.
s=s.replace("V8.247","V8.248")
s=s.replace("service-worker.js?v=8.247","service-worker.js?v=8.248")

# Abnahme: Die kombinierte Kreditraten-Infobox muss weiterhin model()-Werte
# verwenden; Wo geht das Geld hin? muss die kombinierten Zins-/Tilgungswerte nutzen.
required=[
    'Kreditsumme (Weitere Finanzierung)',
    'Monatliche Zinsbelastung (Weitere Finanzierung)',
    'pdfMoney(additionalLoanPdf.monthlyInterest)',
    'Monatliche Tilgung (Weitere Finanzierung)',
    'pdfMoney(additionalLoanPdf.monthlyRepayment)',
    '{title:"Monatliche Kreditrate (Zins + Tilgung)", value:pdfMoney(m.monthlyPayment + m.monthlyRepayment)',
    'const interestCosts = m.interest;',
    'const repaymentCosts = m.repayment;',
    'm.interest=(Number(m.interest)||0)+extra.totalInterest;',
    'm.repayment=(Number(m.repayment)||0)+extra.totalRepayment;',
    'V8.248',
    'service-worker.js?v=8.248'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.248 verification failed: "+", ".join(missing))

for forbidden in [
    'Weitere Finanzierung - Monatsrate',
    'Weitere Finanzierung - Kreditsumme',
    'Weitere Finanzierung - Zins p.a.',
    'Weitere Finanzierung - Tilgung p.a.'
]:
    if forbidden in s:
        raise SystemExit("V8.248 legacy PDF label remains: "+forbidden)

path.write_text(s,encoding="utf-8")
print("V8.248 Eigennutzung PDF additional financing labels and values applied")
