from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

js=r"""
<script>
// V8.244 Dynamische Herkunftsanzeige für Marktwert nach Sanierung
(function(){
  function hasValidMarketComparables(){
    if(currentDealType()!=="own") return false;
    const subjectArea=Math.max(0,val("area"));
    if(subjectArea<=0) return false;

    return [1,2,3].some(function(i){
      const price=Math.max(0,val("comp"+i+"Price"));
      const area=Math.max(0,val("comp"+i+"Area"));
      return price>0 && area>0;
    });
  }

  function updateMarketValueSourceHint(){
    if(!$("saleHint")) return;
    if(currentDealType()!=="own") return;

    $("saleHint").textContent=hasValidMarketComparables()
      ? "Kalkulatorischer Wert (Vergleichseingaben)"
      : "Kalkulatorischer Wert (Kaufpreis, NK, Sanierung)";
  }

  const sourceFields=new Set([
    "purchase","area","notary","buyBroker","buffer",
    "comp1Price","comp1Area","comp2Price","comp2Area","comp3Price","comp3Area"
  ]);

  document.addEventListener("input",function(event){
    const target=event.target;
    if(!target) return;
    const tradeChange=target.classList && (
      target.classList.contains("trade-amount") ||
      target.classList.contains("trade-area")
    );
    if(sourceFields.has(target.id) || tradeChange){
      setTimeout(updateMarketValueSourceHint,0);
    }
  });

  document.addEventListener("change",function(event){
    const target=event.target;
    if(!target) return;
    if(target.name==="dealType" || target.id==="state" || sourceFields.has(target.id)){
      setTimeout(updateMarketValueSourceHint,0);
    }
  });

  const applyReno=document.getElementById("applyTradeSuggestions");
  if(applyReno){
    applyReno.addEventListener("click",function(){
      setTimeout(updateMarketValueSourceHint,0);
    });
  }

  // setDealType setzt den bisherigen statischen Text; nach dem Moduswechsel
  // wird deshalb die tatsächlich aktive Berechnungsquelle erneut ausgewiesen.
  setTimeout(updateMarketValueSourceHint,0);
})();
</script>
"""

if "</body>" not in s:
    raise SystemExit("V8.244 body anchor missing")
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.243","V8.244")
s=s.replace("service-worker.js?v=8.243","service-worker.js?v=8.244")

required=[
  'V8.244 Dynamische Herkunftsanzeige',
  'function hasValidMarketComparables()',
  '"Kalkulatorischer Wert (Vergleichseingaben)"',
  '"Kalkulatorischer Wert (Kaufpreis, NK, Sanierung)"',
  'setTimeout(updateMarketValueSourceHint,0);',
  'V8.244',
  'service-worker.js?v=8.244'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.244 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.244 dynamic market value source hint applied")
