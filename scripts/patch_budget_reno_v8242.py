from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

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
    const totalWithBuffer=actualBase>0
      ? Math.round(actualBase*(1+bufferRate))
      : 0;

    if($("reno")) $("reno").value=String(totalWithBuffer);
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
  'const actualBase=Math.max(0,totalTrades());',
  'const totalWithBuffer=actualBase>0',
  '#renoSheetTotal{display:none!important}',
  'V8.242',
  'service-worker.js?v=8.242'
]
missing=[token for token in required if token not in s]
if missing:
    raise SystemExit("V8.242 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.242 budget refresh and renovation total correction applied")
