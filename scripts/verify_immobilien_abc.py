"""Fast build contract for the shared Immobilien ABC view."""
from pathlib import Path
import json
import re
import subprocess
import sys
site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
entries=json.loads((site/'immobilien-abc.json').read_text())
assert len(entries)==120
assert len({e['id'] for e in entries})==120
assert all(e['term'] and e['explanation'] and e['example'] and e['category'] for e in entries)
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
for file in ('calculator-navigation.js','immobilien-abc.js'):
    subprocess.run(['node','--check',str(site/file)],check=True)
print('Immobilien ABC contract: 120 entries, route, shared shell and JavaScript syntax OK')
