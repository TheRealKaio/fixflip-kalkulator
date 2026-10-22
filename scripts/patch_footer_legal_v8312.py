from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(label+" anchor missing")
    s=s.replace(old,new,1)

old='''    <div class="footer-note">
      <span>Sanierungswerte sind editierbare Orientierungswerte für einen ersten Deal-Check. Der Deal Check ist eine Kalkulationshilfe und keine Steuer-, Rechts- oder Finanzierungsberatung. Steuern werden nicht individuell berechnet. Prüfe vor einem Kauf insbesondere Verkaufspreis, Sanierungsumfang und Finanzierung mit belastbaren Unterlagen.</span>
      <span class="footer-version">V8.311</span>
    </div>'''

new='''    <div class="footer-note">
      <span>Sanierungswerte sind editierbare Orientierungswerte für einen ersten Deal-Check. Der Deal Check ist eine Kalkulationshilfe und keine Steuer-, Rechts- oder Finanzierungsberatung. Steuern werden nicht individuell berechnet. Prüfe vor einem Kauf insbesondere Verkaufspreis, Sanierungsumfang und Finanzierung mit belastbaren Unterlagen.</span>
      <div class="footer-meta">
        <span class="footer-version">V8.312</span>
        <nav class="footer-legal-links" aria-label="Rechtliche Hinweise">
          <a href="#" data-legal-placeholder="impressum">Impressum</a>
          <span aria-hidden="true">·</span>
          <a href="#" data-legal-placeholder="agbs">AGBs</a>
          <span aria-hidden="true">·</span>
          <a href="#" data-legal-placeholder="datenschutz">Datenschutz</a>
        </nav>
      </div>
    </div>'''

rep(old,new,"footer markup")

old_css='''.footer-note{padding:0 18px;color:#7b8492;font-size:11px;line-height:1.45;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:end}
.footer-version{white-space:nowrap;text-align:right;font-weight:700;color:#7b8492}'''

new_css='''.footer-note{padding:0 18px;color:#7b8492;font-size:11px;line-height:1.45;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;align-items:end}
.footer-meta{display:flex;flex-direction:column;align-items:flex-end;justify-content:flex-end;gap:2px;text-align:right}
.footer-version{white-space:nowrap;text-align:right;font-weight:700;color:#7b8492}
.footer-legal-links{display:flex;align-items:center;justify-content:flex-end;gap:5px;white-space:nowrap;font-size:10px;line-height:1.3}
.footer-legal-links a{color:#7b8492;text-decoration:none;font-weight:400}
.footer-legal-links a:hover,.footer-legal-links a:focus{text-decoration:underline;color:#475569}'''

rep(old_css,new_css,"footer css")

s=s.replace("V8.311","V8.312")
s=s.replace("service-worker.js?v=8.311","service-worker.js?v=8.312")

required=[
  'class="footer-meta"',
  'class="footer-legal-links"',
  'data-legal-placeholder="impressum"',
  'data-legal-placeholder="agbs"',
  'data-legal-placeholder="datenschutz"',
  '>Impressum</a>',
  '>AGBs</a>',
  '>Datenschutz</a>',
  "V8.312",
  "service-worker.js?v=8.312"
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.312 missing: "+", ".join(missing))

p.write_text(s,encoding="utf-8")
print("V8.312 legal footer placeholders added")
