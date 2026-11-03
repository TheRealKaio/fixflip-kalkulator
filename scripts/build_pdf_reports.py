"""Connect every report to shared branding, live settings and the current disclaimer."""
from pathlib import Path
import base64,json,re,shutil,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
root=(site/'index.html').read_text()
default=re.search(r'<article class="legal-page-card">(.*?)</article>',root,re.S)
if not default:raise SystemExit('Default disclaimer markup missing')
html=re.sub(r'<h1\b[^>]*>.*?</h1>','',default[1],count=1,flags=re.S)
payload={'disclaimer':html,'logo':'data:image/png;base64,'+base64.b64encode(Path('assets/share-logo.png').read_bytes()).decode(),'version':(site/'.release-version').read_text().strip()}
data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')
wrappers='''async function preparePdfBrandLogo(){return window.NICPDF.prepare();}
function drawPdfBrandLogo(doc){return window.NICPDF.logo(doc);}
function drawPdfBrandHeader(doc,...args){return window.NICPDF.header(doc,...args);}
function drawPdfFooter(doc,...args){return window.NICPDF.footer(doc,...args);}
function appendPdfDisclaimerPage(doc){return window.NICPDF.disclaimer(doc);}

'''
for page in site.rglob('*.html'):
 s=page.read_text()
 if 'function buildBudgetPdf(){' in s:
  a=s.index('const BRAND_DOMAIN =');b=s.index('function buildBudgetPdf(){',a);s=s[:a]+wrappers+s[b:]
  modes=iter(["'budget'",'currentDealType()',"'rent'"])
  s=re.sub(r'new jsPDF\((\{[^}]*\})\)',lambda m:'window.NICPDF.create('+m[1]+','+next(modes)+')',s)
  s=re.sub(r'function nicPdfReportName\(mode,now=new Date\(\)\)\{.*?\n\}', 'function nicPdfReportName(mode,now=new Date()){return window.NICPDF.filename(mode,now).slice(0,-4);}',s,count=1,flags=re.S)
  if s.count('appendPdfDisclaimerPage(doc);')!=3:raise SystemExit('Missing existing report disclaimer calls: '+str(page))
 elif page.parent.name!='finanzierungsrechner':continue
 # Registration checks apply to all four existing reports, including download fallbacks.
 if 'async function sharePdf(){' in s:
  s=s.replace('async function sharePdf(){', "async function sharePdf(){if(window.NICAccess&&!await window.NICAccess.authorize('pdfShare'))return;",1)
  s=s.replace('async function savePdf(){', "async function savePdf(){if(window.NICAccess&&!await window.NICAccess.authorize('pdfDownload'))return;",1)
  s=s.replace('async function rentalPdf(kind){', "async function rentalPdf(kind){if(window.NICAccess&&!await window.NICAccess.authorize(kind==='save'?'pdfDownload':'pdfShare'))return;",1)
  s=s.replace('      const url = URL.createObjectURL(blob);', "      if(window.NICAccess&&!await window.NICAccess.authorize('pdfDownload'))return;\n      const url = URL.createObjectURL(blob);",1)
  s=s.replace("      const u=URL.createObjectURL(blob),a=document.createElement('a');", "      if(window.NICAccess&&!await window.NICAccess.authorize('pdfDownload'))return;\n      const u=URL.createObjectURL(blob),a=document.createElement('a');",1)
 # Route generated document save actions through the shared PDF viewer.
 # Native sharing remains separate; only former download actions open a new tab.
 s=re.sub(r'\\bdoc\\.save\\(([^()]*)\\)',r'window.NICPDF.openReport(doc,\\1)',s)
 s=s.replace('</head>','<script type="application/json" id="nic-pdf-defaults">'+data+'</script><script src="/pdf-reports.js" defer></script></head>',1)
 if page.parent.name=='finanzierungsrechner':
  s=s.replace('</head>','<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script></head>',1)
  s=s.replace('<html lang="de" ', '<html lang="de" data-nic-release="'+payload['version'][1:]+'" ',1)
 page.write_text(s)
shutil.copyfile('assets/pdf-reports.js',site/'pdf-reports.js')
# Apply PDF viewer changes to generated output only. The archived original is immutable.
pdf_asset=site/'pdf-reports.js'
pdf_js=pdf_asset.read_text(encoding='utf-8')
viewer="""// One PDF viewing path for Budget, Eigennutzung, Vermietung, Fix & Flip and Finanzierung.
let pendingPdfWindow=null;
function preparePdfWindow(event){
 const button=event.target.closest?.('button');
 if(!button || !button.matches('.bottom-save,#download'))return;
 if(pendingPdfWindow && !pendingPdfWindow.closed)return;
 // Open synchronously from the user's click, before asynchronous access/PDF work.
 const tab=window.open('about:blank','_blank');
 if(!tab)return;
 try{
   tab.opener=null;
   tab.document.title='PDF wird vorbereitet';
   tab.document.body.textContent='Der PDF-Bericht wird vorbereitet …';
 }catch(_err){}
 pendingPdfWindow=tab;
}
document.addEventListener('click',preparePdfWindow,true);
function openReport(doc,name){
 const url=URL.createObjectURL(doc.output('blob'));
 const tab=pendingPdfWindow && !pendingPdfWindow.closed ? pendingPdfWindow : window.open('about:blank','_blank');
 pendingPdfWindow=null;
 if(tab){
   try{tab.opener=null;tab.location.replace(url);}catch(_err){tab.location.href=url;}
 }else{
   // Browser blocked a delayed popup: offer a normal user-activated viewing link.
   const link=document.createElement('a');
   link.href=url;link.target='_blank';link.rel='noopener noreferrer';
   link.textContent='PDF im neuen Tab öffnen';
   link.style.cssText='position:fixed;z-index:2147483647;right:16px;bottom:16px;padding:14px 18px;background:#075c55;color:white;border-radius:10px;box-shadow:0 3px 14px #0003';
   document.body.appendChild(link);
   link.addEventListener('click',()=>{setTimeout(()=>link.remove(),500);},{once:true});
 }
 setTimeout(()=>URL.revokeObjectURL(url),300000);
}
"""
if 'function openReport(doc,name)' not in pdf_js:
    pdf_js=pdf_js.replace('async function exportFinance(values,download){',viewer+'async function exportFinance(values,download){')
pdf_js=pdf_js.replace('doc.save(name)', 'openReport(doc,name)')
pdf_js=pdf_js.replace('exportFinance,model,legalBlocks','exportFinance,openReport,model,legalBlocks')
pdf_asset.write_text(pdf_js,encoding='utf-8')
shutil.copyfile('scripts/pdf_reports_browser_check.html',site/'_checks'/'pdf-reports.html')
print('All five reports share pdf-reports.js, live branding/settings and a separate final disclaimer section')
