"""Presentation-only pass after route creation; calculator scripts stay untouched."""
from pathlib import Path
import re
import sys
def run(site):
    for page in Path(site).rglob('*.html'):
        source=page.read_text()
        scripts=re.findall(r"<script\b[^>]*>.*?</script>",source,flags=re.S)
        source=re.sub(r'<svg class="brand-logo".*?</svg>|<img class="brand-logo"[^>]*>',r'<img class="brand-logo" src="/header-logo.png" width="920" height="307" alt="Neustart ImmoCheck – Haus mit vier Fenstern und gelber Welle">',source,flags=re.S)
        source=re.sub(r'<link[^>]*rel="(?:shortcut )?icon"[^>]*>', '', source)
        source=source.replace('</head>','<link rel="icon" type="image/svg+xml" href="/icon.svg"><link rel="icon" type="image/png" sizes="64x64" href="/favicon-64.png"></head>',1)
        if 'rel="apple-touch-icon"' not in source:
            source=source.replace('</head>','<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"></head>',1)
        # Move the existing account hook into the separate white brand bar.
        def brand_bar(match):
            top=match[2]
            logo=re.search(r'<div class="brand-logo-wrap">.*?</div>',top,re.S)
            if not logo: raise ValueError('Header logo wrapper missing')
            bar='<div class="nic-brand-bar" id="nicBrandBar" role="banner">'+logo[0]+'<span class="nic-brand-description">Immobilienrechner für<br>Kauf, Sanierung und Investment</span><a class="nic-account-link nic-login-button" id="nicAccountLink" href="/#anmelden" aria-label="Jetzt anmelden"><svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 21v-2a7 7 0 0 1 14 0v2"/></svg><span>Jetzt anmelden</span></a></div>'
            return bar+match[1]
        source=re.sub(r'(<header class="hero"[^>]*>\s*)(<div class="hero-top">.*?</div></div>)',brand_bar,source,flags=re.S)
        disclaimer='Der Deal Check ist eine Kalkulationshilfe und keine Steuer-, Rechts- oder Finanzierungsberatung. Steuern werden nicht individuell berechnet. Prüfe vor einem Kauf insbesondere Verkaufspreis, Sanierungsumfang und Finanzierung mit belastbaren Unterlagen.'
        source=re.sub(r'(<(?:div|footer) class="footer-note"[^>]*>\s*)<span>'+re.escape(disclaimer)+r'</span>',r'\1',source)
        finance_disclaimer='Der Finanzierungsrechner ist eine Kalkulationshilfe und keine Steuer-, Rechts- oder Finanzierungsberatung. Die Ergebnisse sind unverbindliche Modellrechnungen. Prüfe Zinssatz, Tilgung, Sondertilgungen und Restschuld vor Vertragsabschluss anhand belastbarer Unterlagen.'
        if page.parent.name == 'finanzierungsrechner':
            source=re.sub(r'(<footer class="footer-note"[^>]*>\s*)<span>'+re.escape(finance_disclaimer)+r'</span>',r'\1',source,count=1)
        assert scripts==re.findall(r"<script\b[^>]*>.*?</script>",source,flags=re.S), f"Calculator script changed: {page}"
        if 'class="nic-brand-bar"' in source:
            if 'immocheck-ui-details' not in source:
                source=source.replace('</head>','<script defer src="/immocheck-ui-details.js"></script></head>',1)
            if 'immocheck-brand-theme' not in source:
                source=source.replace('</head>','<link rel="stylesheet" href="/immocheck-brand-theme.css"></head>',1)
        page.write_text(source)
if __name__ == '__main__':
    run(sys.argv[1] if len(sys.argv)>1 else '_site')
