from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

equity_field='''          <div class="field"><label>Eigenkapital verfügbar</label><div class="input-wrap"><input id="budgetEquity" inputmode="decimal" value="0"><span class="unit">€</span></div></div>'''

# 1) Eigenkapital aus den Finanzierungsannahmen entfernen.
replace_once(equity_field+"\n","", "remove budget equity from financing assumptions")

# 2) Als letzte Position der Haushaltsinformationen in eigener Zeile einfügen.
household_anchor='''          <div class="field">
            <label>Kindergeld</label>
            <div class="input-wrap"><input id="budgetChildBenefit" inputmode="decimal" value="0"><span class="unit">€</span></div>
            <div class="mini">Orientierung: 259 € je Kind (2026), editierbar.</div>
          </div>
        </div>
      </section>'''

household_new='''          <div class="field">
            <label>Kindergeld</label>
            <div class="input-wrap"><input id="budgetChildBenefit" inputmode="decimal" value="0"><span class="unit">€</span></div>
            <div class="mini">Orientierung: 259 € je Kind (2026), editierbar.</div>
          </div>
        </div>
        <div class="budget-equity-row">
          <div class="field">
            <label>Eigenkapital verfügbar</label>
            <div class="input-wrap"><input id="budgetEquity" inputmode="decimal" value="0"><span class="unit">€</span></div>
          </div>
        </div>
      </section>'''

replace_once(household_anchor,household_new,"move budget equity to household information")

# Eigene volle Zeile, passend zur Breite der Haushaltsinformationen.
css_anchor='#budgetAssumptionsBody .budget-state-field{grid-column:1/-1}'
if css_anchor not in s:
    raise SystemExit("V8.274 CSS anchor missing")
s=s.replace(
    css_anchor,
    css_anchor+'\n.budget-equity-row{display:grid;grid-template-columns:1fr;margin-top:12px;width:100%}\n.budget-equity-row .field,.budget-equity-row .input-wrap{width:100%;min-width:0}',
    1
)

# Version bump.
s=s.replace("V8.273","V8.274")
s=s.replace("service-worker.js?v=8.273","service-worker.js?v=8.274")

required=[
    '<div class="budget-equity-row">',
    '<label>Eigenkapital verfügbar</label>',
    'id="budgetEquity" inputmode="decimal" value="0"',
    '.budget-equity-row{display:grid;grid-template-columns:1fr;margin-top:12px;width:100%}',
    'V8.274',
    'service-worker.js?v=8.274'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.274 verification failed: "+", ".join(missing))

# Genau ein Eingabefeld mit dieser ID darf existieren.
if s.count('id="budgetEquity"') != 1:
    raise SystemExit("V8.274 budgetEquity must exist exactly once")

# Im Annahmen-Bereich darf das Feld nicht mehr liegen.
assumptions_start=s.find('id="budgetAssumptionsSection"')
assumptions_end=s.find('</section>',assumptions_start)
if assumptions_start < 0 or assumptions_end < 0:
    raise SystemExit("V8.274 assumptions section not found")
if 'id="budgetEquity"' in s[assumptions_start:assumptions_end]:
    raise SystemExit("V8.274 budgetEquity still inside financing assumptions")

path.write_text(s,encoding="utf-8")
print("V8.274 budget equity moved to household information")
