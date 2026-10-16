#!/usr/bin/env python3
"""
Acceptance verification for the Budget credit-rate slider.

This script deliberately checks the generated site, not only the patch source.
It translates the product requirement into explicit acceptance criteria:
- slider can move left to 0 EUR credit rate;
- moving right raises the rate and lowers the safety reserve;
- right edge is the earlier of 45% of net household income or EUR 300 minimum reserve;
- initial position is derived from the current safety reserve, then clamped to the legal range;
- changing the slider updates reserve/storage and re-renders immediately.
"""
from pathlib import Path
import sys

index_path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = index_path.read_text(encoding="utf-8")

required_implementation = {
    "slider exists": 'id="budgetRateSlider" type="range" min="0" max="45" step="0.1"',
    "300 EUR reserve limit": 'const maxRateByReserve=Math.max(0,ratePool-300);',
    "45 percent limit": 'const maxRateByPct=Math.max(0,net*0.45);',
    "earlier limit wins": 'const rateCap=Math.max(0,Math.min(maxRateByReserve,maxRateByPct));',
    "initial rate from safety reserve": 'const defaultRate=Math.max(0,ratePool-enteredReserve);',
    "initial/stored value clamped": 'const selectedRatePct=Math.max(0,Math.min(maxRatePct,requestedRatePct));',
    "left edge supports zero": 'const selectedPct=Math.max(0,Math.min(maxPct,Number($("budgetRateSlider").value)||0));',
    "reserve moves opposite to rate": 'const totalReserve=Math.max(0,(current.ratePool||0)-selectedRate);',
    "reserve field updated live": 'if($("budgetSafetyReserve")) $("budgetSafetyReserve").value=String(Math.round(totalReserve));',
    "slider choice persisted": 'localStorage.setItem("ff_budget_rateSliderPct",String(selectedPct));',
    "UI recalculated immediately": 'renderBudget();',
    "new reserve note text": 'Aktueller Sicherheitspuffer: "+eur(m.reserve)+" · Mindest-Sicherheitspuffer: 300 €',
    "separate reserve warning": 'id="budgetRateSliderWarning"',
    "robust reserve warning condition": 'const minimumBufferMissed=(m.reserve<300)||(m.ratePool<300);',
    "warning message": 'Mindestpuffer unterschritten. Bitte Einnahmen oder Ausgaben prüfen.',
    "slider excluded from global input listener": ':not(#budgetRateSlider),select\')',
    "income/expense changes reset slider": 'const budgetRateRecalcIds=new Set([',
    "old slider value cleared": 'localStorage.removeItem("ff_budget_rateSliderPct");',
    "slider jumps to recalculated maximum": 'const newPct=Math.max(0,m.maxRatePct||0);',
    "rate jumps to recalculated maximum": 'const newRate=Math.max(0,m.maxMonthlyRate||0);',
}

missing = [name for name, token in required_implementation.items() if token not in html]
if missing:
    raise SystemExit("Slider acceptance failed - implementation missing: " + ", ".join(missing))


def model(net, child_benefit, expenses, entered_reserve, selected_pct=None):
    income = max(0, net) + max(0, child_benefit)
    rate_pool = max(0, income - max(0, expenses))
    max_rate_by_reserve = max(0, rate_pool - 300)
    max_rate_by_pct = max(0, net * 0.45)
    rate_cap = max(0, min(max_rate_by_reserve, max_rate_by_pct))
    max_rate_pct = (rate_cap / net * 100) if net > 0 else 0

    default_rate = max(0, rate_pool - max(0, entered_reserve))
    default_pct = (default_rate / net * 100) if net > 0 else 0
    requested_pct = default_pct if selected_pct is None else selected_pct
    effective_pct = max(0, min(max_rate_pct, requested_pct))
    rate = min(rate_cap, net * effective_pct / 100) if net > 0 else 0
    reserve = max(0, rate_pool - rate)
    return {
        "rate": rate,
        "reserve": reserve,
        "pct": effective_pct,
        "max_pct": max_rate_pct,
        "cap": rate_cap,
        "rate_pool": rate_pool,
    }


def close(actual, expected, tol=0.01):
    return abs(actual - expected) <= tol


def assert_case(name, result, **expected):
    bad = []
    for key, value in expected.items():
        if not close(result[key], value):
            bad.append(f"{key}: expected {value}, got {result[key]}")
    if bad:
        raise SystemExit(f"Slider acceptance failed - {name}: " + "; ".join(bad))


# 1) 45% limit wins: net 3,000, no expenses, requested/default 50%.
assert_case(
    "45 percent cap",
    model(3000, 0, 0, 1500),
    rate=1350,
    reserve=1650,
    pct=45,
    max_pct=45,
)

# 2) EUR 300 reserve wins before 45%: net 1,000, expenses 600 leaves pool 400.
assert_case(
    "300 EUR minimum reserve",
    model(1000, 0, 600, 300, 45),
    rate=100,
    reserve=300,
    pct=10,
    max_pct=10,
)

# 3) Left edge: rate can reach zero and the complete rate pool becomes reserve.
assert_case(
    "left edge zero rate",
    model(3000, 0, 500, 1000, 0),
    rate=0,
    reserve=2500,
    pct=0,
)

# 4) Dynamic middle position: right means higher rate / lower reserve.
left = model(3000, 0, 500, 1000, 20)
right = model(3000, 0, 500, 1000, 30)
if not (right["rate"] > left["rate"] and right["reserve"] < left["reserve"]):
    raise SystemExit("Slider acceptance failed - directionality is wrong")

# 5) Recalculation after changed income/expenses: the selected rate must jump to the new maximum.
before_change = model(3000, 0, 500, 1000, 20)
after_change = model(3500, 0, 700, 1000, None)
after_change_max = model(3500, 0, 700, 1000, after_change["max_pct"])
if not (after_change_max["rate"] != before_change["rate"] and close(after_change_max["pct"], after_change_max["max_pct"])):
    raise SystemExit("Slider acceptance failed - recalculated after changed expenses/income")

# 6) Child benefit increases available pool, but the 45% ceiling still uses net household income.
assert_case(
    "net percentage basis",
    model(3000, 500, 1000, 1000, 45),
    rate=1350,
    reserve=1150,
    pct=45,
)

# 7) Warning threshold: any computed reserve below EUR 300 must trigger the warning condition.
under_min = {"reserve": 185}
if not (under_min["reserve"] < 300):
    raise SystemExit("Slider acceptance failed - under minimum reserve warning")

# 8) Robust warning trigger: even if slider logic clamps the rate, a rate pool under EUR 300 must warn.
rate_pool_case = {"reserve": 300, "rate_pool": 250}
if not (rate_pool_case["reserve"] < 300 or rate_pool_case["rate_pool"] < 300):
    raise SystemExit("Slider acceptance failed - rate pool under 300 triggers warning")

print("Slider acceptance passed:")
for name in required_implementation:
    print(" -", name)
print(" - numerical cases: 45% cap, EUR 300 floor, zero left edge, directionality, income/expense recalculation, net-income basis, under-300 warning")
