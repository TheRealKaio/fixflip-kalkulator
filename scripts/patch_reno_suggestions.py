from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

marker = "V8.238 renovation suggestion placeholders"
if marker in s:
    raise SystemExit("V8.238 patch already present")

style = r"""
<style>
.reno-head-actions{display:flex;flex-direction:column;align-items:flex-end;gap:7px;flex:0 0 auto}
.reno-suggestion-btn{min-height:38px;white-space:nowrap;font-weight:750}
.trade-amount::placeholder{color:#a6aebb;font-weight:400;opacity:1;text-align:left}
@media(max-width:420px){
  .reno-head{align-items:flex-start}
  .reno-head-actions{max-width:48%}
  .reno-suggestion-btn{white-space:normal;line-height:1.15;padding:7px 9px}
}
</style>
"""

js = r"""
<script>
// V8.238 renovation suggestion placeholders
(function(){
  function suggestionForTrade(t){
    if(!t) return 0;
    if(t.mode==="sqm"){
      if(t.defaultOff) return 0;
      return Math.max(0,Math.round(val("area") * Number(t.rate || 0)));
    }
    const hint=fixedTradeHints[t.name];
    if(hint && hint.rate && hint.areaKey){
      return Math.max(0,Math.round(suggestedFixedAmount(hint)||0));
    }
    return 0;
  }

  defaultTradeValue=function(){ return 0; };

  syncAutoTrades=function(){
    document.querySelectorAll(".trade-amount").forEach(function(inp){
      const trade=trades.find(function(t){ return t.key===inp.dataset.trade; });
      const suggested=suggestionForTrade(trade);
      inp.placeholder=suggested>0 ? String(suggested) : "0";
    });
    syncRenoTotal();
  };

  renderTrades=function(){
    const area=val("area");
    const sqm=trades.filter(function(t){ return t.mode==="sqm"; }).sort(function(a,b){ return a.name.localeCompare(b.name,"de"); });
    const fixed=trades.filter(function(t){ return t.mode!=="sqm"; }).sort(function(a,b){ return a.name.localeCompare(b.name,"de",{sensitivity:"base"}); });
    let out='<div class="trade-section-label">Nach Wohnfläche berechnete Vorschläge</div>';

    sqm.forEach(function(t){
      const suggested=suggestionForTrade(t);
      const actual=Math.round(tradeValues[t.key]||0);
      const basis=t.defaultOff
        ? t.rate+' €/m² × '+area.toLocaleString("de-DE")+' m² · optional'
        : t.rate+' €/m² × '+area.toLocaleString("de-DE")+' m²';
      const autoLabel=actual>0
        ? 'übernommener oder eigener Wert'
        : (t.defaultOff ? 'optional · Standardwert 0 €' : 'grauer Wert = Vorschlag · Standardwert 0 €');

      out+='<div class="trade-row"><div class="trade-top"><div>'+
        '<div class="trade-name">'+t.name+'</div>'+
        '<div class="trade-basis">'+basis+'</div>'+
        '<div class="trade-auto">'+autoLabel+'</div></div>'+
        '<div class="input-wrap"><input class="trade-amount" data-trade="'+t.key+'" inputmode="decimal" value="'+(actual>0?actual:'')+'" placeholder="'+(suggested>0?suggested:'0')+'"><span class="unit">€</span></div>'+
        '</div></div>';
    });

    out+='<div class="trade-section-label">Pauschal / Stück</div>';

    fixed.forEach(function(t){
      const hint=fixedTradeHints[t.name];
      const basis=hint ? hint.basis : t.unit+' · individuell eintragen';
      const autoLabel=hint ? hint.auto : '';
      const areaValue=hint && hint.areaKey ? getTradeAreaValue(hint) : 0;
      const suggested=hint && hint.areaKey ? suggestedFixedAmount(hint) : null;
      const actual=Math.round(tradeValues[t.key]||0);

      out+='<div class="trade-row"><div class="trade-top">'+
        '<div class="trade-copy"><div class="trade-name">'+t.name+'</div><div class="trade-basis">'+basis+'</div>'+
        (autoLabel ? '<div class="trade-auto">'+autoLabel+'</div>' : '')+'</div>'+
        '<div class="trade-inputs-inline">'+
        (hint && hint.areaKey
          ? '<div class="input-wrap trade-area-input"><input class="trade-area" data-area-key="'+hint.areaKey+'" data-trade-key="'+t.key+'" inputmode="decimal" value="'+(areaValue||'')+'" placeholder="0"><span class="unit">m²</span></div>'
          : '')+
        '<div class="input-wrap trade-money-input"><input class="trade-amount" data-trade="'+t.key+'" inputmode="decimal" value="'+(actual>0?actual:'')+'" placeholder="'+(suggested && suggested>0?suggested:'0')+'"><span class="unit">€</span></div>'+
        '</div></div></div>';
    });

    $("tradeList").innerHTML=out;

    document.querySelectorAll(".trade-amount").forEach(function(inp){
      inp.addEventListener("input",function(){
        const id=inp.dataset.trade;
        tradeValues[id]=parseLocalizedNumber(inp.value,false);
        manualTrades.add(id);
        syncRenoTotal();
      });
    });

    document.querySelectorAll(".trade-area").forEach(function(inp){
      inp.addEventListener("input",function(){
        const areaKey=inp.dataset.areaKey;
        const tradeKey=inp.dataset.tradeKey;
        const trade=trades.find(function(t){ return t.key===tradeKey; });
        const hint=trade ? fixedTradeHints[trade.name] : null;
        const areaValue=parseLocalizedNumber(inp.value,false);
        if(hint){
          setTradeAreaValue(hint,areaValue);
          const suggested=Math.round(areaValue*hint.rate);
          const amountInput=document.querySelector('.trade-amount[data-trade="'+tradeKey+'"]');
          if(amountInput) amountInput.placeholder=suggested>0 ? String(suggested) : "0";
        }
      });
    });

    syncRenoTotal();
  };

  function applyTradeSuggestions(){
    trades.forEach(function(t){
      const suggested=suggestionForTrade(t);
      if(!(suggested>0)) return;
      tradeValues[t.key]=suggested;
      manualTrades.add(t.key);
    });
    syncRenoTotal();
    renderTrades();
  }

  const head=document.querySelector("#renoBackdrop .reno-head");
  if(head && !document.getElementById("applyTradeSuggestions")){
    const currentTotal=document.getElementById("renoSheetTotal");
    const right=document.createElement("div");
    right.className="reno-head-actions";

    const btn=document.createElement("button");
    btn.type="button";
    btn.className="budget-apply-btn reno-suggestion-btn";
    btn.id="applyTradeSuggestions";
    btn.textContent="Vorschlag übernehmen";
    btn.addEventListener("click",applyTradeSuggestions);

    right.appendChild(btn);
    if(currentTotal) right.appendChild(currentTotal);
    head.appendChild(right);

    const intro=head.querySelector(".sub");
    if(intro) intro.textContent="Richtwerte erscheinen dezent als Vorschlag. Erst über den Button werden sie in die Berechnung übernommen.";
  }

  const note=document.querySelector("#renoBackdrop .reno-note");
  if(note) note.innerHTML="<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €. Graue Werte im Eingabefeld sind unverbindliche Richtwerte. Du kannst sie gesammelt übernehmen oder jeden Betrag direkt selbst eintragen und später jederzeit ändern.";

  const reset=document.getElementById("resetTrades");
  if(reset) reset.textContent="Auf 0 zurücksetzen";

  // Alte automatisch gesetzte Werte werden auf 0 migriert; explizit manuelle Werte bleiben erhalten.
  trades.forEach(function(t){
    if(!manualTrades.has(t.key)) tradeValues[t.key]=0;
  });
  syncRenoTotal();
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.238 HTML anchors missing")

s = s.replace("</head>", style + "\n</head>", 1)
s = s.replace("</body>", js + "\n</body>", 1)

required = [
    'id="applyTradeSuggestions"',
    'Vorschlag übernehmen',
    '.trade-amount::placeholder',
    'function suggestionForTrade(t)',
    'Alle Sanierungspositionen starten rechnerisch bei 0 €.',
    'Auf 0 zurücksetzen'
]
missing = [x for x in required if x not in s]
if missing:
    raise SystemExit("V8.238 verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.238 renovation suggestions patch applied")
