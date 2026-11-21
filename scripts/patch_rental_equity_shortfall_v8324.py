"""Remove redundant rental warning; retain rental financial diagnostics.

Manual equity updates the financing percentage through the shared slider.
The old red rentFundingGap warning falsely flagged minor rounding differences
and duplicated the grey dynamic equity hint.
"""
from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def replace_once(old,new):
    global s
    count=s.count(old)
    if count!=1:
        raise SystemExit("Rental warning retirement anchor mismatch ("+str(count)+"): "+old[:85])
    s=s.replace(old,new,1)

# Remove the old inline warning element without adding another under equity.
replace_once('<p class="mini" id="rentFundingGap" role="status" hidden></p>', '')
# Preserve the financing-model fundingGap field for any non-UI consumers,
# but no longer render it as a redundant red error.
replace_once('if(gap){gap.hidden=m.fundingGap<0.005;gap.textContent="Zusätzlich benötigte Eigenmittel: "+euro(m.fundingGap)+". Dieser Betrag ist noch nicht durch Darlehen und eingetragenes Eigenkapital gedeckt.";gap.style.color="#b91c1c";}', '')
if 'id="rentFundingGap"' in s:
    raise SystemExit("Rental red warning markup unexpectedly remains")
if 'id="rentEquity"' not in s:
    raise SystemExit("Rental equity input missing")
p.write_text(s,encoding="utf-8")
print("Rental redundant equity shortfall warning removed")
