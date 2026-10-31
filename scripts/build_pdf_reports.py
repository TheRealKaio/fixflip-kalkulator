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
 s=s.replace('</head>','<script type="application/json" id="nic-pdf-defaults">'+data+'</script><script src="/pdf-reports.js" defer></script></head>',1)
 if page.parent.name=='finanzierungsrechner':
  s=s.replace('</head>','<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"></script></head>',1)
  s=s.replace('<html lang="de" ', '<html lang="de" data-nic-release="'+payload['version'][1:]+'" ',1)
 page.write_text(s)
shutil.copyfile('assets/pdf-reports.js',site/'pdf-reports.js')
shutil.copyfile('scripts/pdf_reports_browser_check.html',site/'_checks'/'pdf-reports.html')
print('All five reports share pdf-reports.js, live branding/settings and a separate final disclaimer section')
