from pathlib import Path
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html').parent
script=(site/'statistics.js').read_text()
for token in ["title.textContent='Cookies zustimmen'", "['denied','Ablehnen']", "['granted','Zustimmen']", "b.textContent='Cookie-Hinweis'", 'mit Wirkung für die Zukunft']:
    if token not in script:
        raise SystemExit('Cookie notice verification failed: '+token)
admin=site/'admin.html'
admin.write_text(admin.read_text().replace('V8.326','V8.327'))
print('V8.327 friendly cookie notice labels and copy applied')
