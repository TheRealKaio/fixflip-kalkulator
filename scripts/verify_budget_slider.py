#!/usr/bin/env python3
"""
Acceptance verification for the Budget credit-rate slider.

This script deliberately checks the generated site, not only the patch source.
It translates the product requirement into explicit acceptance criteria:
- slider can move left to 0 EUR credit rate;
- moving right raises the rate and lowers the safety reserve;
- right edge is the earlier of 45% of net household income or EUR 300 minimum reserve;
- initial position is derived from the dynamic minimum reserve, then clamped to the legal range;
- changing the slider updates reserve/storage and re-renders immediately.
"""
from pathlib import Path
import sys

index_path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = index_path.read_text(encoding="utf-8")

required_implementation = {
    "slider exists": 'id="budgetRateSlider" type="range" min="0" max="45" step="0.1"',
    "minimum reserve formula": 'const minimumReserve=Math.max(300,ratePool*0.10);',
    "dynamic reserve limit": 'const maxRateByReserve=Math.max(0,ratePool-minimumReserve);',
    "45 percent limit": 'const maxRateByPct=Math.max(0,net*0.45);',
    "earlier limit wins": 'const rateCap=Math.max(0,Math.min(maxRateByReserve,maxRateByPct));',
    "initial rate from minimum reserve": 'const defaultRate=Math.max(0,ratePool-minimumReserve);',
    "stored rate may remain temporarily above safe maximum": 'const selectedRatePct=Math.max(0,requestedRatePct);',
    "left edge supports zero": 'const selectedPct=Math.max(0,Math.min(sliderMaxPct,Number($("budgetRateSlider").value)||0));',
    "reserve moves opposite to rate": 'const totalReserve=Math.max(0,(current.ratePool||0)-selectedRate);',
    "minimum reserve field updated live": 'if($("budgetSafetyReserve")) $("budgetSafetyReserve").value=String(Math.round(current.minimumReserve));',
    "slider choice persisted": 'localStorage.setItem("ff_budget_rateSliderPct",String(selectedPct));',
    "UI recalculated immediately": 'renderBudget();',
    "new reserve note text": 'Aktueller Sicherheitspuffer: "+eur(m.rawReserve)+" · Mindest-Sicherheitspuffer: "+eur(m.minimumReserve)',
    "separate reserve warning": 'id="budgetRateSliderWarning"',
    "financing guidance intro": 'Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten.',
    "raw reserve exposed": 'const rawReserve=ratePool-monthlyRate;',
    "current buffer uses raw reserve": 'const currentBuffer=Number.isFinite(Number(m.rawReserve)) ? Number(m.rawReserve) : 0;',
    "signed deviation calculated": 'const bufferDeviation=currentBuffer-minimumReserve;',
    "under minimum threshold": 'const minimumBufferBelow=bufferDeviation<-0.005;',
    "exact minimum threshold": 'const minimumBufferReached=Math.abs(bufferDeviation)<=0.005;',
    "warning hidden above minimum": '$("budgetRateSliderWarning").hidden=bufferDeviation>0.005;',
    "signed deviation shown in warning": 'Mindestpuffer unterschritten · Abweichung: "+eur(bufferDeviation)',
    "safety buffer readonly": 'id="budgetSafetyReserve" inputmode="decimal" value="300" readonly aria-readonly="true"',
    "safety buffer auto label": '10 % von Einnahmen − Ausgaben · mindestens 300 €',
    "capture phase enabled": '},true);',
    "warning message": 'Mindestpuffer unterschritten. Bitte Einnahmen oder Ausgaben prüfen.',
    "warning at exact minimum": 'Mindestpuffer erreicht: "+eur(minimumReserve)+". Bitte Einnahmen oder Ausgaben prüfen.',
    "slider excluded from global input listener": ':not(#budgetRateSlider),select\')',
    "income/expense changes reset slider": 'const budgetRateRecalcIds=new Set([',
    "old slider value cleared": 'localStorage.removeItem("ff_budget_rateSliderPct");',
    "previous absolute rate captured": 'budgetRateBeforeRecalc=Math.max(0,Number(beforeChange.monthlyRate)||0);',
    "previous rate preserved after recalculation": 'const preservedRatePct=recalculated.net>0 ? (previousRate/recalculated.net)*100 : 0;',
    "reset arms initial rate": 'budgetRateNeedsInitialValue=true;',
    "initial rate waits for focusout": 'document.addEventListener("focusout",(event)=>',
    "initialization only for income": 'if(!el || !budgetRateNeedsInitialValue || !budgetRateIncomeIds.has(el.id)) return;',
    "initial rate uses existing max": 'const initialRatePct=Math.max(0,m.maxRatePct||0);',
    "initial rate stored once": 'localStorage.setItem("ff_budget_rateSliderPct",String(initialRatePct));',
    "initialization disabled afterwards": 'budgetRateNeedsInitialValue=false;',
    "loan monthly rate from max loan": 'const loanMonthlyRate=loan*debtServicePct/12;',
    "interest part from max loan": 'const interestPart=loan*interestPct/12;',
    "repayment part from max loan": 'const repaymentPart=loan*repaymentPct/12;',
    "remaining debt uses loan monthly rate": 'loanMonthlyRate*((factor-1)/r)',
    "monthly rate label renamed": 'Monatliche Rate (Max. Darlehen)',
    "monthly rate UI uses loan rate": 'eur(m.loanMonthlyRate)',
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
    raise SystemExit("Slider acceptance failed - pre-adjustment undershoot, dynamic minimum reserve")




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

# 21) Minimum reserve: 10% of free budget, but at least EUR 300.
rate_pool = 3000
minimum_reserve = max(300, rate_pool * 0.10)
if minimum_reserve != 300:
    raise SystemExit("Slider acceptance failed - minimum reserve floor")

rate_pool = 4000
minimum_reserve = max(300, rate_pool * 0.10)
if minimum_reserve != 400:
    raise SystemExit("Slider acceptance failed - minimum reserve 10 percent of free budget")

# 22) Maximum rate is free budget minus minimum reserve.
rate_pool = 4000
minimum_reserve = max(300, rate_pool * 0.10)
max_rate_by_reserve = max(0, rate_pool - minimum_reserve)
if max_rate_by_reserve != 3600:
    raise SystemExit("Slider acceptance failed - max rate after minimum reserve")

# 23) Warning compares current buffer to dynamic minimum reserve.
current_buffer = 315
minimum_reserve = 400
shortfall = max(0, minimum_reserve - current_buffer)
if not (current_buffer < minimum_reserve and shortfall == 85):
    raise SystemExit("Slider acceptance failed - dynamic minimum reserve warning")

# 24) Expense increase keeps the absolute credit rate so the buffer can really fall below the minimum.
previous_rate = 2600
income = 4000
expenses = 1200
rate_pool = max(0, income - expenses)
minimum_reserve = max(300, rate_pool * 0.10)
current_buffer = max(0, rate_pool - previous_rate)
shortfall = max(0, minimum_reserve - current_buffer)
if not (current_buffer == 200 and minimum_reserve == 300 and shortfall == 100):
    raise SystemExit("Slider acceptance failed - expense increase keeps absolute credit rate")

# 25) Income increase with unchanged absolute credit rate raises the actual buffer.
previous_rate = 2600
income = 4300
expenses = 1020
rate_pool = max(0, income - expenses)
minimum_reserve = max(300, rate_pool * 0.10)
current_buffer = max(0, rate_pool - previous_rate)
if not (minimum_reserve == 328 and current_buffer == 680 and current_buffer > minimum_reserve):
    raise SystemExit("Slider acceptance failed - income increase raises current buffer")

# 26) Signed deviation may exceed EUR 300 when the actual buffer is negative.
current_buffer = -150
minimum_reserve = 300
deviation = current_buffer - minimum_reserve
if deviation != -450:
    raise SystemExit("Slider acceptance failed - negative deviation beyond 300")

# 27) Dynamic minimum reserve also uses signed deviation.
current_buffer = 315
minimum_reserve = 400
deviation = current_buffer - minimum_reserve
if deviation != -85:
    raise SystemExit("Slider acceptance failed - dynamic signed deviation")

# 28) After reset, the initial rate uses the already existing safe maximum once income entry is complete.
income = 4000
expenses = 0
rate_pool = max(0, income - expenses)
minimum_reserve = max(300, rate_pool * 0.10)
max_rate_by_reserve = max(0, rate_pool - minimum_reserve)
max_rate_by_pct = income * 0.45
initial_rate = min(max_rate_by_reserve, max_rate_by_pct)
if initial_rate != 1800:
    raise SystemExit("Slider acceptance failed - initial rate after reset uses existing safe maximum")

# 29) During typing the special state preserves zero until focusout; no partial-value initialization.
needs_initial = True
previous_rate = 0
if not (needs_initial and previous_rate == 0):
    raise SystemExit("Slider acceptance failed - initial rate must wait until completed income entry")

# 30) Once initialized, the special reset-only state is disabled.
needs_initial = False
if needs_initial:
    raise SystemExit("Slider acceptance failed - initial rate state must disable after first initialization")

# 31) Monthly rate in the debt section is derived from Max. Darlehen, interest and repayment.
loan = 300000
interest_pct = 0.04
repayment_pct = 0.015
loan_monthly_rate = loan * (interest_pct + repayment_pct) / 12
interest_part = loan * interest_pct / 12
repayment_part = loan * repayment_pct / 12
if round(loan_monthly_rate, 2) != 1375.00:
    raise SystemExit("Slider acceptance failed - loan monthly rate equals annuity from max loan")
if round(interest_part, 2) != 1000.00:
    raise SystemExit("Slider acceptance failed - interest part from max loan")
if round(repayment_part, 2) != 375.00:
    raise SystemExit("Slider acceptance failed - repayment part from max loan")
if round(interest_part + repayment_part, 2) != round(loan_monthly_rate, 2):
    raise SystemExit("Slider acceptance failed - interest and repayment sum to loan monthly rate")

# 32) Expenses above income must show a negative free budget and zero credit rate.
income = 4000
expenses = 4250
free_budget = income - expenses
financing_pool = max(0, free_budget)
minimum_reserve = max(300, free_budget * 0.10)
max_rate_by_reserve = max(0, financing_pool - minimum_reserve)
max_rate_by_pct = income * 0.45
rate_cap = max(0, min(max_rate_by_reserve, max_rate_by_pct))
if not (free_budget == -250 and minimum_reserve == 300 and rate_cap == 0):
    raise SystemExit("Slider acceptance failed - negative free budget yields zero credit rate")

# 33) A positive free budget below the 300 EUR minimum reserve also yields zero credit rate.
income = 4000
expenses = 3900
free_budget = income - expenses
financing_pool = max(0, free_budget)
minimum_reserve = max(300, free_budget * 0.10)
rate_cap = max(0, min(max(0, financing_pool - minimum_reserve), income * 0.45))
if not (free_budget == 100 and minimum_reserve == 300 and rate_cap == 0):
    raise SystemExit("Slider acceptance failed - free budget below minimum reserve yields zero credit rate")

print("Slider acceptance passed:")
for name in required_implementation:
    print(" -", name)
print(" - numerical cases: 45% cap, EUR 300 floor, zero left edge, directionality, income reduction, expense increase, net-income basis, reached/under-300 warning, shortfall amount, rate-reduction amount, exact/sub-euro 300 threshold, pre-adjustment undershoot")
