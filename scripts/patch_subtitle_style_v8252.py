from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
/* V8.252: Subtitel wie beim Eigennutzung Kaufpreis-Check */
.section-summary-subtitle{
  color:var(--muted)!important;
  font-size:13px!important;
  line-height:1.45!important;
  font-weight:400!important;
  letter-spacing:normal!important;
}
</style>
"""

if "</head>" not in s:
    raise SystemExit("V8.252 head anchor missing")
s=s.replace("</head>",style+"\n</head>",1)

s=s.replace("V8.251","V8.252")
s=s.replace("service-worker.js?v=8.251","service-worker.js?v=8.252")

required=[
  'V8.252: Subtitel wie beim Eigennutzung Kaufpreis-Check',
  'color:var(--muted)!important;',
  'font-size:13px!important;',
  'line-height:1.45!important;',
  'font-weight:400!important;',
  'V8.252',
  'service-worker.js?v=8.252'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.252 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.252 subtitle styling aligned to purchase-check reference")
