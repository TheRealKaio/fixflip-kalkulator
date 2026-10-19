from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

old='''function resetDealCalculatorToDefaults(){
  const mode=currentDealType();
  const dealStorageIds=[
    "purchase","sale","area","buildYear","plotArea","energyClass","energyDemand","months",
    "interest","repayment","ltv","notary","buyBroker","sellBroker","otherSaleCosts","buffer",
    "holding","targetProfit","targetMargin","maxEquity","targetRoi","personalTax",
    "stressSalePct","stressRenoPct","marketLocation","marketPropertyType","marketCondition",
    "comp1Price","comp1Area","comp2Price","comp2Area","comp3Price","comp3Area","flipSaleTarget"
  ];
  dealStorageIds.forEach(id=>localStorage.removeItem("ff_"+id));
  [
    "ff_state","ff_financeAcquisition","ff_interest_manual","ff_repayment_manual",
    COMP1_OVERRIDE_KEY,PROPERTY_TYPE_SET_KEY,FLIP_SALE_OVERRIDE_KEY
  ].forEach(key=>localStorage.removeItem(key));'''

new='''function resetDealCalculatorToDefaults(){
  const mode=currentDealType();
  const dealStorageIds=[
    "purchase","sale","area","buildYear","plotArea","energyClass","energyDemand","months",
    "interest","repayment","ltv","notary","buyBroker","sellBroker","otherSaleCosts","buffer",
    "holding","targetProfit","targetMargin","maxEquity","targetRoi","personalTax",
    "stressSalePct","stressRenoPct","marketLocation","marketPropertyType","marketCondition",
    "comp1Price","comp1Area","comp2Price","comp2Area","comp3Price","comp3Area","flipSaleTarget"
  ];
  dealStorageIds.forEach(id=>localStorage.removeItem("ff_"+id));

  // Beim Zurücksetzen dürfen keine alten Zinswerte oder Override-Flags
  // wiederhergestellt werden. Der Referenzzins wird anschließend frisch geladen.
  [
    "ff_interest",
    "ff_interest_manual",
    "ff_reference_interest_source",
    "ff_reference_interest_updated",
    "ff_repayment_manual",
    "ff_state",
    "ff_financeAcquisition",
    COMP1_OVERRIDE_KEY,PROPERTY_TYPE_SET_KEY,FLIP_SALE_OVERRIDE_KEY
  ].forEach(key=>localStorage.removeItem(key));'''

replace_once(old,new,"harden deal reset interest cleanup")

# Vor dem erneuten Rendern den alten sichtbaren Zinswert ebenfalls beseitigen.
old2='''  initTwoDecimalPercentFields();
  initializeRepaymentDefaults();
  render();
  initializeReferenceInterest();
}'''
new2='''  initTwoDecimalPercentFields();
  initializeRepaymentDefaults();
  if($("interest")) $("interest").value=Number(REFERENCE_INTEREST_FALLBACK).toFixed(2);
  render();
  initializeReferenceInterest();
}'''
replace_once(old2,new2,"clear visible stale interest before reference reload")

s=s.replace("V8.270","V8.271")
s=s.replace("service-worker.js?v=8.270","service-worker.js?v=8.271")

required=[
    '"ff_interest",',
    '"ff_interest_manual",',
    '"ff_reference_interest_source",',
    '"ff_reference_interest_updated",',
    'if($("interest")) $("interest").value=Number(REFERENCE_INTEREST_FALLBACK).toFixed(2);',
    'V8.271',
    'service-worker.js?v=8.271'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.271 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.271 reset fully clears stale interest state")
