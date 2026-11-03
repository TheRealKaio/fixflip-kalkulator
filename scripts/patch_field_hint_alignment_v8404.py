from pathlib import Path

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")


def replace_once(old, new, label):
    global s
    if s.count(old) != 1:
        raise SystemExit(label + " anchor must occur once, found " + str(s.count(old)))
    s = s.replace(old, new, 1)


# Keep these contextual helpers below their related controls and left aligned.
replace_once(
    '<label>Bundesland <span class="hint">Ort des Objekts</span></label>\n        <select id="state"></select>',
    '<label>Bundesland</label>\n        <select id="state"></select>\n        <div class="hint field-hint-below" id="stateLocationHint">Ort des Objekts</div>',
    "deal calculator object location hint",
)

replace_once(
    '<label>Bundesland <span class="hint">Ort des Objekts</span></label>\n            <select id="rentState"></select>',
    '<label>Bundesland</label>\n            <select id="rentState"></select>\n            <div class="hint field-hint-below" id="rentStateLocationHint">Ort des Objekts</div>',
    "rental object location hint",
)

replace_once(
    '<label>Finanzierte Summe <span class="hint">automatisch berechnet</span></label>\n'
    '          <div class="metric-box">\n'
    '            <div class="metric-value" id="financedAmount">–</div>\n'
    '          </div>',
    '<label>Finanzierte Summe</label>\n'
    '          <div class="metric-box">\n'
    '            <div class="metric-value" id="financedAmount">–</div>\n'
    '          </div>\n'
    '          <div class="hint field-hint-below">automatisch berechnet</div>',
    "financed amount calculation hint",
)

replace_once(
    '<label><span id="saleLabel">Marktwert nach Sanierung</span> <span class="hint" id="saleHint">editierbar</span></label>\n'
    '          <div class="input-wrap"><input id="sale" inputmode="decimal"><span class="unit">€</span></div>',
    '<label><span id="saleLabel">Marktwert nach Sanierung</span></label>\n'
    '          <div class="input-wrap"><input id="sale" inputmode="decimal"><span class="unit">€</span></div>\n'
    '          <div class="hint field-hint-below" id="saleHint">editierbar</div>',
    "market value source hint",
)

required = [
    '<div class="hint field-hint-below" id="stateLocationHint">Ort des Objekts</div>',
    '<div class="hint field-hint-below" id="rentStateLocationHint">Ort des Objekts</div>',
    '<div class="hint field-hint-below">automatisch berechnet</div>',
    '<div class="hint field-hint-below" id="saleHint">editierbar</div>',
]
missing = [token for token in required if token not in s]
if missing:
    raise SystemExit("V8.404 field helper alignment missing: " + ", ".join(missing))
if '<span class="hint" id="saleHint">' in s:
    raise SystemExit("V8.404 market value hint still appears in the label")
if s.count('id="saleHint"') != 1:
    raise SystemExit("V8.404 dynamic market value hint must remain unique")

path.write_text(s, encoding="utf-8")
print("V8.404 location and calculated-value hints moved below their controls")
