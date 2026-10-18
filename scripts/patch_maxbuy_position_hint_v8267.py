from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='''  if(currentDealType()==="own"){
    $("maxBuyNote").textContent="Marktwert abzgl. Kaufnebenkosten, Sanierung & Energierisiko";
  } else {
    $("maxBuyNote").textContent=`bei ${eur(val("targetProfit"))} Ziel-Gewinn`;
  }'''

new='''  if(currentDealType()==="own"){
    $("maxBuyNote").textContent="Marktwert abzgl. Kaufnebenkosten, Sanierung & Energierisiko";
  } else {
    const maxBuyTolerance=1;
    const maxBuyPosition=m.p < m.maxBuy-maxBuyTolerance
      ? "Du liegst drunter"
      : (m.p > m.maxBuy+maxBuyTolerance ? "Du liegst drüber" : "Du liegst genau drauf");
    $("maxBuyNote").textContent=`bei ${eur(val("targetProfit"))} Ziel-Gewinn · ${maxBuyPosition}`;
  }'''

if old not in s:
    raise SystemExit("V8.267 maxBuy note anchor missing")
s=s.replace(old,new,1)

s=s.replace("V8.266","V8.267")
s=s.replace("service-worker.js?v=8.266","service-worker.js?v=8.267")

required=[
  'const maxBuyPosition=m.p < m.maxBuy-maxBuyTolerance',
  '"Du liegst drunter"',
  '"Du liegst drüber"',
  '"Du liegst genau drauf"',
  'V8.267',
  'service-worker.js?v=8.267'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.267 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.267 max-buy position hint applied")
