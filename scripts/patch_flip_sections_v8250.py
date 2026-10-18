from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
.flip-section-card{display:none}
.flip-section-card.active{display:block}
.flip-section-card .advanced{margin:0;border:0;padding:0;background:transparent}
.flip-section-card .advanced>summary{
  list-style:none;
  cursor:pointer;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  font-size:18px;
  line-height:1.2;
  font-weight:700;
  letter-spacing:-.02em;
  color:#172033;
  padding:0;
  margin:0;
}
.flip-section-card .advanced>summary::-webkit-details-marker{display:none}
.flip-section-card .advanced>summary::after{
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
}
.flip-section-card .advanced[open]>summary::after{
  content:"−";
  font-size:22px;
}
.flip-section-subtitle{
  margin:6px 0 14px!important;
  color:#94a3b8!important;
  font-size:12px!important;
  line-height:1.45!important;
  font-weight:400!important;
}
</style>
"""

js=r"""
<script>
// V8.250 Fix & Flip: Finanzierung und Projektziele als getrennte Boxen
(function(){
  const root=document.getElementById("dealCalculatorContent");
  const goals=document.getElementById("projectGoalsSection");
  if(!root || !goals) return;

  const dealCard=Array.from(root.children).find(function(el){
    return el.matches && el.matches("section.card") &&
      el.querySelector && el.querySelector("h2") &&
      ["1. Dein Deal","1. Deine Immobilie"].includes(el.querySelector("h2").textContent.trim());
  });
  if(!dealCard) return;

  const dealHeading=dealCard.querySelector("h2");
  if(dealHeading) dealHeading.textContent="1. Deine Immobilie";

  function findFinanceDetails(){
    const candidates=[
      ...Array.from(dealCard.querySelectorAll("details.advanced")),
      ...Array.from(document.querySelectorAll("#ownFinanceCard details.advanced")),
      ...Array.from(document.querySelectorAll("#flipFinanceCard details.advanced"))
    ];
    return candidates.find(function(el){
      const summary=el.querySelector(":scope > summary");
      return summary && summary.textContent.includes("Finanzierung");
    }) || null;
  }

  const financeDetails=findFinanceDetails();
  if(!financeDetails) return;

  const goalsOriginalNext=goals.nextSibling;

  let flipFinanceCard=document.getElementById("flipFinanceCard");
  if(!flipFinanceCard){
    flipFinanceCard=document.createElement("section");
    flipFinanceCard.id="flipFinanceCard";
    flipFinanceCard.className="card flip-section-card";
    dealCard.insertAdjacentElement("afterend",flipFinanceCard);
  }

  let flipGoalsCard=document.getElementById("flipGoalsCard");
  if(!flipGoalsCard){
    flipGoalsCard=document.createElement("section");
    flipGoalsCard.id="flipGoalsCard";
    flipGoalsCard.className="card flip-section-card";
    flipFinanceCard.insertAdjacentElement("afterend",flipGoalsCard);
  }

  let financeSubtitle=document.getElementById("flipFinanceSubtitle");
  if(!financeSubtitle){
    financeSubtitle=document.createElement("p");
    financeSubtitle.id="flipFinanceSubtitle";
    financeSubtitle.className="flip-section-subtitle";
    financeSubtitle.textContent="Trage hier die Bedingungen deiner Finanzierung ein.";
  }

  let goalsSubtitle=document.getElementById("flipGoalsSubtitle");
  if(!goalsSubtitle){
    goalsSubtitle=document.createElement("p");
    goalsSubtitle.id="flipGoalsSubtitle";
    goalsSubtitle.className="flip-section-subtitle";
    goalsSubtitle.textContent="Trage hier die Bedingungen deiner Finanzziele ein. Sie steuern auch die Farbampel der Ergebnisse.";
  }

  function setFinanceHeading(text){
    const summary=financeDetails.querySelector(":scope > summary");
    if(summary) summary.textContent=text;
  }

  function setGoalsHeading(text){
    const summary=goals.querySelector(":scope > summary");
    if(summary) summary.textContent=text;
  }

  function ensureFinanceSubtitle(){
    const summary=financeDetails.querySelector(":scope > summary");
    if(summary && financeSubtitle.parentElement!==financeDetails){
      summary.insertAdjacentElement("afterend",financeSubtitle);
    }else if(summary && financeSubtitle.previousElementSibling!==summary){
      summary.insertAdjacentElement("afterend",financeSubtitle);
    }
  }

  function ensureGoalsSubtitle(){
    const summary=goals.querySelector(":scope > summary");
    const oldSub=goals.querySelector(":scope > p.sub");
    if(oldSub) oldSub.remove();
    if(summary && goalsSubtitle.parentElement!==goals){
      summary.insertAdjacentElement("afterend",goalsSubtitle);
    }else if(summary && goalsSubtitle.previousElementSibling!==summary){
      summary.insertAdjacentElement("afterend",goalsSubtitle);
    }
  }

  function placeForFlip(){
    setFinanceHeading("2. Finanzierung und Nebenkosten");
    setGoalsHeading("3. Projektziele & Steuer");
    ensureFinanceSubtitle();
    ensureGoalsSubtitle();

    if(financeDetails.parentElement!==flipFinanceCard){
      flipFinanceCard.appendChild(financeDetails);
    }
    if(goals.parentElement!==flipGoalsCard){
      flipGoalsCard.appendChild(goals);
    }

    goals.classList.remove("mode-hidden");
    flipFinanceCard.classList.add("active");
    flipGoalsCard.classList.add("active");
  }

  function placeForOwn(){
    flipFinanceCard.classList.remove("active");
    flipGoalsCard.classList.remove("active");

    // Eigennutzung behält ihre bestehende V8.245-Struktur.
    const ownFinanceCard=document.getElementById("ownFinanceCard");
    setFinanceHeading("3. Finanzierung und Nebenkosten");
    if(ownFinanceCard && financeDetails.parentElement!==ownFinanceCard){
      ownFinanceCard.appendChild(financeDetails);
    }

    setGoalsHeading("Projektziele & Steuer");
    goals.classList.add("mode-hidden");
    if(goals.parentElement!==dealCard){
      if(goalsOriginalNext && goalsOriginalNext.parentNode===dealCard){
        dealCard.insertBefore(goals,goalsOriginalNext);
      }else{
        dealCard.appendChild(goals);
      }
    }
  }

  function syncFlipLayout(){
    let mode="";
    try{ mode=currentDealType(); }catch(_err){}
    if(mode==="flip") placeForFlip();
    else if(mode==="own") placeForOwn();
  }

  document.addEventListener("change",function(event){
    if(event.target && event.target.name==="dealType"){
      setTimeout(syncFlipLayout,0);
    }
  },true);

  syncFlipLayout();
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.250 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.249","V8.250")
s=s.replace("service-worker.js?v=8.249","service-worker.js?v=8.250")

required=[
  'V8.250 Fix & Flip: Finanzierung und Projektziele als getrennte Boxen',
  'flipFinanceCard.className="card flip-section-card";',
  'flipGoalsCard.className="card flip-section-card";',
  '"2. Finanzierung und Nebenkosten"',
  '"3. Projektziele & Steuer"',
  'Trage hier die Bedingungen deiner Finanzierung ein.',
  'Trage hier die Bedingungen deiner Finanzziele ein.',
  'goals.classList.remove("mode-hidden");',
  'V8.250',
  'service-worker.js?v=8.250'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.250 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.250 Fix-&-Flip section layout applied")
