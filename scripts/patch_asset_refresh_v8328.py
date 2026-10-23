from pathlib import Path
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html').parent
admin=site/'admin.html'
admin.write_text(admin.read_text().replace('V8.327','V8.328'))
print('V8.328 release marker prepared for asset refresh')
