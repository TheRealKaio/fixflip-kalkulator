from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

replacements={
'''<strong id="saleExpectedBenchmark">–</strong>
              <b class="vk-transfer-icon" aria-hidden="true">↘</b>''':
'''<div class="vk-value-row"><strong id="saleExpectedBenchmark">–</strong><span class="vk-transfer-mark" aria-hidden="true">↘</span></div>''',
'''<strong id="saleBreakEvenBenchmark">–</strong>
              <b class="vk-transfer-icon" aria-hidden="true">↘</b>''':
'''<div class="vk-value-row"><strong id="saleBreakEvenBenchmark">–</strong><span class="vk-transfer-mark" aria-hidden="true">↘</span></div>''',
'''<strong id="saleGoalBenchmark">–</strong>
              <b class="vk-transfer-icon" aria-hidden="true">↘</b>''':
'''<div class="vk-value-row"><strong id="saleGoalBenchmark">–</strong><span class="vk-transfer-mark" aria-hidden="true">↘</span></div>'''
}
for old,new in replacements.items():
    if old not in s:
        raise SystemExit("V8.298 inline arrow markup anchor missing")
    s=s.replace(old,new,1)

style='''<style id="vk-inline-arrow-v8298">
.flip-sale-benchmark{padding-right:11px !important}
.vk-value-row{
  display:flex !important;
  align-items:center !important;
  justify-content:space-between !important;
  gap:8px !important;
  width:100% !important;
  margin-top:2px !important;
}
.vk-value-row strong{
  display:block !important;
  color:var(--ink) !important;
  flex:1 1 auto !important;
  min-width:0 !important;
}
.vk-transfer-mark{
  display:inline-block !important;
  position:static !important;
  flex:0 0 auto !important;
  color:#64748b !important;
  font-size:18px !important;
  font-weight:900 !important;
  line-height:1 !important;
  opacity:1 !important;
  visibility:visible !important;
}
</style>
'''
if "</head>" not in s:
    raise SystemExit("V8.298 head anchor missing")
s=s.replace("</head>",style+"\n</head>",1)

s=s.replace("V8.297","V8.298")
s=s.replace("service-worker.js?v=8.297","service-worker.js?v=8.298")

required=[
  'class="vk-value-row"',
  'class="vk-transfer-mark" aria-hidden="true">↘</span>',
  '.vk-transfer-mark{',
  'position:static !important;',
  'font-size:18px !important;',
  'V8.298',
  'service-worker.js?v=8.298'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.298 inline arrow verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.298 VK arrow rendered inline beside each price")
