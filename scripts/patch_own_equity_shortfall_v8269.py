"""Legacy compatibility stage for own-use financing.

The redundant red own-use equity shortfall warning has been retired.
The shared financing-percent-slider.js now recalculates equity or LTV
depending on the last deliberate user action and presents the grey hint.
Keep the independent Fix & Flip financing warning unchanged.
"""
from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")
if 'id="ownEquityInput"' not in s:
    raise SystemExit("Own equity field missing")
if 'id="ownEquityShortfallWarning"' in s:
    raise SystemExit("Unexpected pre-existing own-use red shortfall warning")
# The extra red shortfall box duplicates the existing Fix & Flip reserve
# breakdown and the equity-goal warning. Keep those genuine risk indicators.
warning='<div class="equity-shortfall-warning" id="equityShortfallWarning" hidden></div>'
if s.count(warning)!=1:
    raise SystemExit("Expected one legacy Fix & Flip duplicate warning")
s=s.replace(warning,"",1)
start=s.find('  if($("equityShortfallWarning")){')
if start<0:
    raise SystemExit("Expected duplicate Fix & Flip warning render block")
end=s.find('\n  }',start)
if end<0:raise SystemExit("Duplicate warning render end missing")
s=s[:start]+s[end+4:]
if 'id="equityShortfallWarning"' in s or 'if($("equityShortfallWarning")){' in s:
    raise SystemExit("Old duplicate Fix & Flip warning remains")
# Keep the historical version progression for the V8.270+ patch chain.
if "V8.268" not in s or "service-worker.js?v=8.268" not in s:
    raise SystemExit("Expected historical 8.268 version anchor")
s=s.replace("V8.268","V8.269").replace("service-worker.js?v=8.268","service-worker.js?v=8.269")
path.write_text(s,encoding="utf-8")
# Intentionally do not install the former warning markup or render branch.
print("Own-use redundant equity shortfall warning intentionally omitted")
