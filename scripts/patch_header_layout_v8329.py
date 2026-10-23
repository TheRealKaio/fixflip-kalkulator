from pathlib import Path
import shutil
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
s=p.read_text()
if 'header-layout.css' in s:
    raise SystemExit('Header layout already applied')
s=s.replace('</head>','<link rel="stylesheet" href="header-layout.css">\n</head>',1)
p.write_text(s)
shutil.copyfile('assets/header-layout.css',p.parent/'header-layout.css')
admin=p.parent/'admin.html'
admin.write_text(admin.read_text().replace('V8.328','V8.329'))
print('V8.329 responsive full-width header descriptions applied')
