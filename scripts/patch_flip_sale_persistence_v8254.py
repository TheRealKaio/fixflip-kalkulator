from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

js=r"""
<script>
// V8.254 Fix & Flip: Verkaufspreis nach Sanierung als echter gespeicherter Feldwert
(function(){
  const FIELD_ID="flipSaleTarget";
  const STORAGE_KEY="ff_flip_sale_after_reno_value";

  function field(){
    return document.getElementById(FIELD_ID);
  }

  function saveValue(){
    const el=field();
    if(!el) return;
    localStorage.setItem(STORAGE_KEY,String(el.value||"0"));
  }

  function loadValue(){
    const el=field();
    if(!el) return false;
    const saved=localStorage.getItem(STORAGE_KEY);
    if(saved===null) return false;
    el.value=saved;
    return true;
  }

  function recalcAndStore(){
    const el=field();
    if(!el || currentDealType()!=="flip") return false;
    const value=Math.max(0,calculateFlipTargetSale());
    el.value=value>0 ? String(Math.round(value)) : "0";
    el.placeholder="";
    flipSaleManualOverride=false;
    localStorage.setItem(FLIP_SALE_OVERRIDE_KEY,"0");
    saveValue();
    try{ setSaleRecalculatedState(true); }catch(_err){}
    return true;
  }

  // Migration aus dem bisherigen generischen Speicherfeld.
  if(localStorage.getItem(STORAGE_KEY)===null){
    const old=localStorage.getItem("ff_flipSaleTarget");
    if(old!==null && String(old).trim()!==""){
      localStorage.setItem(STORAGE_KEY,old);
    }
  }

  // Eindeutige Kennzeichnung für die Speicherung.
  const el=field();
  if(el){
    el.dataset.storageKey=STORAGE_KEY;

    // Direkte Nutzereingaben ebenfalls sofort im eigenen Speicher sichern.
    el.addEventListener("input",function(){
      saveValue();
    });
    el.addEventListener("change",function(){
      saveValue();
    });
  }

  const formulaIds=new Set([
    "purchase","months","buffer","state","notary","buyBroker",
    "financeAcquisition","ltv","ownEquityInput","interest","repayment",
    "holding","otherSaleCosts","targetMargin","sellBroker"
  ]);

  function isFormulaChange(target){
    if(!target) return false;
    if(formulaIds.has(target.id)) return true;
    if(target.classList && (
      target.classList.contains("trade-amount") ||
      target.classList.contains("trade-area")
    )) return true;
    return false;
  }

  function queueFormulaRefresh(target){
    if(currentDealType()!=="flip" || !isFormulaChange(target)) return;
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      if(recalcAndStore()){
        try{ render(); }catch(_err){}
      }
    },0);
  }

  document.addEventListener("input",function(event){
    queueFormulaRefresh(event.target);
  });
  document.addEventListener("change",function(event){
    if(event.target && event.target.name==="dealType"){
      setTimeout(function(){
        if(currentDealType()==="flip"){
          if(!loadValue()) recalcAndStore();
          else {
            // Nach Moduswechsel direkt auf Basis der aktuellen Formel synchronisieren.
            recalcAndStore();
          }
          try{ render(); }catch(_err){}
        }
      },0);
      return;
    }
    queueFormulaRefresh(event.target);
  });

  // Rechner-Reset: eigenes Speicherfeld ebenfalls vollständig zurücksetzen.
  if(typeof resetDealCalculatorToDefaults==="function"){
    const baseResetDealV8254=resetDealCalculatorToDefaults;
    resetDealCalculatorToDefaults=function(){
      const mode=currentDealType();
      if(mode==="flip") localStorage.removeItem(STORAGE_KEY);
      const result=baseResetDealV8254.apply(this,arguments);
      if(mode==="flip"){
        setTimeout(function(){
          if(currentDealType()!=="flip") return;
          recalcAndStore();
          try{ render(); }catch(_err){}
        },0);
      }
      return result;
    };
  }

  // Programmgesteuerte Änderungen der Sanierung ebenfalls synchronisieren.
  ["applyTradeSuggestions","saveTrades","resetTrades"].forEach(function(id){
    const btn=document.getElementById(id);
    if(!btn) return;
    btn.addEventListener("click",function(){
      setTimeout(function(){
        if(currentDealType()!=="flip") return;
        recalcAndStore();
        try{ render(); }catch(_err){}
      },0);
    });
  });

  // Initial: gespeicherten Wert laden und anschließend mit der aktuellen Formel abgleichen.
  if(currentDealType()==="flip"){
    loadValue();
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      recalcAndStore();
      try{ render(); }catch(_err){}
    },0);
  }
})();
</script>
"""

if "</body>" not in s:
    raise SystemExit("V8.254 body anchor missing")
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.253","V8.254")
s=s.replace("service-worker.js?v=8.253","service-worker.js?v=8.254")

required=[
  'V8.254 Fix & Flip: Verkaufspreis nach Sanierung als echter gespeicherter Feldwert',
  'const FIELD_ID="flipSaleTarget";',
  'const STORAGE_KEY="ff_flip_sale_after_reno_value";',
  'el.dataset.storageKey=STORAGE_KEY;',
  'const value=Math.max(0,calculateFlipTargetSale());',
  'localStorage.setItem(STORAGE_KEY,String(el.value||"0"));',
  '"purchase","months","buffer","state","notary","buyBroker"',
  'target.classList.contains("trade-amount")',
  'target.classList.contains("trade-area")',
  'recalcAndStore();',
  'localStorage.removeItem(STORAGE_KEY);',
  'V8.254',
  'service-worker.js?v=8.254'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.254 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.254 flip sale target persistence and recalculation applied")
