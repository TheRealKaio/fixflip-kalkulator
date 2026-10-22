from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

marker='''</style>\n\n\n<style id="rental-ui-v8304">'''
if marker not in s:
    raise SystemExit("V8.321 style insertion anchor missing")

css='''</style>\n\n<style id="top-footer-layout-v8321">\n/* Vier Auswahlkarten: Titelzeile kompakt, Beschreibung ueber volle Kartenbreite */\n.deal-type-row{gap:6px!important}\n.deal-type-option,.rent-tab-button{\n  display:grid!important;\n  grid-template-columns:20px minmax(0,1fr)!important;\n  grid-template-rows:auto auto!important;\n  column-gap:7px!important;\n  row-gap:5px!important;\n  align-items:center!important;\n  padding:12px 8px!important;\n}\n.deal-type-option>input[type="radio"],.rent-tab-button>.rent-radio-dot{\n  grid-column:1!important;\n  grid-row:1!important;\n  align-self:center!important;\n}\n.deal-type-option>span:not(.rent-radio-dot),.rent-tab-copy{\n  display:contents!important;\n}\n.deal-type-option strong,.rent-tab-copy strong{\n  grid-column:2!important;\n  grid-row:1!important;\n  align-self:center!important;\n  min-width:0!important;\n}\n.deal-type-option small,.rent-tab-copy small{\n  grid-column:1 / -1!important;\n  grid-row:2!important;\n  display:block!important;\n  width:100%!important;\n  min-width:0!important;\n  margin:0!important;\n  padding:0 2px!important;\n  box-sizing:border-box!important;\n  text-align:justify!important;\n  text-align-last:left!important;\n  hyphens:auto!important;\n}\n/* Footer-Hinweis volle Breite oberhalb der separaten Meta-Zeile */\n.footer-note{\n  display:flex!important;\n  flex-direction:column!important;\n  align-items:stretch!important;\n  gap:6px!important;\n}\n.footer-note>span:first-child{\n  display:block!important;\n  width:100%!important;\n  padding:0 2px!important;\n  box-sizing:border-box!important;\n  text-align:justify!important;\n  text-align-last:left!important;\n  hyphens:auto!important;\n}\n.footer-meta{\n  width:100%!important;\n  display:flex!important;\n  flex-direction:row!important;\n  align-items:center!important;\n  justify-content:space-between!important;\n  gap:10px!important;\n  text-align:initial!important;\n}\n.footer-version{text-align:left!important}\n.footer-legal-links{margin-left:auto!important}\n@media(max-width:520px){\n  .deal-type-row{gap:6px!important}\n  .deal-type-option,.rent-tab-button{padding:10px 7px!important;column-gap:6px!important}\n  .footer-meta{align-items:flex-start!important}\n  .footer-legal-links{flex-wrap:wrap!important;row-gap:2px!important;white-space:normal!important;justify-content:flex-end!important}\n}\n</style>\n\n\n<style id="rental-ui-v8304">'''

s=s.replace(marker,css,1)

s=s.replace("V8.320","V8.321")
s=s.replace("service-worker.js?v=8.320","service-worker.js?v=8.321")

required=[
    'id="top-footer-layout-v8321"',
    'grid-template-columns:20px minmax(0,1fr)!important;',
    'grid-column:1 / -1!important;',
    'text-align:justify!important;',
    '.footer-note{',
    'flex-direction:column!important;',
    'justify-content:space-between!important;',
    'V8.321'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.321 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.321 top cards and footer layout applied")
