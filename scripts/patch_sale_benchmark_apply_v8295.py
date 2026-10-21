from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(label + " anchor missing")
    s = s.replace(old, new, 1)

replace_once(
    '<label>VK nach Sanierung <span class="hint">automatisch kalkuliert · editierbar</span></label>',
    '<label>VK nach Sanierung <span class="hint">VK Projektziel • editierbar</span></label>',
    "VK field subtitle"
)

old_boxes = '''          <div class="flip-sale-benchmarks mode-hidden" id="flipSaleBenchmarks">
            <div class="flip-sale-benchmark">
              <span>VK Projektziel</span>
              <strong id="saleExpectedBenchmark">–</strong>
            </div>
            <div class="flip-sale-benchmark">
              <span>VK Break-even</span>
              <strong id="saleBreakEvenBenchmark">–</strong>
            </div>
            <div class="flip-sale-benchmark">
              <span>VK nach Sanierung</span>
              <strong id="saleGoalBenchmark">–</strong>
            </div>
          </div>'''

new_boxes = '''          <div class="flip-sale-benchmarks mode-hidden" id="flipSaleBenchmarks">
            <button type="button" class="flip-sale-benchmark" data-vk-source="project" aria-label="VK Projektziel als VK nach Sanierung übernehmen">
              <span>VK Projektziel</span>
              <strong id="saleExpectedBenchmark">–</strong>
              <b class="vk-transfer-icon" aria-hidden="true">↘</b>
            </button>
            <button type="button" class="flip-sale-benchmark" data-vk-source="breakeven" aria-label="VK Break-even als VK nach Sanierung übernehmen">
              <span>VK Break-even</span>
              <strong id="saleBreakEvenBenchmark">–</strong>
              <b class="vk-transfer-icon" aria-hidden="true">↘</b>
            </button>
            <button type="button" class="flip-sale-benchmark" data-vk-source="postreno" aria-label="VK nach Sanierung erneut übernehmen">
              <span>VK nach Sanierung</span>
              <strong id="saleGoalBenchmark">–</strong>
              <b class="vk-transfer-icon" aria-hidden="true">↘</b>
            </button>
          </div>'''

replace_once(old_boxes, new_boxes, "VK benchmark buttons")

css_anchor = '.flip-sale-benchmark{min-width:0;border:1px solid #e1e6ee;border-radius:12px;background:#f8fafc;padding:10px 11px}'
if css_anchor not in s:
    raise SystemExit("V8.295 VK benchmark CSS anchor missing")
s = s.replace(
    css_anchor,
    css_anchor + ';font:inherit;text-align:left;cursor:pointer;appearance:none;position:relative;padding-right:30px',
    1
)

style = '''
<style id="vk-benchmark-apply-v8295">
.flip-sale-benchmark:hover{background:#f1f5f9;border-color:#cbd5e1}
.flip-sale-benchmark:focus-visible{outline:2px solid #7ca56a;outline-offset:2px}
.vk-transfer-icon{position:absolute;right:9px;top:50%;transform:translateY(-50%);font-size:16px;line-height:1;color:#64748b;font-weight:800}
</style>
'''
if "</head>" not in s:
    raise SystemExit("V8.295 head closing tag missing")
s = s.replace("</head>", style + "\n</head>", 1)

script = r'''
<script id="vk-benchmark-apply-v8295">
(function(){
  function transferValue(source){
    const m=model();
    if(source==="project") return Math.max(0,Number(m.goalSale)||0);
    if(source==="breakeven") return Math.max(0,Number(m.breakEven)||0);
    if(source==="postreno") return Math.max(0,Number(m.s)||0);
    return 0;
  }

  const labels={
    project:"VK Projektziel",
    breakeven:"VK Break-even",
    postreno:"VK nach Sanierung"
  };

  document.querySelectorAll(".flip-sale-benchmark[data-vk-source]").forEach(function(button){
    button.addEventListener("click",function(){
      if(currentDealType()!=="flip") return;

      const source=button.dataset.vkSource;
      const value=transferValue(source);
      if(!(value>0)) return;

      const rounded=Math.round(value);
      const label=labels[source] || "diesen Wert";
      const ok=confirm("Möchtest du "+eur(rounded)+" aus „"+label+"“ als VK nach Sanierung übernehmen?");
      if(!ok) return;

      const field=document.getElementById("flipSaleTarget");
      if(!field) return;

      field.value=String(rounded);
      field.dispatchEvent(new Event("input",{bubbles:true}));
      field.dispatchEvent(new Event("change",{bubbles:true}));

      try{
        flipSaleManualOverride=true;
        localStorage.setItem(FLIP_SALE_OVERRIDE_KEY,"1");
        setSaleRecalculatedState(false);
      }catch(_err){}

      localStorage.setItem("ff_flipSaleTarget",String(rounded));
      localStorage.setItem("ff_flip_sale_after_reno_value",String(rounded));

      try{ render(); }catch(_err){}
    });
  });
})();
</script>
'''
if "</body>" not in s:
    raise SystemExit("V8.295 body closing tag missing")
s = s.replace("</body>", script + "\n</body>", 1)

s = s.replace("V8.294", "V8.295")
s = s.replace("service-worker.js?v=8.294", "service-worker.js?v=8.295")

required = [
    'VK Projektziel • editierbar',
    'data-vk-source="project"',
    'data-vk-source="breakeven"',
    'data-vk-source="postreno"',
    'class="vk-transfer-icon" aria-hidden="true">↘</b>',
    'confirm("Möchtest du "+eur(rounded)+" aus „"+label+"“ als VK nach Sanierung übernehmen?")',
    'field.value=String(rounded);',
    'field.dispatchEvent(new Event("input",{bubbles:true}));',
    'localStorage.setItem("ff_flip_sale_after_reno_value",String(rounded));',
    'V8.295',
    'service-worker.js?v=8.295'
]
missing = [token for token in required if token not in s]
if missing:
    raise SystemExit("V8.295 VK benchmark apply verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.295 VK benchmark values can be confirmed and applied")
