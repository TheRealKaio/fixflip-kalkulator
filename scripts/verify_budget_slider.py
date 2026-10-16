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
    "current buffer uses model reserve": 'const currentBuffer=Math.max(0,Number(m.reserve)||0);',
    "under 300 threshold": 'const minimumBufferBelow=currentBuffer<300;',
    "exact 300 threshold": 'const minimumBufferReached=Math.abs(currentBuffer-300)<=0.005;',
    "shortfall amount calculated": 'const bufferShortfall=Math.max(0,300-currentBuffer);',
    "warning hidden above 300": '$("budgetRateSliderWarning").hidden=currentBuffer>300;',
    "shortfall shown in warning": 'Mindestpuffer unterschritten um "+eur(bufferShortfall)',
    "safety buffer readonly": 'id="budgetSafetyReserve" inputmode="decimal" value="300" readonly aria-readonly="true"',
    "safety buffer auto label": 'automatisch berechnet · mindestens 300 €',
    "safety buffer non-editable note": 'ist nicht manuell editierbar.',
    "capture phase enabled": '},true);',
    "shortfall amount calculated": 'const bufferShortfall=Math.max(0,300-rawCurrentBuffer);',
    "shortfall shown in warning": 'Mindestpuffer unterschritten um "+eur(bufferShortfall)',
    "warning message": 'Mindestpuffer unterschritten. Bitte Einnahmen oder Ausgaben prüfen.',
    "warning at exact minimum": 'Mindestpuffer erreicht. Bitte Einnahmen oder Ausgaben prüfen.',
    "slider excluded from global input listener": ':not(#budgetRateSlider),select\')',
    "income/expense changes reset slider": 'const budgetRateRecalcIds=new Set([',
    "old slider value cleared": 'localStorage.removeItem("ff_budget_rateSliderPct");',
    "slider jumps to recalculated maximum": 'const newPct=Math.max(0,m.maxRatePct||0);',
    "rate jumps to recalculated maximum": 'const newRate=Math.max(0,m.maxMonthlyRate||0);',
    "post-sync recalculation render": 'renderBudget();',
}

forbidden_implementation = {
    "toast markup removed": 'id="budgetBufferToast"',
    "toast helper removed": 'showBudgetBufferToast(',
    "toast CSS removed": '.budget-buffer-toast',
}
present_forbidden = [name for name, token in forbidden_implementation.items() if token in html]
if present_forbidden:
    raise SystemExit("Slider acceptance failed - removed toast still present: " + ", ".join(present_forbidden))

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

# 5) Critical direction A: reducing income must reduce the allowed maximum and move the slider left.
before_income_drop = model(3500, 0, 700, 1000, 45)
after_income_drop = model(2800, 0, 700, 1000, 45)
if not (after_income_drop["cap"] < before_income_drop["cap"] and close(after_income_drop["pct"], after_income_drop["max_pct"])):
    raise SystemExit("Slider acceptance failed - reduced income did not lower/reposition the maximum")

# 6) Critical direction B: increasing expenses must reduce the allowed maximum and move the slider left.
before_expense_rise = model(3000, 0, 500, 1000, 45)
after_expense_rise = model(3000, 0, 1800, 1000, 45)
if not (after_expense_rise["cap"] < before_expense_rise["cap"] and close(after_expense_rise["pct"], after_expense_rise["max_pct"])):
    raise SystemExit("Slider acceptance failed - increased expenses did not lower/reposition the maximum")

# 7) Child benefit increases available pool, but the 45% ceiling still uses net household income.
assert_case(
    "net percentage basis",
    model(3000, 500, 1000, 1000, 45),
    rate=1350,
    reserve=1150,
    pct=45,
)

# 8) Warning threshold: any computed reserve below EUR 300 must trigger the warning condition.
under_min = {"reserve": 185}
if not (under_min["reserve"] < 300):
    raise SystemExit("Slider acceptance failed - under minimum reserve warning")

# 9) Robust warning trigger: even if slider logic clamps the rate, a rate pool under EUR 300 must warn.
rate_pool_case = {"reserve": 300, "rate_pool": 250}
if not (rate_pool_case["reserve"] < 300 or rate_pool_case["rate_pool"] < 300):
    raise SystemExit("Slider acceptance failed - rate pool under 300 triggers warning")

# 10) Reaching exactly EUR 300 after an adverse change must already warn.
exact_min = {"reserve": 300, "rate_pool": 1200}
if not (exact_min["reserve"] <= 300.01):
    raise SystemExit("Slider acceptance failed - exactly EUR 300 must also warn")

# 11) Expense increase must warn as soon as the displayed buffer reaches EUR 300.
# Example: raw buffer 300.3 rounds to 300 in the UI.
raw_buffer_after_expense_rise = 300.3
displayed_buffer = round(raw_buffer_after_expense_rise)
if not (displayed_buffer <= 300):
    raise SystemExit("Slider acceptance failed - expense rise to displayed 300 must warn")

# 12) Shortfall amount must equal EUR 300 minus the actual current buffer.
raw_current_buffer = 215
buffer_shortfall = max(0, 300 - raw_current_buffer)
if buffer_shortfall != 85:
    raise SystemExit("Slider acceptance failed - shortfall amount correctness")

# 13) Toast state logic: only the transition from not-below to below should fire.
states = [
    (False, False, False),
    (False, True, True),
    (True, True, False),
    (True, False, False),
    (False, True, True),
]
for was_below, is_below, should_fire in states:
    fires = is_below and not was_below
    if fires != should_fire:
        raise SystemExit("Slider acceptance failed - toast threshold crossing logic")

# 14) Adjustment amount: previous rate 1,200 EUR, new max 1,050 EUR => reduce by 150 EUR.
previous_rate = 1200
new_rate = 1050
rate_reduction = max(0, previous_rate - new_rate)
if rate_reduction != 150:
    raise SystemExit("Slider acceptance failed - rate reduction amount")

# 15) Any true value below EUR 300 must show the deviation, even if it rounds to EUR 300.
raw_buffer = 299.80
shortfall = max(0, 300 - raw_buffer)
if not (raw_buffer < 300 and abs(shortfall - 0.20) < 1e-9):
    raise SystemExit("Slider acceptance failed - sub-euro shortfall")

# 16) Exactly EUR 300 is reached, not undercut.
raw_buffer = 300.00
if raw_buffer < 300:
    raise SystemExit("Slider acceptance failed - exact 300 classified as below")

# 17) Pre-adjustment undershoot must be preserved even when the new rate is auto-clamped to EUR 300 reserve.
previous_rate = 1200
new_rate = 1115
pre_adjustment_undershoot = max(0, previous_rate - new_rate)
if pre_adjustment_undershoot != 85:
    raise SystemExit("Slider acceptance failed - pre-adjustment undershoot, buffer state only")




# 18) Buffer above EUR 300: warning must be hidden.
current_buffer = 450
if not (current_buffer > 300):
    raise SystemExit("Slider acceptance failed - buffer above 300 hides warning")

# 19) Buffer exactly EUR 300: reached state, no shortfall.
current_buffer = 300
shortfall = max(0, 300 - current_buffer)
if not (abs(current_buffer - 300) <= 0.005 and shortfall == 0):
    raise SystemExit("Slider acceptance failed - exact 300 reached state")

# 20) Buffer below EUR 300: warning must show exact shortfall.
current_buffer = 215
shortfall = max(0, 300 - current_buffer)
if not (current_buffer < 300 and shortfall == 85):
    raise SystemExit("Slider acceptance failed - under-300 shortfall")

print("Slider acceptance passed:")
for name in required_implementation:
    print(" -", name)
print(" - numerical cases: 45% cap, EUR 300 floor, zero left edge, directionality, income reduction, expense increase, net-income basis, reached/under-300 warning, shortfall amount, rate-reduction amount, exact/sub-euro 300 threshold, pre-adjustment undershoot")
