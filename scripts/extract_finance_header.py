from pathlib import Path
import re,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
html=(site/'index.html').read_text(encoding='utf-8')
styles=re.findall(r'<style[^>]*>(.*?)</style>',html,re.S|re.I)
tokens=('.hero','.hero-top','.brand-logo-wrap','.brand-logo','.nic-account-link','#nicAccountLink')
selected=[s for s in styles if any(token in s for token in tokens)]
if not selected:raise SystemExit('Original hero rules missing')
(site/'finance-shared-header.css').write_text('\n'.join(selected)+'\n',encoding='utf-8')
print('Shared hero CSS blocks:',len(selected))
