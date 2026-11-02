"""Add global statistics hooks only to the generated site, preserving source snapshots."""
from pathlib import Path
import sys

site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")

def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"Expected build hook not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    site / "finanzierungsrechner" / "index.html",
    "const start=()=>window.NICAnalytics?.start({section:'website',calculator:null});",
    "const start=()=>window.NICAnalytics?.start({section:'flip',calculator:'finance'});",
)
replace_once(
    site / "pdf-reports.js",
    "if(download){doc.save(name);return;}",
    "if(download){doc.save(name);window.NICAnalytics?.track('pdf_download','finance');return;}",
)
replace_once(
    site / "pdf-reports.js",
    "if(navigator.canShare?.({files:[file]})&&navigator.share)await navigator.share({files:[file],title:name.slice(0,-4),text:name.slice(0,-4)});else{if(window.NICAccess&&!await window.NICAccess.authorize('pdfDownload'))return;doc.save(name);}",
    "if(navigator.canShare?.({files:[file]})&&navigator.share){await navigator.share({files:[file],title:name.slice(0,-4),text:name.slice(0,-4)});window.NICAnalytics?.track('pdf_share','finance',{method:'web_share'});}else{if(window.NICAccess&&!await window.NICAccess.authorize('pdfDownload'))return;doc.save(name);window.NICAnalytics?.track('pdf_download','finance',{method:'share_fallback'});}",
)
replace_once(
    site / "user-access.js",
    "const me=await api('me');user=me.user;csrf=me.csrf;return true;",
    "const me=await api('me');user=me.user;csrf=me.csrf;window.dispatchEvent(new Event('nic-auth-changed'));return true;",
)
replace_once(
    site / "user-access.js",
    "saveSettings,mountUsers,logout,login,saveOwn:",
    "saveSettings,mountUsers,logout,login,recordStatistics:async event=>{if(!await init())return false;return api('statistics-event',event);},loadStatistics:async days=>{if(!await requireAdmin())throw Error('Admin-Anmeldung erforderlich.');return api('statistics',undefined,'days='+days);},resetStatistics:async()=>{if(!await requireAdmin())throw Error('Admin-Anmeldung erforderlich.');return api('statistics-reset',{});},saveOwn:",
)
print("Global statistics hooks applied to generated calculator, PDF and access assets.")
