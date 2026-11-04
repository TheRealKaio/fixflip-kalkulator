"""Conservative CSS cleanup: remove empty rules and earlier byte-identical rules.

Only ordinary style rules are deduplicated, within the same conditional context.
Order, declarations, specificity, fallback values and named layers are retained.
"""
import re
TOKEN=re.compile(r'/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{};]')
COMMENTS=re.compile(r'/\*[\s\S]*?\*/')

def declarations(body):
 # Preserve value bytes, fallbacks and priority; split only outside functions/strings.
 tokens=re.compile(r'/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[()\[\]{};]')
 result=[];start=depth=0
 for match in tokens.finditer(body):
  token=match.group()
  if token in ('{','}'):return None  # Native nested rules need a separate analysis.
  if token in ('(','['):depth+=1
  elif token in (')',']'):depth-=1
  elif token==';' and depth==0:
   part=body[start:match.start()].strip()
   if part:result.append(part)
   start=match.end()
 part=body[start:].strip()
 if part:result.append(part)
 return result if result and all(':' in value for value in result) else None

def fixed_value(prop,value):
 if prop=='font-weight':
  return value in {'normal','bold'} or bool(re.fullmatch(r'\d+(?:\.\d+)?',value)) and 1<=float(value)<=1000
 if prop=='line-height' and value=='normal':return True
 if prop in {'gap','row-gap','column-gap'} and value=='normal':return True
 match=re.fullmatch(r'(-?\d+(?:\.\d+)?)(px|rem|em|%)?',value)
 if not match:return False
 number=float(match[1]);unit=match[2]
 if number<0 and not prop.startswith('margin-'):return False
 return bool(unit) or number==0 or prop=='line-height'

def clean(css, contexts=None, context=()):
 if contexts is None:contexts={}
 chunks=[];start=0;depth=0;opening=None;stats={'empty':0,'duplicate':0,'overridden':0}
 for m in TOKEN.finditer(css):
  token=m.group()
  if token=='{':
   if depth==0:opening=m.start()
   depth+=1
  elif token=='}':
   depth-=1
   if depth<0:raise ValueError('Unbalanced CSS')
   if depth==0:
    chunks.append([css[start:m.end()],opening-start]);start=m.end()
  elif token==';' and depth==0:
   chunks.append([css[start:m.end()],None]);start=m.end()
 if depth:raise ValueError('Unbalanced CSS')
 tail=css[start:];seen=contexts.setdefault(context,set());covered=contexts.setdefault(context+('__declarations__',),set());out=[]
 for raw,op in reversed(chunks):
  if op is None:out.append(raw);continue
  head=raw[:op];plain=COMMENTS.sub('',head).strip();body=raw[op+1:-1]
  conditional=bool(re.match(r'^@(media|supports)\b',plain,re.I))
  ordinary=not plain.startswith('@')
  if conditional:
   body,inner=clean(body,contexts,context+(plain,))
   for k in stats:stats[k]+=inner[k]
   raw=head+'{'+body+'}'
  if (ordinary or conditional) and not COMMENTS.sub('',body).strip():
   stats['empty']+=1;continue
  if ordinary:
   # Remove superseded fixed numeric typography/spacing declarations only.
   # Complex values, shorthand relationships and browser fallbacks are preserved.
   parts=declarations(body)
   fixed=contexts.setdefault(context+('__fixed__',),set())
   retained=[]
   for declaration in reversed(parts or []):
    prop,_,value=declaration.partition(':');prop=prop.strip().lower();value=value.strip()
    important=bool(re.search(r'!important\s*$',value,re.I))
    plain_value=re.sub(r'\s*!important\s*$','',value,flags=re.I).strip()
    supported=prop in {'font-size','font-weight','line-height','margin-top','margin-right','margin-bottom','margin-left','padding-top','padding-right','padding-bottom','padding-left','border-radius','min-width','max-width','min-height','max-height','width','height','gap','row-gap','column-gap'} and fixed_value(prop,plain_value)
    token=(head.strip(),prop,important)
    if supported and (token in fixed or (not important and (head.strip(),prop,True) in fixed)):
     stats['overridden']+=1
    else:retained.append(declaration)
    if supported:fixed.add(token)
   if parts and len(retained)!=len(parts):
    if not retained:continue
    body=';'.join(reversed(retained))+';';raw=head+'{'+body+'}'
   # Compare exact selector and declaration bytes; never normalize CSS values.
   key=raw.strip()
   parts=declarations(body)
   pairs={(head.strip(),value) for value in parts} if parts else set()
   if key in seen or (pairs and pairs.issubset(covered)):stats['duplicate']+=1;continue
   seen.add(key);covered.update(pairs)
  out.append(raw)
 return ''.join(reversed(out))+tail,stats
