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
    '.budget-rate-guidance{margin-top:8px;padding:9px 10px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0;color:#52627a;font-size:11px;line-height:1.45}\n.budget-result-card.budget-loan-highlight{background:#fff7cc;border-color:#f1cf55;box-shadow:0 0 0 1px rgba(241,207,85,.18) inset}\n.budget-summary-row.rate-status-green{background:#eaf8ef;border-color:#8fd3a5}\n.budget-summary-row.rate-status-yellow{background:#fff7cc;border-color:#f1cf55}\n.budget-summary-row.rate-status-red{background:#fdecec;border-color:#e8a0a0}\n.budget-summary-row.rate-status-green .budget-rate-ratio{color:#287a43}\n.budget-summary-row.rate-status-yellow .budget-rate-ratio{color:#8a6810}\n.budget-summary-row.rate-status-red .budget-rate-ratio{color:#a33a3a}',
    "assumptions CSS"
)

# V8.170: Neutral style for the residual-debt explanatory note.
replace_once(
    '.budget-note{margin-top:12px;padding:11px 12px;border-radius:13px;background:#fef3c7;border:1px solid #facc15;color:#475569;font-size:11px;line-height:1.45}',
    '.budget-note{margin-top:12px;padding:11px 12px;border-radius:13px;background:#fef3c7;border:1px solid #facc15;color:#475569;font-size:11px;line-height:1.45}\\n'
    '.budget-note.neutral-note{background:#f8fafc;border-color:#d8dee8;color:#5f6b7a}',
    "neutral note CSS"
)

# Apply neutral styling to the residual-debt note if the old markup is still present.
# The source HTML may already contain the neutral-note class after earlier patches, so
# this step must be idempotent and must not abort the entire Pages build.
old_residual_note = (
    '        <div class="budget-note">\\n'
    '          Restschulden werden hier als Annuitätendarlehen mit konstanter Monatsrate und konstantem Zinssatz modelliert. Tatsächliche Konditionen, Zinsbindungen und Anschlussfinanzierungen können abweichen.\\n'
    '        </div>'
)
new_residual_note = (
    '        <div class="budget-note neutral-note">\\n'
    '          Restschulden werden hier als Annuitätendarlehen mit konstanter Monatsrate und konstantem Zinssatz modelliert. Tatsächliche Konditionen, Zinsbindungen und Anschlussfinanzierungen können abweichen.\\n'
    '        </div>'
)
if old_residual_note in s:
    s = s.replace(old_residual_note, new_residual_note, 1)


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
    '          <div class="budget-summary-row highlight" id="budgetRateRow"><span>Maximal tragbare Kreditrate <span class="budget-rate-ratio" id="budgetRateRatio"></span></span><strong id="budgetRate">–</strong></div>\n'
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
  }
  if($("budgetRateRow")){
    const row = $("budgetRateRow");
    row.classList.remove("rate-status-green","rate-status-yellow","rate-status-red");
    if(m.net > 0){
      row.classList.add(budgetRatePct <= 30 ? "rate-status-green" : (budgetRatePct <= 35 ? "rate-status-yellow" : "rate-status-red"));
    }
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


# Ensure the residual-debt explanatory note is neutral in the final HTML.
residual_text = "Restschulden werden hier als Annuitätendarlehen mit konstanter Monatsrate und konstantem Zinssatz modelliert. Tatsächliche Konditionen, Zinsbindungen und Anschlussfinanzierungen können abweichen."
residual_plain = '<div class="budget-note">\n          ' + residual_text
residual_neutral = '<div class="budget-note neutral-note">\n          ' + residual_text
if residual_plain in s:
    s = s.replace(residual_plain, residual_neutral, 1)

# V8.170: Budget UI refinements.
replace_once(
    '<h2>3. Weitere Annahmen</h2>',
    '<h2>3. Annahme zur möglichen Finanzierung</h2>',
    "assumptions title"
)

replace_once(
    '<div class="budget-result-card"><div class="name">Max. Darlehen</div><div class="value" id="budgetLoan">–</div><div class="note">aus maximal tragbarer Rate, Zins und Tilgung</div></div>',
    '<div class="budget-result-card budget-loan-highlight"><div class="name">Max. Darlehen</div><div class="value" id="budgetLoan">–</div><div class="note">aus maximal tragbarer Rate, Zins und Tilgung</div></div>',
    "max loan highlight"
)

replace_once(
    '.reno-input-row{display:grid;grid-template-columns:1fr 56px;gap:9px}',
    '.reno-input-row{display:grid;grid-template-columns:minmax(0,1fr) 56px;gap:9px;width:100%}\\n'
    '.reno-input-row .input-wrap{min-width:0;width:100%}\\n'
    '@media(max-width:520px){.reno-input-row{grid-template-columns:minmax(0,1fr) 50px;gap:8px;width:100%}}',
    "mobile plus-row width"
)

# V8.170: Default location for Fix & Flip and Eigennutzung.
replace_once(
    'stateEl.value="Schleswig-Holstein";',
    'stateEl.value="Hamburg";',
    "default state Hamburg"
)
replace_once(
    '<input id="marketLocation" inputmode="text" placeholder="z. B. 22850 Norderstedt">',
    '<input id="marketLocation" inputmode="text" value="20095 Hamburg" placeholder="z. B. 20095 Hamburg">',
    "default market location Hamburg"
)

path.write_text(s, encoding="utf-8")
print("V8.170 budget UI patch applied")
