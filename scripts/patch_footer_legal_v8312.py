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

legal = "<div class=\"nic-footer-layout\">\n      <div class=\"nic-footer-left\">\n        <details id=\"nicFooterSocial\" class=\"nic-footer-section nic-footer-social\" hidden>\n          <summary><h2>Folge uns</h2></summary>\n          <nav id=\"nicSocialLinks\" class=\"nic-social-links\" aria-label=\"Social Media\"></nav>\n        </details>\n      </div>\n      <div class=\"nic-footer-right\">\n        <details id=\"nicFooterAboutSection\" class=\"nic-footer-section nic-footer-about\" open hidden>\n          <summary><h2>Über uns</h2></summary>\n          <div id=\"nicFooterAbout\"></div>\n        </details>\n        <details id=\"nicFooterContactSection\" class=\"nic-footer-section nic-footer-contact\" open hidden>\n          <summary><h2>Kontakt</h2></summary>\n          <a id=\"nicFooterEmail\"></a>\n        </details>\n      </div>\n      <div class=\"footer-meta\">\n        <nav class=\"footer-legal-links\" aria-label=\"Rechtliche Hinweise\">\n          <a href=\"#\" data-legal-placeholder=\"impressum\">Impressum</a>\n          <span aria-hidden=\"true\">·</span>\n          <a href=\"#\" data-legal-placeholder=\"agbs\">AGBs</a>\n          <span aria-hidden=\"true\">·</span>\n          <a href=\"#\" data-legal-placeholder=\"datenschutz\">Datenschutz</a>\n        </nav>\n      </div>\n    </div>"
s = s[:match.start()] + match.group(1) + legal + '\n    </div>' + s[match.end():]

# Remove the retired version styling and keep the public legal links readable.
s = re.sub(r'\.footer-version\{[^}]*\}', '', s)
if ".footer-meta{" not in s:
    note = re.search(r'\.footer-note\{[^}]*\}', s)
    if not note:
        raise SystemExit("Footer CSS anchor missing")
    style = '''
.footer-meta{display:flex;align-items:flex-start;justify-content:flex-start;text-align:left}
.footer-legal-links{display:flex;align-items:center;justify-content:flex-start;gap:5px;white-space:normal;flex-wrap:wrap;font-size:10px;line-height:1.3}
.footer-legal-links a{color:inherit;text-decoration:none;font-weight:400}
.footer-legal-links a:hover,.footer-legal-links a:focus{text-decoration:underline}
.nic-footer-layout{display:grid;grid-template-columns:minmax(0,2fr) minmax(250px,1fr);gap:20px 24px;align-items:start}
.nic-footer-left{grid-column:1;grid-row:1;min-width:0}
.nic-footer-right{grid-column:2;grid-row:1;display:grid;gap:18px;min-width:0}
.nic-footer-social{max-width:50%}
.nic-footer-section{min-width:0}
.nic-footer-section summary{cursor:pointer;list-style:none}
.nic-footer-section summary::-webkit-details-marker{display:none}
.nic-footer-section summary h2{margin:0 0 8px;font-size:18px;line-height:1.25;color:inherit}
.nic-footer-section>div,.nic-footer-section>a{display:block;overflow-wrap:anywhere}
.nic-footer-section p{margin:0 0 8px}
.nic-footer-section p:last-child{margin-bottom:0}
.nic-social-links{display:flex;flex-wrap:wrap;gap:6px 12px;margin-top:8px}
.nic-footer-layout .footer-meta{grid-column:1/-1;grid-row:2}
@media(max-width:700px){
 .nic-footer-layout{grid-template-columns:minmax(0,1fr);gap:10px}
 .nic-footer-left,.nic-footer-right{grid-column:1;grid-row:auto}
 .nic-footer-right{gap:10px}
 .nic-footer-social{max-width:none}
 .nic-footer-section{width:100%}
 .nic-footer-section>summary{display:flex;align-items:center;justify-content:space-between;width:100%;box-sizing:border-box;padding:12px 14px;border:1px solid rgba(255,255,255,.35);border-radius:10px;background:rgba(255,255,255,.08)}
 .nic-footer-section>summary h2{margin:0;font-size:16px}
 .nic-footer-section>summary::after{content:"+";font-size:18px!important;line-height:1!important;height:20px!important;max-height:20px!important;overflow:hidden;align-self:center;flex:0 0 20px;display:flex;align-items:center;justify-content:center;box-sizing:border-box}
 .nic-footer-section[open]>summary::after{content:"−"}
 .nic-footer-section[open]>:not(summary){padding:12px 14px 8px}
 .nic-footer-layout .footer-meta{grid-column:1;grid-row:auto;justify-content:center;text-align:center}
 .nic-footer-layout .footer-legal-links{justify-content:center}
}'''
    s = s[:note.end()] + style + s[note.end():]

# Override legacy footer alignment rules emitted by earlier page builds.
# Desktop legal links sit on the left; mobile legal links stay centered.
s += '''\n<style>\n.nic-footer-layout .footer-meta{justify-content:flex-start!important;text-align:left!important}\n.nic-footer-layout .footer-meta .footer-legal-links{justify-content:flex-start!important;margin-left:0!important;margin-right:auto!important}\n.nic-social-links{display:flex;align-items:center;gap:12px}.nic-social-link{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;flex:0 0 40px;color:inherit;text-decoration:none;line-height:1}.nic-social-link svg{display:block;width:40px;height:40px;flex:none;fill:currentColor}.nic-social-link:focus-visible{outline:2px solid currentColor;outline-offset:3px}\n.nic-footer-section summary::after{display:none!important}\n.nic-footer-section summary::marker{content:""}\n.nic-footer-section summary::-webkit-details-marker{display:none}\n@media(max-width:700px){.nic-footer-layout .footer-meta{justify-content:center!important;text-align:center!important}.nic-footer-layout .footer-meta .footer-legal-links{justify-content:center!important;margin-left:auto!important;margin-right:auto!important}.nic-footer-section>summary::after{display:flex!important;font-size:18px!important;line-height:1!important;height:20px!important;max-height:20px!important;overflow:hidden;align-self:center;flex:0 0 20px;align-items:center;justify-content:center;box-sizing:border-box}}\n</style>\n'''

# Keep the historical build contract moving without rendering a public footer version.
s = re.sub(r'V8\.31[123]', 'V8.312', s)
s = re.sub(r'service-worker\.js\?v=8\.31[123]', 'service-worker.js?v=8.312', s)

required = [
    'class="nic-footer-layout"',
    'nic-footer-section nic-footer-social',
    'id="nicFooterAbout"',
    'id="nicFooterEmail"',
    'class="footer-meta"',
    'class="footer-legal-links"',
    'data-legal-placeholder="impressum"',
    'data-legal-placeholder="agbs"',
    'data-legal-placeholder="datenschutz"',
    "V8.312",
    "service-worker.js?v=8.312",
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
