from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

style = '''
<style id="vk-benchmark-visual-fix-v8296">
.flip-sale-benchmark{
  color:var(--ink) !important;
}
.flip-sale-benchmark span{
  color:var(--muted) !important;
}
.flip-sale-benchmark strong{
  color:var(--ink) !important;
}
.flip-sale-benchmark .vk-transfer-icon{
  display:block !important;
  visibility:visible !important;
  opacity:1 !important;
  color:#64748b !important;
  font-size:17px !important;
  font-weight:800 !important;
  z-index:2;
}
.flip-sale-benchmark[data-vk-source]::after{
  content:"↘";
  position:absolute;
  right:9px;
  top:50%;
  transform:translateY(-50%);
  color:#64748b;
  font-size:17px;
  font-weight:800;
  line-height:1;
  pointer-events:none;
}
.flip-sale-benchmark .vk-transfer-icon{
  color:transparent !important;
}
</style>
'''

if "</head>" not in s:
    raise SystemExit("V8.296 head closing tag missing")
s = s.replace("</head>", style + "\n</head>", 1)

s = s.replace("V8.295", "V8.296")
s = s.replace("service-worker.js?v=8.295", "service-worker.js?v=8.296")

required = [
    'id="vk-benchmark-visual-fix-v8296"',
    '.flip-sale-benchmark{\n  color:var(--ink) !important;',
    '.flip-sale-benchmark span{\n  color:var(--muted) !important;',
    '.flip-sale-benchmark strong{\n  color:var(--ink) !important;',
    '.flip-sale-benchmark[data-vk-source]::after{',
    'content:"↘";',
    'V8.296',
    'service-worker.js?v=8.296'
]
missing=[token for token in required if token not in s]
if missing:
    raise SystemExit("V8.296 VK visual fix verification failed: " + ", ".join(missing))

path.write_text(s, encoding="utf-8")
print("V8.296 VK benchmark colors and arrow fixed")
