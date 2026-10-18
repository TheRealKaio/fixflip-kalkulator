from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
.own-finance-card{display:none}
.own-finance-card.active{display:block}
.own-finance-card .advanced{margin:0;border:0;padding:0;background:transparent}
.own-finance-card .advanced>summary{
  list-style:none;
  cursor:pointer;
  font-size:18px;
  line-height:1.25;
  font-weight:800;
  color:#172033;
  padding:0;
  margin:0;
}
.own-finance-card .advanced>summary::-webkit-details-marker{display:none}
.own-finance-card .advanced>summary::after{
  content:"+";
  float:right;
  width:28px;
  height:28px;
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
  background:#eef2f7;
  color:#52627a;
  font-size:18px;
  font-weight:700;
  margin-top:-3px;
}
.own-finance-card .advanced[open]>summary::after{content:"−"}
.own-finance-card .advanced>summary+*{margin-top:14px}
#ownMarketCheckSection .market-check-head h2{margin-bottom:4px}
</style>
"""

js=r"""
<script>
// V8.245 Eigennutzung: Deal, Kaufpreis-Check und Finanzierung als getrennte Boxen
(function(){
  const root=document.getElementById("dealCalculatorContent");
  const market=document.getElementById("ownMarketCheckSection");
  const goals=document.getElementById("projectGoalsSection");
  if(!root || !market) return;

  const dealCard=Array.from(root.children).find(function(el){
    return el.matches && el.matches("section.card") &&
      el.querySelector && el.querySelector("h2") &&
      ["1. Dein Deal","1. Deine Immobilie"].includes(el.querySelector("h2").textContent.trim());
  });
  if(!dealCard) return;\n  const dealHeading=dealCard.querySelector("h2");\n  if(dealHeading) dealHeading.textContent="1. Deine Immobilie";

  const financeDetails=Array.from(dealCard.querySelectorAll("details.advanced")).find(function(el){
    const summary=el.querySelector(":scope > summary");
    return summary && summary.textContent.includes("Finanzierung");
  });
  if(!financeDetails) return;

  // Ursprüngliche Position merken, damit Fix & Flip unverändert bleibt.
  const financeOriginalNext=financeDetails.nextSibling;

  let financeCard=document.getElementById("ownFinanceCard");
  if(!financeCard){
    financeCard=document.createElement("section");
    financeCard.id="ownFinanceCard";
    financeCard.className="card own-finance-card";
    market.insertAdjacentElement("afterend",financeCard);
  }

  function setMarketHeading(){
    const h=market.querySelector(".market-check-head h2");
    if(h) h.textContent="2. Kaufpreis-Check";
  }

  function setFinanceHeading(own){
    const summary=financeDetails.querySelector(":scope > summary");
    if(!summary) return;
    summary.textContent=own
      ? "3. Finanzierung und Nebenkosten"
      : "Finanzierung & Nebenkosten anpassen";
  }

  function placeForOwnUse(){
    setMarketHeading();
    setFinanceHeading(true);

    if(financeDetails.parentElement!==financeCard){
      financeCard.appendChild(financeDetails);
    }
    financeCard.classList.add("active");
  }

  function placeForFlip(){
    setFinanceHeading(false);
    financeCard.classList.remove("active");

    if(financeDetails.parentElement!==dealCard){
      if(financeOriginalNext && financeOriginalNext.parentNode===dealCard){
        dealCard.insertBefore(financeDetails,financeOriginalNext);
      }else if(goals && goals.parentNode===dealCard){
        dealCard.insertBefore(financeDetails,goals);
      }else{
        dealCard.appendChild(financeDetails);
      }
    }
  }

  function syncOwnUseLayout(){
    let mode="";
    try{ mode=currentDealType(); }catch(_err){}
    if(mode==="own") placeForOwnUse();
    else placeForFlip();
  }

  document.addEventListener("change",function(event){
    if(event.target && event.target.name==="dealType"){
      setTimeout(syncOwnUseLayout,0);
    }
  },true);

  syncOwnUseLayout();
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.245 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.244","V8.245")
s=s.replace("service-worker.js?v=8.244","service-worker.js?v=8.245")

required=[
  'V8.245 Eigennutzung: Deal, Kaufpreis-Check und Finanzierung als getrennte Boxen',
  'h.textContent="2. Kaufpreis-Check";',
  '"3. Finanzierung und Nebenkosten"',
  'financeCard.className="card own-finance-card";',
  'dealCard.insertBefore(financeDetails,goals);',
  'V8.245',
  'service-worker.js?v=8.245'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.245 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.245 own-use section layout applied")
