from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

style=r"""
<style>
#renoSuggestionTotal::after{content:" · ohne Puffer";font-weight:400}
</style>
"""

js=r"""
<script>
// V8.241 separated renovation state, automatic proposal tracking and buffer sync
(function(){
  const RENO_STATE_VERSION="v8241";

  function renoMode(){
    try{
      const mode=currentDealType();
      return mode==="own" || mode==="flip" ? mode : null;
    }catch(_err){
      return null;
    }
  }

  function prefix(mode){
    return "ff_"+mode+"_reno_";
  }

  function stateKey(mode,name){
    return prefix(mode)+name;
  }

  function suggestionForTradeV8241(t){
    if(!t) return 0;
    if(t.mode==="sqm"){
      if(t.defaultOff) return 0;
      return Math.max(0,Math.round(val("area")*Number(t.rate||0)));
    }
    const hint=fixedTradeHints[t.name];
    if(hint && hint.rate && hint.areaKey){
      return Math.max(0,Math.round(getTradeAreaValue(hint)*Number(hint.rate||0)));
    }
    return 0;
  }

  function suggestionBaseTotal(){
    return trades.reduce(function(sum,t){
      return sum+suggestionForTradeV8241(t);
    },0);
  }

  function suggestionSignature(){
    return JSON.stringify(trades.map(function(t){
      return [t.key,suggestionForTradeV8241(t)];
    }));
  }

  function suggestionsActive(mode=renoMode()){
    return !!mode && localStorage.getItem(stateKey(mode,"suggestions_active"))==="1";
  }

  function setSuggestionsActive(active,mode=renoMode()){
    if(!mode) return;
    localStorage.setItem(stateKey(mode,"suggestions_active"),active?"1":"0");
  }

  function modeTradeKey(mode,t){
    return stateKey(mode,"trade_"+t.key);
  }

  function modeManualKey(mode,t){
    return stateKey(mode,"manual_"+t.key);
  }

  function modeAreaKey(mode,hint){
    return stateKey(mode,"area_"+hint.areaKey);
  }

  function storeCurrentRenoState(mode=renoMode()){
    if(!mode) return;
    trades.forEach(function(t){
      localStorage.setItem(modeTradeKey(mode,t),String(Number(tradeValues[t.key])||0));
      localStorage.setItem(modeManualKey(mode,t),manualTrades.has(t.key)?"1":"0");
    });
    if($("buffer")) localStorage.setItem(stateKey(mode,"buffer"),String($("buffer").value||"0"));
    localStorage.setItem(stateKey(mode,"initialized"),"1");
  }

  function initializeNamespace(mode,allowLegacyMigration){
    if(!mode || localStorage.getItem(stateKey(mode,"initialized"))==="1") return;

    trades.forEach(function(t){
      let value=0;
      let manual=false;
      if(allowLegacyMigration){
        const legacyValue=localStorage.getItem("ff_trade_"+t.key);
        const legacyManual=localStorage.getItem("ff_trade_manual_"+t.key)==="1";
        if(legacyValue!==null && Number.isFinite(Number(legacyValue))){
          value=Number(legacyValue)||0;
          manual=legacyManual;
        }
      }
      localStorage.setItem(modeTradeKey(mode,t),String(value));
      localStorage.setItem(modeManualKey(mode,t),manual?"1":"0");
    });

    Object.keys(fixedTradeHints).forEach(function(name){
      const hint=fixedTradeHints[name];
      if(!hint || !hint.areaKey) return;
      let area=0;
      if(allowLegacyMigration){
        const legacy=localStorage.getItem("ff_trade_area_"+hint.areaKey);
        if(legacy!==null) area=parseLocalizedNumber(legacy,false);
      }
      localStorage.setItem(modeAreaKey(mode,hint),String(area||0));
    });

    const currentBuffer=$("buffer") ? $("buffer").value : "5";
    localStorage.setItem(stateKey(mode,"buffer"),String(currentBuffer||"5"));

    // Ein bereits in V8.240 bestätigter Vorschlag wird nur für den aktuell
    // migrierten Modus übernommen. Der andere Modus startet bewusst unabhängig.
    if(allowLegacyMigration && localStorage.getItem("ff_"+mode+"_reno_suggestions_applied_signature")){
      localStorage.setItem(stateKey(mode,"suggestions_active"),"1");
    }else{
      localStorage.setItem(stateKey(mode,"suggestions_active"),"0");
    }
    localStorage.setItem(stateKey(mode,"initialized"),"1");
  }

  function loadRenoState(mode,allowLegacyMigration=false){
    if(!mode) return;
    initializeNamespace(mode,allowLegacyMigration);

    manualTrades.clear();
    trades.forEach(function(t){
      const raw=localStorage.getItem(modeTradeKey(mode,t));
      tradeValues[t.key]=raw===null ? 0 : Math.max(0,Number(raw)||0);
      if(localStorage.getItem(modeManualKey(mode,t))==="1") manualTrades.add(t.key);
    });

    const buffer=localStorage.getItem(stateKey(mode,"buffer"));
    if(buffer!==null && $("buffer")) $("buffer").value=buffer;

    syncRenoTotal();
  }

  // Flächen der pauschalen Gewerke werden ebenfalls je Rechner getrennt.
  getTradeAreaValue=function(hint){
    const mode=renoMode();
    if(!mode || !hint || !hint.areaKey) return 0;
    initializeNamespace(mode,false);
    const raw=localStorage.getItem(modeAreaKey(mode,hint));
    return raw===null ? 0 : parseLocalizedNumber(raw,false);
  };

  setTradeAreaValue=function(hint,value){
    const mode=renoMode();
    if(!mode || !hint || !hint.areaKey) return;
    initializeNamespace(mode,false);
    localStorage.setItem(modeAreaKey(mode,hint),String(Math.max(0,Number(value)||0)));
  };

  defaultTradeValue=function(){ return 0; };

  initializeTrades=function(force=false){
    const mode=renoMode();
    if(!mode) return;

    if(force){
      initializeNamespace(mode,false);
      manualTrades.clear();
      trades.forEach(function(t){
        tradeValues[t.key]=0;
        localStorage.setItem(modeTradeKey(mode,t),"0");
        localStorage.setItem(modeManualKey(mode,t),"0");
      });
      Object.keys(fixedTradeHints).forEach(function(name){
        const hint=fixedTradeHints[name];
        if(hint && hint.areaKey) localStorage.setItem(modeAreaKey(mode,hint),"0");
      });
      setSuggestionsActive(false,mode);
      localStorage.removeItem("ff_"+mode+"_reno_suggestions_applied_signature");
      storeCurrentRenoState(mode);
    }else{
      loadRenoState(mode,false);
    }
    syncRenoTotal();
  };

  function storeTrade(t){
    const mode=renoMode();
    if(!mode || !t) return;
    localStorage.setItem(modeTradeKey(mode,t),String(Number(tradeValues[t.key])||0));
    localStorage.setItem(modeManualKey(mode,t),manualTrades.has(t.key)?"1":"0");
  }

  function actualMatchesCurrentSuggestions(){
    if(!suggestionsActive()) return false;
    return trades.every(function(t){
      if(manualTrades.has(t.key)) return Math.abs((Number(tradeValues[t.key])||0)-suggestionForTradeV8241(t))<0.5;
      return Math.abs((Number(tradeValues[t.key])||0)-suggestionForTradeV8241(t))<0.5;
    });
  }

  function updateRenoProposalStatus(){
    const el=document.getElementById("renoSuggestionTotal");
    if(!el) return;
    const total=suggestionBaseTotal();
    el.textContent="Vorschlag gesamt: "+new Intl.NumberFormat("de-DE",{
      style:"currency",currency:"EUR",maximumFractionDigits:0
    }).format(total);
    el.classList.toggle("applied",actualMatchesCurrentSuggestions());
  }

  // Das readonly Feld zeigt den maßgeblichen Sanierungswert inkl. Puffer:
  // vor Übernahme den Vorschlag, danach die tatsächlich übernommenen/manuellen Werte.
  syncRenoTotal=function(){
    const actualBase=Math.max(0,totalTrades());
    const proposedBase=Math.max(0,suggestionBaseTotal());
    const hasManual=manualTrades.size>0;
    const useActual=suggestionsActive() || hasManual || actualBase>0;
    const base=useActual ? actualBase : proposedBase;
    const totalWithBuffer=Math.round(base*(1+pct("buffer")));
    if($("reno")) $("reno").value=String(totalWithBuffer);
    if($("renoSheetTotal")) $("renoSheetTotal").textContent=eur(totalWithBuffer);
    updateRenoProposalStatus();
  };

  // Wenn Vorschläge aktiv sind, folgen nicht manuell überschriebene Positionen
  // automatisch einer Änderung der Wohnfläche.
  syncAutoTrades=function(){
    const mode=renoMode();
    if(!mode) return;
    if(suggestionsActive(mode)){
      trades.forEach(function(t){
        if(manualTrades.has(t.key)) return;
        tradeValues[t.key]=suggestionForTradeV8241(t);
        storeTrade(t);
      });
      localStorage.setItem("ff_"+mode+"_reno_suggestions_applied_signature",suggestionSignature());
    }
    syncRenoTotal();
    if(document.getElementById("tradeList")) renderTrades();
  };

  renderTrades=function(){
    const area=val("area");
    const sqm=trades.filter(function(t){return t.mode==="sqm";}).sort(function(a,b){return a.name.localeCompare(b.name,"de");});
    const fixed=trades.filter(function(t){return t.mode!=="sqm";}).sort(function(a,b){return a.name.localeCompare(b.name,"de",{sensitivity:"base"});});
    let out='<div class="trade-section-label">Nach Wohnfläche berechnete Vorschläge</div>';

    sqm.forEach(function(t){
      const suggested=suggestionForTradeV8241(t);
      const actual=Math.round(Number(tradeValues[t.key])||0);
      const basis=t.defaultOff
        ? t.rate+' €/m² × '+area.toLocaleString("de-DE")+' m² · optional'
        : t.rate+' €/m² × '+area.toLocaleString("de-DE")+' m²';
      const autoLabel=manualTrades.has(t.key)
        ? 'manuell geändert'
        : (suggestionsActive() ? 'wird bei Flächenänderung automatisch aktualisiert' : (t.defaultOff ? 'optional · Standardwert 0 €' : 'grauer Wert = Vorschlag · Standardwert 0 €'));

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
      const areaValue=hint && hint.areaKey ? getTradeAreaValue(hint) : 0;
      const suggested=suggestionForTradeV8241(t);
      const actual=Math.round(Number(tradeValues[t.key])||0);
      const autoLabel=manualTrades.has(t.key)
        ? 'manuell geändert'
        : (hint && hint.areaKey && suggestionsActive() ? 'wird bei Flächenänderung automatisch aktualisiert' : (hint ? hint.auto : ''));

      out+='<div class="trade-row"><div class="trade-top">'+
        '<div class="trade-copy"><div class="trade-name">'+t.name+'</div><div class="trade-basis">'+basis+'</div>'+
        (autoLabel?'<div class="trade-auto">'+autoLabel+'</div>':'')+'</div>'+
        '<div class="trade-inputs-inline">'+
        (hint && hint.areaKey
          ? '<div class="input-wrap trade-area-input"><input class="trade-area" data-area-key="'+hint.areaKey+'" data-trade-key="'+t.key+'" inputmode="decimal" value="'+(areaValue||'')+'" placeholder="0"><span class="unit">m²</span></div>'
          : '')+
        '<div class="input-wrap trade-money-input"><input class="trade-amount" data-trade="'+t.key+'" inputmode="decimal" value="'+(actual>0?actual:'')+'" placeholder="'+(suggested>0?suggested:'0')+'"><span class="unit">€</span></div>'+
        '</div></div></div>';
    });

    $("tradeList").innerHTML=out;

    document.querySelectorAll(".trade-amount").forEach(function(inp){
      inp.addEventListener("input",function(){
        const t=trades.find(function(row){return row.key===inp.dataset.trade;});
        if(!t) return;
        tradeValues[t.key]=Math.max(0,parseLocalizedNumber(inp.value,false));
        manualTrades.add(t.key);
        storeTrade(t);
        syncRenoTotal();
      });
    });

    document.querySelectorAll(".trade-area").forEach(function(inp){
      inp.addEventListener("input",function(){
        const trade=trades.find(function(t){return t.key===inp.dataset.tradeKey;});
        if(!trade) return;
        const hint=fixedTradeHints[trade.name];
        if(!hint) return;

        setTradeAreaValue(hint,parseLocalizedNumber(inp.value,false));
        const suggested=suggestionForTradeV8241(trade);

        if(suggestionsActive() && !manualTrades.has(trade.key)){
          tradeValues[trade.key]=suggested;
          storeTrade(trade);
          localStorage.setItem("ff_"+renoMode()+"_reno_suggestions_applied_signature",suggestionSignature());
        }

        const amountInput=document.querySelector('.trade-amount[data-trade="'+trade.key+'"]');
        if(amountInput){
          amountInput.placeholder=suggested>0?String(suggested):"0";
          if(suggestionsActive() && !manualTrades.has(trade.key)){
            amountInput.value=suggested>0?String(suggested):"";
          }
        }
        syncRenoTotal();
      });
    });

    syncRenoTotal();
  };

  function applyCurrentSuggestions(){
    const mode=renoMode();
    if(!mode) return;
    setSuggestionsActive(true,mode);
    trades.forEach(function(t){
      // Bewusste manuelle Eingaben haben Vorrang.
      if(manualTrades.has(t.key)) return;
      tradeValues[t.key]=suggestionForTradeV8241(t);
      storeTrade(t);
    });
    localStorage.setItem("ff_"+mode+"_reno_suggestions_applied_signature",suggestionSignature());
    storeCurrentRenoState(mode);
    renderTrades();
    syncRenoTotal();
    try{render();}catch(_err){}
  }

  const applyButton=document.getElementById("applyTradeSuggestions");
  if(applyButton){
    applyButton.addEventListener("click",function(event){
      event.preventDefault();
      event.stopImmediatePropagation();
      applyCurrentSuggestions();
    },true);
  }

  const resetButton=document.getElementById("resetTrades");
  if(resetButton){
    resetButton.addEventListener("click",function(event){
      event.preventDefault();
      event.stopImmediatePropagation();
      const ok=confirm("Möchtest du wirklich alle Sanierungswerte in diesem Rechner auf 0 zurücksetzen?");
      if(!ok) return;
      initializeTrades(true);
      renderTrades();
      try{render();}catch(_err){}
    },true);
  }

  const saveButton=document.getElementById("saveTrades");
  if(saveButton){
    saveButton.addEventListener("click",function(){
      storeCurrentRenoState();
    },true);
  }

  // Sanierungspuffer explizit pro Rechner speichern und die Summen sofort neu berechnen.
  const bufferInput=$("buffer");
  if(bufferInput){
    bufferInput.addEventListener("input",function(){
      const mode=renoMode();
      if(mode){
        initializeNamespace(mode,false);
        localStorage.setItem(stateKey(mode,"buffer"),String(bufferInput.value||"0"));
      }
      syncRenoTotal();
    });
    bufferInput.addEventListener("change",function(){
      const mode=renoMode();
      if(mode) localStorage.setItem(stateKey(mode,"buffer"),String(bufferInput.value||"0"));
      syncRenoTotal();
    });
  }

  // Vor dem Moduswechsel sichern, danach den separaten Sanierungsstand laden.
  let activeRenoMode=renoMode();
  if(activeRenoMode){
    initializeNamespace(activeRenoMode,true);
    loadRenoState(activeRenoMode,true);
  }

  document.addEventListener("change",function(event){
    const el=event.target;
    if(!el || el.name!=="dealType") return;
    if(activeRenoMode) storeCurrentRenoState(activeRenoMode);
    const target=el.value==="own" || el.value==="flip" ? el.value : null;
    setTimeout(function(){
      if(!target) return;
      initializeNamespace(target,false);
      loadRenoState(target,false);
      activeRenoMode=target;
      try{render();}catch(_err){}
    },0);
  },true);

  // Bei Änderungen der Wohnfläche übernimmt syncAutoTrades die aktuellen
  // Vorschlagswerte automatisch, solange die jeweilige Position nicht manuell geändert wurde.
  document.addEventListener("input",function(event){
    if(event.target && event.target.id==="area"){
      setTimeout(function(){
        syncAutoTrades();
      },0);
    }
  },true);

  syncRenoTotal();
})();
</script>
"""

if "</head>" not in s or "</body>" not in s:
    raise SystemExit("V8.241 HTML anchors missing")

s=s.replace("</head>",style+"\n</head>",1)
s=s.replace("</body>",js+"\n</body>",1)

# Version im Rechner, in PDF-Berichten und in der SW-Registrierung anheben.
s=s.replace("V8.240","V8.241")
s=s.replace("service-worker.js?v=8.240","service-worker.js?v=8.241")

required=[
  'V8.241 separated renovation state',
  'ff_"+mode+"_reno_',
  'stateKey(mode,"buffer")',
  'function applyCurrentSuggestions()',
  'if(manualTrades.has(t.key)) return;',
  'syncAutoTrades=function()',
  'const totalWithBuffer=Math.round(base*(1+pct("buffer")));',
  'loadRenoState(target,false);',
  'V8.241',
  'service-worker.js?v=8.241'
]
missing=[token for token in required if token not in s]
if missing:
    raise SystemExit("V8.241 verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.241 separated renovation state patch applied")
