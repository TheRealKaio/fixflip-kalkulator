from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''    if((missProfit || missMargin) && m.goalSale>0){
      misses.push("Für Gewinn und Marge wäre ein Verkaufspreis von mindestens "+eur(Math.ceil(m.goalSale))+" erforderlich");
    }'''
new='''    if((missProfit || missMargin) && m.goalSale>0){
      const saleGap=Math.max(0,m.goalSale-m.s);
      goalAdvice =
        "Für Gewinn und Marge wäre ein Verkaufspreis von mindestens "
        +eur(Math.ceil(m.goalSale))
        +" erforderlich. Alternativ müssen die Projektkosten um mindestens "
        +eur(Math.ceil(saleGap))
        +" reduziert werden.";
    }'''

def replace_once(old, new):
    global s
    if s.count(old)!=1:
        raise SystemExit("V8.266 goal hint anchor missing: "+old)
    s=s.replace(old,new,1)

replace_once(old,new)
replace_once('  let cls="go",emoji="🟢",title="Sieht belastbar aus",',
             '  let goalAdvice="";\n  let cls="go",emoji="🟢",title="Sieht belastbar aus",')
replace_once('text=misses.join(" · ")+".";', 'text=misses.join(". ")+".";')
for old_label, new_label in (
    ("Ziel-Gewinn verfehlt um ", "Der Gewinn liegt um "),
    ("Ziel-Marge verfehlt um ", "Die Marge liegt um "),
    ("Mindest-Rendite verfehlt um ", "Die Rendite liegt um "),
):
    replace_once(old_label,new_label)
replace_once('eur(Math.max(0,targetProfit-m.profit)));',
             'eur(Math.max(0,targetProfit-m.profit))+" unter dem Zielgewinn");')
replace_once('format(marginGap)+" Prozentpunkte");','format(marginGap)+" Prozentpunkte unter der Zielmarge");')
replace_once('format(roiGap)+" Prozentpunkte");','format(roiGap)+" Prozentpunkte unter der Mindestrendite");')
replace_once('<p id="decisionText">Die Marge ist zu knapp für Überraschungen.</p>',
             '<p id="decisionText" lang="de">Die Marge ist zu knapp für Überraschungen.</p>'
             '<p id="decisionAdvice" lang="de" hidden></p>')
replace_once('$("decisionText").textContent=text;',
             '$("decisionText").textContent=text;\n'
             '  $("decisionAdvice").textContent=isOwnUse ? "" : goalAdvice;\n'
             '  $("decisionAdvice").hidden=isOwnUse || !goalAdvice;')

s=s.replace("V8.265","V8.266")
s=s.replace("service-worker.js?v=8.265","service-worker.js?v=8.266")

required=[
    'Alternativ müssen die Projektkosten um mindestens ',
    'const saleGap=Math.max(0,m.goalSale-m.s);',
    'V8.266',
    'service-worker.js?v=8.266'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.266 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.266 goal hint includes cost reduction alternative")
