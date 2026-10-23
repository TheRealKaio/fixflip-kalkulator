from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else '_site/index.html')
s = p.read_text(encoding='utf-8')

def replace(old, new):
    global s
    if s.count(old) != 1:
        raise SystemExit('Rental equity shortfall anchor must occur once: ' + old[:100])
    s = s.replace(old, new, 1)

replace('<p class="mini" id="rentFundingGap" role="status" hidden></p>', '')
replace('<input id="rentEquity" inputmode="decimal" value="0"><span class="unit">€</span></div></div>', '<input id="rentEquity" inputmode="decimal" value="0"><span class="unit">€</span></div><div class="equity-shortfall-warning" id="rentFundingGap" role="status" hidden></div></div>')

# Match owner-use: compare the required equity before equity deduction with
# the entered equity. Using the net loan here cancels out increases in equity.
replace('const fundingGap=Math.max(0,totalInvestment-loan-equityUsed);', '''const requiredEquity=Math.max(0,totalInvestment-financingBase*financingShare);
    const fundingGap=Math.max(0,requiredEquity-equity);''')
replace('if(gap){gap.hidden=m.fundingGap<0.005;gap.textContent="Zusätzlich benötigte Eigenmittel: "+euro(m.fundingGap)+". Dieser Betrag ist noch nicht durch Darlehen und eingetragenes Eigenkapital gedeckt.";gap.style.color="#b91c1c";}', '''if(gap){
      const equityIncreaseRequired=(!m.financeAcquisition || m.financingShare<0.999999) && m.fundingGap>1;
      gap.hidden=!equityIncreaseRequired;
      gap.textContent=equityIncreaseRequired ? "Eigenkapital erhöhen – Fehlbetrag: "+euro(m.fundingGap)+"." : "";
    }''')
p.write_text(s, encoding='utf-8')
print('Rental equity shortfall matches owner-use layout and logic')
