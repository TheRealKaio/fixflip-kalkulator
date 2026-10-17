from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
style="""<style id="nic-embed-style">
html.nic-embed,html.nic-embed body{margin-top:0!important;padding-top:0!important;overflow-x:hidden!important}
html.nic-embed .hero,html.nic-embed .hero-top,html.nic-embed .brand-logo-wrap{display:none!important}
html.nic-embed .container,html.nic-embed main{max-width:100%!important}
</style>"""
js="""<script id="nic-wordpress-bridge">
(function(){
  var params=new URLSearchParams(window.location.search);
  if(params.get('embed')!=='1')return;
  document.documentElement.classList.add('nic-embed');
  // Only communicate the page height with our own WordPress domain.
  var allowed=['https://neustart-immocheck.de','https://www.neustart-immocheck.de'];
  var lastHeight=0;
  function report(){
    var b=document.body,d=document.documentElement;
    if(!b||!d)return;
    var h=Math.ceil(Math.max(b.scrollHeight,b.offsetHeight,d.scrollHeight,d.offsetHeight));
    if(h<100||h===lastHeight)return;
    lastHeight=h;
    allowed.forEach(function(origin){window.parent.postMessage({type:'nic:height',height:h},origin)});
  }
  var timer;
  function schedule(){clearTimeout(timer);timer=setTimeout(report,80)}
  window.addEventListener('load',function(){
    schedule();
    if(window.ResizeObserver)new ResizeObserver(schedule).observe(document.body);
    if(window.MutationObserver)new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true,attributes:true});
    setTimeout(report,300);setTimeout(report,1500);
  });
  window.addEventListener('resize',schedule);
})();
</script>"""
needle='</head>'
if needle not in s: raise SystemExit('Missing head tag')
s=s.replace(needle,style+'\n'+js+'\n'+needle,1)
p.write_text(s,encoding='utf-8')
