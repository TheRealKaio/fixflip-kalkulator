"""Remove double equity deductions when the shared percent slider is active.

The slider and euro equity field jointly describe one financing allocation:
    loan = financing basis * percentage
    required equity = max(0, total acquisition/project cost - loan).
The own-use/rental model previously subtracted the same equity AGAIN from
the percentage-based loan.  For Fix & Flip the separate reserve waterfall is
preserved; only its redundant secondary loan reduction is skipped while the
shared slider owns the financing allocation.
"""
from pathlib import Path
import sys

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
# The existing Fix & Flip reserve waterfall remains in charge of mandatory
# equity and holding-cost buffers. A surplus must not reduce the same loan
# for a second time when the percentage itself already includes user equity.
needle="equityForFinancing=Math.min(grossDebt,Math.max(0,availableCapital-requiredReserve));"
if s.count(needle)!=2:
    raise SystemExit("Finance equity consistency: unexpected waterfall layout")
s=s.replace(needle,needle+"\n    if(window.NICFinancingPercent?.managed('ltv'))equityForFinancing=0;")
# Avoid special 100%-full-finance capitalization when the user explicitly
# chooses a DIFFERENT financing ratio, including 0% and 120%.
once(
    "if(availableCapital <= 0){",
    "if(availableCapital <= 0 && Math.abs(ltv-1)<0.000001){",
    "Fix & Flip zero-equity special case only at 100 percent"
)
path.write_text(s,encoding="utf-8")
print("Financing equity consistency: rental, owner-use and Fix & Flip waterfall patched")
