from pathlib import Path
import re
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else '_site/index.html')
s = p.read_text()
pattern = r'<section class="card">\s*<div class="budget-section-title">.*?<h2>2\. Feste monatliche Ausgaben</h2>.*?</section>'
match = re.search(pattern, s, re.S)
if not match:
    raise SystemExit('Budget expenses section missing')
section = match.group()
button = '<button type="button" class="budget-apply-btn" id="budgetApplySuggestions">Vorschläge übernehmen</button>'
if section.count(button) != 1:
    raise SystemExit('Budget apply button missing or duplicated')
section = section.replace('<section class="card">', '<section class="card" id="budgetExpensesSection">', 1)
section = section.replace(button, '<button type="button" class="plus-btn" id="budgetExpensesToggle" aria-expanded="false" aria-controls="budgetExpensesBody" aria-label="Feste monatliche Ausgaben öffnen">+</button>', 1)
section = section.replace('Die Vorschläge passen sich automatisch an Erwachsene und Kinder an. Manuell geänderte Werte bleiben erhalten.', 'Richtwerte nach Haushaltsgröße. Erst mit „Vorschläge übernehmen“ werden sie als echte Werte berechnet.', 1)
section = section.replace('<div class="budget-expense-list">', '<div id="budgetExpensesBody" hidden>\n<div class="budget-expenses-toolbar">' + button + '</div>\n<div class="budget-expense-list">', 1)
section = section.replace('</section>', '</div>\n</section>', 1)
s = s[:match.start()] + section + s[match.end():]
style = '''<style id="budget-expenses-toggle-v8331">
#budgetExpensesSection .budget-section-title{display:grid!important;grid-template-columns:minmax(0,1fr) 34px;gap:12px;align-items:center!important}
#budgetExpensesSection .budget-section-title h2{margin:0}
#budgetExpensesSection .budget-section-title .sub{margin:5px 0 0!important}
#budgetExpensesToggle{justify-self:end;align-self:center}
#budgetExpensesBody[hidden]{display:none!important}
#budgetExpensesBody{margin-top:16px}
.budget-expenses-toolbar{display:flex;justify-content:flex-end;margin-bottom:12px}
@media(max-width:420px){#budgetExpensesSection .budget-section-title{gap:8px}}
</style>'''
s = s.replace('</head>', style + '\n</head>', 1)
script = '''<script id="budget-expenses-toggle-script-v8331">
(function(){
  const button=document.getElementById("budgetExpensesToggle");
  const body=document.getElementById("budgetExpensesBody");
  button.addEventListener("click",function(){
    const open=body.hidden;
    body.hidden=!open;
    button.textContent=open ? "−" : "+";
    button.setAttribute("aria-expanded",String(open));
    button.setAttribute("aria-label","Feste monatliche Ausgaben "+(open ? "schließen" : "öffnen"));
  });
})();
</script>'''
s = s.replace('</body>', script + '\n</body>', 1)
p.write_text(s)
admin = p.parent / 'admin.html'
admin.write_text(admin.read_text().replace('V8.330', 'V8.331'))
print('V8.331 budget expenses collapse control applied')
