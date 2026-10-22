from pathlib import Path
import re
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

short="Richtwerte erscheinen dezent als Vorschlag. Erst über den Button werden sie in die Berechnung übernommen."
new_note='<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €. Graue Werte sind unverbindliche Richtwerte. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen. Erst über den Button werden sie in die Berechnung übernommen.'

# 1) Sichtbare Kurz-Hinweise in den Sanierungs-Köpfen entfernen.
s=re.sub(
    r'<p class="sub" style="margin:4px 0 0">'+re.escape(short)+r'</p>',
    '',
    s
)

# 2) Runtime-Zuweisung entfernen, damit der Kurztext nicht beim Öffnen wieder erscheint.
s=s.replace(
    '    const intro=head.querySelector(".sub");\n    if(intro) intro.textContent="'+short+'";\n',
    ''
)

# 3) Bestehende "So funktioniert es"-Texte in gemeinsamer Sanierung vereinheitlichen.
patterns=[
    r'<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €\. Graue Werte im Eingabefeld sind unverbindliche Richtwerte\. Du kannst sie gesammelt übernehmen oder jeden Betrag direkt selbst eintragen und später jederzeit ändern\.',
    r'<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €\. Graue Werte sind unverbindliche Richtwerte\. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen\.'
]
# Apply both source variants in one pass so replacement text is never matched again.
s,replaced=re.subn("|".join("(?:"+pattern+")" for pattern in patterns),new_note,s)

if replaced < 2:
    raise SystemExit(f"V8.322 expected at least 2 renovation note replacements, got {replaced}")

if short in s:
    raise SystemExit("V8.322 old short renovation hint still present")

if s.count(new_note) < 2:
    raise SystemExit("V8.322 unified renovation note missing in both functions")

# Remove the obsolete subtitle below "Sanierung aufteilen".
obsolete="Richtwerte werden aus der Wohnfläche berechnet. Die Summe oben enthält den Sanierungs-Puffer."
s=re.sub(r'<p\b[^>]*>\s*'+re.escape(obsolete)+r'\s*</p>', '', s)
if obsolete in s:
    raise SystemExit("Obsolete renovation subtitle still present")

s=s.replace("<label>Sanierung (inkl. Puffer)</label>", "<label>Modernisierung</label>")

s=s.replace("Sanierungswerte sind editierbare Orientierungswerte für einen ersten Deal-Check. ", "")

s=s.replace("Laufende Kosten pro Monat", "Lfd. Kosten pro Monat")

# Programmatic renovation changes must refresh the rental results immediately.
old_sync='localStorage.setItem("ff_rent_rentRenovation",String(t));}'
new_sync='localStorage.setItem("ff_rent_rentRenovation",String(t));$r("rentRenovation").dispatchEvent(new Event("input",{bubbles:true}));}'
if old_sync not in s:
    raise SystemExit("Rental renovation sync anchor missing")
s=s.replace(old_sync,new_sync,1)

# Rental financing share and acquisition-cost toggle, matching owner-use logic.
def financing_replace(old,new,label):
    global s
    if old not in s:
        raise SystemExit('Rental financing anchor missing: '+label)
    s=s.replace(old,new,1)

financing_replace('    rentEquity:"0",','    rentEquity:"0",\n    rentLtv:"100.00",\n    rentFinanceAcquisition:"1",','defaults')
financing_replace('if(el) localStorage.setItem(PREFIX+id,el.value);','if(el) localStorage.setItem(PREFIX+id,el.type==="checkbox" ? (el.checked ? "1" : "0") : el.value);','save checkbox')
financing_replace('el.value=saved!==null ? saved : defaults[id];','if(el.type==="checkbox") el.checked=(saved!==null ? saved : defaults[id])==="1";\n      else el.value=saved!==null ? saved : defaults[id];','load checkbox')
financing_replace('if(el) el.value=defaults[id];','if(el){if(el.type==="checkbox") el.checked=defaults[id]==="1";else el.value=defaults[id];}','reset checkbox')

controls='''<div class="quick-grid" id="rentFinancingControls">
  <div class="finance-acq-row">
    <div class="field finance-acq-total">
      <label class="label-split"><span class="label-left">Kaufnebenkosten gesamt <button class="info-btn inline-info rent-info-dot" type="button" data-info="Summe aus Grunderwerbsteuer, Notar- und Grundbuchkosten sowie Maklerkosten beim Kauf.">i</button></span></label>
      <div class="metric-box"><div class="metric-value" id="rentAcquisitionDisplay">–</div></div>
    </div>
    <div class="field finance-acq-option">
      <label class="finance-check-label" for="rentFinanceAcquisition"><span>Mitfinanzieren</span><button class="info-btn inline-info rent-info-dot" type="button" data-info="Wenn aktiviert, gehören die Kaufnebenkosten zur Finanzierungsbasis. Andernfalls müssen sie zusätzlich aus eigenen Mitteln bezahlt werden.">i</button></label>
      <div class="finance-check-box"><input id="rentFinanceAcquisition" type="checkbox" checked aria-label="Kaufnebenkosten in die Finanzierungsbasis einbeziehen"></div>
    </div>
  </div>
</div>
'''
anchor='<div class="budget-summary rent-finance-summary">'
financing_replace(anchor,controls+anchor,'controls')

# Reuse the same metric, rate-grid, checkbox and badge classes as owner-use.
finance_start=s.index('<div class="finance-rate-grid">',s.index('id="rentSection"'))
finance_end=s.index('<div class="quick-grid">',finance_start)
finance_fields='''<div class="field"><label>Kreditsumme <span class="hint">automatisch berechnet</span></label><div class="metric-box"><div class="metric-value" id="rentCreditAmount">–</div></div></div>
<div class="field"><label for="rentEquity">Eigenkapital</label><div class="input-wrap"><input id="rentEquity" inputmode="decimal" value="0"><span class="unit">€</span></div></div>
<div class="finance-rate-grid">
  <div class="field"><label for="rentInterest">Zins p.a. <button class="info-btn inline-info rent-info-dot" type="button" data-info="Jährlicher Sollzins des Darlehens. Zusammen mit der Tilgung bestimmt er die anfängliche Monatsrate.">i</button></label><div class="input-wrap"><input id="rentInterest" inputmode="decimal" value="4.00"><span class="unit">%</span></div></div>
  <div class="field"><label for="rentRepayment">Tilgung p.a. <button class="info-btn inline-info rent-info-dot" type="button" data-info="Anfänglicher jährlicher Tilgungsanteil bezogen auf die Kreditsumme. Er reduziert die Restschuld.">i</button></label><div class="input-wrap"><input id="rentRepayment" inputmode="decimal" value="1.50"><span class="unit">%</span></div></div>
  <div class="field"><label for="rentLtv">Finanziert <button class="info-btn inline-info rent-info-dot" type="button" data-info="Anteil der Finanzierungsbasis vor Abzug des eingetragenen Eigenkapitals. Die Basis enthält Kaufpreis und Modernisierung sowie bei aktivem Häkchen die Kaufnebenkosten.">i</button></label><div class="input-wrap"><input id="rentLtv" inputmode="decimal" value="100.00"><span class="unit">%</span></div></div>
</div>
'''
s=s[:finance_start]+finance_fields+s[finance_end:]
# Place acquisition total and checkbox together before notary/broker inputs.
s=s.replace(controls,'',1)
finance_end=s.index('<div class="quick-grid">',finance_start)
s=s[:finance_end]+controls+s[finance_end:]
financing_replace('    setText("rentAcquisitionCostsResult",euro(m.acquisitionCosts));','    setText("rentAcquisitionCostsResult",euro(m.acquisitionCosts));\n    setText("rentAcquisitionDisplay",euro(m.acquisitionCosts));','acquisition display')
financing_replace('    setText("rentTotalInvestmentResult",euro(m.totalInvestment));','    setText("rentTotalInvestmentResult",euro(m.totalInvestment));\n    setText("rentCreditAmount",euro(m.loan));','credit display')

financing_replace('        </div>\n      </section>\n\n      <section class="card result-card">','        </div>\n        <p class="mini" id="rentFundingGap" role="status" hidden></p>\n      </section>\n\n      <section class="card result-card">','funding status')
financing_replace('    const loan=Math.max(0,totalInvestment-equityUsed);','''    const financingShare=Math.max(0,pctValue("rentLtv"));
    const financeAcquisition=!!document.getElementById("rentFinanceAcquisition")?.checked;
    const financingBase=purchase+renovation+(financeAcquisition ? acquisitionCosts : 0);
    const loan=Math.max(0,financingBase*financingShare-equityUsed);
    const fundingGap=Math.max(0,totalInvestment-loan-equityUsed);''','model')
financing_replace('      totalInvestment,loan,monthlyInterest,monthlyPrincipal,debtService,','      financingShare,financeAcquisition,financingBase,fundingGap,totalInvestment,loan,monthlyInterest,monthlyPrincipal,debtService,','model result')
financing_replace('  function renderRent(){','  window.rentalCalculation=rentModel;\n\n  function renderRent(){','shared calculation')
financing_replace('    setText("rentLoanResult",euro(m.loan));','''    setText("rentLoanResult",euro(m.loan));
    const gap=document.getElementById("rentFundingGap");
    if(gap){gap.hidden=m.fundingGap<0.005;gap.textContent="Zusätzlich benötigte Eigenmittel: "+euro(m.fundingGap)+". Dieser Betrag ist noch nicht durch Darlehen und eingetragenes Eigenkapital gedeckt.";gap.style.color="#b91c1c";}''','funding warning')
# The PDF now uses exactly the same calculation as the on-screen results.
start=s.index('  function rentalModel(){')
end=s.index('\n  function pct(v)',start)
s=s[:start]+'''  function rentalModel(){
    const m=window.rentalCalculation();
    return {...m,acquisition:m.acquisitionCosts,debt:m.debtService,effective:m.effectiveMonthlyRent,owner:m.ownerMonthlyCosts,cashflow:m.monthlyCashflow,other:m.otherCosts,principal:m.annualPrincipal,breakEven:m.breakEvenRent};
  }
'''+s[end:]
financing_replace("    line('Eigenkapital',money(m.equityUsed));",'''    line('Eigenkapital',money(m.equityUsed));
    line('Finanziert',pct(m.financingShare));
    line('Kaufnebenkosten mitfinanzieren',m.financeAcquisition ? 'Ja' : 'Nein');
    line('Finanzierungsbasis',money(m.financingBase));
    if(m.fundingGap>=0.005) line('Zusätzlich benötigte Eigenmittel',money(m.fundingGap),true);''','PDF financing')

# Match the financing card to the owner-use reference layout.
financing_replace('    rentLtv:"100.00",','    rentLtv:"100.00",\n    rentMonths:"120",','term default')
financing_replace('<label>Kreditsumme <span class="hint">automatisch berechnet</span></label>','<label>Finanzierte Summe <span class="hint">automatisch berechnet</span></label>','financed label')
financing_replace('<label for="rentEquity">Eigenkapital</label>','<label for="rentEquity">Eigenkapital <span class="hint">Vermietung</span></label>','equity hint')
financing_replace('    const fundingGap=Math.max(0,totalInvestment-loan-equityUsed);','''    const fundingGap=Math.max(0,totalInvestment-loan-equityUsed);
    const financingMonths=Math.max(0,Math.round(numberValue("rentMonths")));
    const financingProjection=annuityProjection(loan,interest,repayment,financingMonths);
    const remainingDebt=financingProjection.remainingDebt;''','term calculation')
financing_replace('      financingShare,financeAcquisition,financingBase,fundingGap,totalInvestment,','      financingMonths,remainingDebt,financingShare,financeAcquisition,financingBase,fundingGap,totalInvestment,','term result')
financing_replace("    line('Finanzierungsbasis',money(m.financingBase));",'''    line('Finanzierungsbasis',money(m.financingBase));
    line('Laufzeit Finanzierung',String(m.financingMonths)+' Monate');
    line('Restschuld nach dieser Laufzeit',money(m.remainingDebt));''','PDF term')

summary_start=s.index('<div class="budget-summary rent-finance-summary">')
summary_end=s.index('<p class="mini" id="rentFundingGap"',summary_start)
s=s[:summary_start]+s[summary_end:]
heading=s.index('<h2>3. Finanzierung und Nebenkosten</h2>',s.index('id="rentSection"'))
card_start=s.rfind('<section',0,heading)
card_end=s.index('</section>',heading)+len('</section>')
body_start=s.index('</p>',heading)+len('</p>')
body=s[body_start:card_end-len('</section>')]
body=body.replace('<label>Notar &amp; Grundbuch</label>','<label>Notar + Grundbuch</label>').replace('<label>Notar & Grundbuch</label>','<label>Notar + Grundbuch</label>')
body+='''<div class="field"><label for="rentMonths">Laufzeit Finanzierung</label><div class="input-wrap"><input id="rentMonths" inputmode="numeric" value="120"><span class="unit">Mon.</span></div></div>'''
card='''<section class="card" id="rentFinanceCard">
<div class="rent-finance-head"><div><h2>3. Finanzierung und Nebenkosten</h2><p class="sub">Trage hier die Bedingungen deiner Finanzierung ein.</p></div><button type="button" class="plus-btn" id="rentFinanceToggle" aria-label="Finanzierung und Nebenkosten schließen" aria-controls="rentFinanceBody" aria-expanded="true">−</button></div>
<div id="rentFinanceBody">'''+body+'''</div></section>'''
s=s[:card_start]+card+s[card_end:]
css='''
/* Same financing rows on mobile and desktop as owner-use. */
#rentFinanceCard .finance-rate-grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}
#rentFinanceCard .quick-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
#rentFinanceCard .finance-acq-row{grid-template-columns:2fr 1fr;min-width:0}
#rentFinanceCard .field{min-width:0}
#rentFinanceCard .rent-finance-head{display:flex;align-items:center;gap:12px;justify-content:space-between}
#rentFinanceCard .rent-finance-head>div{min-width:0;flex:1}
#rentFinanceToggle{flex-shrink:0}
#rentFinanceCard .rent-finance-head .sub{margin-bottom:12px}
'''
s=s.replace('</style>',css+'\n</style>',1)
js='''<script id="rental-finance-toggle">
(function(){const button=document.getElementById('rentFinanceToggle'),body=document.getElementById('rentFinanceBody');
if(!button||!body)return;
button.addEventListener('click',function(){const open=button.getAttribute('aria-expanded')!=='true';body.hidden=!open;button.textContent=open?'−':'+';button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label','Finanzierung und Nebenkosten '+(open?'schließen':'öffnen'));});
const months=document.getElementById('rentMonths');if(months)months.addEventListener('change',function(){months.value=String(Math.max(0,Math.round(Number(months.value)||0)));months.dispatchEvent(new Event('input',{bubbles:true}));});
})();</script>'''
s=s.replace('</body>',js+'\n</body>',1)

# Both optional rental sections start closed.
financing_replace('id="rentFinanceToggle" aria-label="Finanzierung und Nebenkosten schließen" aria-controls="rentFinanceBody" aria-expanded="true">−','id="rentFinanceToggle" aria-label="Finanzierung und Nebenkosten öffnen" aria-controls="rentFinanceBody" aria-expanded="false">+','closed financing toggle')
financing_replace('<div id="rentFinanceBody">','<div id="rentFinanceBody" hidden>','closed financing body')
heading=s.index('<h2>2. Laufende Vermietung</h2>',s.index('id="rentSection"'))
card_start=s.rfind('<section',0,heading)
card_end=s.index('</section>',heading)+len('</section>')
subtitle_start=s.index('<p class="sub">',heading)
body_start=s.index('</p>',subtitle_start)+len('</p>')
subtitle=s[subtitle_start:body_start]
body=s[body_start:card_end-len('</section>')]
card='''<section class="card" id="rentRunningCard">
<div class="rent-running-head"><div><h2>2. Laufende Vermietung</h2>'''+subtitle+'''</div><button type="button" class="plus-btn" id="rentRunningToggle" aria-label="Laufende Vermietung öffnen" aria-controls="rentRunningBody" aria-expanded="false">+</button></div>
<div id="rentRunningBody" hidden>'''+body+'''</div></section>'''
s=s[:card_start]+card+s[card_end:]
css='''
#rentRunningCard .rent-running-head{display:flex;align-items:center;gap:12px;justify-content:space-between}
#rentRunningCard .rent-running-head>div{min-width:0;flex:1}
#rentRunningToggle{flex-shrink:0}
#rentRunningBody[hidden],#rentFinanceBody[hidden]{display:none!important}
'''
s=s.replace('</style>',css+'\n</style>',1)
js='''<script id="rental-running-toggle">
(function(){const button=document.getElementById('rentRunningToggle'),body=document.getElementById('rentRunningBody');
if(!button||!body)return;
button.addEventListener('click',function(){const open=button.getAttribute('aria-expanded')!=='true';body.hidden=!open;button.textContent=open?'−':'+';button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label','Laufende Vermietung '+(open?'schließen':'öffnen'));});
})();</script>'''
s=s.replace('</body>',js+'\n</body>',1)

# Plain-language rental interpretation based on calculated results.
start=s.index('    const recommendation=(()=>{',s.index('  function buildRentalPdf(){'))
end=s.index('    })();',start)+len('    })();')
s=s[:start]+'    const recommendation=interpretRentalInvestment(m);'+s[end:]
interpretation_js=r'''<script id="rental-investment-interpretation">
function interpretRentalInvestment(m){
  if(!(m.purchase>0&&m.coldRent>0&&m.totalInvestment>0)) return 'Für eine verständliche Einordnung fehlen noch Kaufpreis oder Nettokaltmiete. Ergänze außerdem Eigentümerkosten und Finanzierung.';
  const euro=n=>new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',minimumFractionDigits:2,maximumFractionDigits:2}).format(n);
  const pct=n=>new Intl.NumberFormat('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n*100)+' %';
  const net=m.netYield, financed=m.loan>0.005, cash=m.cashflow;
  const paragraphs=[];
  paragraphs.push(financed&&net<m.interest
    ? 'Für Vermögensaufbau mit wenig Eigenkapital ist die laufende Rechnung derzeit schwach: Nach Eigentümerkosten erwirtschaftet die Immobilie '+pct(net)+', der Kredit kostet '+pct(m.interest)+' Zinsen. Mehr Fremdkapital verschlechtert unter diesen Annahmen den laufenden Ertrag.'
    : financed ? 'Die Immobilie erwirtschaftet nach Eigentümerkosten '+pct(net)+' vor Finanzierung; der Kreditzins liegt bei '+pct(m.interest)+'. Der Ertrag deckt den Zinssatz rechnerisch ab. Das allein belegt noch keine ausreichende Reserve.'
    : 'Ohne Darlehen erwirtschaftet die Immobilie nach Eigentümerkosten '+pct(net)+' auf die Gesamtinvestition. Für die Bewertung zählt, ob dieser Ertrag Kapitalbindung und Immobilienrisiken für dich rechtfertigt.');
  if(m.factor!=null&&m.factor<20) paragraphs.push('Der niedrige Kaufpreisfaktor ist nur ein erster Hinweis: Er lässt Kaufnebenkosten und laufende Eigentümerkosten außer Acht und ist allein kein Kaufargument.');
  paragraphs.push(cash<0
    ? 'Du musst nach Zins und Tilgung '+euro(-cash)+' monatlich aus anderem Einkommen zuschießen ('+euro(-cash*12)+' pro Jahr). Die Wohnung liefert aktuell keine zusätzliche monatliche Rente.'
    : 'Nach Zins und Tilgung bleiben '+euro(cash)+' monatlich vor persönlicher Steuer. Dieser Betrag ist dein rechnerischer Überschuss; ungeplante Ausgaben können ihn aufzehren.');
  const principal=m.principal||0, ownContribution=Math.max(0,-cash*12);
  paragraphs.push('Du bindest '+euro(m.equityUsed)+' eigenes Kapital'+(m.fundingGap>0.005?' und benötigst zusätzlich '+euro(m.fundingGap)+' noch ungedeckte Eigenmittel':'')+'. Anfangs sinken die Schulden durch Tilgung auf ein Jahr hochgerechnet um '+euro(principal)+'. '+(ownContribution>0 ? 'Davon stehen '+euro(ownContribution)+' eigene jährliche Zuschüsse gegenüber; Tilgung ist deshalb nicht vollständig selbst erwirtschafteter Gewinn.' : 'Die Tilgung baut schuldenfreies Vermögen auf und ist kein zusätzlich verfügbarer Geldbetrag.'));
  if(financed) paragraphs.push('Nach '+m.financingMonths+' Monaten verbleiben rechnerisch '+euro(m.remainingDebt)+' Schulden, wenn Zins und Rate unverändert bleiben. Diese Laufzeit ist nicht automatisch dein Rentenbeginn; eine nötige Anschlussfinanzierung kann anders ausfallen.');
  if(financed&&net<m.interest&&m.noi>0){
    const acquisitionRate=m.acquisition/m.purchase;
    const target=(m.noi/m.interest-m.renovation)/(1+acquisitionRate);
    if(target>0&&target<m.purchase){
      const discount=1-target/m.purchase;
      paragraphs.push('Bei unverändertem Nettoertrag müsste der Kaufpreis auf etwa '+euro(target)+' sinken ('+pct(discount)+' Abschlag), damit die Nettorendite den Kreditzins erreicht - noch ohne Risikopuffer. Ob das verhandelbar ist, lässt sich ohne Vergleichspreise und Objektprüfung nicht beurteilen.');
    }else paragraphs.push('Ein niedrigerer Kaufpreis allein reicht bei den angesetzten Kosten möglicherweise nicht aus. Prüfe nachhaltige Mieterträge, Modernisierung und Finanzierung gemeinsam.');
  }else if(m.fundingGap>0.005){
    paragraphs.push('Kläre zuerst die Finanzierungslücke. Eine niedrigere Kreditquote senkt zwar die Rate, verlangt aber weitere eigene Mittel.');
  }else paragraphs.push('Prüfe als Nächstes, ob der monatliche Überschuss auch bei Leerstand, Reparaturen und einer teureren Anschlussfinanzierung ausreicht. Weniger Tilgung verbessert die Liquidität, verlangsamt aber die Entschuldung.');
  paragraphs.push('Eine verfügbare Liquiditätsreserve, dein Rentenbeginn und Steuerdaten fehlen. AfA und Einkommensteuer sind nicht eingerechnet; Steuerentlastungen und Wertsteigerungen werden nicht vorausgesetzt. Eine langfristige Gesamtrendite oder sichere Zusatzrente ist daraus noch nicht ableitbar.');
  return paragraphs.join('\n\n');
}
</script>'''
s=s.replace('</body>',interpretation_js+'\n</body>',1)

# Render justified paragraphs line by line; empty lines must never emit infinite spacing.
old_paragraph_text='''      doc.text(lines,L+padding,y+bodyTop,justify?{
        align:"justify",
        maxWidth:W-padding*2,
        baseline:"top",
        lineHeightFactor:lineHeightFactor
      }:undefined);'''
new_paragraph_text='''      if(justify){
        lines.forEach(function(line,index){
          if(!String(line).trim()) return;
          const next=lines[index+1];
          const paragraphEnd=index===lines.length-1 || !String(next||"").trim();
          const words=String(line).trim().split(/\\s+/);
          doc.setCharSpace(0);
          const top=y+bodyTop+index*lineH;
          if(!paragraphEnd && words.length>1){
            const wordWidth=words.reduce((sum,word)=>sum+doc.getTextWidth(word),0);
            const spacing=Math.max(0,(W-padding*2-wordWidth)/(words.length-1));
            let x=L+padding;
            words.forEach(function(word){doc.text(word,x,top,{baseline:"top"});x+=doc.getTextWidth(word)+spacing;});
          }else doc.text(line,L+padding,top,{baseline:"top"});
        });
      }else doc.text(lines,L+padding,y+bodyTop);'''
financing_replace(old_paragraph_text,new_paragraph_text,'rental summary paragraph rendering')

p.write_text(s,encoding="utf-8")
print("V8.322 renovation helper texts unified")
