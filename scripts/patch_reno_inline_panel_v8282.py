from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Existing modal markup is reused as an inline expandable panel.
modal='''<div class="sheet-backdrop" id="renoBackdrop">
  <div class="reno-sheet">
    <div class="handle"></div>
    <div class="reno-head">
      <div>
        <h3>Sanierung aufteilen</h3>
        <p class="sub" style="margin:4px 0 0">Richtwerte werden aus der Wohnfläche berechnet. Die Summe oben enthält den Sanierungs-Puffer.</p>
      </div>
      <div class="reno-total-pill" id="renoSheetTotal">0 €</div>
    </div>
    <div class="reno-note">
      <strong>So funktioniert es:</strong> m²-Positionen werden automatisch aus deiner Wohnfläche vorbelegt.
      Pauschal- und Stückpositionen starten bei 0 €. Jeden Betrag kannst du überschreiben.
    </div>
    <div id="tradeList" class="trade-list"></div>
    <div class="reno-actions">
      <button class="reset-btn" id="resetTrades" type="button">Standard zurücksetzen</button>
      <button class="save-reno-btn" id="saveTrades" type="button">Übernehmen</button>
    </div>
  </div>
</div>

'''

if modal not in s:
    raise SystemExit("V8.282 renovation modal markup missing")
s=s.replace(modal,"",1)

inline='''        <div class="reno-inline-panel" id="renoBackdrop">
          <div class="reno-sheet">
            <div class="reno-head">
              <div>
                <h3>Sanierung aufteilen</h3>
                <p class="sub" style="margin:4px 0 0">Richtwerte werden aus der Wohnfläche berechnet. Die Summe oben enthält den Sanierungs-Puffer.</p>
              </div>
              <div class="reno-total-pill" id="renoSheetTotal">0 €</div>
            </div>
            <div class="reno-note">
              <strong>So funktioniert es:</strong> m²-Positionen werden automatisch aus deiner Wohnfläche vorbelegt.
              Pauschal- und Stückpositionen starten bei 0 €. Jeden Betrag kannst du überschreiben.
            </div>
            <div id="tradeList" class="trade-list"></div>
            <div class="reno-actions">
              <button class="reset-btn" id="resetTrades" type="button">Standard zurücksetzen</button>
              <button class="save-reno-btn" id="saveTrades" type="button">Übernehmen</button>
            </div>
          </div>
        </div>
'''

quick_anchor='''        <div class="field"><label>Laufende Kosten pro Monat</label><div class="input-wrap"><input id="holding" inputmode="decimal" value="740"><span class="unit">€</span></div><div class="mini">WEG, Energie, Versicherung etc.</div></div>
      </div>'''
replace_once(
    quick_anchor,
    '''        <div class="field"><label>Laufende Kosten pro Monat</label><div class="input-wrap"><input id="holding" inputmode="decimal" value="740"><span class="unit">€</span></div><div class="mini">WEG, Energie, Versicherung etc.</div></div>
'''+inline+'''      </div>''',
    "insert inline renovation panel"
)

# Accessibility: toggle communicates its expanded state.
replace_once(
    '<button class="plus-btn" id="openReno" type="button" aria-label="Sanierungsgewerke öffnen">+</button>',
    '<button class="plus-btn" id="openReno" type="button" aria-label="Sanierungsgewerke öffnen" aria-expanded="false" aria-controls="renoBackdrop">+</button>',
    "renovation toggle aria"
)

# Inline panel styling; no fixed backdrop, no bottom sheet, no sticky actions.
css_anchor='.reno-sheet{width:min(520px,100%);max-height:88vh;overflow:auto;background:#fff;border-radius:26px 26px 0 0;padding:10px 16px calc(24px + env(safe-area-inset-bottom));box-shadow:0 -20px 60px rgba(0,0,0,.18)}'
if css_anchor not in s:
    raise SystemExit("V8.282 renovation sheet CSS anchor missing")

inline_css='''.reno-inline-panel{display:none;grid-column:1/-1;width:100%;margin-top:2px}
.reno-inline-panel.show{display:block}
.reno-inline-panel .reno-sheet{width:100%;max-height:none;overflow:visible;background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;padding:14px;box-shadow:none}
.reno-inline-panel .reno-actions{position:static;bottom:auto;background:none;padding:12px 0 0}
@media(max-width:520px){.reno-inline-panel .reno-sheet{padding:12px}}'''
s=s.replace(css_anchor,css_anchor+'\n'+inline_css,1)

# Toggle instead of opening a modal. The panel keeps all existing trade functionality.
old_open='''const renoBackdrop=$("renoBackdrop");
$("openReno").addEventListener("click",()=>{initializeTrades();
renderTrades();renoBackdrop.classList.add("show")});'''
new_open='''const renoBackdrop=$("renoBackdrop");
$("openReno").addEventListener("click",()=>{
  const opening=!renoBackdrop.classList.contains("show");
  if(opening){
    initializeTrades();
    renderTrades();
  }
  renoBackdrop.classList.toggle("show",opening);
  $("openReno").textContent=opening ? "−" : "+";
  $("openReno").setAttribute("aria-expanded",opening ? "true" : "false");
  $("openReno").setAttribute("aria-label",opening ? "Sanierungsgewerke schließen" : "Sanierungsgewerke öffnen");
});'''
replace_once(old_open,new_open,"renovation inline toggle")

# Save/Übernehmen now closes the inline panel, preserving the existing persistence logic.
old_save='''  syncRenoTotal(); render(); renoBackdrop.classList.remove("show");
});'''
new_save='''  syncRenoTotal(); render(); renoBackdrop.classList.remove("show");
  $("openReno").textContent="+";
  $("openReno").setAttribute("aria-expanded","false");
  $("openReno").setAttribute("aria-label","Sanierungsgewerke öffnen");
});'''
replace_once(old_save,new_save,"renovation save collapse")

# Backdrop-click closing is obsolete because there is no backdrop anymore.
old_backdrop='''renoBackdrop.addEventListener("click",e=>{if(e.target===renoBackdrop)renoBackdrop.classList.remove("show")});
'''
if old_backdrop in s:
    s=s.replace(old_backdrop,"",1)

# Version bump.
s=s.replace("V8.281","V8.282")
s=s.replace("service-worker.js?v=8.281","service-worker.js?v=8.282")

required=[
    'class="reno-inline-panel" id="renoBackdrop"',
    '.reno-inline-panel.show{display:block}',
    'grid-column:1/-1',
    'aria-controls="renoBackdrop"',
    'const opening=!renoBackdrop.classList.contains("show");',
    '$("openReno").textContent=opening ? "−" : "+";',
    'V8.282',
    'service-worker.js?v=8.282'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.282 verification failed: "+", ".join(missing))

if '<div class="sheet-backdrop" id="renoBackdrop">' in s:
    raise SystemExit("V8.282 renovation modal backdrop still present")

path.write_text(s,encoding="utf-8")
print("V8.282 renovation details converted from modal to inline panel")
