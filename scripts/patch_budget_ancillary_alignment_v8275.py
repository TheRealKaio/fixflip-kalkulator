from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Kurzer statischer Hinweis unter Kaufnebenkosten gesamt.
replace_once(
'''            <div class="mini" id="budgetAncillaryNote">Grunderwerbsteuer + Notar/Grundbuch + Makler beim Kauf</div>''',
'''            <div class="mini" id="budgetAncillaryNote">Notar, Grundbuch, Makler.</div>''',
"budget ancillary short note markup"
)

old_render='''  if($("budgetAncillaryNote")){
    $("budgetAncillaryNote").textContent=
      new Intl.NumberFormat("de-DE",{minimumFractionDigits:1,maximumFractionDigits:1}).format(m.transferTaxPct*100)
      +" % GrESt + "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.notaryPct*100)
      +" % Notar/Grundbuch + "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.buyBrokerPct*100)
      +" % Makler = "
      +new Intl.NumberFormat("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}).format(m.ancillaryPct*100)
      +" % gesamt";
  }'''
new_render='''  if($("budgetAncillaryNote")){
    $("budgetAncillaryNote").textContent="Notar, Grundbuch, Makler.";
  }'''
replace_once(old_render,new_render,"budget ancillary short note render")

# 2) Eingabefelder im Finanzierungsraster wieder sauber auf einer Höhe ausrichten.
css_anchor='#budgetAssumptionsBody .budget-state-field{grid-column:1/-1}'
if css_anchor not in s:
    raise SystemExit("V8.275 assumptions CSS anchor missing")

alignment_css='''#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field){display:flex;flex-direction:column;min-width:0}
#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{display:flex;align-items:flex-end;min-height:34px;line-height:1.25}
#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>.input-wrap{width:100%;min-width:0}
@media(max-width:520px){#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{min-height:0}}'''

if alignment_css not in s:
    s=s.replace(css_anchor,css_anchor+'\n'+alignment_css,1)

# Version bump.
s=s.replace("V8.274","V8.275")
s=s.replace("service-worker.js?v=8.274","service-worker.js?v=8.275")

required=[
    'id="budgetAncillaryNote">Notar, Grundbuch, Makler.</div>',
    '$("budgetAncillaryNote").textContent="Notar, Grundbuch, Makler.";',
    '#budgetAssumptionsBody .budget-grid.three>.field:not(.budget-state-field)>label{display:flex;align-items:flex-end;min-height:34px;line-height:1.25}',
    'V8.275',
    'service-worker.js?v=8.275'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.275 verification failed: "+", ".join(missing))

# Die lange dynamische Summenanzeige darf nicht mehr vorhanden sein.
forbidden=[
    '% GrESt + ',
    '% Notar/Grundbuch + ',
    '% Makler = '
]
left=[x for x in forbidden if x in s]
if left:
    raise SystemExit("V8.275 old ancillary detail text still present: "+", ".join(left))

path.write_text(s,encoding="utf-8")
print("V8.275 ancillary hint shortened and financing fields aligned")
