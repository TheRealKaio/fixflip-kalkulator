from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
s = path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f"{label} target not found")
    s = s.replace(old, new, 1)

replace_once(
    '.market-check-card.collapsed .market-check-body{display:none}',
    '.market-check-card.collapsed .market-check-body{display:none}\n'
    '.budget-assumptions-body{display:block}\n'
    '.budget-assumptions-card.collapsed .budget-assumptions-body{display:none}\n'
    '.budget-assumptions-card .market-check-head h2{margin:0}\n'
    '.budget-rate-ratio{font-size:11px;font-weight:700;color:#365b96;margin-left:4px}\n'
    '.budget-rate-guidance{margin-top:8px;padding:9px 10px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;color:#52627a;font-size:11px;line-height:1.45}',
    "assumptions CSS"
)

old_head = '''      <section class="card">
        <h2>3. Weitere Annahmen</h2>
        <div class="budget-grid three">'''
new_head = '''      <section class="card budget-assumptions-card collapsed" id="budgetAssumptionsSection">
        <div class="market-check-head">
          <h2>3. Weitere Annahmen</h2>
          <button type="button" class="plus-btn" id="budgetAssumptionsToggle" aria-expanded="false" aria-controls="budgetAssumptionsBody" aria-label="Weitere Annahmen öffnen">+</button>
        </div>
        <div class="budget-assumptions-body" id="budgetAssumptionsBody">
        <div class="budget-grid three">'''
replace_once(old_head, new_head, "assumptions header")

old_note = '''        <div class="budget-note">
          <strong>Hinweis:</strong> Der Budgetanteil bestimmt, welcher Anteil deines frei verfügbaren Monatsbudgets maximal für die Kreditrate eingesetzt wird. Der verbleibende Anteil bleibt als zusätzlicher monatlicher Puffer. Die Berechnung ist eine Orientierung und keine Finanzierungszusage einer Bank.
        </div>
      </section>'''
new_note = '''        <div class="budget-note">
          <strong>Hinweis:</strong> Der Budgetanteil bestimmt, welcher Anteil deines frei verfügbaren Monatsbudgets maximal für die Kreditrate eingesetzt wird. Der verbleibende Anteil bleibt als zusätzlicher monatlicher Puffer. Die Berechnung ist eine Orientierung und keine Finanzierungszusage einer Bank.
        </div>
        </div>
      </section>'''
replace_once(old_note, new_note, "assumptions body")

replace_once(
    '          <div class="budget-summary-row highlight"><span>Maximal tragbare Kreditrate</span><strong id="budgetRate">–</strong></div>',
    '          <div class="budget-summary-row highlight"><span>Maximal tragbare Kreditrate <span class="budget-rate-ratio" id="budgetRateRatio"></span></span><strong id="budgetRate">–</strong></div>\n'
    '          <div class="budget-rate-guidance" id="budgetRateGuidance">Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung.</div>',
    "rate display"
)

old_render = '  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);'
new_render = '''  if($("budgetRate")) $("budgetRate").textContent=eur(m.monthlyRate);
  const budgetRatePct = m.net > 0 ? (m.monthlyRate / m.net) * 100 : 0;
  if($("budgetRateRatio")){
    $("budgetRateRatio").textContent = m.net > 0
      ? "(ca. " + new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(budgetRatePct) + " % vom Haushaltsnetto)"
      : "";
  }
  if($("budgetRateGuidance")){
    let budgetRateStatus = "";
    if(m.net > 0){
      budgetRateStatus = budgetRatePct <= 30 ? "komfortabel" : (budgetRatePct <= 35 ? "solide" : "erhöhte Belastung");
    }
    $("budgetRateGuidance").textContent = "Orientierung: bis 30 % komfortabel · 30–35 % solide · über 35 % erhöhte Belastung." + (budgetRateStatus ? " Aktuelle Einordnung: " + budgetRateStatus + "." : "");
  }'''
replace_once(old_render, new_render, "rate render")

marker = 'if($("budgetApplySuggestions")){'
toggle_js = '''if($("budgetAssumptionsToggle") && $("budgetAssumptionsSection")){
  $("budgetAssumptionsToggle").addEventListener("click",()=>{
    const section=$("budgetAssumptionsSection");
    const collapsed=!section.classList.contains("collapsed");
    section.classList.toggle("collapsed",collapsed);
    $("budgetAssumptionsToggle").textContent=collapsed ? "+" : "−";
    $("budgetAssumptionsToggle").setAttribute("aria-expanded",collapsed ? "false" : "true");
    $("budgetAssumptionsToggle").setAttribute("aria-label",collapsed ? "Weitere Annahmen öffnen" : "Weitere Annahmen schließen");
  });
}

'''
replace_once(marker, toggle_js + marker, "assumptions toggle JS")

path.write_text(s, encoding="utf-8")
print("V8.165 budget UI patch applied")
