from pathlib import Path
import re
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/index.html")
s = p.read_text(encoding="utf-8")

footer = re.compile(
    r'(<div class="footer-note">\s*<span>.*?</span>)'
    r'(?:\s*<span class="footer-version">.*?</span>)?\s*</div>',
    re.S,
)
match = footer.search(s)
if not match:
    raise SystemExit("Footer markup anchor missing")

legal = '''\n      <div class="footer-meta">
        <nav class="footer-legal-links" aria-label="Rechtliche Hinweise">
          <a href="#" data-legal-placeholder="impressum">Impressum</a>
          <span aria-hidden="true">·</span>
          <a href="#" data-legal-placeholder="agbs">AGBs</a>
          <span aria-hidden="true">·</span>
          <a href="#" data-legal-placeholder="datenschutz">Datenschutz</a>
        </nav>
      </div>'''
if 'class="footer-legal-links"' not in s:
    s = s[:match.start()] + match.group(1) + legal + '\n    </div>' + s[match.end():]

# Remove the retired version styling and keep the public legal links readable.
s = re.sub(r'\.footer-version\{[^}]*\}', '', s)
if ".footer-meta{" not in s:
    note = re.search(r'\.footer-note\{[^}]*\}', s)
    if not note:
        raise SystemExit("Footer CSS anchor missing")
    style = '''
.footer-meta{display:flex;flex-direction:column;align-items:flex-end;justify-content:flex-end;gap:2px;text-align:right}
.footer-legal-links{display:flex;align-items:center;justify-content:flex-end;gap:5px;white-space:nowrap;font-size:10px;line-height:1.3}
.footer-legal-links a{color:#7b8492;text-decoration:none;font-weight:400}
.footer-legal-links a:hover,.footer-legal-links a:focus{text-decoration:underline;color:#475569}'''
    s = s[:note.end()] + style + s[note.end():]

required = [
    'class="footer-meta"',
    'class="footer-legal-links"',
    'data-legal-placeholder="impressum"',
    'data-legal-placeholder="agbs"',
    'data-legal-placeholder="datenschutz"',
    '>Impressum</a>',
    '>AGBs</a>',
    '>Datenschutz</a>',
]
missing = [item for item in required if item not in s]
if missing:
    raise SystemExit("Footer legal links missing: " + ", ".join(missing))
if 'class="footer-version"' in s:
    raise SystemExit("Public footer version must be removed")

p.write_text(s, encoding="utf-8")
print("Legal footer links added without a public version number")
