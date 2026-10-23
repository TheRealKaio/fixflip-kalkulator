from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else '_site/index.html')
s = p.read_text()
replacements = {
    '<button id="recalc" class="bottom-primary">Deal neu berechnen</button>': '<button id="recalc" class="bottom-primary">Fix und Flip neu kalkulieren</button>',
    '$("recalc").textContent = budget ? "Budget neu berechnen" : "Deal neu berechnen";': '$("recalc").textContent = budget ? "Budget neu kalkulieren" : own ? "Eigennutzung neu kalkulieren" : "Fix und Flip neu kalkulieren";',
    'recalc.textContent="Vermietung neu berechnen";': 'recalc.textContent="Vermietung neu kalkulieren";',
    'recalc.textContent=currentDealType()==="budget" ? "Budget neu berechnen" : "Deal neu berechnen";': 'recalc.textContent=currentDealType()==="budget" ? "Budget neu kalkulieren" : currentDealType()==="own" ? "Eigennutzung neu kalkulieren" : "Fix und Flip neu kalkulieren";',
}
for old, new in replacements.items():
    if s.count(old) != 1:
        raise SystemExit('Calculator button anchor missing or duplicated: ' + old)
    s = s.replace(old, new, 1)
p.write_text(s)
admin = p.parent / 'admin.html'
admin.write_text(admin.read_text().replace('V8.331', 'V8.332'))
print('V8.332 calculator-specific reset button names applied')
