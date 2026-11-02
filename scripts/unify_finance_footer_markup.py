"""Render the original calculator footer markup on the financing route."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys


class FooterParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=False)
        self.html = html
        self.offsets = [0]
        for line in html.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.level = 0
        self.start = None
        self.end = None

    def index(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "").split()
        if self.start is None and "footer-note" in classes:
            self.start = self.index()
            self.level = 1
        elif self.start is not None and self.end is None:
            if tag not in ("area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"):
                self.level += 1

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if self.start is not None and self.end is None:
            self.level -= 1
            if self.level == 0:
                close = self.html.find(">", self.index())
                if close != -1:
                    self.end = close + 1


def extract_footer(html):
    parser = FooterParser(html)
    parser.feed(html)
    if parser.start is None or parser.end is None:
        raise ValueError("Calculator footer with class footer-note missing")
    return html[parser.start:parser.end], parser.start, parser.end


def main():
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    home = (site / "index.html").read_text(encoding="utf-8")
    shared, _, _ = extract_footer(home)
    target = site / "finanzierungsrechner/index.html"
    finance = target.read_text(encoding="utf-8")
    _, start, end = extract_footer(finance)
    target.write_text(finance[:start] + shared + finance[end:], encoding="utf-8")
    print("Finance footer replaced with main calculator footer markup")


if __name__ == "__main__":
    main()
