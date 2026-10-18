from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

style = r"""
<style>
.budget-section-title>div:first-child{min-width:0;flex:1}
.budget-section-title .sub{font-size:10.5px;line-height:1.3;max-width:560px}
.budget-suggestion-actions,.reno-head-actions{display:flex;flex-direction:column;align-items:flex-end;gap:5px;flex:0 0 auto}
#budgetApplySuggestions,.reno-suggestion-btn{white-space:nowrap;flex:0 0 auto}
.suggestion-total{font-size:10.5px;font-weight:400;color:#a6aebb;line-height:1.2;text-align:right;white-space:nowrap}
.suggestion-total.applied{color:#2563eb}
@media(max-width:520px){
  .budget-section-title{align-items:flex-start}
  .budget-section-title .sub{font-size:10px;line-height:1.25}
  #budgetApplySuggestions,.reno-suggestion-btn{font-size:11px;padding-left:9px;padding-right:9px;white-space:nowrap}
  .reno-head-actions{max-width:none}
}
</style>
"""

js = r"""
<script>
// V8.240 visible suggestion placeholders and suggestion totals
(function(){
  function money(value){
    return new Intl.NumberFormat("de-DE",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(Math.max(0,Number(value)||0));
  }

  function budgetSuggestionData(){
    const suggestions=getBudgetSuggestions();
    const ids=["budgetFood","budgetMobility","budgetInsurance","budgetTelecom","budgetLeisure","budgetChildCosts","budgetOther"];
    const total=ids.reduce((sum,id)=>sum+Math.max(0,Number(suggestions[id])||0),0);
    const signature=JSON.stringify(ids.map(id=>[id,Math.round(Number(suggestions[id])||0)]));
    return {suggestions,ids,total,signature};
  }

  function ensureBudgetSuggestionUi(){
    const button=document.getElementById("budgetApplySuggestions");
    if(!button) return;
    let actions=document.getElementById("budgetSuggestionActions");
    if(!actions){
      actions=document.createElement("div");
      actions.id="budgetSuggestionActions";
      actions.className="budget-suggestion-actions";
      button.parentNode.insertBefore(actions,button);
      actions.appendChild(button);
      const total=document.createElement("div");
      total.id="budgetSuggestionTotal";
      total.className="suggestion-total";
      actions.appendChild(total);
    }
    const title=button.closest(".budget-section-title");
    const info=title ? title.querySelector(".sub") : null;
    if(info) info.textContent='Richtwerte nach Haushaltsgröße. Erst mit „Vorschläge übernehmen“ werden sie als echte Werte berechnet.';
  }

  function updateBudgetSuggestionTotal(){
    ensureBudgetSuggestionUi();
    const el=document.getElementById("budgetSuggestionTotal");
    if(!el) return;
    const data=budgetSuggestionData();
    const applied=localStorage.getItem("ff_budget_suggestions_applied_signature")===data.signature;
    el.textContent="Vorschlag gesamt: "+money(data.total);
    el.classList.toggle("applied",applied);
  }

  renderBudgetSuggestions=function(){
    const data=budgetSuggestionData();
    const map={
      budgetFood:"budgetFoodSuggestion",
      budgetMobility:"budgetMobilitySuggestion",
      budgetInsurance:"budgetInsuranceSuggestion",
      budgetTelecom:"budgetTelecomSuggestion",
      budgetLeisure:"budgetLeisureSuggestion",
      budgetChildCosts:"budgetChildCostsSuggestion",
      budgetOther:"budgetOtherSuggestion"
    };
    Object.entries(map).forEach(function(entry){
      const key=entry[0], id=entry[1];
      const input=$(key);
      if(input){
        const amount=Math.max(0,Math.round(Number(data.suggestions[key])||0));
        input.placeholder=amount>0 ? String(amount) : "0";
        // Ursache fuer die bisher unsichtbaren Platzhalter:
        // value="0" verdeckt den Placeholder. Optisch leer, rechnerisch weiterhin 0.
        if(!budgetExpenseManual[key] && Math.abs(budgetVal(key))<0.005){
          input.value="";
        }
      }
      if($(id)) $(id).textContent="";
    });
    updateBudgetSuggestionTotal();
  };

  ensureBudgetSuggestionUi();
  const budgetButton=document.getElementById("budgetApplySuggestions");
  if(budgetButton){
    budgetButton.addEventListener("click",function(){
      const data=budgetSuggestionData();
      localStorage.setItem("ff_budget_suggestions_applied_signature",data.signature);
      setTimeout(updateBudgetSuggestionTotal,0);
    });
  }

  document.addEventListener("input",function(event){
    if(event.target && (event.target.id==="budgetAdults" || event.target.id==="budgetChildren")){
      setTimeout(function(){
        renderBudgetSuggestions();
      },0);
    }
  },true);

  function renoSuggestionValue(t){
    if(!t) return 0;
    if(t.mode==="sqm"){
      if(t.defaultOff) return 0;
      return Math.max(0,Math.round(val("area")*Number(t.rate||0)));
    }
    const hint=fixedTradeHints[t.name];
    if(hint && hint.rate && hint.areaKey){
      return Math.max(0,Math.round(suggestedFixedAmount(hint)||0));
    }
    return 0;
  }

  function renoSuggestionData(){
    const rows=trades.map(function(t){ return [t.key,renoSuggestionValue(t)]; });
    return {
      total:rows.reduce(function(sum,row){ return sum+Math.max(0,Number(row[1])||0); },0),
      signature:JSON.stringify(rows)
    };
  }

  function renoSignatureKey(){
    let mode="flip";
    try{ mode=currentDealType()==="own" ? "own" : "flip"; }catch(_err){}
    return "ff_"+mode+"_reno_suggestions_applied_signature";
  }

  function ensureRenoSuggestionUi(){
    const button=document.getElementById("applyTradeSuggestions");
    if(!button) return;
    const actions=button.parentElement;
    if(actions && !document.getElementById("renoSuggestionTotal")){
      const total=document.createElement("div");
      total.id="renoSuggestionTotal";
      total.className="suggestion-total";
      button.insertAdjacentElement("afterend",total);
    }
  }

  function updateRenoSuggestionTotal(){
    ensureRenoSuggestionUi();
    const el=document.getElementById("renoSuggestionTotal");
    if(!el) return;
    const data=renoSuggestionData();
    const applied=localStorage.getItem(renoSignatureKey())===data.signature;
    el.textContent="Vorschlag gesamt: "+money(data.total);
    el.classList.toggle("applied",applied);
  }

  if(typeof renderTrades==="function"){
    const originalRenderTrades=renderTrades;
    renderTrades=function(){
      originalRenderTrades();
      updateRenoSuggestionTotal();
    };
  }

  ensureRenoSuggestionUi();
  const renoButton=document.getElementById("applyTradeSuggestions");
  if(renoButton){
    renoButton.addEventListener("click",function(){
      const data=renoSuggestionData();
      localStorage.setItem(renoSignatureKey(),data.signature);
      setTimeout(updateRenoSuggestionTotal,0);
    });
  }

  document.addEventListener("input",function(event){
    if(!event.target) return;
    if(event.target.classList && event.target.classList.contains("trade-area")){
      setTimeout(updateRenoSuggestionTotal,0);
    }
    if(event.target.id==="area"){
      setTimeout(updateRenoSuggestionTotal,0);
    }
  },true);

  document.addEventListener("change",function(event){
    if(event.target && event.target.name==="dealType"){
      setTimeout(updateRenoSuggestionTotal,0);
    }
  },true);

  renderBudgetSuggestions();
  updateRenoSuggestionTotal();
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.240 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

# Versionsnummern in Kalkulator, PDF-Berichten und Service-Worker-Registrierung.
s=s.replace("V8.239","V8.240")
s=s.replace("service-worker.js?v=8.239","service-worker.js?v=8.240")

required=[
    'V8.240 visible suggestion placeholders and suggestion totals',
    'if(!budgetExpenseManual[key] && Math.abs(budgetVal(key))<0.005)',
    'id="budgetSuggestionTotal"',
    '"Vorschlag gesamt: "+money(data.total)',
    'classList.toggle("applied",applied)',
    'id="renoSuggestionTotal"',
    '#budgetApplySuggestions,.reno-suggestion-btn{white-space:nowrap',
    'V8.240',
    'service-worker.js?v=8.240'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.240 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.240 suggestion display patch applied")
