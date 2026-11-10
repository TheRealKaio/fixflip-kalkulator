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

pattern=re.compile(r'\.(?:hero(?:-top)?|brand-logo(?:-wrap)?|deal-type-(?:row|option|card|title)|nic-menu-icon|footer-(?:note|meta|version|legal-links)|nic-footer-cookie-pair|finance-check-box|bottom(?:-actions|-primary|-pdf|-save|-share)?|save-arrow)(?![\w-])|#(?:recalc|nicFinancingTab)(?![\w-])')
# Follow the actual cascade once. Shared selectors are removed from their sources.
rules=[]
html=root.read_text()
for m in re.finditer(r'<style\b[^>]*>(.*?)</style>|<link\b[^>]*rel="stylesheet"[^>]*href="([^"]+)"[^>]*>',html,re.S|re.I):
 if m[1] is not None:rules.extend(split(m[1],pattern)[1])
 elif (p:=site/Path(urlsplit(m[2]).path).name).is_file():rules.extend(split(p.read_text(),pattern)[1])
# Exact duplicates provide no further cascade behavior.
rules=list(dict.fromkeys(rules))
# Keep one shared checkbox rule. Override the generic input min-height and padding,
# which otherwise expand the intended 22.5px control to a 50px input on every device.
checkbox_rule='.finance-check-box input[type="checkbox"]'
checkbox_matches=sum(rule.count(checkbox_rule+'{') for rule in rules)
if checkbox_matches!=1:raise SystemExit('Expected one shared finance checkbox size rule')
rules=[rule.replace(checkbox_rule+'{',checkbox_rule+'{min-width:22.5px;max-width:22.5px;min-height:22.5px;max-height:22.5px;padding:0;box-sizing:border-box;') for rule in rules]

# The 22.5px checkbox remains unchanged. Draw a single inset checkmark:
# stroke extents stay at least 3px inside the outer square on all sides.
# Suppress older native/pseudo checkmarks so no duplicate ticks appear.
rules.append("""
body:not(.nic-admin) .finance-check-box input[type="checkbox"]{
 appearance:none!important;-webkit-appearance:none!important;
 background-image:none!important;
}
body:not(.nic-admin) .finance-check-box input[type="checkbox"]:checked{
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 22.5 22.5'%3E%3Cpath d='M5 11.2l4.1 4.1L17.7 5.4' fill='none' stroke='%23172033' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")!important;
 background-size:100% 100%!important;
 background-position:center!important;
 background-repeat:no-repeat!important;
}
body:not(.nic-admin) .finance-check-box input[type="checkbox"]::before,
body:not(.nic-admin) .finance-check-box input[type="checkbox"]::after{
 content:none!important;
}
""")

for p in site.glob('*.css'):
 p.write_text(split(p.read_text(),pattern)[0])
for p in site.rglob('*.html'):
 s=p.read_text()
 # Put the equity helper under its input after all older patches have finished
 # editing the original label markup.
 equity_hint_pattern=re.compile(
  r'(<label\b[^>]*>(?:(?!</label>).)*?<span id="equityInputLabel">.*?</span>)\s*'
  r'(<span class="hint" id="equityInputHint">.*?</span>)'
  r'(</label>\s*<div class="input-wrap">.*?</div>)',re.S
 )
 def move_equity_hint(match):
  hint=re.sub(r'^<span\b','<div',match.group(2),count=1)
  hint=re.sub(r'</span>$','</div>',hint,count=1)
  return match.group(1)+match.group(3)+hint
 s,equity_hint_moves=equity_hint_pattern.subn(move_equity_hint,s,count=1)
 if 'id="equityInputHint"' in s and equity_hint_moves!=1:
  raise SystemExit('Could not move equity helper below its input: '+str(p))
 # Tag the heading inside the calculator HTML string so it follows the admin body-size variable.
 s=s.replace('<h3>Weitere Finanzierung berücksichtigen</h3>','<h3 class="nic-body-font-text">Weitere Finanzierung berücksichtigen</h3>')
 # Rename visible field captions after all route and presentation transformations.
 labels={"Energieeffizienzklasse":"Effizienzkl. EEK","Lfd. Kosten pro Monat":"Lfd. mtl. Kosten","Laufende Kosten pro Monat":"Lfd. mtl. Kosten","Kaufnebenkosten gesamt":"Kaufnebenkosten"}
 parts=re.split(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)',s,flags=re.S|re.I)
 for i in range(0,len(parts),2):
  for old,new in labels.items():
   parts[i]=re.sub(r'(?<=>)(\s*)'+re.escape(old)+r'(\s*)(?=<)',lambda m:m[1]+new+m[2],parts[i])
   parts[i]=parts[i].replace('aria-label="'+old+'"','aria-label="'+new+'"')
 for i in range(0,len(parts),2):
  if 'Weitere Finanzierung berücksichtigen' in parts[i] and 'class="nic-body-font-text"' not in parts[i]:
   parts[i]=parts[i].replace('Weitere Finanzierung berücksichtigen','<span class="nic-body-font-text">Weitere Finanzierung berücksichtigen</span>')
 s=''.join(parts)
 # Group the existing finance fields without replacing inputs or their handlers.
 rate_start=s.find('<div class="finance-rate-grid">')
 if rate_start>=0 and 'class="nic-finance-mobile-fields"' not in s:
  rate_end=s.find('<div class="sale-cost-grid">',rate_start)
  if rate_end<0:raise SystemExit('Finance mobile grouping anchor missing: '+str(p))
  s=s[:rate_start]+'<div class="nic-finance-mobile-fields">'+s[rate_start:rate_end]+'</div>'+s[rate_end:]
 # Rental uses the same mobile grid, with its own isolated controls and IDs.
 rental_body=s.find('id="rentFinanceBody"')
 if rental_body>=0:
  rental_start=s.find('<div class="finance-rate-grid">',rental_body)
  rental_controls=s.find('<div class="quick-grid" id="rentFinancingControls">',rental_start)
  if rental_start<0 or rental_controls<0:raise SystemExit('Rental finance grouping anchor missing: '+str(p))
  _,_,controls_end=element(s[rental_controls:],'quick-grid')
  rental_end=rental_controls+controls_end
  s=s[:rental_start]+'<div class="nic-finance-mobile-fields">'+s[rental_start:rental_end]+'</div>'+s[rental_end:]
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
rules.append('body:not(.nic-admin) :is(.kpis,.kpi,.kpi>*,.rent-kpi-value-row){min-width:0!important;max-width:100%!important;box-sizing:border-box}body:not(.nic-admin) .kpis{grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr))!important}body:not(.nic-admin) .kpi{overflow-wrap:anywhere}body:not(.nic-admin) :is(#rentSection,#result.own-use) .kpi,body:not(.nic-admin) :is(#rentSection,#result.own-use) .kpi :is(.name,.name>span,.note){overflow-wrap:normal!important;word-break:normal!important;hyphens:none!important}body:not(.nic-admin) .kpi:not(:has(.info-btn)) .name,body:not(.nic-admin) .kpi .rent-kpi-name{padding-right:0!important}body:not(.nic-admin) .rent-kpi-name>span{min-width:0;flex:1 1 auto}body:not(.nic-admin) .rent-kpi-value-row{flex-wrap:wrap}')
rules.append("""
:root{--nic-content-footer-gap:16px}
body:not(.nic-embed):not(.nic-admin) .app{display:flex!important;flex-direction:column!important;min-height:100vh!important;min-height:100dvh!important}
body:not(.nic-embed):not(.nic-admin) .app>main{flex:1 0 auto!important}
body:not(.nic-embed):not(.nic-admin) .app>:is(.nic-brand-bar,.hero,.footer-note,.nic-shared-footer){flex-shrink:0!important}
body.nic-admin-open .app>#nicAdminPanel{padding-bottom:var(--nic-content-footer-gap,16px)!important;box-sizing:border-box}
""")
rules.append('body:not(.nic-embed) .app>.footer-note{box-sizing:border-box!important;width:100%!important;max-width:100%!important;margin:0!important;transform:none!important;border-radius:16px!important}')
rules.append('body:not(.nic-embed) .deal-type-row>:is(label,#dealTypeRent,#nicFinancingTab,.deal-type-option){border:2px solid #dce8e2!important;box-sizing:border-box!important}body:not(.nic-embed) .deal-type-row>:is(label,#dealTypeRent,#nicFinancingTab,.deal-type-option).nic-tile-active{border:2px solid var(--nic-green-bg,#075c55)!important;background:var(--nic-green-bg,#075c55)!important;color:var(--nic-green-text,#fff)!important}')
# Single final action sizing rule for Budget and modernization proposal controls.
# Exclude the separate renovation reset/save toolbar.
rules.append("""
body:not(.nic-admin) :is(.reno-head-actions,.budget-expenses-toolbar){
 display:flex!important;flex-direction:row!important;align-items:center!important;
 justify-content:center!important;gap:8px!important;box-sizing:border-box!important;
 width:100%!important;max-width:100%!important;min-width:0!important;
}
body:not(.nic-admin) :is(.reno-head-actions,.budget-expenses-toolbar)
:is(#applyTradeSuggestions,#rentApplyTradeSuggestions,#budgetApplySuggestions){
 flex:1 1 auto!important;width:auto!important;max-width:none!important;min-width:0!important;
 margin:0!important;white-space:nowrap!important;overflow-wrap:normal!important;
 line-height:1.2!important;box-sizing:border-box!important;
}
body:not(.nic-admin) .reno-head-actions{flex:1 1 auto!important;min-width:0!important}
body:not(.nic-admin) .budget-expenses-toolbar>:is(button,.nic-clear-reno):not(#budgetApplySuggestions){
 flex:0 0 36px!important;width:36px!important;min-width:36px!important;
 max-width:36px!important;margin:0!important;
}
/* Match the right-aligned renovation proposal group above its blue summary. */
body:not(.nic-admin) #budgetExpensesSection .budget-expenses-toolbar{
 width:48%!important;max-width:48%!important;margin-left:auto!important;margin-right:auto!important;
 justify-content:center!important;
}
body:not(.nic-admin) #budgetExpensesSection #budgetSuggestionActions{
 margin-left:auto!important;margin-right:auto!important;justify-content:center!important;text-align:center!important;
}
body:not(.nic-admin) #budgetExpensesSection #budgetApplySuggestions{
 flex:1 1 0!important;width:100%!important;min-width:0!important;
}
@media(max-width:650px){
 body:not(.nic-admin) #budgetExpensesSection .budget-expenses-toolbar{
  width:100%!important;max-width:100%!important;
 }
}
@media(max-width:420px){
 body:not(.nic-admin) :is(.reno-head-actions,.budget-expenses-toolbar){max-width:100%!important}
}
""")

# Mobile project goals: one input per row, with available equity in position four.
rules.append("""
@media(max-width:700px){
 body:not(.nic-admin) :is(
  .field:has(#targetProfit),
  .field:has(#targetMargin),
  .field:has(#targetRoi),
  .field:has(#maxEquity),
  .field:has(#personalTax)
 ){
  grid-column:1 / -1!important;width:100%!important;max-width:100%!important;
  min-width:0!important;box-sizing:border-box!important;
 }
 body:not(.nic-admin) .field:has(#targetProfit){order:1!important}
 body:not(.nic-admin) .field:has(#targetMargin){order:2!important}
 body:not(.nic-admin) .field:has(#targetRoi){order:3!important}
 body:not(.nic-admin) .field:has(#maxEquity){order:4!important}
 body:not(.nic-admin) .field:has(#personalTax){order:5!important}
}
""")

# Footer utility text follows the admin subtext size, including the cookie button.
rules.append("""
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) .footer-version,
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) .nic-footer-cookie-pair,
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) #nicConsentSettings,
body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) .nic-consent-settings{
 font-size:var(--nic-subtext-font-size,14px)!important;line-height:1.5!important;
 font-weight:400!important;
}
@media(max-width:700px){
 body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) .nic-footer-cookie-pair{
  display:flex!important;justify-content:center!important;align-items:center!important;
  flex:1 0 100%!important;grid-column:1 / -1!important;justify-self:center!important;
  width:100%!important;max-width:100%!important;min-width:0!important;
  margin-left:auto!important;margin-right:auto!important;text-align:center!important;
  gap:8px!important;flex-wrap:wrap!important;white-space:normal!important;
 }
 body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) .nic-footer-cookie-pair .footer-version,
 body:not(.nic-admin) :is(.footer-note,.nic-shared-footer,.public-footer) .nic-footer-cookie-pair #nicConsentSettings{
  text-align:center!important;margin:0!important;
 }
}
""")


# Renovation proposal actions occupy their own right-aligned row; totals stay below.
rules.append("""
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .reno-head{
 display:flex!important;flex-direction:column!important;align-items:stretch!important;
 gap:10px!important;min-width:0!important;
}
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .reno-head .reno-head-actions{
 display:flex!important;flex-direction:column!important;align-items:flex-end!important;
 flex:0 0 auto!important;gap:0!important;width:100%!important;max-width:100%!important;
 min-width:0!important;box-sizing:border-box!important;
}
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .reno-head .reno-head-actions .nic-reno-action-row{
 display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;
 justify-content:center!important;align-items:center!important;
 width:48%!important;max-width:100%!important;min-width:0!important;
 margin-left:auto!important;margin-right:auto!important;box-sizing:border-box!important;
}
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .reno-head .reno-head-actions :is(#renoSuggestionTotal,#rentRenoSheetTotal,.suggestion-total){
 display:block!important;flex:none!important;width:100%!important;max-width:100%!important;
 box-sizing:border-box!important;margin:8px 0 0!important;text-align:center!important;
}
@media(max-width:650px){
 body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .reno-head .reno-head-actions .nic-reno-action-row{
  width:100%!important;
 }
}
""")


# Shared renovation-list typography follows the two admin text scales.
rules.append("""
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .trade-name,
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) .trade-name *{
 font-size:var(--nic-subtext-font-size,14px)!important;line-height:1.5!important;
}
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) :is(.trade-basis,.trade-auto,.trade-section-label,.reno-note,.reno-head .sub,.trade-row .unit),
body:not(.nic-admin) :is(#renoBackdrop,#rentRenoPanel) :is(.trade-basis,.trade-auto,.trade-section-label,.reno-note,.reno-head .sub) *,
body:not(.nic-admin) #renoBackdrop :is(#renoSuggestionTotal,.reno-suggestion-total,.nic-reno-proposal-total),
body:not(.nic-admin) #rentRenoPanel #rentRenoSheetTotal.nic-rental-proposal-total{
 font-size:var(--nic-hint-font-size,12px)!important;line-height:1.5!important;
}
""")

# Input units follow the admin hint-text scale. The Haushaltsbudget transfer
# summary uses plain text values, not input unit spans, so remains unchanged.
rules.append("""
body:not(.nic-admin) .input-wrap .unit{
 font-size:var(--nic-hint-font-size,12px)!important;
}
""")

# Field helper copy stays below its control and left aligned.
rules.append("""
body:not(.nic-admin) .field-hint-below{
 display:block!important;box-sizing:border-box!important;min-width:0!important;
 width:100%!important;text-align:left!important;margin:4px 0 0!important;
 float:none!important;
}
""")

# All subtitles and helper copy beneath section headings follow the admin body-text scale.
rules.append("""
body:not(.nic-admin) .sub,
body:not(.nic-admin) .section-summary-subtitle{
 font-size:var(--nic-body-font-size,16px)!important;
}
""")

# This financing section title follows the configurable base text size.
rules.append("""
body:not(.nic-admin) #ownAdditionalFinance h3.nic-body-font-text,
body:not(.nic-admin) #ownAdditionalFinance h3.nic-body-font-text *,
body:not(.nic-admin) .nic-body-font-text,
body:not(.nic-admin) .nic-body-font-text *{
 font-size:var(--nic-body-font-size,16px)!important;
}
""")

# Mobile: rates, financing choices, then the full-width acquisition total.
rules.append("""
@media(max-width:700px){
 body:not(.nic-admin) .nic-finance-mobile-fields{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px 12px!important;min-width:0!important;max-width:100%!important;
 }
 body:not(.nic-admin) .nic-finance-mobile-fields>.finance-rate-grid,
 body:not(.nic-admin) .nic-finance-mobile-fields>.quick-grid,
 body:not(.nic-admin) .nic-finance-mobile-fields>.quick-grid>.finance-acq-row{display:contents!important}
 body:not(.nic-admin) .nic-finance-mobile-fields .field{grid-column:auto!important;min-width:0!important;order:6}
 body:not(.nic-admin) .nic-finance-mobile-fields .field:has(:is(#interest,#rentInterest)){order:1}
 body:not(.nic-admin) .nic-finance-mobile-fields .field:has(:is(#repayment,#rentRepayment)){order:2}
 body:not(.nic-admin) .nic-finance-mobile-fields .field:has(:is(#ltv,#rentLtv)){order:3}
 body:not(.nic-admin) .nic-finance-mobile-fields .finance-acq-option{order:4}
 body:not(.nic-admin) .nic-finance-mobile-fields .finance-acq-total{order:5;grid-column:1 / -1!important}
}
""")


# Eigennutzung financing responsive layout mirrors the desktop field groups.
# Keep the 3-rate row, full-width duration, paired purchase fees, and acquisition row.
rules.append("""
@media (min-width:701px) and (max-width:1000px){
 body:not(.nic-admin) #ownFinanceCard .nic-finance-mobile-fields{
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;
  gap:14px!important;min-width:0!important;max-width:100%!important;
 }
 body:not(.nic-admin) #ownFinanceCard .nic-finance-mobile-fields>.finance-rate-grid{
  display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:10px!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #ownFinanceCard .nic-finance-mobile-fields>.quick-grid{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:14px 10px!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-rate-grid .field:has(#ltv){
  grid-column:auto!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-duration-swap-v8403{
  grid-column:1/-1!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-acq-row{
  display:grid!important;grid-template-columns:minmax(0,2fr) minmax(0,1fr)!important;
  gap:10px!important;align-items:end!important;grid-column:1/-1!important;order:7!important;min-width:0!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-acq-total{grid-column:1!important}
 body:not(.nic-admin) #ownFinanceCard .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) #ownFinanceCard .sale-cost-grid{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:14px 10px!important;min-width:0!important;
 }
 body:not(.nic-admin) #ownFinanceCard .field,
 body:not(.nic-admin) #ownFinanceCard .finance-acq-row>*{
  min-width:0!important;max-width:100%!important;box-sizing:border-box!important;
 }
}
@media(max-width:700px){
 body:not(.nic-admin) #ownFinanceCard .nic-finance-mobile-fields{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px 12px!important;min-width:0!important;max-width:100%!important;
 }
 body:not(.nic-admin) #ownFinanceCard .nic-finance-mobile-fields>.finance-rate-grid,
 body:not(.nic-admin) #ownFinanceCard .nic-finance-mobile-fields>.quick-grid{
  display:contents!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-rate-grid .field:has(#ltv){
  grid-column:1/-1!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-duration-swap-v8403{
  grid-column:1/-1!important;order:4!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-acq-row{
  display:grid!important;grid-template-columns:minmax(0,2fr) minmax(0,1fr)!important;
  gap:10px!important;align-items:start!important;grid-column:1/-1!important;order:7!important;min-width:0!important;
 }
 body:not(.nic-admin) #ownFinanceCard .finance-acq-total{grid-column:1!important}
 body:not(.nic-admin) #ownFinanceCard .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) #ownFinanceCard .finance-acq-row>.finance-acq-total,
 body:not(.nic-admin) #ownFinanceCard .finance-acq-row>.finance-acq-option{
  order:0!important;grid-row:1!important;
 }
 body:not(.nic-admin) #ownFinanceCard .sale-cost-grid{
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;
  gap:14px!important;min-width:0!important;
 }
 body:not(.nic-admin) #ownFinanceCard .sale-cost-grid .field{
  grid-column:1/-1!important;width:100%!important;max-width:100%!important;
 }
 body:not(.nic-admin) #ownFinanceCard .field,
 body:not(.nic-admin) #ownFinanceCard .finance-acq-row>*{
  min-width:0!important;max-width:100%!important;box-sizing:border-box!important;
 }
}
""")

# Vermietung financing follows the desktop order across tablet and mobile.
rules.append("""
@media (min-width:701px) and (max-width:1000px){
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields{
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;
  gap:14px!important;min-width:0!important;max-width:100%!important;
 }
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.finance-rate-grid{
  display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
  gap:10px!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .finance-rate-grid .field:has(#rentLtv){
  grid-column:auto!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.quick-grid:not(#rentFinancingControls){
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:14px 10px!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.field:has(#rentMonths){
  grid-column:1/-1!important;
 }
 body:not(.nic-admin) #rentFinanceCard #rentFinancingControls{
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;
  gap:10px!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .finance-acq-row{
  display:grid!important;grid-template-columns:minmax(0,2fr) minmax(0,1fr)!important;
  gap:10px!important;align-items:start!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .finance-acq-total{grid-column:1!important}
 body:not(.nic-admin) #rentFinanceCard .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) #rentFinanceCard #rentFinancingControls .finance-acq-row>.finance-acq-total,
 body:not(.nic-admin) #rentFinanceCard #rentFinancingControls .finance-acq-row>.finance-acq-option{
  order:0!important;grid-row:1!important;
 }
 body:not(.nic-admin) #rentFinanceCard .field,
 body:not(.nic-admin) #rentFinanceCard .finance-acq-row>*{
  min-width:0!important;max-width:100%!important;box-sizing:border-box!important;
 }
}
@media(max-width:700px){
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px 12px!important;min-width:0!important;max-width:100%!important;
 }
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.finance-rate-grid,
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.quick-grid:not(#rentFinancingControls){
  display:contents!important;
 }
 body:not(.nic-admin) #rentFinanceCard .finance-rate-grid .field:has(#rentLtv),
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.field:has(#rentMonths){
  grid-column:1/-1!important;order:4!important;
 }
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.quick-grid:not(#rentFinancingControls) .field:has(#rentNotary){
  order:5!important;
 }
 body:not(.nic-admin) #rentFinanceCard .nic-finance-mobile-fields>.quick-grid:not(#rentFinancingControls) .field:has(#rentBroker){
  order:6!important;
 }
 body:not(.nic-admin) #rentFinanceCard #rentFinancingControls{
  display:grid!important;grid-template-columns:minmax(0,1fr)!important;
  gap:10px!important;grid-column:1/-1!important;order:7!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .finance-acq-row{
  display:grid!important;grid-template-columns:minmax(0,2fr) minmax(0,1fr)!important;
  gap:10px!important;align-items:start!important;grid-column:1/-1!important;min-width:0!important;
 }
 body:not(.nic-admin) #rentFinanceCard .finance-acq-total{grid-column:1!important}
 body:not(.nic-admin) #rentFinanceCard .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) #rentFinanceCard #rentFinancingControls .finance-acq-row>.finance-acq-total,
 body:not(.nic-admin) #rentFinanceCard #rentFinancingControls .finance-acq-row>.finance-acq-option{
  order:0!important;grid-row:1!important;
 }
 body:not(.nic-admin) #rentFinanceCard .field,
 body:not(.nic-admin) #rentFinanceCard .finance-acq-row>*{
  min-width:0!important;max-width:100%!important;box-sizing:border-box!important;
 }
}
""")

# Both sale fields occupy separate full-width rows on phones, including landscape.
rules.append("""
@media(max-width:700px), (max-width:1000px) and (max-height:600px) and (orientation:landscape){
 body:not(.nic-admin) .sale-cost-grid .field:has(:is(#sellBroker,#otherSaleCosts)){
  grid-column:1 / -1!important;min-width:0!important;
  width:100%!important;max-width:100%!important;box-sizing:border-box;
 }
}
""")

# Acquisition cost and financing checkbox share a row. Match the amount field
# to one rate column; let the checkbox area use the remaining columns.
rules.append("""
body:not(.nic-admin) .finance-acq-row{
 display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
 gap:10px!important;align-items:start!important;
}
body:not(.nic-admin) .finance-acq-total{grid-column:1!important}
body:not(.nic-admin) .finance-acq-option{grid-column:2/-1!important}
body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-row{
 grid-template-columns:repeat(3,minmax(0,1fr))!important;align-items:start!important;
}
body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-total{grid-column:1!important}
body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-option{grid-column:2/-1!important}
body:not(.nic-admin) #finance-acq-row-swap-v8403{
 grid-template-columns:repeat(3,minmax(0,1fr))!important;align-items:start!important;
}
body:not(.nic-admin) #finance-acq-row-swap-v8403 .finance-acq-total{grid-column:1!important}
body:not(.nic-admin) #finance-acq-row-swap-v8403 .finance-acq-option{grid-column:2/-1!important}
@media(max-width:700px){
 body:not(.nic-admin) .finance-acq-row{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important;
 }
 body:not(.nic-admin) .finance-acq-total{grid-column:1!important}
 body:not(.nic-admin) .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-row{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
 }
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard) .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) #finance-acq-row-swap-v8403{
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
 }
 body:not(.nic-admin) #finance-acq-row-swap-v8403 .finance-acq-option{grid-column:2!important}
 body:not(.nic-admin) .finance-acq-row>.finance-acq-total,
 body:not(.nic-admin) .finance-acq-row>.finance-acq-option{
  order:0!important;grid-row:1!important;
 }
}
""")



# Fix & Flip phone layout: financed share fills its row, and purchase costs sit
# beside the co-financing checkbox at the same width as one interest field.
rules.append("""
@media(max-width:700px){
 body:not(.nic-admin) #flipFinanceCard .nic-finance-mobile-fields .finance-rate-grid .field:has(#ltv){
  grid-column:1 / -1!important;order:3!important;width:100%!important;
  max-width:100%!important;min-width:0!important;box-sizing:border-box!important;
 }
 body:not(.nic-admin) #flipFinanceCard .finance-acq-row{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;align-items:start!important;grid-column:1/-1!important;
  width:100%!important;max-width:100%!important;min-width:0!important;
  box-sizing:border-box!important;
 }
 body:not(.nic-admin) #flipFinanceCard .finance-acq-total{
  grid-column:1!important;order:0!important;grid-row:1!important;
 }
 body:not(.nic-admin) #flipFinanceCard .finance-acq-option{
  grid-column:2!important;order:0!important;grid-row:1!important;
 }
}
""")
if not any(" #flipFinanceCard .nic-finance-mobile-fields .finance-rate-grid .field:has(#ltv)" in rule for rule in rules):
 raise SystemExit("Fix & Flip financed full-width mobile rule missing")
if not any(" #flipFinanceCard .finance-acq-total" in rule and "grid-template-columns:repeat(2,minmax(0,1fr))!important" in rule for rule in rules):
 raise SystemExit("Fix & Flip acquisition-cost/checkbox mobile row missing")


# Eigennutzung has no sale-cost inputs; the shared fields remain available in Fix & Flip.
rules.append("""
body:not(.nic-admin) #ownFinanceCard .field:has(#sellBroker),
body:not(.nic-admin) #ownFinanceCard .field:has(#otherSaleCosts){
 display:none!important;
}
""")
if not any("#ownFinanceCard .field:has(#sellBroker)" in rule and "#ownFinanceCard .field:has(#otherSaleCosts)" in rule for rule in rules):
 raise SystemExit("Eigennutzung sale-cost field visibility rule missing")


# On tablets, acquisition costs match the two-column purchase-fee field width.
rules.append("""
@media (min-width:701px) and (max-width:1000px){
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-row{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;align-items:start!important;grid-column:1/-1!important;
  width:100%!important;max-width:100%!important;min-width:0!important;
  box-sizing:border-box!important;
 }
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-total{
  grid-column:1!important;
 }
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-option{
  grid-column:2!important;
 }
}
""")
if not any("@media (min-width:701px) and (max-width:1000px)" in rule and
           ":is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-row" in rule and
           "grid-template-columns:repeat(2,minmax(0,1fr))!important" in rule
           for rule in rules):
 raise SystemExit("Tablet acquisition-cost width rule is missing")


# Desktop acquisition costs use the same half-row width as Notar + Grundbuch.
rules.append("""
@media (min-width:1001px){
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-row{
  display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:10px!important;align-items:start!important;grid-column:1/-1!important;
  width:100%!important;max-width:100%!important;min-width:0!important;
  box-sizing:border-box!important;
 }
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-total{
  grid-column:1!important;
 }
 body:not(.nic-admin) :is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-option{
  grid-column:2!important;
 }
}
""")
if not any("@media (min-width:1001px)" in rule and
           ":is(#ownFinanceCard,#rentFinanceCard,#flipFinanceCard) .finance-acq-row" in rule and
           "grid-template-columns:repeat(2,minmax(0,1fr))!important" in rule
           for rule in rules):
 raise SystemExit("Desktop acquisition-cost width rule is missing")

(site/'calculator-shell.css').write_text('/* Authoritative shell cascade for all five calculators. */\n'+'\n'.join(rules)+'\nbody:not(.nic-embed) .deal-type-row{grid-auto-rows:1fr!important;align-items:stretch!important}\nbody:not(.nic-embed) .deal-type-row>.deal-type-option{height:100%!important;min-height:78px!important}\n')
print('Central calculator-shell.css:',len(rules),'shared rules; removed competing declarations')

# Keep content pages on the shared shell while hiding the calculator-only hero.
# This final inline override is added after the shared calculator CSS is consolidated.
content_pages={'settlement','prices','why','about','contact','login'}
for page in site.rglob('*.html'):
 source=page.read_text()
 match=re.search(r'<html\b[^>]*data-nic-page="([^"]+)"',source)
 if not match or match.group(1) not in content_pages:
  continue
 key=match.group(1)
 style=(
  '<style id="nic-content-page-layout">'
  'html[data-nic-page="'+key+'"] body{margin:0;min-height:100vh}'
  'html[data-nic-page="'+key+'"] body .app{min-height:100vh!important;display:flex!important;flex-direction:column!important}'
  'html[data-nic-page="'+key+'"] body .app .hero{display:none!important}'
  'html[data-nic-page="'+key+'"] body .app main.nic-content-main{display:flex!important;flex-direction:column!important;flex:1 0 auto!important;width:100%;max-width:1180px;box-sizing:border-box;margin:0 auto;padding:32px 20px 16px}'
  'html[data-nic-page="'+key+'"] body .app .nic-content-card{flex:1 0 auto!important;width:100%;max-width:980px;box-sizing:border-box;margin:0 auto;padding:32px;border:1px solid #e2e9e5;border-radius:16px;background:#fff}'
  '@media(max-width:760px){html[data-nic-page="'+key+'"] body .app main.nic-content-main{padding:24px 16px 16px}html[data-nic-page="'+key+'"] body .app .nic-content-card{padding:24px 18px}}'
  '</style>'
 )
 if 'id="nic-content-page-layout"' not in source:
  if '</head>' not in source:
   raise SystemExit('Content page head missing: '+str(page))
  source=source.replace('</head>',style+'</head>',1)
 page.write_text(source)

