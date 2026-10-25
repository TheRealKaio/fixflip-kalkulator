from pathlib import Path
import shutil,sys
p=Path(sys.argv[1]);s=p.read_text()
# Supersede the old disclaimer overlay while keeping its full existing wording.
s=s.replace('  const $=id=>document.getElementById(id);\n  const disclaimerPage=$("legalDisclaimerPage");','  if(window.NIC_EMBEDDED_LEGAL)return;\n  const $=id=>document.getElementById(id);\n  const disclaimerPage=$("legalDisclaimerPage");',1)
s=s.replace('</head>','<script>window.NIC_EMBEDDED_LEGAL=true;</script><link rel="stylesheet" href="legal-views.css"><script src="legal-views.js" defer></script></head>',1)
p.write_text(s)
for name in ['legal-views.js','legal-views.css']:
    shutil.copyfile(Path('assets')/name,p.parent/name)
print('V8.341 configurable logo link and legal views below shared header enabled')
