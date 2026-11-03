from pathlib import Path
import re

SITE = Path("_site")
SCRIPT = r'''<script id="nic-clear-calculator-input-hints">
(function(){
  const page=document.documentElement;
  if(!page || !/^(budget|own|rent|flip|finance)$/.test(page.getAttribute('data-nic-page')||''))return;
  function clearHints(root){
    const fields=[];
    if(root instanceof Element && root.matches('input[placeholder],textarea[placeholder]'))fields.push(root);
    if(root.querySelectorAll)fields.push(...root.querySelectorAll('input[placeholder],textarea[placeholder]'));
    fields.forEach(field=>{
      if(field.closest('#ownBudgetTransferCard'))return;
      field.removeAttribute('placeholder');
    });
  }
  clearHints(document);
  new MutationObserver(records=>records.forEach(record=>{
    if(record.type==='attributes')clearHints(record.target);
    record.addedNodes.forEach(node=>{if(node.nodeType===1)clearHints(node);});
  })).observe(document.documentElement,{subtree:true,childList:true,attributes:true,attributeFilter:['placeholder']});
})();
</script>'''

pages=0
for path in SITE.rglob('*.html'):
    source=path.read_text(encoding='utf-8')
    if not re.search(r'<html\b[^>]*\bdata-nic-page="(?:budget|own|rent|flip|finance)"',source):
        continue
    if 'id="nic-clear-calculator-input-hints"' not in source:
        if '</body>' not in source:
            raise SystemExit(f'Body anchor missing for calculator page: {path}')
        source=source.replace('</body>',SCRIPT+'\n</body>',1)
    path.write_text(source,encoding='utf-8')
    pages+=1
if not pages:
    raise SystemExit('No generated calculator pages found')
print(f'Calculator input hints cleared on {pages} pages; household budget import stays excluded')
