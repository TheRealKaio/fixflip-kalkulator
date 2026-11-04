"""Externalize static calculator style blocks, preserving their exact cascade positions.

Existing shared component styles stay authoritative. Runtime-managed styles stay inline.
Files are content-addressed because the same block is reused by several calculator routes.
"""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,sys

class Styles(HTMLParser):
 def __init__(self,source):
  super().__init__(convert_charrefs=False);self.source=source;self.lines=[0];self.blocks=[];self.start=None
  for m in re.finditer('\n',source):self.lines.append(m.end())
 def position_offset(self):
  line,col=self.getpos();return self.lines[line-1]+col
 def handle_starttag(self,tag,attrs):
  if tag=='style':self.start=(self.position_offset(),self.get_starttag_text(),dict(attrs))
 def handle_endtag(self,tag):
  if tag=='style' and self.start:
   a,opening,attrs=self.start;b=self.position_offset();self.blocks.append((a,b+8,opening,self.source[a+len(opening):b],attrs));self.start=None

def build(site):
 manifest={};counts={}
 for slug in ('','budget','eigennutzung','vermietung','fix-flip','finanzierungsrechner'):
  page=site/slug/'index.html';source=page.read_text();parser=Styles(source);parser.feed(source);edits=[]
  for a,b,opening,css,attrs in parser.blocks:
   # Config/runtime scripts may rewrite these by ID; keep their element contract.
   if (attrs.get('id') and source.count(attrs['id'])>1) or attrs.get('id','').startswith('nic-') or any(k in attrs for k in ('media','type','nonce','disabled')):continue
   if not css.strip() or '@import' in css or re.search(r'url\(\s*["\']?(?!data:|https?:|/|#)',css,re.I):continue
   ident=attrs.get('id','')
   group='shared'
   if ident.startswith('rental-'):group='rent'
   elif ident.startswith(('vk-','flip-')) or css.lstrip().startswith('.flip-section-card'):group='flip'
   elif css.lstrip().startswith(('.own-finance-','/* V8.404: nummerierte Eigennutzungs')):group='own'
   elif ident.startswith('budget-'):group='budget'
   digest=hashlib.sha256(css.encode()).hexdigest()[:16]
   name=f'calculator-{group}-{digest}.css';(site/name).write_text(css)
   # Keep IDs available to DOM queries without creating a second style authority.
   id_attr=' id="'+ident+'"' if ident else ''
   edits.append((a,b,f'<link rel="stylesheet"{id_attr} href="/{name}">'))
   manifest.setdefault(group,{})[name]=digest
  for a,b,replacement in reversed(edits):source=source[:a]+replacement+source[b:]
  page.write_text(source);counts[slug or '/']=len(edits)
 (site/'calculator-styles.json').write_text(json.dumps({'groups':manifest,'pages':counts},indent=2)+'\n')
 print('Calculator CSS externalized without reordering:',counts)

if __name__=='__main__':build(Path(sys.argv[1] if len(sys.argv)>1 else '_site'))
