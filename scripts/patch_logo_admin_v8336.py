"""Keep the shared calculator header when opening administration."""
from pathlib import Path
import shutil,sys
p=Path(sys.argv[1]);s=p.read_text()
s=s.replace('</head>','''<style id="nic-embedded-admin-style">
body.nic-admin-open .app > :not(.hero):not(#nicAdminPanel){display:none!important}
#nicAdminPanel[hidden]{display:none!important}
#nicAdminPanel{padding:16px 0 0;min-width:0}
#nicAdminFrame{display:block;width:100%;height:1000px;border:0;background:#f5f7fb}
.nic-admin-back{margin:0 12px 8px;padding:10px 14px;border:1px solid #cbd5e1;border-radius:10px;background:white;color:#172033;font:inherit;cursor:pointer}
</style></head>''',1)
p.write_text(s)
shutil.copyfile('neustart-immocheck-logo.svg',p.parent/'neustart-immocheck-logo.svg')
admin=p.parent/'admin.html';admin.write_text(admin.read_text().replace('id="adminVersion">V8.335','id="adminVersion">V8.336'))
print('V8.336 website logo and embedded admin integrated')
