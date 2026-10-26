"""Publish one authoritative header stylesheet for all five calculator pages."""
from pathlib import Path
import re,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
TOKEN=re.compile(r'\.(?:hero(?:-top)?|brand-logo(?:-wrap)?|nic-account-link)(?![\w-])|#nicAccountLink(?![\w-])')
LEX=re.compile(r'/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]')
def selectors(s):
    out=[];start=depth=0
    for i,c in enumerate(s):
        if c in '([':depth+=1
        elif c in ')]':depth-=1
        elif c==',' and depth==0:out.append(s[start:i]);start=i+1
    out.append(s[start:]);return out
def split(css):
    stack=[];pos=0;edits=[];rules=[]
    for m in LEX.finditer(css):
        token=m.group()
        if token not in ['{','}']:continue
        if token=='{':
            if stack:stack[-1]['nested']=True
            stack.append(dict(start=pos,head=css[pos:m.start()],body=m.end(),nested=False))
        elif stack:
            n=stack.pop()
            if not n['nested'] and not n['head'].lstrip().startswith('@'):
                parts=selectors(n['head']);yes=[s for s in parts if TOKEN.search(s) and ':not(.hero)' not in s]
                if yes:
                    no=[s for s in parts if s not in yes];body=css[n['body']:m.start()]
                    rule=','.join(yes)+'{'+body+'}'
                    for parent in reversed(stack):rule=parent['head']+'{'+rule+'}'
                    rules.append(rule)
                    edits.append((n['start'],m.end(),','.join(no)+'{'+body+'}' if no else ''))
        pos=m.end()
    for a,b,value in reversed(edits):css=css[:a]+value+css[b:]
    return css,rules
original=(site/'index.html').read_text();common=[]
for block in re.findall(r'<style\b[^>]*>(.*?)</style>',original,re.S|re.I):common.extend(split(block)[1])
layout=site/'header-layout.css';rest,rules=split(layout.read_text());common.extend(rules);layout.write_text(rest)
common.append((site/'stable-header.css').read_text())
if len(common)<8:raise SystemExit('Shared header rules missing')
(site/'calculator-header.css').write_text('/* Shared by Budget, Eigennutzung, Vermietung, Fix und Flip and Finanzierung. */\n'+'\n'.join(common)+'\n')
# Keep only non-header shell declarations in the legacy finance bundle.
legacy=site/'finance-shared-header.css';legacy.write_text(split(legacy.read_text())[0])
for page in site.rglob('*.html'):
    html=page.read_text()
    html=re.sub(r'(<style\b[^>]*>)(.*?)(</style>)',lambda m:m[1]+split(m[2])[0]+m[3],html,flags=re.S|re.I)
    html=html.replace('href="stable-header.css"','href="/calculator-header.css"').replace('href="/stable-header.css"','href="/calculator-header.css"')
    page.write_text(html)
for name in ['budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner']:
    html=(site/name/'index.html').read_text()
    if html.count('href="/calculator-header.css"')!=1:raise SystemExit('Shared header stylesheet missing: '+name)
    if any(split(css)[1] for css in re.findall(r'<style\b[^>]*>(.*?)</style>',html,re.S|re.I)):raise SystemExit('Inline header override: '+name)
print('All five calculators use calculator-header.css; inline and finance header copies removed')
