"""V8.389: update owner-use hero copy while preserving shared typography."""
from pathlib import Path
import json,re,sys
path=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
html=path.read_text(encoding="utf-8")
title="Kannst Du Dir Dein Eigenheim leisten?"
description="Berechne Kaufpreis, Kaufnebenkosten, Sanierung und Finanzierung für Dein Eigenheim. Prüfe die monatliche Belastung für ein Haus oder eine Eigentumswohnung zur Eigennutzung und finde heraus, ob Deine Wunschimmobilie zu Deinem Budget passt."
old_title='"Lohnt sich diese Eigentumswohnung?"'
count=html.count(old_title)
if count<1:raise SystemExit("Expected runtime owner-use heading")
html=html.replace(old_title,json.dumps(title,ensure_ascii=False))

old=': '+json.dumps("Du gibst ein, was du kaufst und sanierst. Die App übernimmt die Finanzmathematik und zeigt dir, wo das Risiko steckt.",ensure_ascii=False)+';'
new=': own ? '+json.dumps(description,ensure_ascii=False)+' '+old
if html.count(old)!=1:raise SystemExit("Expected one runtime hero description")
html=html.replace(old,new,1)
pattern=r'(<script type="application/json" id="nic-header-variants">)(.*?)(</script>)'
m=re.search(pattern,html,re.S)
if not m:raise SystemExit("Header variants missing")
variants=json.loads(m[2]);variants[2]=[title,description]
html=html[:m.start(2)]+json.dumps(variants,ensure_ascii=False).replace("<","\\u003c")+html[m.end(2):]
path.write_text(html,encoding="utf-8")
print("V8.389 owner-use title and description updated with unchanged typography")
