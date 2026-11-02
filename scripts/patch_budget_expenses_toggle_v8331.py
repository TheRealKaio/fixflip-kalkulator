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
# Assign semantics before initial paint: no JS class substitution needed.
note_text = 'Richtwerte nach Haushaltsgröße. Erst mit „Vorschläge übernehmen“ werden sie als echte Werte berechnet.'
note_at = section.find(note_text)
if note_at < 0:
    raise SystemExit('Budget guidance missing')
tag_start = section.rfind('<', 0, note_at)
tag_end = section.find('>', tag_start)
tag = section[tag_start:tag_end+1]
if not re.search(r'\bsub\b', tag):
    raise SystemExit('Legacy guidance class not found')
new_tag = re.sub(r'\bsub\b', 'budget-expense-guidance', tag)
section = section[:tag_start] + new_tag + section[tag_end+1:]
section = section.replace('<div class="budget-expense-list">', '<div id="budgetExpensesBody" hidden>\n<div class="budget-expenses-toolbar">' + button + '</div>\n<div class="budget-expense-list">', 1)
section = section.replace('</section>', '</div>\n</section>', 1)
s = s[:match.start()] + section + s[match.end():]
style = '''<style id="budget-expenses-toggle-v8331">
#budgetExpensesSection .budget-section-title{display:grid!important;grid-template-columns:minmax(0,1fr) 34px;gap:12px;align-items:center!important}
#budgetExpensesSection .budget-section-title h2{margin:0}
#budgetExpensesToggle{justify-self:end;align-self:center}
#budgetExpensesBody[hidden]{display:none!important}
#budgetExpensesBody{margin-top:16px}
.budget-expenses-toolbar{display:flex;justify-content:flex-end;margin-bottom:12px}
#budgetExpensesSection .budget-expense-guidance{
 grid-column:1 / -1!important;
 flex:0 0 100%!important;
 align-self:stretch!important;
 margin-left:0!important;margin-right:0!important;
 left:auto!important;right:auto!important;

 display:block!important;position:static!important;width:100%!important;max-width:none!important;
 text-align:center!important;color:#667085;
 margin:14px 0 0!important;padding:0 0 13px!important;
 border-bottom:1px solid #e2e8f0!important;line-height:1.5!important;
}

@media(max-width:420px){#budgetExpensesSection .budget-section-title{gap:8px}}
</style>'''
s = s.replace('</head>', style + '\n</head>', 1)
script = '''<script id="budget-expenses-toggle-script-v8331">
(function(){
  const button=document.getElementById("budgetExpensesToggle");
  const body=document.getElementById("budgetExpensesBody");
  function positionGuidance(){
    const section=document.getElementById("budgetExpensesSection");
    if(!section)return;
    const original=section.querySelector(".budget-expense-guidance");
    if(!original)return;
    const total=document.getElementById("budgetSuggestionTotal");
    const toolbar=section.querySelector(".budget-expenses-toolbar");
    const target=toolbar || section.querySelector("#budgetExpensesBody");
    // Move the note outside the narrow action/total group.
    // This keeps both the text and its bottom border full-width.
    if(target && original.previousElementSibling!==target){
      target.insertAdjacentElement("afterend",original);
    }
    // Typography belongs solely to the central site-settings stylesheet.
    // Remove inline legacy font-size declarations from this component.

  }
  positionGuidance();
  window.addEventListener("nic-settings-updated",positionGuidance);
  requestAnimationFrame(positionGuidance);
  window.addEventListener("load",positionGuidance,{once:true});
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
