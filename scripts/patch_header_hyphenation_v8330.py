from pathlib import Path
import sys

p=Path(sys.argv[1] if len(sys.argv)>1 else '_site/index.html')
s=p.read_text()
# Optional, syllable-aligned breaks also work without a browser dictionary.
replacements={
    'Wie viel Immobilie<br>kannst du dir leisten?':'Wie viel Im&shy;mo&shy;bi&shy;lie<br>kannst du dir leis&shy;ten?',
    'Lohnt sich<br>diese Eigentumswohnung?':'Lohnt sich<br>diese Ei&shy;gen&shy;tums&shy;woh&shy;nung?',
    'Lohnt sich<br>diese Mietwohnung?':'Lohnt sich<br>diese Miet&shy;woh&shy;nung?',
    'Lohnt sich<br>dieses Objekt?':'Lohnt sich<br>dieses Ob&shy;jekt?',
}
for old,new in replacements.items():
    if old not in s:
        raise SystemExit('Header hyphenation anchor missing: '+old)
    s=s.replace(old,new)
s=s.replace('<h1 id="heroTitle">','<h1 id="heroTitle" lang="de">',1)
p.write_text(s)
admin=p.parent/'admin.html'
admin.write_text(admin.read_text().replace('V8.329','V8.330'))
print('V8.330 German syllable-aligned responsive header titles applied')
