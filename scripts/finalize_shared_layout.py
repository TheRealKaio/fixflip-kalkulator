"""Consolidate generated shell CSS after every branding/build transformation.
Protected compressed calculator sources and standalone originals stay byte-identical.
"""
from pathlib import Path
import re,sys,shutil
from urllib.parse import urlsplit
from unify_calculator_header import split
from unify_finance_footer_markup import FooterParser,extract_footer

class AppParser(FooterParser):
 def handle_starttag(self,tag,attrs):
  attrs=[(k, "footer-note" if k=="class" and "app" in v.split() else v) for k,v in attrs]
  super().handle_starttag(tag,attrs)
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
def element(source,classname):
 class Parser(FooterParser):
  def handle_starttag(self,tag,attrs):
   attrs=[(k,'footer-note' if k=='class' and classname in v.split() else '' if k=='class' else v) for k,v in attrs]
   super().handle_starttag(tag,attrs)
 parser=Parser(source);parser.feed(source)
 if parser.start is None or parser.end is None:raise ValueError('Missing '+classname)
 return source[parser.start:parser.end],parser.start,parser.end

shutil.copyfile('assets/calculator-shell.js',site/'calculator-shell.js')
root=site/'index.html'
menu,_,_=element(root.read_text(),'deal-type-card')
menu=menu.replace('class="card deal-type-card"','class="menu card deal-type-card"',1)
for mode,slug in [('budget','budget'),('own','eigennutzung'),('rent','vermietung'),('flip','fix-flip')]:
 if mode=='rent':menu=menu.replace('id="dealTypeRent"','id="dealTypeRent" data-href="/'+slug+'/"',1)
 else:
  ident={'budget':'Budget','own':'Own','flip':'Flip'}[mode]
  menu=menu.replace('for="dealType'+ident+'"','for="dealType'+ident+'" data-href="/'+slug+'/"',1)
anchor='<a id="nicFinancingTab" class="deal-type-option" data-calculator="finance" data-href="/finanzierungsrechner/" href="/finanzierungsrechner/"><span><strong>Finanzierungsrechner</strong><small>Darlehen, Tilgung, Sondertilgung und Restschuld</small></span></a>'
if 'id="nicFinancingTab"' not in menu:
 end=menu.rfind('</div>');menu=menu[:end]+anchor+menu[end:]
for slug in ['', 'budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']:
 p=site/slug/'index.html';source=p.read_text();_,a,b=element(source,'deal-type-card');shared=menu
 if slug=='finanzierungsrechner':
  shared=re.sub(r'\schecked(?:="[^"]*")?','',shared)
  shared=shared.replace('id="nicFinancingTab"','id="nicFinancingTab" aria-current="page"',1)
 else:
  mode={'eigennutzung':'own','fix-flip':'flip','vermietung':'rent'}.get(slug,'budget')
  shared=re.sub(r'\schecked(?:="[^"]*")?','',shared)
  shared=shared.replace('value="'+mode+'"','value="'+mode+'" checked',1)
 p.write_text(source[:a]+shared+source[b:])

pattern=re.compile(r'\.(?:hero(?:-top)?|brand-logo(?:-wrap)?|deal-type-(?:row|option|card|title)|nic-menu-icon|footer-(?:note|meta|version|legal-links)|nic-footer-cookie-pair|bottom(?:-actions|-primary|-pdf|-save|-share)?|save-arrow)(?![\w-])|#(?:recalc|nicFinancingTab)(?![\w-])')
# Follow the actual cascade once. Shared selectors are removed from their sources.
rules=[]
html=root.read_text()
for m in re.finditer(r'<style\b[^>]*>(.*?)</style>|<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>',html,re.S|re.I):
 if m[1] is not None:rules.extend(split(m[1],pattern)[1])
 elif (p:=site/Path(urlsplit(m[2]).path).name).is_file():rules.extend(split(p.read_text(),pattern)[1])
# Exact duplicates provide no further cascade behavior.
rules=list(dict.fromkeys(rules))
for p in site.glob('*.css'):
 p.write_text(split(p.read_text(),pattern)[0])
for p in site.rglob('*.html'):
 s=p.read_text()
 s=re.sub(r'<link[^>]*href="/calculator-shell.css[^"]*"[^>]*>','',s)
 s=re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',lambda m:m[1]+split(m[2],pattern)[0]+m[3],s,flags=re.S|re.I)
 if 'class="bottom-actions"' in s:
  footer,a,b=extract_footer(s);s=s[:a]+s[b:]
  app=AppParser(s);app.feed(s)
  if app.end is None:raise SystemExit('App container missing: '+str(p))
  end=s.rfind('</',app.start,app.end);s=s[:end]+footer+s[end:]
  if 'legal-views.js' not in s:s=s.replace('</head>','<link rel="stylesheet" href="/legal-views.css"><script defer src="/legal-views.js"></script></head>',1)
  s=s.replace('</head>','<link rel="stylesheet" href="/calculator-shell.css"><script defer src="/calculator-shell.js"></script></head>',1)
 p.write_text(s)
rules.append('body:not(.nic-embed) .deal-type-row{grid-template-columns:repeat(5,minmax(0,1fr))!important}body:not(.nic-embed) .deal-type-row>.deal-type-option{grid-column:auto!important}@media(max-width:700px){body:not(.nic-embed) .deal-type-row{grid-template-columns:minmax(0,1fr)!important}}')
rules.append('body:not(.nic-admin) :is(.field,.input-wrap,.finance-check-label,.finance-check-label>span){min-width:0!important;max-width:100%!important}body:not(.nic-admin) label{white-space:normal!important;overflow-wrap:anywhere}body:not(.nic-admin) .finance-check-label{flex-wrap:wrap}body:not(.nic-admin) .field input{max-width:100%;box-sizing:border-box}')
rules.append('body:not(.nic-admin) :is(.kpis,.kpi,.kpi>*,.rent-kpi-value-row){min-width:0!important;max-width:100%!important;box-sizing:border-box}body:not(.nic-admin) .kpi{overflow-wrap:anywhere}body:not(.nic-admin) .rent-kpi-value-row{flex-wrap:wrap}')
rules.append('body:not(.nic-embed) .app>.footer-note{box-sizing:border-box!important;width:100%!important;max-width:100%!important;margin:0!important;transform:none!important;border-radius:16px!important}')
rules.append('body:not(.nic-embed) .deal-type-row>:is(label,#dealTypeRent,#nicFinancingTab,.deal-type-option){border:2px solid #dce8e2!important;box-sizing:border-box!important}body:not(.nic-embed) .deal-type-row>:is(label,#dealTypeRent,#nicFinancingTab,.deal-type-option).nic-tile-active{border:2px solid var(--nic-green-bg,#075c55)!important;background:var(--nic-green-bg,#075c55)!important;color:var(--nic-green-text,#fff)!important}')
# Final cascade: the Budget recommendation CTA must never stretch to fill the row.
# The red clear button retains its own compact width alongside it.
rules.append('body:not(.nic-admin) #budgetExpensesSection .budget-expenses-toolbar{display:flex!important;width:100%!important;max-width:100%!important;justify-content:flex-end!important;align-items:center!important;gap:8px!important}')
rules.append('body:not(.nic-admin) #budgetExpensesSection #budgetApplySuggestions{flex:0 0 48%!important;width:48%!important;max-width:48%!important;min-width:0!important;margin-left:auto!important}')
rules.append('@media(max-width:650px){body:not(.nic-admin) #budgetExpensesSection #budgetApplySuggestions{flex-basis:calc(100% - 46px)!important;width:calc(100% - 46px)!important;max-width:calc(100% - 46px)!important}}')
(site/'calculator-shell.css').write_text('/* Authoritative shell cascade for all five calculators. */\n'+'\n'.join(rules)+'\nbody:not(.nic-embed) .deal-type-row{grid-auto-rows:1fr!important;align-items:stretch!important}\nbody:not(.nic-embed) .deal-type-row>.deal-type-option{height:100%!important;min-height:78px!important}\n')
print('Central calculator-shell.css:',len(rules),'shared rules; removed competing declarations')
