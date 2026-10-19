from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Zielwerte dürfen den gespeicherten Verkaufspreis nach Sanierung nicht neu berechnen.
replace_once(
'''    "holding","otherSaleCosts","targetMargin","targetProfit","sellBroker"''',
'''    "holding","otherSaleCosts","sellBroker"''',
"remove goal values from sale-field formula triggers"
)

# 2) Erwarteter Verkaufspreis ist der aus Ziel-Gewinn / Ziel-Marge notwendige Preis.
replace_once(
'''    if($("saleExpectedBenchmark")) $("saleExpectedBenchmark").textContent=eur(m.s);''',
'''    if($("saleExpectedBenchmark")) $("saleExpectedBenchmark").textContent=eur(m.goalSale);''',
"expected sale benchmark"
)

# 3) Dritten Vergleichswert klar vom Erwartungswert trennen.
replace_once(
'''          <span>Verkaufspreis Projektziele</span>''',
'''          <span>Verkaufspreis nach Sanierung</span>''',
"third sale benchmark label"
)
replace_once(
'''    if($("saleGoalBenchmark")) $("saleGoalBenchmark").textContent=eur(m.goalSale);''',
'''    if($("saleGoalBenchmark")) $("saleGoalBenchmark").textContent=eur(m.s);''',
"third sale benchmark value"
)

# 4) Zieländerungen aktualisieren nur Vergleichswerte/Ampel, niemals das Verkaufsfeld.
goal_listener=r'''
["targetMargin","targetProfit"].forEach(function(id){
  const el=document.getElementById(id);
  if(!el) return;
  ["input","change"].forEach(function(eventName){
    el.addEventListener(eventName,function(){
      if(currentDealType()!=="flip") return;
      try{ render(); }catch(_err){}
    });
  });
});
'''
anchor='''  document.addEventListener("input",function(event){
    queueFormulaRefresh(event.target);
  });'''
if anchor not in s:
    raise SystemExit("goal-only render listener anchor missing")
s=s.replace(anchor,goal_listener+"\n"+anchor,1)

# 5) Hilfetext verdeutlicht die Trennung.
old_note='''            <strong>Hinweis:</strong> Der erwartete Verkaufspreis wird automatisch aus den aktuellen Projekt- und Finanzierungskosten kalkuliert. Änderungen am Eigenkapital, an der Finanzierung oder an den Projektkosten aktualisieren den Wert automatisch. Du kannst ihn weiterhin manuell überschreiben.'''
new_note='''            <strong>Hinweis:</strong> Der Verkaufspreis nach Sanierung wird aus den aktuellen Projekt- und Finanzierungskosten kalkuliert und gespeichert. Änderungen an Ziel-Gewinn oder Ziel-Marge verändern dieses Feld nicht. Der separate erwartete Verkaufspreis zeigt stattdessen, welcher Verkaufspreis für deine aktuellen Zielwerte erforderlich ist.'''
replace_once(old_note,new_note,"sale separation note")

s=s.replace("V8.291","V8.292")
s=s.replace("service-worker.js?v=8.291","service-worker.js?v=8.292")

required=[
    '"holding","otherSaleCosts","sellBroker"',
    'if($("saleExpectedBenchmark")) $("saleExpectedBenchmark").textContent=eur(m.goalSale);',
    '<span>Verkaufspreis nach Sanierung</span>',
    'if($("saleGoalBenchmark")) $("saleGoalBenchmark").textContent=eur(m.s);',
    '["targetMargin","targetProfit"].forEach(function(id){',
    'Änderungen an Ziel-Gewinn oder Ziel-Marge verändern dieses Feld nicht.',
    'V8.292',
    'service-worker.js?v=8.292'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.292 verification failed: "+", ".join(missing))

# Guard: Zielwerte must not remain in the automatic sale-field trigger row.
if '"holding","otherSaleCosts","targetMargin","targetProfit","sellBroker"' in s:
    raise SystemExit("V8.292 target values still recalculate sale field")

path.write_text(s,encoding="utf-8")
print("V8.292 target-driven expected sale separated from stored post-renovation sale")
