from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Remove benchmark block from under purchase.
old_block='''

      <div class="flip-sale-benchmarks mode-hidden" id="flipSaleBenchmarks">
        <div class="flip-sale-benchmark">
          <span>Erwarteter Verkaufspreis</span>
          <strong id="saleExpectedBenchmark">–</strong>
        </div>
        <div class="flip-sale-benchmark">
          <span>Break-even-Verkaufspreis</span>
          <strong id="saleBreakEvenBenchmark">–</strong>
        </div>
        <div class="flip-sale-benchmark">
          <span>Verkaufspreis für deine Projektziele</span>
          <strong id="saleGoalBenchmark">–</strong>
        </div>
      </div>'''
if old_block not in s:
    raise SystemExit("V8.264 old benchmark block missing")
s=s.replace(old_block,"",1)

# Add the 3 benchmark boxes immediately below the sale input.
sale_anchor='''        <div class="input-wrap"><input id="flipSaleTarget" inputmode="decimal" value="0"><span class="unit">€</span></div>
        <div class="mini">'''
sale_insert='''        <div class="input-wrap"><input id="flipSaleTarget" inputmode="decimal" value="0"><span class="unit">€</span></div>
        <div class="flip-sale-benchmarks mode-hidden" id="flipSaleBenchmarks">
          <div class="flip-sale-benchmark">
            <span>Erwarteter Verkaufspreis</span>
            <strong id="saleExpectedBenchmark">–</strong>
          </div>
          <div class="flip-sale-benchmark">
            <span>Break-even-Verkaufspreis</span>
            <strong id="saleBreakEvenBenchmark">–</strong>
          </div>
          <div class="flip-sale-benchmark">
            <span>Verkaufspreis Projektziele</span>
            <strong id="saleGoalBenchmark">–</strong>
          </div>
        </div>
        <div class="mini">'''
replace_once(sale_anchor,sale_insert,"sale benchmark placement")

# Tighten spacing for boxes under sale field.
s=s.replace(
    '.flip-sale-benchmarks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:-2px 0 16px}',
    '.flip-sale-benchmarks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:10px 0 10px}'
)

# Version bump.
s=s.replace("V8.263","V8.264")
s=s.replace("service-worker.js?v=8.263","service-worker.js?v=8.264")

required=[
    'id="flipSaleTarget"',
    'id="flipSaleBenchmarks"',
    'Verkaufspreis Projektziele',
    'V8.264',
    'service-worker.js?v=8.264'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.264 verification failed: "+", ".join(missing))
if "Verkaufspreis für deine Projektziele" in s:
    raise SystemExit("V8.264 old goal sale label still present")

# Ensure benchmark block now follows sale field, not purchase.
sale_pos=s.find('id="flipSaleTarget"')
bench_pos=s.find('id="flipSaleBenchmarks"')
purchase_pos=s.find('id="purchase"')
if not (purchase_pos < sale_pos < bench_pos):
    raise SystemExit("V8.264 benchmark placement order invalid")

path.write_text(s,encoding="utf-8")
print("V8.264 sale benchmark boxes moved below sale field")
