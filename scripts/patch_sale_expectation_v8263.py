from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

# 1) Verkaufspreis ist Markterwartung, nicht Wunschziel.
replace_once(
'''          <label>Verkaufspreis nach Sanierung <span class="hint">kalkulatorisch vorbelegt · editierbar</span></label>''',
'''          <label>Verkaufspreis nach Sanierung <span class="hint">deine Markterwartung · editierbar</span></label>''',
"sale field hint"
)

replace_once(
'''            <strong>Hinweis:</strong> Kalkulatorischer Verkaufspreis auf Basis Deiner Projektziele. Führe vor der Bewertung des Projektgewinns einen Kaufpreis-Check durch oder gebe Dein ermitteltes Verkaufsziel ein. So prüfst du, ob es zum aktuellen Marktwert des Objekts passt.''',
'''            <strong>Hinweis:</strong> Trage hier deine realistische Verkaufserwartung nach der Sanierung ein. Ziel-Gewinn und Ziel-Marge verändern diesen Wert nicht; die Ampel zeigt dir stattdessen, ob deine Ziele mit dieser Verkaufserwartung erreichbar sind.''',
"sale field note"
)

# 2) Drei Vergleichswerte direkt unter dem Kaufpreis.
purchase_anchor='''      <div class="field">
        <label>Kaufpreis <span class="hint">laut Angebot</span></label>
        <div class="input-wrap"><input id="purchase" inputmode="decimal" value="250000"><span class="unit">€</span></div>
      </div>'''
purchase_new=purchase_anchor+'''

      <div class="flip-sale-benchmarks mode-hidden" id="flipSaleBenchmarks">
        <div class="flip-sale-benchmark">
          <span>Erwarteter Verkaufspreis</span>
          <strong id="saleExpectedBenchmark">–</strong>
        </div>
        <div class="flip-sale-benchmark">
          <span>Break-even-Verkaufspreis</span>
          <strong id="saleBreakEvenBenchmark">–</strong>
        </div>
        <div class="flip-sale-benchmark">
          <span>Verkaufspreis für deine Projektziele</span>
          <strong id="saleGoalBenchmark">–</strong>
        </div>
      </div>'''
replace_once(purchase_anchor,purchase_new,"sale benchmarks below purchase")

css_anchor='.metric-box .metric-value{font-size:17px;font-weight:850;margin-top:2px}'
if css_anchor not in s:
    raise SystemExit("benchmark CSS anchor missing")
s=s.replace(css_anchor,css_anchor+'''
.flip-sale-benchmarks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:-2px 0 16px}
.flip-sale-benchmark{min-width:0;border:1px solid #e1e6ee;border-radius:12px;background:#f8fafc;padding:10px 11px}
.flip-sale-benchmark span{display:block;color:var(--muted);font-size:11px;line-height:1.3;margin-bottom:4px}
.flip-sale-benchmark strong{display:block;font-size:14px;line-height:1.25;color:var(--ink);overflow-wrap:anywhere}
@media(max-width:560px){.flip-sale-benchmarks{grid-template-columns:1fr}.flip-sale-benchmark{display:flex;align-items:center;justify-content:space-between;gap:12px}.flip-sale-benchmark span{margin:0}}
''',1)

# 3) Initialer Verkaufspreis = Break-even inkl. Verkaufskosten und Verkaufsmakler.
old_sale_calc='''  const targetMargin = Math.max(0, pct("targetMargin"));
  const targetProfit = Math.max(0, val("targetProfit"));
  const sellBrokerRate = Math.max(0, pct("sellBroker"));

  // Der automatische Verkaufspreis muss beide Projektziele erfüllen:
  // 1) die eingegebene Ziel-Marge und 2) den eingegebenen Ziel-Gewinn.
  // Maßgeblich ist deshalb der höhere der beiden notwendigen Verkaufspreise.
  const marginDenominator = 1 - targetMargin - sellBrokerRate;
  const profitDenominator = 1 - sellBrokerRate;
  if(marginDenominator <= 0 || profitDenominator <= 0) return 0;

  const saleForTargetMargin = nonBrokerCosts / marginDenominator;
  const saleForTargetProfit = (nonBrokerCosts + targetProfit) / profitDenominator;

  return Math.max(saleForTargetMargin, saleForTargetProfit);'''
new_sale_calc='''  const sellBrokerRate = Math.max(0, pct("sellBroker"));

  // Initialwert ist ausschließlich der kostendeckende Verkaufspreis.
  // Ziel-Gewinn und Ziel-Marge verändern die Markterwartung nicht.
  const breakEvenDenominator = 1 - sellBrokerRate;
  if(breakEvenDenominator <= 0) return 0;

  return nonBrokerCosts / breakEvenDenominator;'''
replace_once(old_sale_calc,new_sale_calc,"decouple initial sale from goals")

# 4) Im Modell die notwendigen Ziel-Verkaufspreise separat berechnen.
model_anchor='''  const nonSaleBrokerCosts = total-sellBroker;
  const breakEven = (1-pct("sellBroker"))>0 ? nonSaleBrokerCosts/(1-pct("sellBroker")) : 0;
  const safety = s ? (s-breakEven)/s : 0;

  const targetProfit = currentDealType()==="own" ? 0 : val("targetProfit");'''
model_new='''  const nonSaleBrokerCosts = total-sellBroker;
  const sellBrokerRate = pct("sellBroker");
  const breakEven = (1-sellBrokerRate)>0 ? nonSaleBrokerCosts/(1-sellBrokerRate) : 0;
  const safety = s ? (s-breakEven)/s : 0;

  const targetProfit = currentDealType()==="own" ? 0 : val("targetProfit");
  const targetMarginForSale = currentDealType()==="own" ? 0 : Math.max(0,pct("targetMargin"));
  const profitSaleDenominator = 1-sellBrokerRate;
  const marginSaleDenominator = 1-sellBrokerRate-targetMarginForSale;
  const saleForTargetProfit = profitSaleDenominator>0
    ? (nonSaleBrokerCosts + Math.max(0,targetProfit))/profitSaleDenominator
    : 0;
  const saleForTargetMargin = marginSaleDenominator>0
    ? nonSaleBrokerCosts/marginSaleDenominator
    : 0;
  const goalSale = currentDealType()==="own"
    ? 0
    : Math.max(saleForTargetProfit,saleForTargetMargin);'''
replace_once(model_anchor,model_new,"goal sale benchmarks in model")

return_anchor='''    profit,personalTaxRate,taxOnProfit,profitAfterTax,initialOwnUseCosts,equity,roi,margin,breakEven,safety,maxBuy,'''
return_new='''    profit,personalTaxRate,taxOnProfit,profitAfterTax,initialOwnUseCosts,equity,roi,margin,breakEven,safety,maxBuy,
    saleForTargetProfit,saleForTargetMargin,goalSale,'''
replace_once(return_anchor,return_new,"return sale benchmarks")

# 5) Drei Werte rendern und nur bei Fix & Flip zeigen.
render_anchor='''  $("purchaseSqm").textContent = area > 0 ? eur(m.p/area) + " / m²" : "–";
  $("financedAmount").textContent = eur(m.debt);'''
render_new='''  $("purchaseSqm").textContent = area > 0 ? eur(m.p/area) + " / m²" : "–";
  if($("flipSaleBenchmarks")){
    $("flipSaleBenchmarks").classList.toggle("mode-hidden",currentDealType()!=="flip");
    if($("saleExpectedBenchmark")) $("saleExpectedBenchmark").textContent=eur(m.s);
    if($("saleBreakEvenBenchmark")) $("saleBreakEvenBenchmark").textContent=eur(m.breakEven);
    if($("saleGoalBenchmark")) $("saleGoalBenchmark").textContent=eur(m.goalSale);
  }
  $("financedAmount").textContent = eur(m.debt);'''
replace_once(render_anchor,render_new,"render sale benchmarks")

# 6) Ampel sagt konkret, um wie viel Gewinn/Marge verfehlt werden.
decision_old='''  else if(missProfit || missMargin || missRoi || missMaxBuy){cls="check";emoji="🟡";title="Noch verhandeln oder prüfen";text="Mindestens eines deiner Projektziele wird noch nicht erreicht."}'''
decision_new='''  else if(missProfit || missMargin || missRoi || missMaxBuy){
    cls="check";emoji="🟡";title="Noch verhandeln oder prüfen";
    const misses=[];
    if(missProfit) misses.push("Ziel-Gewinn verfehlt um "+eur(Math.max(0,targetProfit-m.profit)));
    if(missMargin){
      const marginGap=Math.max(0,(targetMargin-m.margin)*100);
      misses.push("Ziel-Marge verfehlt um "+new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(marginGap)+" Prozentpunkte");
    }
    if(missRoi){
      const roiGap=Math.max(0,(targetRoi-m.roi)*100);
      misses.push("Mindest-Rendite verfehlt um "+new Intl.NumberFormat("de-DE",{maximumFractionDigits:1}).format(roiGap)+" Prozentpunkte");
    }
    if(missMaxBuy) misses.push("Kaufpreis liegt "+eur(Math.max(0,m.p-m.maxBuy))+" über dem maximal sinnvollen Kaufpreis");
    if((missProfit || missMargin) && m.goalSale>0){
      misses.push("Für Gewinn und Marge wäre ein Verkaufspreis von mindestens "+eur(Math.ceil(m.goalSale))+" erforderlich");
    }
    text=misses.join(" · ")+".";
  }'''
replace_once(decision_old,decision_new,"detailed goal miss text")

# 7) Gespeicherten manuellen Verkaufspreis nicht mehr bei Kosten-/Zieländerungen überschreiben.
queue_old='''  function queueFormulaRefresh(target){
    if(currentDealType()!=="flip" || !isFormulaChange(target)) return;
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      if(recalcAndStore()){
        try{ render(); }catch(_err){}
      }
    },0);
  }'''
queue_new='''  function queueFormulaRefresh(target){
    if(currentDealType()!=="flip" || !isFormulaChange(target)) return;
    // Der erwartete Verkaufspreis ist eine Nutzereinschätzung und bleibt bestehen.
    // Änderungen der Kosten/Ziele aktualisieren nur Break-even, Zielpreis und Ampel.
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      try{ render(); }catch(_err){}
    },0);
  }'''
replace_once(queue_old,queue_new,"preserve manual expected sale")

mode_old='''        if(currentDealType()==="flip"){
          if(!loadValue()) recalcAndStore();
          else {
            // Nach Moduswechsel direkt auf Basis der aktuellen Formel synchronisieren.
            recalcAndStore();
          }
          try{ render(); }catch(_err){}
        }'''
mode_new='''        if(currentDealType()==="flip"){
          if(!loadValue()) recalcAndStore();
          try{ render(); }catch(_err){}
        }'''
replace_once(mode_old,mode_new,"preserve sale on mode switch")

trade_old='''        if(currentDealType()!=="flip") return;
        recalcAndStore();
        try{ render(); }catch(_err){}'''
trade_new='''        if(currentDealType()!=="flip") return;
        try{ render(); }catch(_err){}'''
# There is one trade click block with this exact body; reset block also contains it but reset should recalc.
if trade_old not in s:
    raise SystemExit("trade refresh anchor missing")
# replace only last relevant occurrence by locating after Programmgesteuerte comment
pos=s.find("// Programmgesteuerte Änderungen der Sanierung")
idx=s.find(trade_old,pos)
if idx<0:
    raise SystemExit("programmatic trade refresh anchor missing")
s=s[:idx]+trade_new+s[idx+len(trade_old):]

initial_old='''  // Initial: gespeicherten Wert laden und anschließend mit der aktuellen Formel abgleichen.
  if(currentDealType()==="flip"){
    loadValue();
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      recalcAndStore();
      try{ render(); }catch(_err){}
    },0);
  }'''
initial_new='''  // Initial: gespeicherten Marktwert laden. Nur ohne gespeicherten Wert
  // wird einmalig der kostendeckende Break-even als Startwert vorbelegt.
  if(currentDealType()==="flip"){
    const hadSavedValue=loadValue();
    setTimeout(function(){
      if(currentDealType()!=="flip") return;
      if(!hadSavedValue) recalcAndStore();
      try{ render(); }catch(_err){}
    },0);
  }'''
replace_once(initial_old,initial_new,"initial expected sale preservation")

# Nutzereingabe klar als manuell markieren.
input_old='''    el.addEventListener("input",function(){
      saveValue();
    });
    el.addEventListener("change",function(){
      saveValue();
    });'''
input_new='''    el.addEventListener("input",function(){
      flipSaleManualOverride=true;
      localStorage.setItem(FLIP_SALE_OVERRIDE_KEY,"1");
      setSaleRecalculatedState(false);
      saveValue();
    });
    el.addEventListener("change",function(){
      flipSaleManualOverride=true;
      localStorage.setItem(FLIP_SALE_OVERRIDE_KEY,"1");
      setSaleRecalculatedState(false);
      saveValue();
    });'''
replace_once(input_old,input_new,"manual sale persistence state")

# Zielwerte dürfen den erwarteten Verkaufspreis nicht als Formeltrigger behandeln.
# Trigger dürfen für render bestehen, aber die Dokumentation soll nicht mehr das Gegenteil behaupten.
s=s.replace(
  '// Ziel-Marge ist wieder Bestandteil der Verkaufspreisformel und muss deshalb\n// bei Änderungen den gespeicherten Verkaufspreis aktualisieren.',
  '// Zielwerte aktualisieren nur die Vergleichswerte und Ampel; der erwartete Verkaufspreis bleibt bestehen.'
)

# 8) Version bump.
s=s.replace("V8.262","V8.263")
s=s.replace("service-worker.js?v=8.262","service-worker.js?v=8.263")

required=[
    'deine Markterwartung · editierbar',
    'id="flipSaleBenchmarks"',
    'id="saleExpectedBenchmark"',
    'id="saleBreakEvenBenchmark"',
    'id="saleGoalBenchmark"',
    'return nonBrokerCosts / breakEvenDenominator;',
    'const goalSale = currentDealType()==="own"',
    'saleForTargetProfit,saleForTargetMargin,goalSale',
    'Ziel-Gewinn verfehlt um ',
    'Ziel-Marge verfehlt um ',
    'Für Gewinn und Marge wäre ein Verkaufspreis von mindestens ',
    'Der erwartete Verkaufspreis ist eine Nutzereinschätzung und bleibt bestehen.',
    'if(!hadSavedValue) recalcAndStore();',
    'V8.263',
    'service-worker.js?v=8.263'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.263 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.263 market-based sale expectation applied")
