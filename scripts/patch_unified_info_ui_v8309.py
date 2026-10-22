from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# Vermietung: eigenes dunkles Kurz-Popup entfernen.
old_pop="""  const pop=document.createElement('div');pop.className='rent-info-popover';pop.hidden=true;document.body.appendChild(pop);
  document.addEventListener('click',e=>{const b=e.target.closest?.('.rent-info-dot');if(b){e.preventDefault();e.stopPropagation();pop.textContent=b.dataset.info||'';pop.hidden=false;clearTimeout(pop._t);pop._t=setTimeout(()=>pop.hidden=true,7000);}else if(!pop.hidden){pop.hidden=true;}});
"""
rep(old_pop,"","rental legacy info popover")

# Einheitlicher Badge-Stil: Vermietungs-Badge auf alle info-btn übertragen.
css=r'''
<style id="unified-info-ui-v8309">
/* Einheitlicher kleiner Info-Badge in allen Kalkulatoren. */
.info-btn,
.info-dot{
  width:18px!important;
  height:18px!important;
  min-width:18px!important;
  min-height:18px!important;
  padding:0!important;
  border:1px solid #94a3b8!important;
  border-radius:50%!important;
  background:#fff!important;
  color:#475569!important;
  font-size:11px!important;
  font-weight:800!important;
  line-height:16px!important;
  text-align:center!important;
  box-sizing:border-box!important;
  cursor:pointer!important;
}
.info-btn{
  right:10px;
  top:10px;
}
.inline-info{
  position:static!important;
  margin-left:4px!important;
  vertical-align:middle!important;
  flex:0 0 18px!important;
}
.kpi.compact .info-btn{
  width:18px!important;
  height:18px!important;
  min-width:18px!important;
  min-height:18px!important;
  right:7px!important;
  top:7px!important;
  font-size:11px!important;
}
.field label:has(.inline-info){
  align-items:center!important;
}
</style>
'''
rep("</head>",css+"\n</head>","head css")

# Vermietungs-Infos in dasselbe Bottom-Sheet wie Fix & Flip überführen.
js=r'''
<script id="unified-rental-info-sheet-v8309">
(function(){
  const $=id=>document.getElementById(id);

  const rentalInfo={
    "Nettokaltmiete pro Monat":{
      title:"Nettokaltmiete pro Monat",
      body:"Die Nettokaltmiete ist die monatliche Miete ohne Betriebs- und Heizkosten. Sie ist die zentrale Einnahmegröße für die Rendite- und Cashflowberechnung.",
      plain:"Hier zählt nur die eigentliche Miete für die Wohnung – ohne Nebenkosten.",
      know:"Eine unrealistisch hoch angesetzte Miete verbessert die Kennzahlen nur rechnerisch. Verwende möglichst die nachhaltig erzielbare Nettokaltmiete."
    },
    "Hausgeld gesamt pro Monat":{
      title:"Hausgeld gesamt pro Monat",
      body:"Das Hausgeld ist die monatliche Zahlung an die Wohnungseigentümergemeinschaft und enthält sowohl umlagefähige als auch nicht umlagefähige Bestandteile.",
      plain:"Das gesamte Hausgeld ist nicht automatisch deine tatsächliche Eigentümerbelastung.",
      know:"Für den Cashflow wird der separat eingetragene nicht umlagefähige Anteil berücksichtigt. Typische Bestandteile des Hausgelds sind zum Beispiel Wasser, Heizung und Müllentsorgung."
    },
    "Davon nicht umlagefähig":{
      title:"Davon nicht umlagefähig",
      body:"Dieser Teil des Hausgeldes verbleibt beim Eigentümer und kann grundsätzlich nicht über die Betriebskostenabrechnung auf den Mieter übertragen werden.",
      plain:"Diesen Betrag zahlst du als Vermieter selbst – deshalb reduziert er deinen monatlichen Cashflow.",
      know:"Typische Beispiele sind Verwalterkosten, Instandhaltung beziehungsweise Instandsetzung und Zuführungen zur Erhaltungsrücklage."
    },
    "Mietausfall / Leerstand":{
      title:"Mietausfall / Leerstand",
      body:"Der Sicherheitsabschlag berücksichtigt Zeiträume oder Situationen, in denen die kalkulierte Miete nicht vollständig eingeht.",
      plain:"Der Rechner reduziert die erwartete Miete vorsichtshalber um diesen Prozentsatz.",
      know:"Auch bei gefragten Wohnungen kann ein kleiner Puffer sinnvoll sein, etwa für Mieterwechsel, Zahlungsrisiken oder vorübergehenden Leerstand."
    },
    "Verwaltung pro Monat":{
      title:"Verwaltung pro Monat",
      body:"Hier können laufende Kosten für eine externe oder interne Verwaltung der vermieteten Wohnung berücksichtigt werden.",
      plain:"Trage hier nur Verwaltungskosten ein, die zusätzlich bei dir als Eigentümer anfallen.",
      know:"Sind Verwaltungsanteile bereits vollständig im nicht umlagefähigen Hausgeld enthalten, solltest du sie nicht doppelt erfassen."
    },
    "Zusätzliche Instandhaltung":{
      title:"Zusätzliche Instandhaltung",
      body:"Der Kalkulator setzt als Richtwert 1,50 € pro m² Wohnfläche und Monat an. Der Wert bleibt vollständig editierbar.",
      plain:"Das ist ein zusätzlicher kalkulatorischer Puffer für Reparaturen und laufende Instandhaltung.",
      know:"Passe den Betrag an Alter, Zustand und Ausstattung des Objekts an. Bereits anderweitig berücksichtigte Rücklagen sollten nicht doppelt angesetzt werden."
    },
    "Sonstige Vermieterkosten":{
      title:"Sonstige Vermieterkosten",
      body:"Hier gehören weitere laufende Eigentümerkosten hinein, die weder umlagefähig noch bereits in einer anderen Position berücksichtigt sind.",
      plain:"Nutze das Feld für regelmäßige Zusatzkosten, die sonst im Cashflow fehlen würden.",
      know:"Achte darauf, Kosten nicht doppelt zu erfassen, wenn sie bereits im Hausgeld, in der Verwaltung oder bei der Instandhaltung enthalten sind."
    },
    "Monatlicher Cashflow":{
      title:"Monatlicher Cashflow",
      body:"Der Cashflow zeigt die laufende Liquidität nach Mietausfall, nicht umlagefähigen Eigentümerkosten, Verwaltung, Instandhaltung sowie Zins und Tilgung – vor persönlicher Einkommensteuer.",
      plain:"Positiver Cashflow bedeutet, dass nach den angesetzten laufenden Kosten und der Kreditrate monatlich Geld übrig bleibt.",
      know:"Eine mögliche AfA ist kein Geldzufluss, kann aber die persönliche Steuerbelastung reduzieren. Eine mögliche Wertsteigerung kann Vermögen aufbauen, ist jedoch kein laufender Cashflow und nicht garantiert."
    },
    "Kaufpreisfaktor":{
      title:"Kaufpreisfaktor",
      body:"Der Kaufpreisfaktor entspricht Kaufpreis geteilt durch Jahresnettokaltmiete und zeigt, wie viele Jahresmieten rechnerisch dem Kaufpreis entsprechen.",
      plain:"Je niedriger der Faktor, desto höher ist bei gleicher Kostenstruktur grundsätzlich die laufende Mietrendite.",
      know:"Unter 20 gilt als sehr gut, 20 bis 25 als gut bis solide, über 25 bis 30 als mäßig beziehungsweise teuer und über 30 als sehr teuer. Lage, Zustand, Finanzierung und Entwicklungspotenzial müssen trotzdem separat geprüft werden."
    }
  };

  document.addEventListener("click",function(e){
    const btn=e.target.closest?.(".rent-info-dot");
    if(!btn) return;

    e.preventDefault();
    e.stopPropagation();

    const raw=(btn.getAttribute("aria-label")||"").replace(/^Info zu\s*/,"").trim();
    const x=rentalInfo[raw]||{
      title:raw||"Information",
      body:btn.dataset.info||"",
      plain:btn.dataset.info||"",
      know:"Die Angabe dient der Kalkulation und sollte an das konkrete Objekt angepasst werden."
    };

    const backdrop=$("sheetBackdrop");
    if(!backdrop) return;

    $("sheetTitle").textContent=x.title;
    $("sheetBody").textContent=x.body;
    $("sheetPlain").innerHTML="<strong>Einfach gesagt:</strong><br>"+x.plain;
    $("sheetKnow").innerHTML="<strong>Gut zu wissen:</strong><br>"+x.know;
    backdrop.classList.add("show");
  },true);
})();
</script>
'''
rep("</body>",js+"\n</body>","body script")

s=s.replace("V8.308","V8.309")
s=s.replace("service-worker.js?v=8.308","service-worker.js?v=8.309")

required=[
  'id="unified-info-ui-v8309"',
  'id="unified-rental-info-sheet-v8309"',
  'document.addEventListener("click",function(e){',
  'const btn=e.target.closest?.(".rent-info-dot");',
  'backdrop.classList.add("show");',
  'Einfach gesagt:',
  'Gut zu wissen:',
  "V8.309",
  "service-worker.js?v=8.309"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.309 missing: "+", ".join(missing))

if "rent-info-popover';pop.hidden=true" in s:
    raise SystemExit("V8.309 legacy rental popover still present")

p.write_text(s,encoding="utf-8")
print("V8.309 unified info badges and Fix-&-Flip bottom sheets applied")
