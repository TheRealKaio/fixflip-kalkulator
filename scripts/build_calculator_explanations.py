"""Render the same admin-editable content cards in complete route HTML."""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROUTES={'budget':'budget','own':'eigennutzung','rent':'vermietung','flip':'fix-flip','finance':'finanzierungsrechner','settlement':'nebenkostenabrechnung'}
IDS={'budget':'nicBudgetIntro','own':'nicOwnIntro','rent':'nicRentIntro','flip':'nicFlipIntro','finance':'nicFinanceIntro','settlement':'nicSettlementIntro'}

class SafeContent(HTMLParser):
    allowed={'p','br','h2','h3','h4','strong','b','em','i','ul','ol','li','a','blockquote','div','span'}
    def __init__(self):super().__init__(convert_charrefs=True);self.out=[];self.blocked=0
    def handle_starttag(self,tag,attrs):
        if tag in {'script','style','iframe','object'}:self.blocked+=1;return
        if self.blocked or tag not in self.allowed:return
        attr=''
        if tag=='a':
            href=dict(attrs).get('href','') or ''
            if (href.startswith('/') and not href.startswith('//') and '\\' not in href) or urlparse(href).scheme in {'https','http','mailto','tel'}:attr=' href="'+html.escape(href,quote=True)+'" rel="noopener noreferrer"'
        self.out.append('<'+tag+attr+'>')
    def handle_endtag(self,tag):
        if tag in {'script','style','iframe','object'}:self.blocked=max(0,self.blocked-1);return
        if not self.blocked and tag in self.allowed and tag!='br':self.out.append('</'+tag+'>')
    def handle_data(self,data):
        if not self.blocked:self.out.append(html.escape(data))

def templates(config=None):
    config=config or json.loads(Path('assets/site-settings.json').read_text())
    content=config.get('content') or config.get('meta',{}).get('content',{})
    defaults=json.loads(Path('assets/site-settings.json').read_text())['content']
    result={}
    for key in ROUTES:
        card=content.get(key,defaults[key]);ident=IDS[key]
        parser=SafeContent();parser.feed(card.get('description',defaults[key]['description']));body=''.join(parser.out)
        first=re.search(r'<p>.*?</p>',body,re.S)
        intro=first[0] if first else '<p>'+html.escape(re.sub('<[^>]*>','',body))+'</p>'
        rest=body[:first.start()]+body[first.end():] if first else ''
        intro=intro.replace('<p>','<p class="nic-explanation-intro">',1)
        title=html.escape(card.get('boxTitle') or card.get('title') or defaults[key]['title'])
        result[key]=(f'<section id="{ident}" class="nic-explanation-card" data-nic-explanation="{key}" aria-labelledby="{ident}Title">'
                     f'<h2 id="{ident}Title">{title}</h2>{intro}'
                     f'<details class="nic-explanation-details" open><summary>weiterlesen</summary><div class="nic-explanation-rest">{rest}</div></details></section>')
    return result
