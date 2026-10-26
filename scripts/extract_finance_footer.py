from pathlib import Path
import re
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
html=(site/'index.html').read_text(encoding='utf-8')
styles=re.findall(r'<style[^>]*>(.*?)</style>',html,re.S|re.I)
target=('.footer-note','.footer-meta','.footer-version','.footer-legal-links')
rules=[]
for style in styles:
    stack=[]
    pos=0
    for match in re.finditer(r'[{}]',style):
        chunk=style[pos:match.start()]
        if match.group()=='{':
            selector=chunk.strip()
            stack.append({'selector':selector,'start':match.end(),'children':False})
        elif stack:
            node=stack.pop()
            if not node['children'] and any(t in node['selector'] for t in target):
                media=[x['selector'] for x in stack if x['selector'].startswith('@media')]
                rule=node['selector']+'{'+style[node['start']:match.start()]+'}'
                for m in reversed(media):rule=m+'{'+rule+'}'
                rules.append(rule)
            if stack:stack[-1]['children']=True
        pos=match.end()
if not rules:
    raise SystemExit('Original footer CSS rules not found')
(site/'finance-shared-footer.css').write_text('\n'.join(rules),encoding='utf-8')
print('Original calculator footer rules copied:',len(rules))
