"""Render one complete, indexable explanation per calculator/content route."""
import html
import json
from pathlib import Path

ROUTES={'budget':'budget','own':'eigennutzung','rent':'vermietung','flip':'fix-flip','finance':'finanzierungsrechner','settlement':'nebenkostenabrechnung'}


def templates():
    cards=json.loads(Path('assets/calculator-explanations.json').read_text())
    if set(cards)!=set(ROUTES):
        raise ValueError('Expected exactly six explanation cards')
    result={}
    for key,card in cards.items():
        title=html.escape(card['title']);ident=card['id']
        if len(card['sections'])!=2:
            raise ValueError('Every explanation needs two supplementary sections')
        rest=''.join('<h3>'+html.escape(section['title'])+'</h3><p>'+section['text']+'</p>' for section in card['sections'])
        result[key]=(f'<section id="{ident}" class="nic-explanation-card" data-nic-explanation="{key}" aria-labelledby="{ident}Title">'
                     f'<h2 id="{ident}Title">{title}</h2><p class="nic-explanation-intro">{html.escape(card["intro"])}</p>'
                     f'<details class="nic-explanation-details" open><summary>weiterlesen</summary><div class="nic-explanation-rest">{rest}</div></details></section>')
    return result
