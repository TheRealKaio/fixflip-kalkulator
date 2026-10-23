from pathlib import Path
import shutil
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
s=p.read_text(encoding='utf-8')
if 'id="nicAccountLink"' in s:
    raise SystemExit('Admin integration already applied')
anchor='<div class="hero-top"><div class="brand-logo-wrap">'
if s.count(anchor)!=1:
    raise SystemExit('Admin profile icon anchor missing')
s=s.replace(anchor,'''<div class="hero-top"><a class="nic-account-link" id="nicAccountLink" href="admin.html" aria-label="Profil und Verwaltung" title="Verwaltung"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 21v-2a7 7 0 0 1 14 0v2"/></svg></a><div class="brand-logo-wrap">''',1)
s=s.replace('if(localStorage.getItem(PREFIX+"active")==="1"){','if(localStorage.getItem(PREFIX+"active")==="1" && !["budget","own","flip"].includes(document.documentElement.dataset.nicPage)){',1)
s=s.replace('</head>','''<style id="nic-settings-integration">
.hero-top{position:relative}.nic-account-link{order:2;flex:0 0 36px;width:36px;height:36px;display:inline-flex;align-items:center;justify-content:center;border:1px solid #ffffff4d;border-radius:50%;color:white;background:#ffffff12;text-decoration:none}.nic-account-link:hover{background:#ffffff26}.nic-account-link:focus-visible{outline:3px solid #93c5fd;outline-offset:4px}.nic-social-links{display:flex;flex-wrap:wrap;gap:6px 15px;margin-top:10px}.nic-social-links[hidden]{display:none}.nic-social-links a{color:var(--muted);font-size:12px;text-decoration:underline;text-underline-offset:3px}.nic-social-links a:hover{color:var(--ink)}
</style>
<script src="site-settings.js" defer></script><script src="site-integration.js" defer></script>
</head>''',1)
p.write_text(s,encoding='utf-8')
for name in ['site-settings.js','site-settings.json','site-integration.js','admin.html','admin.css','admin.js','icon.svg']:
    shutil.copyfile(Path('assets')/name,p.parent/name)
print('V8.325 admin, profile link and settings assets integrated')

admin=p.parent/'admin.html'
admin.write_text(admin.read_text().replace('<span id="adminVersion"></span>','<span id="adminVersion">V8.325</span>'))
