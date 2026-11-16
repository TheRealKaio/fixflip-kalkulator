"""Fast build contract for the shared Immobilien ABC view."""
from pathlib import Path
import json
import re
import subprocess
import sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
entries=json.loads((site/'immobilien-abc.json').read_text())
assert len(entries)>=120
assert len({e['id'] for e in entries})==len(entries)
assert all(e['term'] and e['explanation'] and e['category'] for e in entries)
original=json.loads(Path('assets/immobilien-abc.json').read_text())
assert len(original)==120
assert {e['id'] for e in original}.issubset({e['id'] for e in entries})
contexts=json.loads((site/'immobilien-abc-context.json').read_text())
audit=json.loads((site/'immobilien-abc-legacy-audit.json').read_text())
assert len(contexts)>=14
assert audit['fullRentalSheets']==9 and audit['totalInfoButtons']>=9
assert all(all(c.get(k) for k in ('term','body','source')) for c in contexts)
assert sum(bool(c.get('plain')) and bool(c.get('know')) for c in contexts)==9
assert all(any(e['term']==c['term'] for e in entries) for c in contexts)
nav=(site/'calculator-navigation.js').read_text()
assert "immobilien-abc':'/immobilien-abc/" in nav
assert "['/immobilien-abc/','Immobilien ABC']" in nav
assert "['/nebenkostenabrechnung/','Mieterabrechnung']" not in nav
assert "window.NICABC?.render(panel)" in nav
assert (site/'immobilien-abc/index.html').exists()
for path in ('index.html','preise/index.html','immobilien-abc/index.html','finanzierungsrechner/index.html'):
    markup=(site/path).read_text()
    assert '/immobilien-abc.css' in markup and '/immobilien-abc.js' in markup, path
    assert 'nic-header-variants' in markup, path
for file in ('calculator-navigation.js','immobilien-abc.js','admin-immobilien-abc.js','admin.js'):
    subprocess.run(['node','--check',str(site/file)],check=True)

admin=(site/'admin.html').read_text()
assert 'tab-immobilien-abc' in admin and 'panel-immobilien-abc' in admin
assert 'admin-immobilien-abc' in admin
assert 'abcAdminRows' in admin and 'abcAdd' in admin
settings=(site/'site-settings.js').read_text()
assert 'immobilienABC' in settings
assert 'Immobilien ABC' in (site/'immobilien-abc/index.html').read_text()
print(f'Immobilien ABC contract: {len(entries)} terms, {len(contexts)} rich rental sheets, original 120 retained, shared shell and JS syntax OK')
