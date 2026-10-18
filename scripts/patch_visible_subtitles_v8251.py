from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
/* V8.251: Subtitel bleiben auch bei geschlossenem Details-Bereich sichtbar */
.section-summary-copy{
  min-width:0;
  display:flex;
  flex-direction:column;
  align-items:flex-start;
  gap:4px;
}
.section-summary-title{
  display:block;
  font:inherit;
  color:inherit;
}
.section-summary-subtitle{
  display:block;
  color:#94a3b8;
  font-size:12px;
  line-height:1.45;
  font-weight:400;
  letter-spacing:0;
}
#ownFinanceSubtitle,
#flipFinanceSubtitle,
#flipGoalsSubtitle{
  display:none!important;
}
</style>
"""

js=r"""
<script>
// V8.251: sichtbare Subtitel direkt in den Summary-Kopf integrieren
(function(){
  function decorate(details,title,subtitle){
    if(!details) return;
    const summary=details.querySelector(":scope > summary");
    if(!summary) return;

    const currentTitle=summary.querySelector(".section-summary-title");
    const currentSubtitle=summary.querySelector(".section-summary-subtitle");
    if(currentTitle && currentSubtitle &&
       currentTitle.textContent===title &&
       currentSubtitle.textContent===subtitle){
      return;
    }

    summary.textContent="";
    const copy=document.createElement("span");
    copy.className="section-summary-copy";

    const titleEl=document.createElement("span");
    titleEl.className="section-summary-title";
    titleEl.textContent=title;

    const subtitleEl=document.createElement("span");
    subtitleEl.className="section-summary-subtitle";
    subtitleEl.textContent=subtitle;

    copy.appendChild(titleEl);
    copy.appendChild(subtitleEl);
    summary.appendChild(copy);
  }

  function syncVisibleSectionSubtitles(){
    let mode="";
    try{ mode=currentDealType(); }catch(_err){}

    if(mode==="own"){
      const ownFinance=document.querySelector("#ownFinanceCard details.advanced");
      decorate(
        ownFinance,
        "3. Finanzierung und Nebenkosten",
        "Trage hier die Bedingungen deiner Finanzierung ein."
      );
      return;
    }

    if(mode==="flip"){
      const flipFinance=document.querySelector("#flipFinanceCard details.advanced");
      const flipGoals=document.querySelector("#flipGoalsCard #projectGoalsSection");
      decorate(
        flipFinance,
        "2. Finanzierung und Nebenkosten",
        "Trage hier die Bedingungen deiner Finanzierung ein."
      );
      decorate(
        flipGoals,
        "3. Projektziele & Steuer",
        "Trage hier die Bedingungen deiner Finanzziele ein. Sie steuern auch die Farbampel der Ergebnisse."
      );
    }
  }

  document.addEventListener("change",function(event){
    if(event.target && event.target.name==="dealType"){
      setTimeout(syncVisibleSectionSubtitles,10);
    }
  },true);

  setTimeout(syncVisibleSectionSubtitles,10);
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.251 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

s=s.replace("V8.250","V8.251")
s=s.replace("service-worker.js?v=8.250","service-worker.js?v=8.251")

required=[
  'V8.251: Subtitel bleiben auch bei geschlossenem Details-Bereich sichtbar',
  'className="section-summary-copy"',
  '"3. Finanzierung und Nebenkosten"',
  '"2. Finanzierung und Nebenkosten"',
  '"3. Projektziele & Steuer"',
  '"Trage hier die Bedingungen deiner Finanzierung ein."',
  '"Trage hier die Bedingungen deiner Finanzziele ein. Sie steuern auch die Farbampel der Ergebnisse."',
  'setTimeout(syncVisibleSectionSubtitles,10);',
  'V8.251',
  'service-worker.js?v=8.251'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.251 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.251 persistent section subtitles applied")
