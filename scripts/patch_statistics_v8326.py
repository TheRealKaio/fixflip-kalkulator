from pathlib import Path
import shutil
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
s=p.read_text()

def replace(old,new,label):
    global s
    if s.count(old)!=1:
        raise SystemExit('Statistics anchor not unique: '+label)
    s=s.replace(old,new,1)

replace('<script src="site-integration.js" defer></script>','<link rel="stylesheet" href="statistics.css"><script src="statistics-core.js" defer></script><script src="statistics.js" defer></script><script src="site-integration.js" defer></script>','public scripts')
# Instrument successful PDF actions, rather than button clicks. Keep the action's
# calculator identity even when the visitor changes tabs during async generation.
start=s.index('async function sharePdf(){')
end=s.index('\nconst OWN_BUDGET_INCOME_KEY',start)
chunk=s[start:end]
chunk=chunk.replace('    const doc = buildPdf();','    const doc = buildPdf();\n    const analyticsCalculator=currentDealType();')
needle='''        files:[file]
      });'''
if chunk.count(needle)!=1:
    raise SystemExit('Statistics native share anchor missing')
chunk=chunk.replace(needle,needle+'\n      window.NICAnalytics?.track("pdf_share",analyticsCalculator,{method:"web_share"});',1)
chunk=chunk.replace('      a.click();','      a.click();\n      window.NICAnalytics?.track("pdf_download",analyticsCalculator,{method:"share_fallback"});',1)
chunk=chunk.replace('    doc.save(filename);','    doc.save(filename);\n    window.NICAnalytics?.track("pdf_download",analyticsCalculator,{method:"save"});',1)
chunk=chunk.replace('  }catch(err){','  }catch(err){\n    if(err?.name==="AbortError") return;')
s=s[:start]+chunk+s[end:]

start=s.index('  async function rentalPdf(kind){')
end=s.index("  $r('sharePdf')",start)
s=s[:start]+'''  async function rentalPdf(kind){
    await preparePdfBrandLogo();
    const doc=buildRentalPdf(),name='Vermietung_Deal_Report_'+new Date().toISOString().slice(0,10)+'.pdf';
    if(kind==='save'){
      doc.save(name);
      window.NICAnalytics?.track('pdf_download','rent',{method:'save'});
      return;
    }
    const blob=doc.output('blob'),file=new File([blob],name,{type:'application/pdf'});
    if(navigator.canShare&&navigator.canShare({files:[file]})&&navigator.share){
      await navigator.share({title:'Vermietung - Deal Report',text:'Meine Vermietungs-Kalkulation',files:[file]});
      window.NICAnalytics?.track('pdf_share','rent',{method:'web_share'});
    }else{
      const u=URL.createObjectURL(blob),a=document.createElement('a');
      a.href=u;a.download=name;document.body.appendChild(a);a.click();a.remove();
      window.NICAnalytics?.track('pdf_download','rent',{method:'share_fallback'});
      setTimeout(()=>URL.revokeObjectURL(u),15000);
    }
  }
'''+s[end:]
replace("rentalPdf('share').catch(err=>{console.error(err);", "rentalPdf('share').catch(err=>{if(err?.name==='AbortError')return;console.error(err);",'rental share cancellation')
p.write_text(s)
for name in ['statistics-core.js','statistics.js','statistics-admin.js','statistics.css']:
    shutil.copyfile(Path('assets')/name,p.parent/name)
admin=p.parent/'admin.html'
admin.write_text(admin.read_text().replace('V8.325','V8.326'))
print('V8.326 statistics, Google tags and footer typography integrated')
