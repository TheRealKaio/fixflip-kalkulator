from pathlib import Path
import re

path = Path("_site/index.html")
s = path.read_text(encoding="utf-8")


def div_end(html, start):
    depth = 0
    for match in re.finditer(r"</?div\\b[^>]*>", html[start:]):
        tag = match.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return start + match.end()
        else:
            depth += 1
    raise SystemExit("V8.403 unbalanced div while locating financing row")


def block_at_class(html, class_name, before=None):
    marker = f'class="{class_name}"'
    end_limit = len(html) if before is None else before
    pos = html.find(marker, 0, end_limit)
    if pos < 0 or html.find(marker, pos + len(marker), end_limit) >= 0:
        raise SystemExit(f"V8.403 expected one {class_name} marker")
    start = html.rfind("<div", 0, pos)
    if start < 0:
        raise SystemExit(f"V8.403 missing opening div for {class_name}")
    end = div_end(html, start)
    return start, end, html[start:end]


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
    if label_pos >= end:
        raise SystemExit(f"V8.403 invalid field wrapper for {label_id}")
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

quick_without_acq = quick_block.replace(acq_block, "", 1)
between = s[quick_end:term_start]
replacement = term_block + between + quick_without_acq + between + acq_block
s = s[:quick_start] + replacement + s[term_end:]

term_pos = s.find('id="monthsLabel"')
notary_pos = s.find(">Notar + Grundbuch</label>")
buy_broker_pos = s.find(">Makler beim Kauf</label>")
acq_pos = s.find('class="finance-acq-row"')
sale_cost_pos = s.find('<div class="sale-cost-grid">')
if not (0 <= term_pos < notary_pos < buy_broker_pos < acq_pos < sale_cost_pos):
    raise SystemExit("V8.403 verification failed: rows are not in the requested order")
if s.count('id="financeAcquisition"') != 1:
    raise SystemExit("V8.403 verification failed: Mitfinanzieren control missing or duplicated")

s = s.replace(
    '<div class="finance-acq-row">',
    '<div class="finance-acq-row" id="finance-acq-row-swap-v8403">',
    1,
)
css = '''<style id="finance-acq-row-swap-style-v8403">
#finance-acq-row-swap-v8403{
  display:grid!important;
  grid-template-columns:minmax(0,2fr) minmax(0,1fr)!important;
  gap:10px!important;
  align-items:end!important;
  width:100%!important;
  grid-column:1/-1!important;
}
#finance-acq-row-swap-v8403>.finance-acq-total{grid-column:1!important}
#finance-acq-row-swap-v8403>.finance-acq-option{grid-column:2!important}
</style>'''
if "</head>" not in s:
    raise SystemExit("V8.403 style insertion anchor missing")
s = s.replace("</head>", css + "</head>", 1)

path.write_text(s, encoding="utf-8")
print("V8.403 financing rows swapped with the complete acquisition row kept in a two-column layout")
