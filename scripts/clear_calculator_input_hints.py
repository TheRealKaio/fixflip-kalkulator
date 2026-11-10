from pathlib import Path
import re

SITE = Path("_site")
SCRIPT = r'''<script id="nic-clear-calculator-input-hints">
(function(){
  // The shared document can start on Home or a content route before opening
  // a calculator. Scope cleanup to main, not to the initial route attribute.
  const observed=new WeakSet();
  function clearHints(root){
    const fields=[];
    if(root instanceof Element && root.matches('input[placeholder],textarea[placeholder]'))fields.push(root);
    if(root.querySelectorAll)fields.push(...root.querySelectorAll('input[placeholder],textarea[placeholder]'));
    fields.forEach(field=>{
      if(field.closest('#ownBudgetTransferCard'))return;
      field.removeAttribute('placeholder');
    });
    // Financing has its own open Shadow DOM, outside document selectors.
    const elements=root.querySelectorAll?[...root.querySelectorAll('*')]:[];
    if(root instanceof Element)elements.unshift(root);
    for(const element of elements)if(element.shadowRoot)watch(element.shadowRoot);
  }
  function watch(root){
    if(observed.has(root))return;
    observed.add(root);
    clearHints(root);
    new MutationObserver(records=>records.forEach(record=>{
      if(record.type==='attributes')clearHints(record.target);
      record.addedNodes.forEach(node=>{if(node.nodeType===1)clearHints(node);});
    })).observe(root,{subtree:true,childList:true,attributes:true,attributeFilter:['placeholder']});
  }
  const main=document.querySelector('.app > main, main.section');
  if(main)watch(main);
})();
</script>'''

pages=0
for path in SITE.rglob('*.html'):
    source=path.read_text(encoding='utf-8')
    if "function updateDealTypeUI(){" not in source:
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
