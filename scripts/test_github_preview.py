"""Preview output must be isolated from both production files and the API."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from prepare_github_preview import prepare, public_layout, PREFIX, PUBLIC_SETTINGS


class PreviewTests(unittest.TestCase):
    def test_project_paths_and_production_isolation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); source=root/'site'; target=root/'preview'; source.mkdir()
            (source/'budget').mkdir();(source/'budget/index.html').write_text('<head></head>')
            js="const routes={'/budget/':'budget'};routes['/']='home';new URL('/',ROOT);p.split('/');u.startsWith('/');const outside='https://example.com/budget/';"
            (source/'app.js').write_text(js)
            hashed='app.'+hashlib.sha256(js.encode()).hexdigest()[:16]+'.js'
            (source/hashed).write_text(js)
            (source/'.asset-manifest.json').write_text(json.dumps({'app.js':hashed}))
            (source/'index.html').write_text('<head><base href="/"><script src="/'+hashed+'"></script></head><a href="/budget/">Budget</a>')
            (source/'CNAME').write_text('www.neustart-immocheck.de')
            (source/'backend-config.json').write_text('{"enabled":true,"apiUrl":"live"}')
            (source/'site-settings.json').write_text(json.dumps({'layout':{'bodySize':16,'h1':45},'content':{'title':'development draft'}}))
            before={p.relative_to(source):p.read_bytes() for p in source.rglob('*') if p.is_file()}
            with patch('prepare_github_preview.public_layout',return_value={'bodySize':20,'h1':30}):
                prepare(source,target,live_layout=True)
            self.assertEqual(json.loads((target/'site-settings.json').read_text()),{'layout':{'bodySize':20,'h1':30},'content':{'title':'development draft'}})
            self.assertEqual(before,{p.relative_to(source):p.read_bytes() for p in source.rglob('*') if p.is_file()})
            self.assertFalse((target/'CNAME').exists())
            self.assertEqual(json.loads((target/'backend-config.json').read_text()),{'enabled':False,'apiUrl':''})
            output=(target/'app.js').read_text()
            self.assertIn("routes['"+PREFIX+"']",output)
            self.assertIn("new URL('"+PREFIX+"',ROOT)",output)
            self.assertIn("p.split('/')",output)
            self.assertIn("u.startsWith('/')",output)
            self.assertIn('https://example.com/budget/',output)
            self.assertIn('noindex,nofollow',(target/'index.html').read_text())
            new_hashed=json.loads((target/'.asset-manifest.json').read_text())['app.js']
            self.assertNotEqual(hashed,new_hashed)
            self.assertIn(new_hashed,(target/'index.html').read_text())
            self.assertIn(PREFIX+'budget/',(target/'index.html').read_text())

    def test_public_layout_copies_only_valid_visual_settings(self):
        defaults={'font':'system','bodySize':16,'h1':45,'buttonText':'AUTO'}
        expected={'font':'system','bodySize':20,'h1':30,'buttonText':'#FFFFFF'}
        opener=MagicMock()
        response=opener.return_value.__enter__.return_value
        response.read.return_value=json.dumps({'settings':{'layout':{**expected,'extra':'ignore'},'content':'live content must not replace draft'},'csrf':'ignore'}).encode()
        self.assertEqual(public_layout(defaults,opener),expected)
        opener.assert_called_once_with(PUBLIC_SETTINGS,timeout=25)
        for bad in [True,100,'20px']:
            response.read.return_value=json.dumps({'settings':{'layout':{**expected,'bodySize':bad}}}).encode()
            with self.assertRaises(ValueError):public_layout(defaults,opener)

    def test_rejects_overwriting_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            for target in [path,path/'preview']:
                with self.assertRaises(ValueError):prepare(path,target)


if __name__=='__main__':unittest.main()
