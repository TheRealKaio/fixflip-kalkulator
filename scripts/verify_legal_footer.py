"""Guard original legal navigation and financing footer against accidental UI edits."""
from pathlib import Path
import re
import subprocess

finance=Path('assets/financing.html').read_text(encoding='utf-8')
original_links=[('/#impressum','Impressum'),('/#agbs','AGBs'),('/#datenschutz','Datenschutz'),('/#haftungsausschluss','Haftungsausschluss')]
nav=re.search(r'<nav class="footer-legal-links"[^>]*>(.*?)</nav>',finance,re.S)
assert nav,'Financing legal nav missing'
for href,label in original_links:
    assert re.search(r'<a href="'+re.escape(href)+r'">'+label+r'</a>',nav.group(1)),f'Financing legal link modified: {label}'
assert 'footer-note' in finance and 'footer-version' in finance, 'Original footer sections missing'
extract=Path('scripts/extract_finance_footer.py').read_text(encoding='utf-8')
assert "('.footer-note','.footer-meta','.footer-version','.footer-legal-links')" in extract
build=Path('.github/workflows/pages.yml').read_text(encoding='utf-8')
assert 'python scripts/extract_finance_footer.py _site' in build
assert 'python scripts/build_settings_pages.py _site' in build
assert "data-legal-placeholder" in build, 'Original legal placeholder verification missing'
# Visual footer styling is permitted. Preserve the original legal links and
# prohibit hiding legal navigation or its surrounding footer in the design layer.
css=Path('assets/immocheck-ui-refresh.css').read_text(encoding='utf-8')
css=re.sub(r'/\\*.*?\\*/','',css,flags=re.S)
for match in re.finditer(r'([^{}]+)\\{([^{}]*)\\}',css):
    selectors, declarations=match.groups()
    if any(token in selectors for token in ('.footer-legal-links','.footer-note','.footer-meta','.footer-version','.nic-shared-footer')):
        assert not re.search(r'(?:^|;)\\s*(?:display\\s*:\\s*none|visibility\\s*:\\s*hidden)',declarations,re.I), 'Legal footer hidden by design layer'
print('Legal source checks passed: original footer links, disclaimer, extraction and compatible visual styling.')
