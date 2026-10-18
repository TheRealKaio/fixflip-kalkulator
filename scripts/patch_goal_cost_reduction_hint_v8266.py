from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''    if((missProfit || missMargin) && m.goalSale>0){
      misses.push("Für Gewinn und Marge wäre ein Verkaufspreis von mindestens "+eur(Math.ceil(m.goalSale))+" erforderlich");
    }'''
new='''    if((missProfit || missMargin) && m.goalSale>0){
      const saleGap=Math.max(0,m.goalSale-m.s);
      misses.push(
        "Für Gewinn und Marge wäre ein Verkaufspreis von mindestens "
        +eur(Math.ceil(m.goalSale))
        +" erforderlich. Alternativ müssen die Projektkosten um mindestens "
        +eur(Math.ceil(saleGap))
        +" reduziert werden"
      );
    }'''

if old not in s:
    raise SystemExit("V8.266 goal hint anchor missing")
s=s.replace(old,new,1)

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
