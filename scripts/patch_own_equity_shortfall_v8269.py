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
if 'id="equityShortfallWarning"' not in s:
    raise SystemExit("Keep the independent Fix & Flip warning")
# Keep the historical version progression for the V8.270+ patch chain.
if "V8.268" not in s or "service-worker.js?v=8.268" not in s:
    raise SystemExit("Expected historical 8.268 version anchor")
s=s.replace("V8.268","V8.269").replace("service-worker.js?v=8.268","service-worker.js?v=8.269")
path.write_text(s,encoding="utf-8")
# Intentionally do not install the former warning markup or render branch.
print("Own-use redundant equity shortfall warning intentionally omitted")
