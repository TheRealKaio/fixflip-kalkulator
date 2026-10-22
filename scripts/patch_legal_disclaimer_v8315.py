from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label, count=1):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,count)

# Footer: add Haftungsausschluss next to Datenschutz.
old_footer='''          <a href="#" data-legal-placeholder="datenschutz">Datenschutz</a>
        </nav>'''
new_footer='''          <a href="#" data-legal-placeholder="datenschutz">Datenschutz</a>
          <span aria-hidden="true">·</span>
          <a href="#haftungsausschluss" data-legal-placeholder="haftungsausschluss">Haftungsausschluss</a>
        </nav>'''
rep(old_footer,new_footer,"legal footer")

# Styling for bottom-sheet CTA and dedicated legal page.
css=r'''
<style id="legal-disclaimer-v8315">
.legal-sheet-cta{
  display:block;
  width:100%;
  margin-top:14px;
  padding:11px 14px;
  border-radius:10px;
  border:0;
  background:#0f172a;
  color:#fff;
  text-decoration:none;
  text-align:center;
  font-weight:700;
  font-size:14px;
  box-sizing:border-box;
}
.legal-sheet-cta:hover,.legal-sheet-cta:focus{background:#1e293b;color:#fff}
.legal-page-overlay{
  position:fixed;
  inset:0;
  z-index:9999;
  background:#f8fafc;
  overflow:auto;
  display:none;
}
.legal-page-overlay.show{display:block}
.legal-page-shell{max-width:760px;margin:0 auto;padding:24px 18px 48px}
.legal-page-top{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:24px}
.legal-page-back{
  border:1px solid #cbd5e1;
  background:#fff;
  color:#334155;
  border-radius:9px;
  padding:8px 12px;
  font-weight:700;
  cursor:pointer;
}
.legal-page-card{
  background:#fff;
  border:1px solid #e2e8f0;
  border-radius:16px;
  padding:24px;
  box-shadow:0 8px 24px rgba(15,23,42,.06);
}
.legal-page-card h1{margin:0 0 8px;font-size:28px;line-height:1.15;color:#0f172a}
.legal-page-card .legal-subtitle{margin:0 0 22px;color:#64748b;font-size:14px}
.legal-page-card h2{font-size:17px;margin:24px 0 8px;color:#0f172a}
.legal-page-card p{font-size:14px;line-height:1.65;color:#334155;margin:0 0 12px}
@media(max-width:640px){
  .legal-page-shell{padding:16px 12px 36px}
  .legal-page-card{padding:18px}
  .legal-page-card h1{font-size:24px}
}
</style>
'''
rep("</head>",css+"\n</head>","legal css")

# Dedicated full-page legal view.
page=r'''
<div id="legalDisclaimerPage" class="legal-page-overlay" aria-hidden="true">
  <div class="legal-page-shell">
    <div class="legal-page-top">
      <strong>Neustart Immo Check</strong>
      <button type="button" class="legal-page-back" id="legalDisclaimerBack">Zurück</button>
    </div>
    <article class="legal-page-card">
      <h1>Haftungsausschluss / Disclaimer</h1>
      <p class="legal-subtitle">Hinweise zur Nutzung der Kalkulatoren und PDF-Berichte</p>

      <h2>Unverbindliche Orientierung</h2>
      <p>Die auf dieser Website bereitgestellten Kalkulatoren, Auswertungen und PDF-Berichte basieren auf den vom Nutzer eingegebenen Daten sowie auf hinterlegten Annahmen und Berechnungsmodellen. Sie dienen ausschließlich der unverbindlichen Information und Orientierung.</p>

      <h2>Keine individuelle Beratung</h2>
      <p>Die Inhalte stellen keine Anlage-, Finanzierungs-, Immobilien-, Steuer- oder Rechtsberatung dar. Insbesondere handelt es sich nicht um eine Kauf-, Verkaufs-, Finanzierungs- oder sonstige Handlungsempfehlung. Eine individuelle Prüfung durch entsprechend qualifizierte Fachleute wird hierdurch nicht ersetzt.</p>

      <h2>Eigene Prüfung der Eingaben und Ergebnisse</h2>
      <p>Alle Eingaben, Annahmen und Ergebnisse sind eigenverantwortlich zu prüfen. Tatsächliche Kosten, Finanzierungskonditionen, Mieten, Steuern, Renditen, Sanierungsaufwendungen und Verkaufserlöse können von den berechneten Modellwerten abweichen.</p>

      <h2>Markt-, Zins- und Wertentwicklung</h2>
      <p>Markt-, Zins-, Miet-, Kosten- und Wertentwicklungen sind nicht zuverlässig vorhersehbar. Eine bestimmte Rendite, Wertsteigerung, Vermögensentwicklung oder Wirtschaftlichkeit kann nicht zugesichert werden.</p>

      <h2>Steuern und AfA</h2>
      <p>Steuerliche Auswirkungen, einschließlich einer möglichen Abschreibung für Abnutzung (AfA), werden nur vereinfacht beziehungsweise modellhaft dargestellt. Die tatsächliche steuerliche Wirkung hängt von der individuellen Situation ab und sollte bei Bedarf mit einer Steuerberatung geprüft werden.</p>

      <h2>Haftung</h2>
      <p>Für die Richtigkeit, Vollständigkeit, Aktualität und Übertragbarkeit der dargestellten Berechnungen und Informationen auf den konkreten Einzelfall wird keine Gewähr übernommen. Eine Haftung für Entscheidungen oder wirtschaftliche Folgen, die allein auf Grundlage der bereitgestellten Kalkulationen oder Berichte getroffen werden, ist soweit gesetzlich zulässig ausgeschlossen.</p>
    </article>
  </div>
</div>
'''
rep("</body>",page+"\n</body>","legal page")

# Same text as a final page in every PDF report.
pdf_helper=r'''
          function appendPdfDisclaimerPage(doc){
            const L=16, R=194, W=178;
            doc.addPage();
            drawPdfBrandHeader(
              doc,
              "Haftungsausschluss / Disclaimer",
              "Hinweise zur Nutzung der Kalkulatoren und PDF-Berichte",
              new Date().toLocaleDateString("de-DE")
            );
            let y=45;
            const paragraphs=[
              ["Unverbindliche Orientierung","Die auf dieser Website bereitgestellten Kalkulatoren, Auswertungen und PDF-Berichte basieren auf den vom Nutzer eingegebenen Daten sowie auf hinterlegten Annahmen und Berechnungsmodellen. Sie dienen ausschließlich der unverbindlichen Information und Orientierung."],
              ["Keine individuelle Beratung","Die Inhalte stellen keine Anlage-, Finanzierungs-, Immobilien-, Steuer- oder Rechtsberatung dar. Insbesondere handelt es sich nicht um eine Kauf-, Verkaufs-, Finanzierungs- oder sonstige Handlungsempfehlung. Eine individuelle Prüfung durch entsprechend qualifizierte Fachleute wird hierdurch nicht ersetzt."],
              ["Eigene Prüfung der Eingaben und Ergebnisse","Alle Eingaben, Annahmen und Ergebnisse sind eigenverantwortlich zu prüfen. Tatsächliche Kosten, Finanzierungskonditionen, Mieten, Steuern, Renditen, Sanierungsaufwendungen und Verkaufserlöse können von den berechneten Modellwerten abweichen."],
              ["Markt-, Zins- und Wertentwicklung","Markt-, Zins-, Miet-, Kosten- und Wertentwicklungen sind nicht zuverlässig vorhersehbar. Eine bestimmte Rendite, Wertsteigerung, Vermögensentwicklung oder Wirtschaftlichkeit kann nicht zugesichert werden."],
              ["Steuern und AfA","Steuerliche Auswirkungen, einschließlich einer möglichen Abschreibung für Abnutzung (AfA), werden nur vereinfacht beziehungsweise modellhaft dargestellt. Die tatsächliche steuerliche Wirkung hängt von der individuellen Situation ab und sollte bei Bedarf mit einer Steuerberatung geprüft werden."],
              ["Haftung","Für die Richtigkeit, Vollständigkeit, Aktualität und Übertragbarkeit der dargestellten Berechnungen und Informationen auf den konkreten Einzelfall wird keine Gewähr übernommen. Eine Haftung für Entscheidungen oder wirtschaftliche Folgen, die allein auf Grundlage der bereitgestellten Kalkulationen oder Berichte getroffen werden, ist soweit gesetzlich zulässig ausgeschlossen."]
            ];
            paragraphs.forEach(([heading,body])=>{
              doc.setTextColor(15,23,42);
              doc.setFont("helvetica","bold");
              doc.setFontSize(9.2);
              doc.text(pdfSafeText(heading),L,y);
              y+=4.6;
              doc.setTextColor(71,85,105);
              doc.setFont("helvetica","normal");
              doc.setFontSize(7.8);
              const lines=doc.splitTextToSize(pdfSafeText(body),W);
              try{
                doc.text(lines,L,y,{align:"justify",maxWidth:W,lineHeightFactor:1.25});
              }catch(e){
                doc.text(lines,L,y,{lineHeightFactor:1.25});
              }
              y+=lines.length*3.8+5.5;
            });
            doc.setTextColor(23,32,51);
          }

'''
anchor='function drawPdfFooter(doc, pageNo, totalPages, version){'
if anchor not in s:
    raise SystemExit("PDF helper anchor missing")
s=s.replace(anchor,pdf_helper+anchor,1)

# Auf der letzten PDF-Seite den rechtlichen Footer ergänzen,
# ohne vom inneren Aufbau der bestehenden Footer-Funktion abhängig zu sein.
footer_anchor='function drawPdfFooter(doc, pageNo, totalPages, version){'
if footer_anchor not in s:
    raise SystemExit("PDF footer declaration missing")

footer_wrapper=r'''function drawPdfFooter(doc, pageNo, totalPages, version){
            drawPdfFooterBase(doc,pageNo,totalPages,version);
            if(pageNo && totalPages && pageNo===totalPages){
              doc.setFont("helvetica","normal");
              doc.setFontSize(6.7);
              doc.setTextColor(100,110,125);
              doc.text("Datenschutz · Haftungsausschluss",194,286,{align:"right"});
              doc.setTextColor(23,32,51);
            }
          }

          function drawPdfFooterBase(doc, pageNo, totalPages, version){'''
s=s.replace(footer_anchor,footer_wrapper,1)

pdf_count=s.count("const totalPages=doc.getNumberOfPages();")
if pdf_count < 3:
    raise SystemExit(f"Expected at least 3 PDF totalPages anchors, found {pdf_count}")
s=s.replace("const totalPages=doc.getNumberOfPages();","appendPdfDisclaimerPage(doc);\n    const totalPages=doc.getNumberOfPages();")

# Footer click opens existing unified bottom sheet; CTA opens dedicated page.
js=r'''
<script id="legal-disclaimer-script-v8315">
(function(){
  const $=id=>document.getElementById(id);
  const disclaimerPage=$("legalDisclaimerPage");
  const backBtn=$("legalDisclaimerBack");

  function hideSheet(){
    const backdrop=$("sheetBackdrop");
    if(backdrop) backdrop.classList.remove("show");
  }

  function openDisclaimerPage(pushHash=true){
    hideSheet();
    if(!disclaimerPage) return;
    disclaimerPage.classList.add("show");
    disclaimerPage.setAttribute("aria-hidden","false");
    document.body.style.overflow="hidden";
    if(pushHash && location.hash!=="#haftungsausschluss"){
      history.pushState({legalDisclaimer:true},"","#haftungsausschluss");
    }
  }

  function closeDisclaimerPage(){
    if(!disclaimerPage) return;
    disclaimerPage.classList.remove("show");
    disclaimerPage.setAttribute("aria-hidden","true");
    document.body.style.overflow="";
    if(location.hash==="#haftungsausschluss"){
      history.replaceState(null,"",location.pathname+location.search);
    }
  }

  function addSheetCta(){
    const know=$("sheetKnow");
    if(!know) return;
    let cta=$("legalDisclaimerSheetCta");
    if(!cta){
      cta=document.createElement("a");
      cta.id="legalDisclaimerSheetCta";
      cta.className="legal-sheet-cta";
      cta.href="#haftungsausschluss";
      cta.textContent="Vollständigen Haftungsausschluss lesen";
      know.insertAdjacentElement("afterend",cta);
    }
    cta.hidden=false;
  }

  document.addEventListener("click",function(e){
    const link=e.target.closest?.('[data-legal-placeholder="haftungsausschluss"]');
    if(link){
      e.preventDefault();
      const backdrop=$("sheetBackdrop");
      if(!backdrop){
        openDisclaimerPage(true);
        return;
      }
      $("sheetTitle").textContent="Haftungsausschluss";
      $("sheetBody").textContent="Die Kalkulatoren und PDF-Berichte dienen ausschließlich der unverbindlichen Orientierung und ersetzen keine individuelle Finanzierungs-, Anlage-, Immobilien-, Steuer- oder Rechtsberatung.";
      $("sheetPlain").innerHTML="<strong>Einfach gesagt:</strong><br>Die Ergebnisse sind Modellrechnungen auf Basis deiner Eingaben. Sie sind keine Kauf-, Verkaufs- oder Finanzierungsempfehlung.";
      $("sheetKnow").innerHTML="<strong>Gut zu wissen:</strong><br>Markt-, Zins-, Miet-, Kosten- und Wertentwicklungen können abweichen. Auch steuerliche Effekte wie AfA hängen von der individuellen Situation ab.";
      addSheetCta();
      backdrop.classList.add("show");
      return;
    }

    if(e.target.closest?.("#legalDisclaimerSheetCta")){
      e.preventDefault();
      openDisclaimerPage(true);
    }
  },true);

  if(backBtn) backBtn.addEventListener("click",function(){
    if(history.length>1 && location.hash==="#haftungsausschluss"){
      history.back();
    }else{
      closeDisclaimerPage();
    }
  });

  window.addEventListener("popstate",function(){
    if(location.hash==="#haftungsausschluss") openDisclaimerPage(false);
    else closeDisclaimerPage();
  });

  if(location.hash==="#haftungsausschluss") openDisclaimerPage(false);
})();
</script>
'''
rep("</body>",js+"\n</body>","legal script")

s=s.replace("V8.314","V8.315")
s=s.replace("service-worker.js?v=8.314","service-worker.js?v=8.315")

required=[
  'data-legal-placeholder="haftungsausschluss"',
  '>Haftungsausschluss</a>',
  'id="legalDisclaimerPage"',
  'Haftungsausschluss / Disclaimer',
  'Vollständigen Haftungsausschluss lesen',
  'appendPdfDisclaimerPage(doc);',
  'align:"justify"',
  'service-worker.js?v=8.315',
  'V8.315'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.315 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print(f"V8.315 disclaimer page, bottom sheet, footer link and {pdf_count} PDF disclaimer pages added")
