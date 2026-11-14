"""Published route copy must be complete before any mobile interaction."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
from build_calculator_explanations import templates, ROUTES

class Markup(HTMLParser):
    def __init__(self):super().__init__();self.tags=[];self.links=[];self.text=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag)
        if tag=='a':self.links.append(dict(attrs)['href'])
    def handle_data(self,data):self.text.append(data)

class ExplanationTests(unittest.TestCase):
    def test_six_complete_unique_explanations(self):
        cards=templates();sources=json.loads(Path('assets/site-settings.json').read_text())['content']
        self.assertEqual(set(cards),set(ROUTES))
        titles=set()
        for key,markup in cards.items():
            with self.subTest(key=key):
                parsed=Markup();parsed.feed(markup)
                self.assertEqual(parsed.tags.count('h2'),1)
                self.assertEqual(parsed.tags.count('h3'),2)
                self.assertEqual(parsed.tags.count('p'),3)
                self.assertEqual(parsed.tags.count('details'),1)
                self.assertEqual(parsed.tags.count('summary'),1)
                self.assertEqual(len(parsed.links),2)
                self.assertTrue(all(link in ['/'+slug+'/' for slug in ROUTES.values()]+['/preise/'] for link in parsed.links))
                text=' '.join(parsed.text)
                self.assertTrue(900<=len(text)<=1200,(key,len(text)))
                self.assertIn('Deutschland',text)
                titles.add(sources[key].get('boxTitle') or sources[key]['title'])
                self.assertIn('data-nic-explanation="'+key+'"',markup)
        self.assertEqual(len(titles),6)
        self.assertIn('id="nicOwnIntro"',cards['own'])

    def test_runtime_defaults_match_published_source(self):
        source=Path('assets/site-settings.js').read_text()
        defaults=json.loads(re.search(r'const contentPageDefaults=(.*?);\n',source)[1])
        self.assertEqual(defaults,json.loads(Path('assets/site-settings.json').read_text())['content'])

    def test_custom_content_is_static_and_safe(self):
        config=json.loads(Path('assets/site-settings.json').read_text())
        config['content']['budget'].update(title='Mein Budget',description='<p>Eigene Einleitung</p><h3>Mehr</h3><p>Eigener Text <a href="/eigennutzung/">weiter</a><script>alert(1)</script></p>')
        markup=templates(config)['budget']
        self.assertIn('Mein Budget',markup);self.assertIn('Eigene Einleitung',markup)
        self.assertNotIn('alert(1)',markup);self.assertNotIn('<script',markup)

if __name__=='__main__':unittest.main()
