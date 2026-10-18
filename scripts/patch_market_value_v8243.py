from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

js=r"""
<script>
// V8.243 Marktwert nach Sanierung immer aus der aktuellen Formel aktualisieren
(function(){
  function recalcOwnMarketValueAfterReno(){
    if(currentDealType()!=="own" || !$("sale")) return false;

    // Gueltige Vergleichswerte 1-3 haben wie bisher Vorrang.
    if(updateOwnUseMarketValueFromComparables()){
      return true;
    }

    // Ohne Vergleichswerte immer den aktuellen kalkulatorischen Marktwert setzen:
    // Kaufpreis + Kaufnebenkosten + Sanierung inkl. Puffer, anschließend 10 % Wertpuffer.
    const purchase=Math.max(0,val("purchase"));
    const renoBase=Math.max(0,totalTrades());
    const renoWithBuffer=renoBase*(1+pct("buffer"));
    const acquisitionCosts=
      purchase*(states[stateEl.value]/100)
      + purchase*pct("notary")
      + purchase*pct("buyBroker");
    const initialOwnUseCosts=purchase+acquisitionCosts+renoWithBuffer;
    const ownUseValueBuffer=0.10;
    const requiredMarketValue=initialOwnUseCosts/(1-ownUseValueBuffer);
    $("sale").value=requiredMarketValue>0 ? String(Math.round(requiredMarketValue)) : "";
    return true;
  }

  // Bestehenden Helfer auf die neue, immer aktuelle Logik umstellen.
  updateOwnUseSaleDefault=recalcOwnMarketValueAfterReno;

  const formulaIds=new Set([
    "purchase","area","notary","buyBroker","buffer",
    "comp1Price","comp1Area","comp2Price","comp2Area","comp3Price","comp3Area"
  ]);

  function refreshIfFormulaChanged(target){
    if(currentDealType()!=="own" || !target) return;
    const isTradeAmount=target.classList && target.classList.contains("trade-amount");
    const isTradeArea=target.classList && target.classList.contains("trade-area");
    const isFormulaField=formulaIds.has(target.id);
    const isState=target.id==="state";
    if(!isTradeAmount && !isTradeArea && !isFormulaField && !isState) return;

    // Nach den bestehenden Feld-Handlern rechnen, damit tradeValues usw. bereits aktuell sind.
    setTimeout(function(){
      if(currentDealType()!=="own") return;
      const before=String($("sale").value||"");
      recalcOwnMarketValueAfterReno();
      const after=String($("sale").value||"");
      if(before!==after){
        try{ render(); }catch(_err){}
      }
    },0);
  }

  document.addEventListener("input",function(event){
    refreshIfFormulaChanged(event.target);
  });
  document.addEventListener("change",function(event){
    refreshIfFormulaChanged(event.target);
  });

  // Auch programmatische Änderungen der Sanierungsvorschläge berücksichtigen.
  const applyReno=document.getElementById("applyTradeSuggestions");
  if(applyReno){
    applyReno.addEventListener("click",function(){
      setTimeout(function(){
        if(currentDealType()!=="own") return;
        recalcOwnMarketValueAfterReno();
        try{ render(); }catch(_err){}
      },0);
    });
  }

  // Initial ebenfalls auf Basis der aktuellen Formel synchronisieren.
  if(currentDealType()==="own"){
    recalcOwnMarketValueAfterReno();
  }
})();
</script>
"""

if "</body>" not in s:
    raise SystemExit("V8.243 body anchor missing")
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.242","V8.243")
s=s.replace("service-worker.js?v=8.242","service-worker.js?v=8.243")

required=[
  'V8.243 Marktwert nach Sanierung immer aus der aktuellen Formel aktualisieren',
  'const initialOwnUseCosts=purchase+acquisitionCosts+renoWithBuffer;',
  'const ownUseValueBuffer=0.10;',
  'updateOwnUseSaleDefault=recalcOwnMarketValueAfterReno;',
  '"purchase","area","notary","buyBroker","buffer"',
  'isTradeAmount',
  'updateOwnUseMarketValueFromComparables()',
  'V8.243',
  'service-worker.js?v=8.243'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.243 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.243 market value auto update applied")
