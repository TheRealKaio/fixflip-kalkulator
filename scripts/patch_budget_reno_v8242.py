from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

# The manual #reno amount is a final inclusive total, while detailed trade
# amounts remain the base to which the renovation buffer is applied.
reno_helper = r"""
function calculatedRenoBase(){
  const mode=typeof currentDealType==="function" ? currentDealType() : "";
  if(mode!=="own" && mode!=="flip") return Math.max(0,totalTrades());
  let manual=null;
  try{ manual=localStorage.getItem("ff_"+mode+"_reno_manual_total"); }catch(_err){}
  if(manual===null || manual.trim()==="" || !Number.isFinite(Number(manual))) return Math.max(0,totalTrades());
  return Math.max(0,Number(manual))/(1+Math.max(0,pct("buffer")));
}
"""
if "function calculatedRenoBase(){" not in s:
    anchor='function calculateFlipTargetSale(){'
    if anchor not in s: raise SystemExit("Manual renovation calculation anchor missing")
    s=s.replace(anchor,reno_helper+"\n"+anchor,1)
old_flip='const renoBase = Math.max(0, totalTrades());'
if old_flip not in s: raise SystemExit("Flip sale renovation base anchor missing")
s=s.replace(old_flip,'const renoBase = Math.max(0, calculatedRenoBase());',1)
old_model='const renoBase = overrides.reno ?? totalTrades();'
if old_model not in s: raise SystemExit("Project model renovation base anchor missing")
s=s.replace(old_model,'const renoBase = overrides.reno ?? calculatedRenoBase();',1)

style=r"""
<style>
#renoSheetTotal{display:none!important}
</style>
"""

js=r"""
<script>
// V8.242 budget suggestion refresh and renovation total correction
(function(){
  const BUDGET_ACTIVE_KEY="ff_budget_suggestions_active";

  function budgetSuggestionSignatureV8242(){
    const suggestions=getBudgetSuggestions();
    return JSON.stringify(budgetSuggestedExpenseIds.map(function(id){
      return [id,Math.round(Number(suggestions[id])||0)];
    }));
  }

  function budgetSuggestionsWereApplied(){
    if(localStorage.getItem(BUDGET_ACTIVE_KEY)==="1") return true;
    // Migration des bisherigen V8.240-Zustands.
    if(localStorage.getItem("ff_budget_suggestions_applied_signature")){
      localStorage.setItem(BUDGET_ACTIVE_KEY,"1");
      return true;
    }
    return false;
  }

  // Nach der ersten bewussten Übernahme folgen nur die nicht manuell
  // überschriebenen Ausgabenfelder weiterhin automatisch der Haushaltsgröße.
  syncBudgetSuggestions=function(){
    const suggestions=getBudgetSuggestions();
    if(budgetSuggestionsWereApplied()){
      budgetAutoUpdating=true;
      budgetSuggestedExpenseIds.forEach(function(id){
        if(!budgetExpenseManual[id] && $(id)){
          $(id).value=String(Math.round(Number(suggestions[id])||0));
        }
      });
      budgetAutoUpdating=false;
    }
    renderBudgetSuggestions();
    try{ renderBudget(); }catch(_err){}
  };

  const budgetButton=document.getElementById("budgetApplySuggestions");
  if(budgetButton){
    budgetButton.addEventListener("click",function(){
      localStorage.setItem(BUDGET_ACTIVE_KEY,"1");
      localStorage.setItem("ff_budget_suggestions_applied_signature",budgetSuggestionSignatureV8242());
    },true);
  }

  // Nach Reset bleiben Vorschläge wieder unverbindlich, bis der Button erneut gedrückt wird.
  const recalc=document.getElementById("recalc");
  if(recalc){
    recalc.addEventListener("click",function(){
      setTimeout(function(){
        try{
          if(currentDealType()==="budget" && budgetSuggestedExpenseIds.every(function(id){
            return !$(id) || Math.abs(budgetVal(id))<0.005;
          })){
            localStorage.removeItem(BUDGET_ACTIVE_KEY);
            localStorage.removeItem("ff_budget_suggestions_applied_signature");
          }
        }catch(_err){}
      },0);
    },true);
  }

  // Korrektur Sanierung:
  // "Sanierung (inkl. Puffer)" basiert ausschließlich auf tatsächlich
  // übernommenen bzw. manuell eingegebenen Sanierungswerten.
  // Ein bloßer Vorschlag darf dieses Feld nicht verändern.
  syncRenoTotal=function(){
    const actualBase=Math.max(0,totalTrades());
    const bufferRate=Math.max(0,pct("buffer"));
    const mode=typeof currentDealType==="function" ? currentDealType() : "";
    const manualKey=(mode==="own" || mode==="flip")
      ? "ff_"+mode+"_reno_manual_total"
      : "";
    const manual=manualKey ? localStorage.getItem(manualKey) : null;
    const hasManual=manual!==null && Number.isFinite(Number(manual));
    const totalWithBuffer=hasManual
      ? Math.max(0,Number(manual))
      : (actualBase>0 ? Math.round(actualBase*(1+bufferRate)) : 0);

    if($("reno") && document.activeElement!==$("reno")) $("reno").value=String(totalWithBuffer);
    if($("renoSheetTotal")) $("renoSheetTotal").textContent="";
    try{ updateRenoProposalStatus(); }catch(_err){}
  };

  // Die Vorschlagssumme bleibt als grauer/blauer Status unter dem Button,
  // die separate große blaue Gesamtsumme wird nicht mehr angezeigt.
  const blueTotal=document.getElementById("renoSheetTotal");
  if(blueTotal){
    blueTotal.textContent="";
    blueTotal.setAttribute("aria-hidden","true");
  }

  // Beim Pufferwechsel wird ausschließlich ein vorhandener tatsächlicher
  // Sanierungswert neu inklusive Puffer berechnet.
  const buffer=$("buffer");
  if(buffer){
    buffer.addEventListener("input",function(){
      syncRenoTotal();
      try{ render(); }catch(_err){}
    },true);
    buffer.addEventListener("change",function(){
      syncRenoTotal();
      try{ render(); }catch(_err){}
    },true);
  }

  syncBudgetSuggestions();
  syncRenoTotal();
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.242 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.241","V8.242")
s=s.replace("service-worker.js?v=8.241","service-worker.js?v=8.242")

required=[
  'V8.242 budget suggestion refresh and renovation total correction',
  'const BUDGET_ACTIVE_KEY="ff_budget_suggestions_active";',
  'if(!budgetExpenseManual[id] && $(id))',
  'function calculatedRenoBase(){',
  'const renoBase = Math.max(0, calculatedRenoBase());',
  'const renoBase = overrides.reno ?? calculatedRenoBase();',
  'const actualBase=Math.max(0,totalTrades());',
  'const totalWithBuffer=hasManual',
  '#renoSheetTotal{display:none!important}',
  'V8.242',
  'service-worker.js?v=8.242'
]
missing=[token for token in required if token not in s]
if missing:
    raise SystemExit("V8.242 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.242 budget refresh and renovation total correction applied")
