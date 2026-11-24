"""V8.410: transfer the fixed budget rate into the financing calculator."""
from pathlib import Path
import re

site = Path("_site/index.html")
html = site.read_text(encoding="utf-8")
button_id = "budgetFinanceTransfer"
row = '''
          <div id="budgetFinanceTransferRow">
            <button type="button" class="budget-apply-btn" id="budgetFinanceTransfer">Budget in Finanzierung übernehmen</button>
            <small id="budgetFinanceTransferHint">Monatsrate, Zinssatz und Tilgung werden übernommen.</small>
          </div>'''
if f'id="{button_id}"' in html:
    html, moved = re.subn(r'\s*<div id="budgetFinanceTransferRow">.*?</div>', '', html, count=1, flags=re.S)
    if moved != 1:
        raise SystemExit("Existing budget transfer button row is malformed")
pattern = r'(<section\b[^>]*>(?:(?!<section\b).)*?<h2>(?:\d+\.\s*)?Dein monatlich verfügbares Budget</h2>(?:(?!</section>).)*?)(</section>)'
match = re.search(pattern, html, re.S)
if not match:
    raise SystemExit("Monthly budget section missing")
html = html[:match.end(1)] + row + html[match.start(2):]

style = '''<style id="nic-budget-finance-transfer-style">
#budgetFinanceTransferRow{display:flex;flex-direction:column;justify-content:center;align-items:center;gap:6px;width:100%;margin:14px 0 2px;text-align:center}
#budgetFinanceTransferHint{max-width:100%;font-size:var(--nic-hint-font-size,12px)!important;line-height:1.4;color:var(--nic-text-muted,#64748b);text-align:center}
#budgetFinanceTransfer{display:flex;justify-content:center;align-items:center;box-sizing:border-box;width:max-content;max-width:100%;min-height:44px;padding:10px 18px;font-size:var(--nic-body-font-size,16px)!important;line-height:1.25;white-space:normal;overflow-wrap:anywhere;text-align:center;transition:transform .12s ease,box-shadow .12s ease,filter .12s ease}
#budgetFinanceTransfer:hover{filter:brightness(.94);box-shadow:0 5px 12px rgba(15,23,42,.18)}
#budgetFinanceTransfer:active{transform:translateY(2px) scale(.985);filter:brightness(.88);box-shadow:0 1px 2px rgba(15,23,42,.16)}
#budgetFinanceTransfer:focus-visible{outline:3px solid #174f4a;outline-offset:3px}
@media(max-width:700px) and (orientation:portrait){#budgetFinanceTransfer{font-size:var(--nic-subtext-font-size,14px)!important}}
@media(prefers-reduced-motion:reduce){#budgetFinanceTransfer{transition:none}}
</style>'''
transfer_style_pattern = r'<style\b[^>]*id="nic-budget-finance-transfer-style"[^>]*>.*?</style>'
existing_transfer_styles = re.findall(transfer_style_pattern, html, re.S)
if len(existing_transfer_styles) > 1:
    html = re.sub(transfer_style_pattern, '', html, flags=re.S)
if len(existing_transfer_styles) == 1:
    html = re.sub(transfer_style_pattern, style, html, count=1, flags=re.S)
else:
    html = html.replace("</head>", style + "</head>", 1)

listener = '''
if($("budgetFinanceTransfer")){
  $("budgetFinanceTransfer").addEventListener("click",()=>{
    const m=budgetModel();
    const transfer={version:1,monthlyRate:Math.max(0,Number(m.monthlyRate)||0),loan:Math.max(0,Math.round(Number(m.loan)||0)),interest:Number(m.interestPct)*100,repay:Number(m.repaymentPct)*100,extra:0,years:10};
    try{localStorage.setItem("nic_financing_budget_transfer_v1",JSON.stringify(transfer));localStorage.setItem("nic_financing_interest_manual_v1","1");}
    catch(_){try{localStorage.removeItem("nic_financing_budget_transfer_v1");localStorage.removeItem("nic_financing_interest_manual_v1");}catch(__){}alert("Die Budgetwerte konnten nicht für den Finanzierungsrechner übernommen werden.");return;}
    if(window.NICCalculatorNavigation?.select) window.NICCalculatorNavigation.select("finance",true);
    requestAnimationFrame(()=>requestAnimationFrame(()=>window.scrollTo({top:0,left:0,behavior:"instant"})));
  });
}
'''
listener_old = '''
if($("budgetFinanceTransfer")){
  $("budgetFinanceTransfer").addEventListener("click",()=>{
    const m=budgetModel();
    const transfer={version:1,monthlyRate:Math.max(0,Number(m.monthlyRate)||0),loan:Math.max(0,Math.round(Number(m.loan)||0)),interest:Number(m.interestPct)*100,repay:Number(m.repaymentPct)*100,extra:0,years:10};
    try{localStorage.setItem("nic_financing_budget_transfer_v1",JSON.stringify(transfer));}
    catch(_){alert("Die Budgetwerte konnten nicht für den Finanzierungsrechner übernommen werden.");return;}
    if(window.NICCalculatorNavigation?.select) window.NICCalculatorNavigation.select("finance",true);
    requestAnimationFrame(()=>requestAnimationFrame(()=>window.scrollTo({top:0,left:0,behavior:"instant"})));
  });
}
'''
html, listener_replaced = re.subn(
    r'\nif\(\$\("budgetFinanceTransfer"\)\)\{.*?\n\}\n',
    listener,
    html,
    count=1,
    flags=re.S,
)
if 'id="budgetFinanceTransfer"' not in html:
    raise SystemExit("Budget transfer button insertion failed")
if listener_replaced == 0 and 'nic_financing_budget_transfer_v1' not in html:
    anchor = 'if($("budgetApplySuggestions")){'
    if anchor not in html:
        raise SystemExit("Budget action listener anchor missing")
    html = html.replace(anchor, listener + anchor, 1)
elif listener_replaced == 0:
    raise SystemExit("Existing budget transfer listener could not be updated")
site.write_text(html, encoding="utf-8")

finance = Path("assets/financing.html")
source = finance.read_text(encoding="utf-8")
source = source.replace(
    "const $=id=>document.getElementById(id), K='nic_financing_slots_v1', F='nic_financing_draft_v1';",
    "const $=id=>document.getElementById(id), K='nic_financing_slots_v1', F='nic_financing_draft_v1', TRANSFER='nic_financing_budget_transfer_v1', FIXED='nic_financing_fixed_monthly_rate_v1';\nlet fixedMonthlyRate=null,preserveImportedLoan=false;try{const stored=localStorage.getItem(FIXED);if(stored!==null&&Number.isFinite(Number(stored))&&Number(stored)>=0)fixedMonthlyRate=Number(stored)}catch(_){}"
)
source = source.replace(
    "let fixedMonthlyRate=null;try{const stored=localStorage.getItem(FIXED);if(stored!==null&&Number.isFinite(Number(stored))&&Number(stored)>=0)fixedMonthlyRate=Number(stored)}catch(_){}",
    "let fixedMonthlyRate=null,preserveImportedLoan=false;try{const stored=localStorage.getItem(FIXED);if(stored!==null&&Number.isFinite(Number(stored))&&Number(stored)>=0)fixedMonthlyRate=Number(stored)}catch(_){}",
    1,
)
calculate_old = "function calculate(){let {loan,interest,repay,extra,years}=values();loan=Math.max(0,Math.min(1e9,loan));const monthly=loan*(interest+repay)/1200,annualExtra=loan*extra/100;"
calculate_transfer_old = "function calculate(){let {loan,interest,repay,extra,years}=values();loan=Math.max(0,Math.min(1e9,loan));let monthly=loan*(interest+repay)/1200;if(fixedMonthlyRate!==null){const rateFactor=interest+repay;loan=rateFactor>0?Math.max(0,Math.min(1e9,Math.round(fixedMonthlyRate*1200/rateFactor*100)/100)):0;monthly=fixedMonthlyRate;$('loan').value=String(loan);$('loan').readOnly=true;}else $('loan').readOnly=false;const annualExtra=loan*extra/100;"
calculate_new = "function calculate(){let {loan,interest,repay,extra,years}=values();loan=Math.max(0,Math.min(1e9,loan));let monthly=loan*(interest+repay)/1200;if(fixedMonthlyRate!==null){const rateFactor=interest+repay;if(typeof preserveImportedLoan!=='undefined'&&preserveImportedLoan){loan=Math.max(0,Math.min(1e9,Math.round(loan)));preserveImportedLoan=false;}else loan=rateFactor>0?Math.max(0,Math.min(1e9,Math.floor(fixedMonthlyRate*1200/rateFactor))):0;monthly=fixedMonthlyRate;$('loan').value=String(loan);$('loan').readOnly=true;}else $('loan').readOnly=false;const annualExtra=loan*extra/100;"
source = source.replace(calculate_old, calculate_new, 1)
source = source.replace(calculate_transfer_old, calculate_new, 1)
calculate_floor_old = "function calculate(){let {loan,interest,repay,extra,years}=values();loan=Math.max(0,Math.min(1e9,loan));let monthly=loan*(interest+repay)/1200;if(fixedMonthlyRate!==null){const rateFactor=interest+repay;loan=rateFactor>0?Math.max(0,Math.min(1e9,Math.floor(fixedMonthlyRate*1200/rateFactor))):0;monthly=fixedMonthlyRate;$('loan').value=String(loan);$('loan').readOnly=true;}else $('loan').readOnly=false;const annualExtra=loan*extra/100;"
source = source.replace(calculate_floor_old, calculate_new, 1)
calculate_new_before_isolated_check = calculate_new.replace(
    "if(typeof preserveImportedLoan!=='undefined'&&preserveImportedLoan)",
    "if(preserveImportedLoan)",
    1,
)
source = source.replace(calculate_new_before_isolated_check, calculate_new, 1)
reset_old = "$('newCalc').addEventListener('click',()=>{try{localStorage.removeItem('nic_financing_interest_manual_v1')}catch(_){}setValues({...defaults,interest:currentRate??defaults.interest});$('loan').focus({preventScroll:false});$('loan').select();});"
reset_new = "$('newCalc').addEventListener('click',()=>{try{[F,TRANSFER,FIXED,'nic_financing_interest_manual_v1'].forEach(key=>localStorage.removeItem(key));}catch(_){}fixedMonthlyRate=null;setValues({...defaults,interest:currentRate??defaults.interest});$('loan').focus({preventScroll:false});$('loan').select();});"
if reset_old not in source and reset_new not in source:
    raise SystemExit("Financing reset handler anchor missing")
source = source.replace(reset_old, reset_new, 1)

startup_old = "try{const saved=JSON.parse(localStorage.getItem(F)||'null');if(saved){setValues({...saved,repay:saved.repay===2?1.5:saved.repay})}else calculate()}catch(e){calculate()}loadRates();"
startup_transfer_old = "try{const saved=JSON.parse(localStorage.getItem(F)||'null');if(saved){setValues({...saved,repay:saved.repay===2?1.5:saved.repay})}else calculate()}catch(e){calculate()}try{const transfer=JSON.parse(localStorage.getItem(TRANSFER)||'null');if(transfer&&transfer.version===1&&Number.isFinite(Number(transfer.monthlyRate))){fixedMonthlyRate=Math.max(0,Number(transfer.monthlyRate));localStorage.setItem(FIXED,String(fixedMonthlyRate));localStorage.removeItem(TRANSFER);setValues({loan:Number(transfer.loan)||0,interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});}}catch(e){console.error('Budgetwerte konnten nicht übernommen werden.',e)}loadRates();"
startup_new = "try{const saved=JSON.parse(localStorage.getItem(F)||'null');if(saved){setValues({...saved,repay:saved.repay===2?1.5:saved.repay})}else calculate()}catch(e){calculate()}try{const transfer=JSON.parse(localStorage.getItem(TRANSFER)||'null');if(transfer&&transfer.version===1&&Number.isFinite(Number(transfer.monthlyRate))){fixedMonthlyRate=Math.max(0,Number(transfer.monthlyRate));localStorage.setItem(FIXED,String(fixedMonthlyRate));localStorage.setItem('nic_financing_interest_manual_v1','1');localStorage.removeItem(TRANSFER);preserveImportedLoan=true;setValues({loan:Math.round(Number(transfer.loan)||0),interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});}}catch(e){console.error('Budgetwerte konnten nicht übernommen werden.',e)}loadRates();"
if startup_old not in source and startup_transfer_old not in source and startup_new not in source and "const notice=$('budgetTransferNotice')" not in source:
    raise SystemExit("Financing startup anchor missing")
source = source.replace(startup_old, startup_new, 1)
source = source.replace(startup_transfer_old, startup_new, 1)
startup_new_with_notice = startup_new.replace(
    "setValues({loan:Math.floor(Number(transfer.loan)||0),interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});",
    "setValues({loan:Math.round(Number(transfer.loan)||0),interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});const notice=$('budgetTransferNotice');if(notice){notice.hidden=false;window.setTimeout(()=>{notice.hidden=true},6500)}",
    1,
)
source = source.replace(startup_new, startup_new_with_notice, 1)
source = source.replace(
    "setValues({loan:Math.floor(Number(transfer.loan)||0),interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});",
    "preserveImportedLoan=true;setValues({loan:Math.round(Number(transfer.loan)||0),interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});",
    1,
)
notice = '<p id="budgetTransferNotice" class="budget-transfer-notice mini" role="status" aria-live="polite" hidden>Budgetwerte übernommen. Deine Monatsrate bleibt fix.</p>'
if 'id="budgetTransferNotice"' not in source:
    source = source.replace('<section class="card"><h2>1. Finanzierung einstellen</h2>', '<section class="card"><h2>1. Finanzierung einstellen</h2>' + notice, 1)
finance.write_text(source, encoding="utf-8")

print("V8.410 budget-to-finance transfer and fixed monthly rate installed")
