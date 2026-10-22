from pathlib import Path
import re
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

short="Richtwerte erscheinen dezent als Vorschlag. Erst über den Button werden sie in die Berechnung übernommen."
new_note='<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €. Graue Werte sind unverbindliche Richtwerte. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen. Erst über den Button werden sie in die Berechnung übernommen.'

# 1) Sichtbare Kurz-Hinweise in den Sanierungs-Köpfen entfernen.
s=re.sub(
    r'<p class="sub" style="margin:4px 0 0">'+re.escape(short)+r'</p>',
    '',
    s
)

# 2) Runtime-Zuweisung entfernen, damit der Kurztext nicht beim Öffnen wieder erscheint.
s=s.replace(
    '    const intro=head.querySelector(".sub");\n    if(intro) intro.textContent="'+short+'";\n',
    ''
)

# 3) Bestehende "So funktioniert es"-Texte in gemeinsamer Sanierung vereinheitlichen.
patterns=[
    r'<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €\. Graue Werte im Eingabefeld sind unverbindliche Richtwerte\. Du kannst sie gesammelt übernehmen oder jeden Betrag direkt selbst eintragen und später jederzeit ändern\.',
    r'<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €\. Graue Werte sind unverbindliche Richtwerte\. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen\.'
]
# Apply both source variants in one pass so replacement text is never matched again.
s,replaced=re.subn("|".join("(?:"+pattern+")" for pattern in patterns),new_note,s)

if replaced < 2:
    raise SystemExit(f"V8.322 expected at least 2 renovation note replacements, got {replaced}")

if short in s:
    raise SystemExit("V8.322 old short renovation hint still present")

if s.count(new_note) < 2:
    raise SystemExit("V8.322 unified renovation note missing in both functions")

# Remove the obsolete subtitle below "Sanierung aufteilen".
obsolete="Richtwerte werden aus der Wohnfläche berechnet. Die Summe oben enthält den Sanierungs-Puffer."
s=re.sub(r'<p\b[^>]*>\s*'+re.escape(obsolete)+r'\s*</p>', '', s)
if obsolete in s:
    raise SystemExit("Obsolete renovation subtitle still present")

s=s.replace("<label>Sanierung (inkl. Puffer)</label>", "<label>Modernisierung</label>")

s=s.replace("Sanierungswerte sind editierbare Orientierungswerte für einen ersten Deal-Check. ", "")

s=s.replace("Laufende Kosten pro Monat", "Lfd. Kosten pro Monat")

# Programmatic renovation changes must refresh the rental results immediately.
old_sync='localStorage.setItem("ff_rent_rentRenovation",String(t));}'
new_sync='localStorage.setItem("ff_rent_rentRenovation",String(t));$r("rentRenovation").dispatchEvent(new Event("input",{bubbles:true}));}'
if old_sync not in s:
    raise SystemExit("Rental renovation sync anchor missing")
s=s.replace(old_sync,new_sync,1)

# Rental financing share and acquisition-cost toggle, matching owner-use logic.
def financing_replace(old,new,label):
    global s
    if old not in s:
        raise SystemExit('Rental financing anchor missing: '+label)
    s=s.replace(old,new,1)

financing_replace('    rentEquity:"0",','    rentEquity:"0",\n    rentLtv:"100.00",\n    rentFinanceAcquisition:"1",','defaults')
financing_replace('if(el) localStorage.setItem(PREFIX+id,el.value);','if(el) localStorage.setItem(PREFIX+id,el.type==="checkbox" ? (el.checked ? "1" : "0") : el.value);','save checkbox')
financing_replace('el.value=saved!==null ? saved : defaults[id];','if(el.type==="checkbox") el.checked=(saved!==null ? saved : defaults[id])==="1";\n      else el.value=saved!==null ? saved : defaults[id];','load checkbox')
financing_replace('if(el) el.value=defaults[id];','if(el){if(el.type==="checkbox") el.checked=defaults[id]==="1";else el.value=defaults[id];}','reset checkbox')

controls='''<div class="quick-grid" id="rentFinancingControls">
  <div class="field"><label for="rentLtv">Finanziert <button type="button" class="rent-info-dot" data-info="Anteil der Finanzierungsbasis vor Abzug deines eingetragenen Eigenkapitals. Die Basis enthält Kaufpreis und Modernisierung sowie bei aktivem Häkchen die Kaufnebenkosten. 100 % entspricht der gesamten Basis; dies ist keine Auszahlungsquote bzw. kein Disagio.">i</button></label><div class="input-wrap"><input id="rentLtv" inputmode="decimal" value="100.00"><span class="unit">%</span></div></div>
  <div class="field"><label for="rentFinanceAcquisition">Mitfinanzieren <button type="button" class="rent-info-dot" data-info="Wenn aktiviert, gehören die Kaufnebenkosten zur Finanzierungsbasis. Andernfalls müssen sie zusätzlich aus eigenen Mitteln bezahlt werden.">i</button></label><div style="min-height:50px;display:flex;align-items:center;justify-content:center"><input id="rentFinanceAcquisition" type="checkbox" checked style="width:32px;height:32px;min-height:32px;padding:0;accent-color:#2563eb"></div></div>
</div>
'''
anchor='<div class="budget-summary rent-finance-summary">'
financing_replace(anchor,controls+anchor,'controls')
financing_replace('        </div>\n      </section>\n\n      <section class="card result-card">','        </div>\n        <p class="mini" id="rentFundingGap" role="status" hidden></p>\n      </section>\n\n      <section class="card result-card">','funding status')
financing_replace('    const loan=Math.max(0,totalInvestment-equityUsed);','''    const financingShare=Math.max(0,pctValue("rentLtv"));
    const financeAcquisition=!!document.getElementById("rentFinanceAcquisition")?.checked;
    const financingBase=purchase+renovation+(financeAcquisition ? acquisitionCosts : 0);
    const loan=Math.max(0,financingBase*financingShare-equityUsed);
    const fundingGap=Math.max(0,totalInvestment-loan-equityUsed);''','model')
financing_replace('      totalInvestment,loan,monthlyInterest,monthlyPrincipal,debtService,','      financingShare,financeAcquisition,financingBase,fundingGap,totalInvestment,loan,monthlyInterest,monthlyPrincipal,debtService,','model result')
financing_replace('  function renderRent(){','  window.rentalCalculation=rentModel;\n\n  function renderRent(){','shared calculation')
financing_replace('    setText("rentLoanResult",euro(m.loan));','''    setText("rentLoanResult",euro(m.loan));
    const gap=document.getElementById("rentFundingGap");
    if(gap){gap.hidden=m.fundingGap<0.005;gap.textContent="Zusätzlich benötigte Eigenmittel: "+euro(m.fundingGap)+". Dieser Betrag ist noch nicht durch Darlehen und eingetragenes Eigenkapital gedeckt.";gap.style.color="#b91c1c";}''','funding warning')
# The PDF now uses exactly the same calculation as the on-screen results.
start=s.index('  function rentalModel(){')
end=s.index('\n  function pct(v)',start)
s=s[:start]+'''  function rentalModel(){
    const m=window.rentalCalculation();
    return {...m,acquisition:m.acquisitionCosts,debt:m.debtService,effective:m.effectiveMonthlyRent,owner:m.ownerMonthlyCosts,cashflow:m.monthlyCashflow,other:m.otherCosts,principal:m.annualPrincipal,breakEven:m.breakEvenRent};
  }
'''+s[end:]
financing_replace("    line('Eigenkapital',money(m.equityUsed));",'''    line('Eigenkapital',money(m.equityUsed));
    line('Finanziert',pct(m.financingShare));
    line('Kaufnebenkosten mitfinanzieren',m.financeAcquisition ? 'Ja' : 'Nein');
    line('Finanzierungsbasis',money(m.financingBase));
    if(m.fundingGap>=0.005) line('Zusätzlich benötigte Eigenmittel',money(m.fundingGap),true);''','PDF financing')

p.write_text(s,encoding="utf-8")
print("V8.322 renovation helper texts unified")
