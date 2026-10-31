"""Ship the opt-in STRATO client, without publishing PHP or private server files."""
from pathlib import Path
import re,shutil,sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
for name in ['user-access.js','backend-config.json']:
    shutil.copyfile(Path('assets')/name,site/name)
for page in site.rglob('*.html'):
    s=page.read_text()
    match=re.search(r'<script\b[^>]*\bsrc=[\"\'](?:/)?site-settings\.js[\"\'][^>]*></script>',s)
    if not match:continue
    s=s[:match.start()]+'<script src="/user-access.js" defer></script>'+s[match.start():]
    page.write_text(s)
print('Opt-in STRATO user access client installed. API remains disabled until server setup.')
