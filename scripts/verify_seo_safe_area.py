"""Verify SEO indexing controls and iOS safe-area metadata in the built site."""
from pathlib import Path
import json
import re
import sys

site=Path(sys.argv[1] if len(sys.argv)>1 else '_site')
settings=json.loads((site/'site-settings.json').read_text(encoding='utf-8'))
rules=settings.get('seoIndexing',{})
routes={'website':'','company':'unternehmen/','budget':'budget/','own':'eigennutzung/','rent':'vermietung/','flip':'fix-flip/','finance':'finanzierungsrechner/','settlement':'nebenkostenabrechnung/','prices':'preise/','why':'warum-immocheck/','about':'ueber-uns/','contact':'kontakt/','login':'anmelden/','impressum':'impressum/'}
default_off={'login','impressum'}
sitemap=(site/'sitemap.xml').read_text(encoding='utf-8')
for key,route in routes.items():
    path=site/route/'index.html'
    html=path.read_text(encoding='utf-8')
    expected=(bool(rules.get(key,key not in default_off)) and key!='login')
    if key=='impressum':expected=bool(rules.get('impressum',False))
    robots=re.findall(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']',html,re.I)
    directive='index,follow' if expected else 'noindex,follow'
    if robots!=[directive]:
        raise SystemExit(f'{path}: expected one robots tag {directive}, got {robots}')
    if not re.search(r'<meta\b[^>]*name=["\']viewport["\'][^>]*viewport-fit=cover',html,re.I):
        raise SystemExit(f'{path}: missing iOS safe area viewport')
    canonical='https://www.neustart-immocheck.de/'+route
    in_sitemap='<loc>'+canonical+'</loc>' in sitemap
    if in_sitemap!=expected:
        raise SystemExit(f'{path}: sitemap membership incorrect ({in_sitemap})')
robots_txt=(site/'robots.txt').read_text(encoding='utf-8')
for expected in ('Sitemap: https://www.neustart-immocheck.de/sitemap.xml','Disallow: /admin.html','Disallow: /api/'):
    if expected not in robots_txt:raise SystemExit('robots.txt missing '+expected)
print('Verified SEO robots, sitemap and iOS viewport for',len(routes),'public routes')
