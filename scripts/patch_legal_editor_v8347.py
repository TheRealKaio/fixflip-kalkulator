from pathlib import Path
import json,re,sys
p=Path(sys.argv[1]);s=p.read_text()
m=re.search(r'(<script type="application/json" id="nic-header-variants">)(.*?)(</script>)',s,re.S)
if not m:raise SystemExit('Header variants missing')
variants=json.loads(m[2]);variants.append(['Cookie-Hinweis','Rechtliche Informationen zu Neustart ImmoCheck'])
s=s[:m.start(2)]+json.dumps(variants,ensure_ascii=False).replace('<','\\u003c')+s[m.end(2):]
p.write_text(s)
print('V8.347 legal HTML editor, operator placeholders and JSON publication enabled')
