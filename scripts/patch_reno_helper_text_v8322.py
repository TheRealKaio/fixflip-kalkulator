from pathlib import Path
import re
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else "_site/index.html")
s=p.read_text(encoding="utf-8")

short="Richtwerte erscheinen dezent als Vorschlag. Erst über den Button werden sie in die Berechnung übernommen."
new_note='<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €. Graue Werte sind unverbindliche Richtwerte. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen. Erst über den Button werden sie in die Berechnung übernommen.'

# 1) Sichtbare Kurz-Hinweise in den Sanierungs-Köpfen entfernen.
s=re.sub(
    r'<p class="sub" style="margin:4px 0 0">'+re.escape(short)+r'</p>',
    '',
    s
)

# 2) Runtime-Zuweisung entfernen, damit der Kurztext nicht beim Öffnen wieder erscheint.
s=s.replace(
    '    const intro=head.querySelector(".sub");\n    if(intro) intro.textContent="'+short+'";\n',
    ''
)

# 3) Bestehende "So funktioniert es"-Texte in gemeinsamer Sanierung vereinheitlichen.
patterns=[
    r'<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €\. Graue Werte im Eingabefeld sind unverbindliche Richtwerte\. Du kannst sie gesammelt übernehmen oder jeden Betrag direkt selbst eintragen und später jederzeit ändern\.',
    r'<strong>So funktioniert es:</strong> Alle Sanierungspositionen starten rechnerisch bei 0 €\. Graue Werte sind unverbindliche Richtwerte\. Du kannst sie gesammelt übernehmen oder jeden Betrag selbst eintragen\.'
]
# Apply both source variants in one pass so replacement text is never matched again.
s,replaced=re.subn("|".join("(?:"+pattern+")" for pattern in patterns),new_note,s)

if replaced < 2:
    raise SystemExit(f"V8.322 expected at least 2 renovation note replacements, got {replaced}")

if short in s:
    raise SystemExit("V8.322 old short renovation hint still present")

if s.count(new_note) < 2:
    raise SystemExit("V8.322 unified renovation note missing in both functions")

# Remove the obsolete subtitle below "Sanierung aufteilen".
obsolete="Richtwerte werden aus der Wohnfläche berechnet. Die Summe oben enthält den Sanierungs-Puffer."
s=re.sub(r'<p\b[^>]*>\s*'+re.escape(obsolete)+r'\s*</p>', '', s)
if obsolete in s:
    raise SystemExit("Obsolete renovation subtitle still present")

p.write_text(s,encoding="utf-8")
print("V8.322 renovation helper texts unified")
