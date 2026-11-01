"""Static integration contract for all five non-destructive step navigators."""
from pathlib import Path
js=Path('assets/immocheck-ui-steps.js').read_text()
css=Path('assets/immocheck-ui-steps.css').read_text()
wf=Path('.github/workflows/pages.yml').read_text()
for name,selector in [('budget','#budgetSection'),('rent','#rentSection'),('own','#dealCalculatorContent'),('flip','#dealCalculatorContent')]:
    assert "'"+name+"':'"+selector+"'" in js, name
assert "location.pathname.includes('finanzierungsrechner')" in js
assert "document.querySelector('main.section')" in js
assert 'cards.length!==6' in js
assert "root.querySelector('#repayChart')" in js
assert "root.querySelector('#rateChart')" in js
assert "root.querySelector('#refinanceChange')" in js
assert ".nic-step-inactive" in css
for route in ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']:
    assert route in wf,route
assert 'cp assets/immocheck-ui-steps.js' in wf
assert 'cp assets/immocheck-ui-steps.css' in wf
print('Five-route navigation source contract passed (not a browser test).')
