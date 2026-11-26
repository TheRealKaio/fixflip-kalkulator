"""Local WEG document pipeline. Run with --help for setup and options.

Install paddlepaddle, paddleocr[doc-parser], pymupdf and marker-pdf.
Qwen must be served by a local OpenAI-compatible inference server.
Output is evidence for review, never a confirmed statement.
"""
import argparse
import base64
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, ProxyHandler, build_opener

import fitz

MONEY = re.compile(r"(?<![\d.,])[−-]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}(?!\d)")


def table_warnings(table):
    html = table.get("pred_html", "")
    if not html:
        return True
    rows = re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, re.S | re.I)
    if not rows:
        return True
    for row in rows:
        cells = re.findall(r"<td\b([^>]*)>(.*?)</td>", row, re.S | re.I)
        amounts = [MONEY.findall(re.sub(r"<[^>]*>", " ", cell)) for _, cell in cells]
        if any(re.search(r"€\s*[A-Za-zÄÖÜäöü]", re.sub(r"<[^>]*>", " ", cell)) for _, cell in cells):
            return True
        if any(len(matches) > 1 for matches in amounts):
            return True
        if any(re.search(r'rowspan\s*=\s*["\']?(?:[2-9]|\d{2,})', attrs) for attrs, _ in cells):
            return True
    return False


def query_qwen(image, endpoint, model):
    url = urlparse(endpoint)
    if url.scheme != "http" or url.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Qwen endpoint must be an HTTP loopback address.")
    encoded = base64.b64encode(image).decode("ascii")
    prompt = (
        "Transkribiere ausschließlich sichtbare Tabellenzeilen dieser deutschen WEG-Abrechnung. "
        "Antworte mit JSON: {rows:[{block, position, key, total, base, share, unitAmount}], "
        "totals:[{label,total,unitAmount}]}. Beträge exakt als Zeichenketten, fehlende oder "
        "unsichere Angaben als null. Keine Werte berechnen, ergänzen oder schätzen."
    )
    body = json.dumps({
        "model": model, "temperature": 0,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + encoded}},
        ]}],
    }).encode()
    request = Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    with build_opener(ProxyHandler({})).open(request, timeout=240) as response:
        answer = json.load(response)["choices"][0]["message"]["content"]
    answer = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", answer)
    return json.loads(answer)


def process(paths, qwen_endpoint, qwen_model):
    paddle = None
    marker = None
    for path in paths:
        with fitz.open(path) as document:
            for number, page in enumerate(document, 1):
                text = page.get_text().strip() if document.is_pdf else ""
                digital = len(text) >= 100 and len(MONEY.findall(text)) >= 2 and "\ufffd" not in text
                output = {"file": path.name, "page": number, "reviewRequired": True, "regions": []}
                if digital:
                    if marker is None:
                        from marker.converters.pdf import PdfConverter
                        from marker.models import create_model_dict
                        marker = PdfConverter(artifact_dict=create_model_dict())
                    with tempfile.TemporaryDirectory() as folder:
                        single = Path(folder) / "page.pdf"
                        with fitz.open() as pdf:
                            pdf.insert_pdf(document, from_page=number - 1, to_page=number - 1)
                            pdf.save(single)
                        from marker.output import text_from_rendered
                        markdown, _, _ = text_from_rendered(marker(str(single)))
                    output.update(engine="Marker", text=markdown)
                    if not table_warnings({"pred_html": markdown}) and len(MONEY.findall(markdown)) >= 2:
                        yield output
                        continue
                if paddle is None:
                    from paddleocr import PPStructureV3
                    paddle = PPStructureV3(
                        device="cpu", enable_mkldnn=False,
                        text_recognition_model_name="latin_PP-OCRv5_mobile_rec",
                        text_detection_model_name="PP-OCRv5_mobile_det",
                        use_doc_orientation_classify=False, use_doc_unwarping=False,
                        use_formula_recognition=False, use_seal_recognition=False,
                        use_chart_recognition=False,
                    )
                with tempfile.TemporaryDirectory() as folder:
                    raster = Path(folder) / "page.png"
                    pixmap = page.get_pixmap(dpi=180 if document.is_pdf else 96)
                    pixmap.save(raster)
                    result = next(iter(paddle.predict(str(raster)))).json["res"]
                    output["engine"] = "PaddleOCR"
                    output["text"] = result["overall_ocr_res"]["rec_texts"]
                    tables = result.get("table_res_list", [])
                    regions = output["regions"]
                    for table in tables:
                        regions.append({"html": table.get("pred_html", ""), "needsSecondRead": table_warnings(table)})
                    if not tables:
                        regions.append({"needsSecondRead": True})
                    if qwen_endpoint and any(region["needsSecondRead"] for region in regions):
                        # Share the page so the second model also sees the headers and block labels.
                        try:
                            output["qwenProposal"] = query_qwen(raster.read_bytes(), qwen_endpoint, qwen_model)
                        except (OSError, ValueError, KeyError, IndexError) as error:
                            output["secondReadError"] = str(error)
                    yield output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--qwen-endpoint", help="Loopback /v1/chat/completions URL")
    parser.add_argument("--qwen-model", default="Qwen/Qwen3-VL-4B-Instruct")
    args = parser.parse_args()
    for page in process(args.files, args.qwen_endpoint, args.qwen_model):
        print(json.dumps(page, ensure_ascii=False), flush=True)
