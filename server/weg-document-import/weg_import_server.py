"""Serve the ImmoCheck WEG import on loopback for local testing."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import tempfile

from weg_document_import import process


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset", required=True, type=Path, help="ImmoCheck nebenkostenabrechnung.js")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--qwen-endpoint")
    parser.add_argument("--qwen-model", default="Qwen/Qwen3-VL-4B-Instruct")
    args = parser.parse_args()
    asset = args.asset.read_bytes()
    landing = """<!doctype html><meta charset="utf-8"><title>ImmoCheck Importtest</title>
    <script>window.nicWegImportEndpoint='/ocr';</script>
    <main id="nicContentView"><h1>Nebenkostenabrechnung</h1></main>
    <script src="/nebenkostenabrechnung.js"></script>""".encode()

    class Handler(BaseHTTPRequestHandler):
        def send_data(self, status, content_type, data):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/nebenkostenabrechnung.js":
                self.send_data(200, "text/javascript; charset=utf-8", asset)
            elif self.path == "/nebenkostenabrechnung/":
                self.send_data(200, "text/html; charset=utf-8", landing)
            else:
                self.send_error(404)

        def do_POST(self):
            if self.path != "/ocr":
                self.send_error(404)
                return
            if self.headers.get("Origin") != "http://" + self.headers.get("Host", ""):
                self.send_error(403)
                return
            if self.headers.get("Content-Type") != "application/octet-stream":
                self.send_error(415)
                return
            size = self.headers.get("Content-Length", "")
            if not size.isdecimal() or not 0 < int(size) <= 25 * 1024 * 1024:
                self.send_error(413)
                return
            suffix = {"pdf": ".pdf", "image": ".png"}.get(self.headers.get("X-Weg-Type"))
            if not suffix:
                self.send_error(415)
                return
            try:
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / ("beleg" + suffix)
                    path.write_bytes(self.rfile.read(int(size)))
                    pages = list(process([path], args.qwen_endpoint, args.qwen_model))
                self.send_data(200, "application/json", json.dumps(pages, ensure_ascii=False).encode())
            except Exception as error:
                self.log_error("Recognition failed: %s", type(error).__name__)
                self.send_data(422, "application/json", b'{"error":"Beleg konnte nicht verarbeitet werden."}')

    HTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
