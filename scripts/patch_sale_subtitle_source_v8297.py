from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

s=s.replace("V8.296","V8.297")
s=s.replace("service-worker.js?v=8.296","service-worker.js?v=8.297")

required=[
    'const subtitleSourceKey="ff_flip_sale_after_reno_source";',
    'hint.textContent=label+" • editierbar";',
    'localStorage.setItem(subtitleSourceKey,source);',
    'updateSaleSubtitle(source);',
    'const savedSubtitleSource=localStorage.getItem(subtitleSourceKey);',
    'V8.297',
    'service-worker.js?v=8.297'
]
missing=[x for x in required if x not in s]
if missing:
    raise SystemExit("V8.297 VK subtitle verification failed: "+", ".join(missing))

path.write_text(s,encoding="utf-8")
print("V8.297 VK subtitle follows selected source")
