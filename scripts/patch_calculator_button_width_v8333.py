from pathlib import Path
import sys

p = Path(sys.argv[1] if len(sys.argv) > 1 else '_site/index.html')
s = p.read_text()
css = '''<style id="calculator-button-width-v8333">
/* Reserve the same space for every calculator's label, including Eigennutzung. */
.bottom-actions{grid-template-columns:minmax(0,260px) minmax(96px,1fr) 52px}
.bottom-actions>button{min-width:0}
#recalc{width:100%;white-space:normal;overflow-wrap:normal;line-height:1.2;padding:0 10px}
@media(max-width:370px){
  .bottom-actions{grid-template-columns:minmax(0,260px) minmax(72px,1fr) 46px;gap:7px}
}
</style>'''
s = s.replace('</head>', css + '\n</head>', 1)
p.write_text(s)
admin = p.parent / 'admin.html'
admin.write_text(admin.read_text().replace('V8.332', 'V8.333'))
print('V8.333 stable calculator button widths applied')
