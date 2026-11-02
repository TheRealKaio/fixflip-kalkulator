"""V8.369: remove the persistent surplus note and reached-reserve notice."""

from pathlib import Path
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
html = path.read_text(encoding="utf-8")

note = '<div class="budget-rate-slider-note" id="budgetRateSliderNote">Nach links sinkt die Kreditrate und der verbleibende Monatsüberschuss steigt. Nach rechts umgekehrt.</div>'
if note not in html:
    raise SystemExit("V8.369 budget-rate note markup not found")
html = html.replace(note, "", 1)

start_marker = '    if($("budgetRateSliderNote")){'
end_marker = '    if($("budgetSafetyReserve") && localStorage.getItem("ff_budget_rateSliderPct")!==null){'
start = html.find(start_marker)
end = html.find(end_marker, start + len(start_marker))
if start < 0 or end < 0:
    raise SystemExit("V8.369 budget-rate message block not found")

replacement = '''    if($("budgetRateSliderWarning")){
      const currentBuffer=Number.isFinite(Number(m.rawReserve)) ? Number(m.rawReserve) : 0;
      const minimumReserve=Math.max(300,Number(m.minimumReserve)||300);
      const bufferDeviation=currentBuffer-minimumReserve;
      const minimumBufferBelow=bufferDeviation<-0.005;
      $("budgetRateSliderWarning").hidden=!minimumBufferBelow;
      if(minimumBufferBelow){
        $("budgetRateSliderWarning").textContent="Finanzierungsreserve unterschritten · Abweichung: "+eur(bufferDeviation)+" · Finanzierungsreserve: "+eur(minimumReserve)+" · Aktueller Puffer: "+eur(currentBuffer)+" · Bitte Einnahmen oder Ausgaben prüfen.";
      }else{
        $("budgetRateSliderWarning").textContent="";
      }
    }
'''
html = html[:start] + replacement + html[end:]

if 'id="budgetRateSliderNote"' in html:
    raise SystemExit("V8.369 budget-rate note element remains")
if 'Verbleibender Monatsüberschuss: "+eur(m.remainingMonthlySurplus)' in html:
    raise SystemExit("V8.369 persistent surplus note remains")
if 'Finanzierungsreserve erreicht: "+eur(minimumReserve)' in html:
    raise SystemExit("V8.369 reached-reserve wording remains")

path.write_text(html, encoding="utf-8")
print("V8.369 persistent budget-rate note and reached-reserve notice removed")
