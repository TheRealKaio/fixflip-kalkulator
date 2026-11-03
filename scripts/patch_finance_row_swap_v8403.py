from pathlib import Path
import re

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")


def div_end(html, start):
    depth = 0
    for match in re.finditer(r"</?div\b[^>]*>", html[start:]):
        if match.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return start + match.end()
        else:
            depth += 1
    raise SystemExit("V8.403 unbalanced div while locating financing row")


def block_at_class(html, class_name):
    marker = f'class="{class_name}"'
    pos = html.find(marker)
    if pos < 0 or html.find(marker, pos + len(marker)) >= 0:
        raise SystemExit(f"V8.403 expected one {class_name} marker")
    start = html.rfind("<div", 0, pos)
    if start < 0:
        raise SystemExit(f"V8.403 missing opening div for {class_name}")
    return start, div_end(html, start), html[start:div_end(html, start)]


def field_at_label_id(html, label_id):
    marker = f'id="{label_id}"'
    positions = [m.start() for m in re.finditer(re.escape(marker), html)]
    if len(positions) != 1:
        raise SystemExit(f"V8.403 expected one {label_id} marker, found {len(positions)}")
    label_pos = positions[0]
    start = html.rfind('<div class="field"', 0, label_pos)
    if start < 0:
        raise SystemExit(f"V8.403 missing field wrapper for {label_id}")
    end = div_end(html, start)
    return start, end, html[start:end]


if 'id="finance-acq-row-swap-v8403"' in s:
    raise SystemExit("V8.403 finance row swap patch already applied")

acq_start, acq_end, acq_block = block_at_class(s, "finance-acq-row")
term_start, term_end, term_block = field_at_label_id(s, "monthsLabel")
quick_start = s.rfind('<div class="quick-grid">', 0, acq_start)
if quick_start < 0:
    raise SystemExit("V8.403 acquisition row quick-grid missing")
quick_end = div_end(s, quick_start)
quick_block = s[quick_start:quick_end]
if not (quick_start < acq_start < acq_end <= quick_end < term_start < term_end):
    raise SystemExit("V8.403 rows are not in the expected original order")
if quick_block.count(acq_block) != 1:
    raise SystemExit("V8.403 acquisition row is not uniquely inside the quick-grid")

# Keep the purchase costs and Mitfinanzieren controls together in their original
# quick-grid. Put the full-width duration field first, then Notar/Makler, then
# the complete acquisition row at the duration's former position.
opening_end = quick_block.find(">") + 1
closing_start = quick_block.rfind("</div>")
if opening_end <= 0 or closing_start <= opening_end:
    raise SystemExit("V8.403 quick-grid boundaries are invalid")
quick_inner = quick_block[opening_end:closing_start]
if quick_inner.count(acq_block) != 1:
    raise SystemExit("V8.403 acquisition row is not uniquely inside the quick-grid")
quick_inner = quick_inner.replace(acq_block, "", 1)
term_block, class_count = re.subn(
    r'<div class="([^"]*)"',
    lambda m: '<div class="'+m.group(1)+' finance-duration-swap-v8403" style="grid-column:1 / -1!important"',
    term_block,
    count=1,
)
if class_count != 1:
    raise SystemExit("V8.403 duration field wrapper class missing")
acq_block = acq_block.replace(
    '<div class="finance-acq-row">',
    '<div class="finance-acq-row" id="finance-acq-row-swap-v8403">',
    1,
)
quick_open = quick_block[:opening_end].replace(
    'class="quick-grid"',
    'class="quick-grid finance-row-order-v8403" style="display:grid!important;grid-template-columns:1fr 1fr!important"',
    1,
)
new_quick = (
    quick_open
    + term_block
    + quick_inner
    + acq_block
    + quick_block[closing_start:]
)
s = s[:quick_start] + new_quick + s[term_end:]

term_pos = s.find('id="monthsLabel"')
notary_pos = s.find(">Notar + Grundbuch</label>")
buy_broker_pos = s.find(">Makler beim Kauf</label>")
acq_pos = s.find('id="finance-acq-row-swap-v8403"')
sale_cost_pos = s.find('<div class="sale-cost-grid">')
if not (0 <= term_pos < notary_pos < buy_broker_pos < acq_pos < sale_cost_pos):
    raise SystemExit("V8.403 verification failed: rows are not in the requested order")
if s.count('id="financeAcquisition"') != 1:
    raise SystemExit("V8.403 verification failed: Mitfinanzieren control missing or duplicated")

css = '''<style id="finance-row-order-v8403">
#finance-acq-row-swap-v8403{
  display:grid!important;
  grid-template-columns:minmax(0,2fr) minmax(0,1fr)!important;
  gap:10px!important;
  align-items:end!important;
  width:100%!important;
  grid-column:1/-1!important;
  grid-row:auto!important;
}
#finance-acq-row-swap-v8403 .finance-acq-total{grid-column:1!important;grid-row:1!important}
#finance-acq-row-swap-v8403 .finance-acq-option{grid-column:2!important;grid-row:1!important}
</style>'''
if "</head>" not in s:
    raise SystemExit("V8.403 style insertion anchor missing")
s = s.replace("</head>", css + "</head>", 1)

path.write_text(s, encoding="utf-8")
print("V8.403 financing rows swapped while preserving the complete costs row layout")
