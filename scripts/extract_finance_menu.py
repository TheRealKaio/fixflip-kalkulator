from pathlib import Path
import re, sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
html=(site/'index.html').read_text(encoding='utf-8')
blocks=re.findall(r'<style[^>]*>(.*?)</style>',html,re.S|re.I)
# Extract only original rule sets relevant to shared calculator selection cards.
selectors=('deal-type-row','deal-type-option','rent-tab-button','rent-radio-dot')
selected=[]
for block in blocks:
    if not any('.'+name in block for name in selectors):
        continue
    # Include original whole style block so @media and selector specificity survive.
    selected.append(block)
if not selected:
    raise SystemExit('Original calculator menu CSS missing')
(site/'finance-shared-menu.css').write_text('\n'.join(selected),encoding='utf-8')
print('Original shared calculator menu CSS blocks:',len(selected))
