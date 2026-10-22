from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

rep(
  '<label>Einmalige Sanierung / Renovierung <span class="hint">inkl. Puffer</span></label>',
  '<label>Modernisierung (Anfangsinvestition) <span class="hint">inkl. Puffer</span></label>',
  "rental modernization label"
)

rep(
  '<div class="mini">zur Orientierung · nicht vollständig als Eigentümerkosten angesetzt</div>',
  '<div class="mini">nicht vollständig als Eigentümerkosten angesetzt</div>',
  "housegeld orientation wording"
)

css=r"""
<style id="rental-ui-v8301">
.deal-type-option,.rent-tab-button{
  align-items:flex-start!important;
}
.deal-type-option>span:not(.rent-radio-dot),.rent-tab-copy{
  justify-content:flex-start!important;
  align-self:stretch!important;
}
.deal-type-option strong,.rent-tab-copy strong{
  display:block!important;
  min-height:17px!important;
  margin:0!important;
}
</style>
"""
rep("</head>",css+"\n</head>","head css")

s=s.replace("V8.300","V8.301")
s=s.replace("service-worker.js?v=8.300","service-worker.js?v=8.301")

required=[
  'id="rental-ui-v8301"',
  'Modernisierung (Anfangsinvestition)',
  'nicht vollständig als Eigentümerkosten angesetzt',
  'V8.301',
  'service-worker.js?v=8.301'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.301 missing: "+", ".join(missing))
if "zur Orientierung · nicht vollständig als Eigentümerkosten angesetzt" in s:
    raise SystemExit("V8.301 old housegeld wording still present")

p.write_text(s,encoding="utf-8")
print("V8.301 rental wording and tab alignment applied")
