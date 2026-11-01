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
css=Path('assets/immocheck-ui-refresh.css').read_text(encoding='utf-8')
for selector in ('.footer-legal-links','.footer-note','.footer-meta','.footer-version'):
    assert not re.search(r'[^}]*'+re.escape(selector)+r'[^{}]*{',css),f'Design override potentially changes legal footer: {selector}'
print('Legal source checks passed: original footer links, disclaimer, extraction and no design override.')
