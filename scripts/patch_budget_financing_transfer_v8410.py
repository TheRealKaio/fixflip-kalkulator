"""V8.410: transfer the fixed budget rate into the financing calculator."""
from pathlib import Path
import re

site = Path("_site/index.html")
html = site.read_text(encoding="utf-8")
button_id = "budgetFinanceTransfer"
if f'id="{button_id}"' not in html:
    pattern = r'(<section\b[^>]*>(?:(?!<section\b).)*?<h2>3\. Weitere Annahmen</h2>(?:(?!</section>).)*?)(</section>)'
    match = re.search(pattern, html, re.S)
    if not match:
        raise SystemExit("Budget assumptions section missing")
    row = '''
          <div id="budgetFinanceTransferRow"><button type="button" class="budget-apply-btn" id="budgetFinanceTransfer">Mit Budget-Darlehen kalkulieren</button></div>'''
    html = html[:match.end(1)] + row + html[match.start(2):]

style = '''<style id="nic-budget-finance-transfer-style">
#budgetFinanceTransferRow{display:flex;justify-content:center;align-items:center;width:100%;margin:14px 0 2px}
#budgetFinanceTransfer{display:flex;justify-content:center;align-items:center;box-sizing:border-box;width:max-content;max-width:100%;min-height:44px;padding:10px 18px;font-size:var(--nic-body-font-size,16px)!important;line-height:1.25;white-space:normal;overflow-wrap:anywhere;text-align:center}
@media(max-width:700px) and (orientation:portrait){#budgetFinanceTransfer{font-size:var(--nic-subtext-font-size,14px)!important}}
</style>'''
if 'id="nic-budget-finance-transfer-style"' not in html:
    html = html.replace("</head>", style + "</head>", 1)

listener = '''
if($("budgetFinanceTransfer")){
  $("budgetFinanceTransfer").addEventListener("click",()=>{
    const m=budgetModel();
    const transfer={version:1,monthlyRate:Math.max(0,Number(m.monthlyRate)||0),loan:Math.max(0,Number(m.loan)||0),interest:Number(m.interestPct)*100,repay:Number(m.repaymentPct)*100,extra:0,years:10};
    try{localStorage.setItem("nic_financing_budget_transfer_v1",JSON.stringify(transfer));}
    catch(_){alert("Die Budgetwerte konnten nicht für den Finanzierungsrechner übernommen werden.");return;}
    if(window.NICCalculatorNavigation?.select) window.NICCalculatorNavigation.select("finance",true);
  });
}
'''
if 'id="budgetFinanceTransfer"' not in html:
    raise SystemExit("Budget transfer button insertion failed")
if 'nic_financing_budget_transfer_v1' not in html:
    anchor = 'if($("budgetApplySuggestions")){'
    if anchor not in html:
        raise SystemExit("Budget action listener anchor missing")
    html = html.replace(anchor, listener + anchor, 1)
site.write_text(html, encoding="utf-8")

finance = Path("assets/financing.html")
source = finance.read_text(encoding="utf-8")
source = source.replace(
    "const $=id=>document.getElementById(id), K='nic_financing_slots_v1', F='nic_financing_draft_v1';",
    "const $=id=>document.getElementById(id), K='nic_financing_slots_v1', F='nic_financing_draft_v1', TRANSFER='nic_financing_budget_transfer_v1', FIXED='nic_financing_fixed_monthly_rate_v1';\nlet fixedMonthlyRate=null;try{const stored=localStorage.getItem(FIXED);if(stored!==null&&Number.isFinite(Number(stored))&&Number(stored)>=0)fixedMonthlyRate=Number(stored)}catch(_){}"
)
source = source.replace(
    "function calculate(){let {loan,interest,repay,extra,years}=values();loan=Math.max(0,Math.min(1e9,loan));const monthly=loan*(interest+repay)/1200,annualExtra=loan*extra/100;",
    "function calculate(){let {loan,interest,repay,extra,years}=values();loan=Math.max(0,Math.min(1e9,loan));let monthly=loan*(interest+repay)/1200;if(fixedMonthlyRate!==null){const rateFactor=interest+repay;loan=rateFactor>0?Math.max(0,Math.min(1e9,Math.round(fixedMonthlyRate*1200/rateFactor*100)/100)):0;monthly=fixedMonthlyRate;$('loan').value=String(loan);$('loan').readOnly=true;}else $('loan').readOnly=false;const annualExtra=loan*extra/100;"
)
reset_old = "$('newCalc').addEventListener('click',()=>{try{localStorage.removeItem('nic_financing_interest_manual_v1')}catch(_){}setValues({...defaults,interest:currentRate??defaults.interest});$('loan').focus({preventScroll:false});$('loan').select();});"
reset_new = "$('newCalc').addEventListener('click',()=>{try{[F,TRANSFER,FIXED,'nic_financing_interest_manual_v1'].forEach(key=>localStorage.removeItem(key));}catch(_){}fixedMonthlyRate=null;setValues({...defaults,interest:currentRate??defaults.interest});$('loan').focus({preventScroll:false});$('loan').select();});"
if reset_old not in source and reset_new not in source:
    raise SystemExit("Financing reset handler anchor missing")
source = source.replace(reset_old, reset_new, 1)

startup_old = "try{const saved=JSON.parse(localStorage.getItem(F)||'null');if(saved){setValues({...saved,repay:saved.repay===2?1.5:saved.repay})}else calculate()}catch(e){calculate()}loadRates();"
startup_new = "try{const saved=JSON.parse(localStorage.getItem(F)||'null');if(saved){setValues({...saved,repay:saved.repay===2?1.5:saved.repay})}else calculate()}catch(e){calculate()}try{const transfer=JSON.parse(localStorage.getItem(TRANSFER)||'null');if(transfer&&transfer.version===1&&Number.isFinite(Number(transfer.monthlyRate))){fixedMonthlyRate=Math.max(0,Number(transfer.monthlyRate));localStorage.setItem(FIXED,String(fixedMonthlyRate));localStorage.removeItem(TRANSFER);setValues({loan:Number(transfer.loan)||0,interest:Number(transfer.interest)||0,repay:Number(transfer.repay)||0,extra:0,years:10});}}catch(e){console.error('Budgetwerte konnten nicht übernommen werden.',e)}loadRates();"
if startup_old not in source:
    raise SystemExit("Financing startup anchor missing")
source = source.replace(startup_old, startup_new, 1)
finance.write_text(source, encoding="utf-8")

print("V8.410 budget-to-finance transfer and fixed monthly rate installed")
