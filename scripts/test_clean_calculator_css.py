import unittest
from clean_calculator_css import clean

class CleanupTests(unittest.TestCase):
 def test_keeps_last_duplicate_in_place(self):
  source='.a{color:red}.b{color:blue}.a{color:red}'
  self.assertEqual(clean(source),('.b{color:blue}.a{color:red}',{'empty':0,'duplicate':1,'overridden':0}))
 def test_keeps_conflicting_rules_and_fallbacks(self):
  source='.a{color:red;color:var(--ink)}.a{color:blue}'
  self.assertEqual(clean(source)[0],source)
 def test_contexts_and_named_layer_order(self):
  source='.a{color:red}@media(max-width:500px){.a{color:red}}@layer reset{}@layer theme{}'
  self.assertEqual(clean(source)[0],source)
 def test_strings_comments_and_empty_media(self):
  source='.a{content:"{};"}/*{}*/@media(min-width:1px){.empty{/* comment */}}'
  output,stats=clean(source)
  self.assertEqual(output,'.a{content:"{};"}')
  self.assertEqual(stats,{'empty':2,'duplicate':0,'overridden':0})
 def test_keyframes_are_untouched(self):
  source='@keyframes a{from{}to{opacity:1}}@font-face{font-family:a;src:url(a.woff2)}'
  self.assertEqual(clean(source)[0],source)
 def test_covered_declarations(self):
  source='.a{color:red}.a{color:red;background:blue}'
  self.assertEqual(clean(source)[0],'.a{color:red;background:blue}')
 def test_semicolons_in_values(self):
  source='.a{background:url("data:a;b");content:"a;b"}.a{content:"a;b";background:url("data:a;b")}'
  self.assertEqual(clean(source)[0],'.a{content:"a;b";background:url("data:a;b")}')
 def test_cross_block_context(self):
  contexts={}
  clean('.a{color:red}',contexts)
  self.assertEqual(clean('.a{color:red}',contexts)[1]['duplicate'],1)
  self.assertEqual(clean('@media print{.a{color:red}}',contexts)[1]['duplicate'],0)
 def test_numeric_override_priority(self):
  self.assertEqual(clean('.a{font-size:12px}.a{font-size:14px}')[0],'.a{font-size:14px}')
  source='.a{font-size:12px!important}.a{font-size:14px}'
  self.assertEqual(clean(source)[0],source)
  self.assertEqual(clean('.a{font-size:12px}.a{font-size:14px!important}')[0],'.a{font-size:14px!important}')
 def test_preserves_complex_fallback_values(self):
  source='.a{font-size:14px}.a{font-size:clamp(12px,2vw,18px)}'
  self.assertEqual(clean(source)[0],source)
 def test_invalid_later_declaration_is_not_authority(self):
  for prop,value in [('width','12'),('font-size','-2px'),('font-weight','2000'),('padding-top','-5px')]:
   source=f'.a{{{prop}:14px}}.a{{{prop}:{value}}}'
   self.assertEqual(clean(source)[0],source)
 def test_idempotent(self):
  result=clean('.a{}.b{color:red}.b{color:red}')[0]
  self.assertEqual(clean(result),(result,{'empty':0,'duplicate':0,'overridden':0}))
if __name__=='__main__':unittest.main()
