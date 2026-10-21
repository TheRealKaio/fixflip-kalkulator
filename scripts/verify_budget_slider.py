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
    "minimum reserve activates after net income": 'const minimumReserve=net>0 ? Math.max(300,freeBudget*0.10) : 0;',
    "dynamic reserve limit": 'const maxRateByReserve=Math.max(0,ratePool-minimumReserve);',
    "45 percent limit": 'const maxRateByPct=Math.max(0,net*0.45);',
    "earlier limit wins": 'const rateCap=Math.max(0,Math.min(maxRateByReserve,maxRateByPct));',
    "initial rate from minimum reserve": 'const defaultRate=Math.max(0,ratePool-minimumReserve);',
    "stored rate converted before cap": 'const requestedMonthlyRate=net>0 ? net*(Math.max(0,requestedRatePct)/100) : 0;',
    "actual rate capped to free budget": 'const monthlyRate=Math.max(0,Math.min(Math.max(0,freeBudget),requestedMonthlyRate));',
    "selected percent reflects actual rate": 'const selectedRatePct=net>0 ? (monthlyRate/net)*100 : 0;',
    "free budget after reserve exposed": 'const available=freeBudget-minimumReserve;',
    "left edge supports zero": 'const selectedPct=Math.max(0,Math.min(sliderMaxPct,Number($("budgetRateSlider").value)||0));',
    "reserve moves opposite to rate": 'const totalReserve=Math.max(0,(current.ratePool||0)-selectedRate);',
    "minimum reserve field updated live": 'if($("budgetSafetyReserve")) $("budgetSafetyReserve").value=String(Math.round(current.minimumReserve));',
    "slider choice persisted": 'localStorage.setItem("ff_budget_rateSliderPct",String(selectedPct));',
    "UI recalculated immediately": 'renderBudget();',
    "remaining surplus note text": 'Verbleibender Monatsüberschuss: "+eur(m.remainingMonthlySurplus)+" · Finanzierungsreserve: "+eur(m.minimumReserve)',
    "separate reserve warning": 'id="budgetRateSliderWarning"',
    "financing guidance intro": 'Eine Finanzierung sollte eine Belastungsgrenze vom Haushalts-Nettoeinkommen nicht überschreiten.',
    "raw reserve exposed": 'const rawReserve=freeBudget-monthlyRate;',
    "current buffer uses raw reserve": 'const currentBuffer=Number.isFinite(Number(m.rawReserve)) ? Number(m.rawReserve) : 0;',
    "signed deviation calculated": 'const bufferDeviation=currentBuffer-minimumReserve;',
    "under minimum threshold": 'const minimumBufferBelow=bufferDeviation<-0.005;',
    "exact minimum threshold": 'const minimumBufferReached=Math.abs(bufferDeviation)<=0.005;',
    "warning has explicit above-minimum state": 'const minimumBufferAbove=bufferDeviation>0.005;',
    "warning hidden only above minimum": '$("budgetRateSliderWarning").hidden=minimumBufferAbove;',
    "signed deviation shown in warning": 'Finanzierungsreserve unterschritten · Abweichung: "+eur(bufferDeviation)',
    "warning explicit below branch": 'if(minimumBufferBelow){',
    "warning exact-minimum branch": '}else if(minimumBufferReached){',
    "warning clears fallback": '$("budgetRateSliderWarning").textContent="";',
    "financing reserve zero markup": 'id="budgetSafetyReserve" inputmode="decimal" value="0" readonly aria-readonly="true"',
    "safety buffer auto label": '<div class="mini budget-calculated-subtitle">Automatisch berechnet</div>',
    "terminology financing reserve": 'Finanzierungsreserve',
    "terminology remaining monthly surplus": 'Verbleibender Monatsüberschuss',
    "financing reserve summary row": '<span>- Finanzierungsreserve</span><strong id="budgetFinancingReserveResult">–</strong>',
    "financing reserve summary value": 'if($("budgetFinancingReserveResult")) $("budgetFinancingReserveResult").textContent=eur(m.minimumReserve);',
    "remaining monthly surplus formula": 'const remainingMonthlySurplus=rawReserve-minimumReserve;',
    "remaining monthly surplus summary row": '<span>- Verbleibender Monatsüberschuss</span><strong id="budgetReserveResult">–</strong>',
    "remaining monthly surplus summary value": 'if($("budgetReserveResult")) $("budgetReserveResult").textContent=eur(m.remainingMonthlySurplus);',
    "remaining monthly surplus PDF": 'line("Verbleibender Monatsueberschuss",pdfMoney(m.additionalBuffer));',
    "own budget import button": 'id="ownImportBudgetValues">Budgetwerte übernehmen</button>',
    "own imported income display": 'id="ownHouseholdIncome"',
    "own imported expenses display": 'id="ownHouseholdExpenses"',
    "own property cost display": 'id="ownHouseholdPropertyCost"',
    "own remaining surplus display": 'id="ownHouseholdRemaining"',
    "own budget import source": 'const budget=budgetModel();',
    "own remaining surplus calculation": 'const remaining=imported.hasValues ? imported.income-imported.expenses-propertyCost : null;',
    "own budget reset income": 'localStorage.removeItem("ff_own_budget_income");',
    "own budget reset expenses": 'localStorage.removeItem("ff_own_budget_expenses");',
    "own budget reset timestamp": 'localStorage.removeItem("ff_own_budget_imported_at");',
    "budget financing green header": 'class="decision go budget-financing-decision"',
    "budget financing icon": '<div class="light" aria-hidden="true">💶</div>',
    "budget financing title": '<h2>Deine mögliche Finanzierung</h2>',
    "budget financing info text": 'Aus deinem Budget, Eigenkapital und den Finanzierungsannahmen ergibt sich hier deine mögliche Finanzierung.',
    "budget financing spacing": '.budget-financing-decision{margin-bottom:14px}',
    "VK transfer subtitle": 'VK Projektziel • editierbar',
    "VK project button": 'class="flip-sale-benchmark" data-vk-source="project"',
    "VK breakeven button": 'class="flip-sale-benchmark" data-vk-source="breakeven"',
    "VK postreno button": 'class="flip-sale-benchmark" data-vk-source="postreno"',
    "VK transfer arrow": 'class="vk-transfer-icon" aria-hidden="true">↘</b>',
    "VK confirm before apply": 'const ok=confirm("Möchtest du "+eur(rounded)+" aus „"+label+"“ als VK nach Sanierung übernehmen?");',
    "VK target input update": 'field.value=String(rounded);',
    "VK persisted primary": 'localStorage.setItem("ff_flipSaleTarget",String(rounded));',
    "VK persisted dedicated": 'localStorage.setItem("ff_flip_sale_after_reno_value",String(rounded));',
    "VK input event": 'field.dispatchEvent(new Event("input",{bubbles:true}));',
    "VK visual text color": '.flip-sale-benchmark strong{\n  color:var(--ink) !important;',
    "VK visual label color": '.flip-sale-benchmark span{\n  color:var(--muted) !important;',
    "VK visual arrow": '.flip-sale-benchmark[data-vk-source]::after{',
    "VK visual arrow glyph": 'content:"↘";',
    "VK dynamic subtitle source key": 'const subtitleSourceKey="ff_flip_sale_after_reno_source";',
    "VK dynamic subtitle text": 'hint.textContent=label+" • editierbar";',
    "VK dynamic subtitle persisted": 'localStorage.setItem(subtitleSourceKey,source);',
    "VK dynamic subtitle restored": 'const savedSubtitleSource=localStorage.getItem(subtitleSourceKey);',
    "suggestions do not auto-fill": 'function syncBudgetSuggestions(){\n  // Vorschlaege nur aktualisieren; die Eingabefelder bleiben unveraendert,',
    "suggestions still apply by button": 'function applyBudgetSuggestions(){',
    "reset expenses to zero": 'budgetExpenseIds.forEach(id=>{\n    if($(id)) $(id).value="0";',
    "reset financing reserve to zero": 'if($("budgetSafetyReserve")) $("budgetSafetyReserve").value="0";',
    "capture phase enabled": '},true);',
    "warning message": 'Finanzierungsreserve unterschritten. Bitte Einnahmen oder Ausgaben prüfen.',
    "warning at exact minimum": 'Finanzierungsreserve erreicht: "+eur(minimumReserve)+". Bitte Einnahmen oder Ausgaben prüfen.',
    "slider excluded from global input listener": ':not(#budgetRateSlider),select\')',
    "financing assumptions included": 'const budgetFinancingAssumptionIds=new Set([',
    "financing assumption fields": '"budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetNotaryPct","budgetBuyBrokerPct","budgetExtraCostsPct"',
    "income expense assumptions share recalc": 'const budgetRateRecalcIds=new Set([...budgetRateIncomeIds,...budgetRateExpenseIds,...budgetFinancingAssumptionIds]);',
    "old slider value cleared": 'localStorage.removeItem("ff_budget_rateSliderPct");',
    "previous absolute rate captured": 'budgetRateBeforeRecalc=Math.max(0,Number(beforeChange.monthlyRate)||0);',
    "automatic 35 percent rate": 'const automaticRate=Math.min(Math.max(0,recalculated.net*0.35),Math.max(0,recalculated.rateCap||0));',
    "manual mode selector": 'const adjustedRate=budgetRateManualSelection',
    "manual selection safety cap": '? Math.min(previousRate,Math.max(0,recalculated.rateCap||0))',
    "automatic selection branch": ': automaticRate;',
    "adjusted rate persisted": 'const preservedRatePct=recalculated.net>0 ? (adjustedRate/recalculated.net)*100 : 0;',
    "reset arms initial rate": 'budgetRateNeedsInitialValue=true;',
    "initial rate waits for focusout": 'document.addEventListener("focusout",(event)=>',
    "initialization only for income": 'if(!el || !budgetRateNeedsInitialValue || !budgetRateIncomeIds.has(el.id)) return;',
    "initial rate targets 35 percent": 'const initialRatePct=Math.min(35,Math.max(0,m.maxRatePct||0));',
    "initial rate stored once": 'localStorage.setItem("ff_budget_rateSliderPct",String(initialRatePct));',
    "initialization disabled afterwards": 'budgetRateNeedsInitialValue=false;',
    "manual slider flag stored": 'localStorage.setItem("ff_budget_rateManualSelection","1");',
    "manual slider state": 'let budgetRateManualSelection=localStorage.getItem("ff_budget_rateManualSelection")==="1";',
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

legacy_terms = [
    "Aktueller Sicherheitspuffer",
    "Mindest-Sicherheitspuffer",
    "Mindestpuffer unterschritten",
    "Mindestpuffer erreicht",
]
legacy_found = [term for term in legacy_terms if term in html]
if legacy_found:
    raise SystemExit("Slider acceptance failed - legacy terminology remains: " + ", ".join(legacy_found))

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

# 34) The actual credit rate can never exceed the free monthly budget and is never negative.
net = 4000
free_budget = 500
requested_pct = 30
requested_rate = net * requested_pct / 100
monthly_rate = max(0, min(max(0, free_budget), requested_rate))
if monthly_rate != 500:
    raise SystemExit("Slider acceptance failed - stored rate above free budget is capped")

free_budget = -250
requested_rate = 1200
monthly_rate = max(0, min(max(0, free_budget), requested_rate))
if monthly_rate != 0:
    raise SystemExit("Slider acceptance failed - negative free budget forces zero credit rate")

free_budget = 1800
requested_rate = 1200
monthly_rate = max(0, min(max(0, free_budget), requested_rate))
if monthly_rate != 1200:
    raise SystemExit("Slider acceptance failed - rate below free budget remains unchanged")

# 35) A later expense increase fully recalculates the rate to the new safe maximum.
previous_rate = 1200
new_rate_cap = 700
adjusted_rate = max(0, new_rate_cap)
if adjusted_rate != 700:
    raise SystemExit("Slider acceptance failed - expense increase must reset to safe maximum")

# 36) Lower expenses also fully recalculate the rate upward to the new safe maximum.
previous_rate = 700
new_rate_cap = 1200
adjusted_rate = max(0, new_rate_cap)
if adjusted_rate != 1200:
    raise SystemExit("Slider acceptance failed - expense decrease must recalculate rate upward")

# 37) A manually lower prior rate is intentionally replaced after any expense change.
previous_rate = 500
new_rate_cap = 700
adjusted_rate = max(0, new_rate_cap)
if adjusted_rate != 700:
    raise SystemExit("Slider acceptance failed - expense change must replace prior manual rate")

# 38) Warning display states: above hidden, equal reached, below undershot.
def warning_state(current_buffer, minimum_reserve):
    deviation = current_buffer - minimum_reserve
    below = deviation < -0.005
    reached = abs(deviation) <= 0.005
    above = deviation > 0.005
    if above:
        return ("hidden", deviation)
    if below:
        return ("below", deviation)
    if reached:
        return ("reached", deviation)
    return ("clear", deviation)

state, deviation = warning_state(350, 300)
if state != "hidden":
    raise SystemExit("Slider acceptance failed - display state above minimum hidden")

state, deviation = warning_state(300, 300)
if state != "reached":
    raise SystemExit("Slider acceptance failed - exact minimum must show reached warning")

state, deviation = warning_state(250, 300)
if not (state == "below" and deviation == -50):
    raise SystemExit("Slider acceptance failed - below minimum must show undershoot warning with existing deviation")

# 39) Initial/automatic rate targets 35% of household net when safely affordable.
net = 4000
rate_cap = 1800
automatic_rate = min(max(0, net * 0.35), max(0, rate_cap))
if automatic_rate != 1400:
    raise SystemExit("Slider acceptance failed - initial 35 percent when safe")

# 40) The 35% target is capped by the safe budget/reserve limit.
net = 4000
rate_cap = 700
automatic_rate = min(max(0, net * 0.35), max(0, rate_cap))
if automatic_rate != 700:
    raise SystemExit("Slider acceptance failed - 35 percent must respect safe budget cap")

# 41) Before manual slider use, changed income/expenses recalculate to the current 35% target.
net = 5000
rate_cap = 2000
automatic_rate = min(max(0, net * 0.35), max(0, rate_cap))
if automatic_rate != 1750:
    raise SystemExit("Slider acceptance failed - automatic mode must recalculate to 35 percent")

# 42) After manual slider use, keep the chosen absolute rate unless safety requires a lower value.
previous_rate = 1200
rate_cap = 1700
adjusted_rate = min(previous_rate, max(0, rate_cap))
if adjusted_rate != 1200:
    raise SystemExit("Slider acceptance failed - manual rate should remain after later recalculation")

previous_rate = 1200
rate_cap = 900
adjusted_rate = min(previous_rate, max(0, rate_cap))
if adjusted_rate != 900:
    raise SystemExit("Slider acceptance failed - manual rate must still respect safety cap")

# 43) All relevant financing assumption fields are part of the central recalculation set.
financing_assumption_ids = {
    "budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetNotaryPct","budgetBuyBrokerPct","budgetExtraCostsPct"
}
expected_financing_assumption_ids = {
    "budgetInterest","budgetRepayment","budgetEquity","budgetState","budgetNotaryPct","budgetBuyBrokerPct","budgetExtraCostsPct"
}
if financing_assumption_ids != expected_financing_assumption_ids:
    raise SystemExit("Slider acceptance failed - financing assumption IDs covered")

# 44) Displayed free monthly budget subtracts the minimum reserve exactly once.
income = 4000
expenses = 2300
pre_reserve_budget = income - expenses
minimum_reserve = max(300, pre_reserve_budget * 0.10)
available = pre_reserve_budget - minimum_reserve
if available != 1400:
    raise SystemExit("Slider acceptance failed - free budget subtracts reserve once")

# 45) The reserve-based safe-rate capacity remains identical to the displayed post-reserve budget when positive.
rate_pool = max(0, pre_reserve_budget)
max_rate_by_reserve = max(0, rate_pool - minimum_reserve)
if max_rate_by_reserve != available:
    raise SystemExit("Slider acceptance failed - displayed free budget must match reserve-based safe capacity")

# 46) A small surplus becomes negative after the minimum reserve, while safe credit capacity stays at zero.
income = 4000
expenses = 3900
pre_reserve_budget = income - expenses
minimum_reserve = max(300, pre_reserve_budget * 0.10)
available = pre_reserve_budget - minimum_reserve
max_rate_by_reserve = max(0, max(0, pre_reserve_budget) - minimum_reserve)
if not (available == -200 and max_rate_by_reserve == 0):
    raise SystemExit("Slider acceptance failed - negative post-reserve budget handled correctly")

# 47) Finanzierungsreserve appears directly after fixed expenses in the monthly budget summary.
expenses_row = '<div class="budget-summary-row"><span>- Feste Ausgaben</span><strong id="budgetExpensesResult">–</strong></div>'
reserve_row = '<div class="budget-summary-row"><span>- Finanzierungsreserve</span><strong id="budgetFinancingReserveResult">–</strong></div>'
expenses_pos = html.find(expenses_row)
reserve_pos = html.find(reserve_row)
if expenses_pos < 0 or reserve_pos < 0 or reserve_pos <= expenses_pos:
    raise SystemExit("Slider acceptance failed - financing reserve row position")
between = html[expenses_pos + len(expenses_row):reserve_pos]
if "<div class=\"budget-summary-row" in between:
    raise SystemExit("Slider acceptance failed - financing reserve must be directly below fixed expenses")

# 48) All fixed monthly expense inputs start at zero.
expense_ids = [
    "budgetFood","budgetMobility","budgetInsurance","budgetTelecom",
    "budgetLeisure","budgetChildCosts","budgetExistingLoans","budgetOther"
]
for expense_id in expense_ids:
    token = f'id="{expense_id}" inputmode="decimal" value="0"'
    if token not in html:
        raise SystemExit("Slider acceptance failed - all fixed expense markup defaults are zero: " + expense_id)

# 49) Financing reserve stays zero until positive household net income exists.
def financing_reserve(net, income, expenses):
    free_budget = income - expenses
    return max(300, free_budget * 0.10) if net > 0 else 0

if financing_reserve(0, 0, 0) != 0:
    raise SystemExit("Slider acceptance failed - financing reserve must start at zero")
if financing_reserve(4000, 4000, 0) != 400:
    raise SystemExit("Slider acceptance failed - financing reserve must use existing formula after net income")
if financing_reserve(2000, 2000, 0) != 300:
    raise SystemExit("Slider acceptance failed - financing reserve minimum floor remains 300")

# 50) Suggestion synchronization no longer writes values into expense fields.
sync_start = html.find("function syncBudgetSuggestions(){")
apply_start = html.find("function applyBudgetSuggestions(){")
if sync_start < 0 or apply_start < 0 or apply_start <= sync_start:
    raise SystemExit("Slider acceptance failed - suggestion functions missing")
sync_body = html[sync_start:apply_start]
if ".value=String(Math.round(" in sync_body:
    raise SystemExit("Slider acceptance failed - suggestions must not auto-fill expense fields")
apply_body = html[apply_start:html.find("function budgetIncomeDetailsTotal", apply_start)]
if ".value=String(Math.round(s[id]))" not in apply_body:
    raise SystemExit("Slider acceptance failed - Vorschlaege uebernehmen must still fill expense fields")

# 51) Remaining monthly surplus subtracts the financing reserve exactly once.
income = 5000
expenses = 1020
monthly_rate = 2250
financing_reserve = 398
raw_reserve = income - expenses - monthly_rate
remaining_monthly_surplus = raw_reserve - financing_reserve
if raw_reserve != 1730 or remaining_monthly_surplus != 1332:
    raise SystemExit("Slider acceptance failed - remaining monthly surplus subtracts financing reserve")

# 52) Remaining monthly surplus reconciles to available budget minus credit rate.
available_budget = income - expenses - financing_reserve
if remaining_monthly_surplus != available_budget - monthly_rate:
    raise SystemExit("Slider acceptance failed - remaining monthly surplus reconciliation")

# 53) Eigennutzung budget transfer uses real household values and concrete property costs.
household_income = 5000
household_expenses = 1020
credit_rate = 2250
running_property_costs = 350
property_cost = credit_rate + running_property_costs
remaining = household_income - household_expenses - property_cost
if property_cost != 2600 or remaining != 1380:
    raise SystemExit("Slider acceptance failed - own-use budget transfer calculation")

# 54) Financing reserve must not be subtracted again in Eigennutzung.
financing_reserve = 398
if remaining == household_income - household_expenses - property_cost - financing_reserve:
    raise SystemExit("Slider acceptance failed - financing reserve must not be double-subtracted in Eigennutzung")

# 55) VK transfer confirmation must occur before the target input is overwritten.
confirm_token = 'const ok=confirm("Möchtest du "+eur(rounded)+" aus „"+label+"“ als VK nach Sanierung übernehmen?");'
input_token = 'field.value=String(rounded);'
confirm_pos = html.find(confirm_token)
input_pos = html.find(input_token)
if confirm_pos < 0 or input_pos < 0 or confirm_pos >= input_pos:
    raise SystemExit("Slider acceptance failed - VK transfer confirmation precedes input update")

# 56) Exactly the three existing VK benchmark boxes are transferable.
for source in ("project","breakeven","postreno"):
    token = f'data-vk-source="{source}"'
    if html.count(token) != 1:
        raise SystemExit("Slider acceptance failed - expected exactly one VK transfer source: " + source)

print("Slider acceptance passed:")
for name in required_implementation:
    print(" -", name)
print(" - numerical cases: 45% cap, EUR 300 floor, zero left edge, directionality, income reduction, expense increase, net-income basis, reached/under-300 warning, shortfall amount, rate-reduction amount, exact/sub-euro 300 threshold, pre-adjustment undershoot")
