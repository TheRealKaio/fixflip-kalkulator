from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
/* V8.247: nummerierte Eigennutzungs-Überschriften wie die normalen Card-H2 */
.own-numbered-heading{
  font-size:18px!important;
  font-weight:700!important;
  letter-spacing:-.02em!important;
  line-height:1.2!important;
  color:#172033!important;
}

/* Der Plus-/Minus-Button von 3. Finanzierung entspricht exakt dem Kaufpreis-Check. */
.own-finance-card .advanced>summary{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}
.own-finance-card .advanced>summary::after{
  content:"+";
  width:34px;
  height:34px;
  min-width:34px;
  min-height:34px;
  flex:0 0 34px;
  border:1.5px solid #c7d8ff;
  border-radius:11px;
  background:#edf3ff;
  color:#2563eb;
  font-size:24px;
  font-weight:500;
  line-height:1;
  display:flex;
  align-items:center;
  justify-content:center;
  box-shadow:none;
  padding:0;
  margin:0;
  float:none;
}
.own-finance-card .advanced[open]>summary::after{
  content:"−";
  font-size:22px;
}
</style>
"""

js=r"""
<script>
// V8.247 einheitlicher Überschriftenstil in Eigennutzung
(function(){
  function applyOwnHeadingStyle(){
    const root=document.getElementById("dealCalculatorContent");
    if(!root) return;

    const dealHeading=Array.from(root.querySelectorAll("section.card > h2")).find(function(h){
      return h.textContent.trim()==="1. Deine Immobilie";
    });
    if(dealHeading) dealHeading.classList.add("own-numbered-heading");

    const market=document.getElementById("ownMarketCheckSection");
    const marketHeading=market ? market.querySelector(".market-check-head h2") : null;
    if(marketHeading) marketHeading.classList.add("own-numbered-heading");

    const finance=document.querySelector("#ownFinanceCard details.advanced > summary");
    if(finance) finance.classList.add("own-numbered-heading");
  }

  document.addEventListener("change",function(event){
    if(event.target && event.target.name==="dealType"){
      setTimeout(applyOwnHeadingStyle,0);
    }
  },true);

  setTimeout(applyOwnHeadingStyle,0);
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.247 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.246","V8.247")
s=s.replace("service-worker.js?v=8.246","service-worker.js?v=8.247")

required=[
  'V8.247: nummerierte Eigennutzungs-Überschriften',
  '.own-numbered-heading',
  'width:34px;',
  'border:1.5px solid #c7d8ff;',
  'background:#edf3ff;',
  'color:#2563eb;',
  'V8.247 einheitlicher Überschriftenstil',
  'V8.247',
  'service-worker.js?v=8.247'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.247 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.247 own-use visual consistency patch applied")
