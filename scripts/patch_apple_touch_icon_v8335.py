"""Release marker: independent Apple Touch Icon uploads and PNG default.
The actual icon integration is performed by build_settings_pages.py.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])
if not p.is_file():
    raise SystemExit('Generated index missing')
admin=p.parent/'admin.html'
admin.write_text(admin.read_text().replace('id="adminVersion">V8.325', 'id="adminVersion">V8.335'))
print('V8.335 Apple Touch Icon settings enabled')
