from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")

old = '<div class="quick-grid rent-reno-buffer-grid"><div class="field"><label>Sanierungs-Puffer</label><div class="input-wrap"><input id="rentRenoBuffer" inputmode="decimal" value="0.00"><span class="unit">%</span></div><div class="mini">Renovierungsaufschlag für Unerwartetes</div></div></div>'
new = '<div class="trade-row trade-row-fixed reno-buffer-row rent-reno-buffer-row" style="margin-top:8px!important"><div class="trade-top"><div class="trade-copy"><label class="trade-name" for="rentRenoBuffer">Sanierungs-Puffer</label><div class="trade-basis">Aufschlag für unerwartetes (ca. 5%)</div></div><div class="trade-inputs-inline"><div class="input-wrap trade-money-input"><input id="rentRenoBuffer" inputmode="decimal" value="0.00" aria-label="Sanierungs-Puffer in Prozent"><span class="unit">%</span></div></div></div></div>'

if old not in s:
    raise SystemExit("Rental Sanierungs-Puffer field anchor missing")
if s.count(old) != 1:
    raise SystemExit("Rental Sanierungs-Puffer field anchor is not unique")

s = s.replace(old, new, 1)

required = [
    'class="trade-row trade-row-fixed reno-buffer-row rent-reno-buffer-row" style="margin-top:8px!important"',
    '<label class="trade-name" for="rentRenoBuffer">Sanierungs-Puffer</label>',
    '<div class="trade-basis">Aufschlag für unerwartetes (ca. 5%)</div>',
    '<input id="rentRenoBuffer" inputmode="decimal" value="0.00" aria-label="Sanierungs-Puffer in Prozent">',
    'id="rentRenoPanel"',
]
missing = [item for item in required if item not in s]
if missing:
    raise SystemExit("Rental buffer row verification failed: " + ", ".join(missing))
if 'Renovierungsaufschlag für Unerwartetes' in s:
    raise SystemExit("Old rental buffer helper is still present")

path.write_text(s, encoding="utf-8")
print("Rental Sanierungs-Puffer now matches the Staging / Möblierung row layout")
