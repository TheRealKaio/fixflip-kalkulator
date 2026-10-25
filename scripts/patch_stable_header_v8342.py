from pathlib import Path
import json,re,shutil,sys
p=Path(sys.argv[1]);s=p.read_text()
m=re.search(r'innerHTML = budget \? "([^"]+)" : own \? "([^"]+)" : "([^"]+)"',s)
if not m:raise SystemExit('Calculator header variants missing')
budget='Ermittle aus Einkommen, Ausgaben, Eigenkapital und Finanzierung eine realistische Kaufpreis-Spanne.'
deal='Du gibst ein, was du kaufst und sanierst. Die App übernimmt die Finanzmathematik und zeigt dir, wo das Risiko steckt.'
rent=re.search(r'heroTitle.innerHTML="([^"]+)";',s)
variants=[[m[1],budget],[m[2],deal],[m[3],deal],[rent[1],'Prüfe Miete, laufende Kosten und Finanzierung. Der Rechner zeigt dir Cashflow, Renditen und die notwendige Break-even-Miete.'],['Admin-Bereich','Verwalte Unternehmensdaten, Layout, Logos, Social Media, Meta-Daten und Statistik.']]+[[name,'Rechtliche Informationen zu Neustart ImmoCheck'] for name in ['Impressum','Datenschutz','AGBs','Haftungsausschluss']]
s=s.replace('</head>','<script type="application/json" id="nic-header-variants">'+json.dumps(variants,ensure_ascii=False).replace('<','\\u003c')+'</script><link rel="stylesheet" href="stable-header.css"><script src="stable-header.js" defer></script></head>',1)
p.write_text(s)
for name in ['stable-header.css','stable-header.js']:
    shutil.copyfile(Path('assets')/name,p.parent/name)
checks=p.parent/'_checks';checks.mkdir(exist_ok=True)
shutil.copyfile('scripts/header_browser_check.html',checks/'header.html')
print('V8.342 common viewport-relative header height enabled for all views')
