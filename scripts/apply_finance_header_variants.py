from pathlib import Path
import json,re,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
original=(site/'index.html').read_text(encoding='utf-8')
finance=site/'finanzierungsrechner'/'index.html'
source=re.search(r'<script type="application/json" id="nic-header-variants">([^<]*)</script>',original)
if not source:raise SystemExit('Original responsive-header variants not found')
variants=json.loads(source.group(1))
finance_variant=['Finanzierungsrechner','Darlehen, Tilgung, Sondertilgung und Restschuld']
if finance_variant not in variants:variants.append(finance_variant)
target='<script type="application/json" id="nic-header-variants">[]</script>'
html=finance.read_text(encoding='utf-8')
if target not in html:raise SystemExit('Finance responsive-header placeholder missing')
html=html.replace(target,'<script type="application/json" id="nic-header-variants">'+json.dumps(variants,ensure_ascii=False).replace('<','\\u003c')+'</script>',1)
finance.write_text(html,encoding='utf-8')
print('Financing uses shared responsive header measurements:',len(variants),'variants')
