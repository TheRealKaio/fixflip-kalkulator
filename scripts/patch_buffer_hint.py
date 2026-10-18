from pathlib import Path

path=Path("_site/index.html")
s=path.read_text(encoding="utf-8")

old='<div class="field"><label>Sanierungs-Puffer</label><div class="input-wrap"><input id="buffer" inputmode="decimal" value="15"><span class="unit">%</span></div></div>'
new='<div class="field"><label>Sanierungs-Puffer</label><div class="input-wrap"><input id="buffer" inputmode="decimal" value="15"><span class="unit">%</span></div><div class="mini">Renovierungsaufschlag für unerwartetes</div></div>'

if old not in s:
    raise SystemExit("Sanierungs-Puffer field anchor not found")
s=s.replace(old,new,1)

if s.count('id="buffer"') != 1:
    raise SystemExit("buffer input duplicated or missing")
if 'Renovierungsaufschlag für unerwartetes' not in s:
    raise SystemExit("buffer hint missing")

path.write_text(s,encoding="utf-8")
print("Sanierungs-Puffer hint applied")
