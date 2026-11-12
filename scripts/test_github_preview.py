"""Preview output must be isolated from both production files and the API."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from prepare_github_preview import prepare, PREFIX


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
            before={p.relative_to(source):p.read_bytes() for p in source.rglob('*') if p.is_file()}
            prepare(source,target)
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

    def test_rejects_overwriting_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            for target in [path,path/'preview']:
                with self.assertRaises(ValueError):prepare(path,target)


if __name__=='__main__':unittest.main()
