"""Convert a copied spreadsheet HTML table into WhatsApp-safe plain text."""

from __future__ import annotations

import re
from html.parser import HTMLParser


class _FirstClipboardTable(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.seen = False
        self.depth = 0
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            if not self.seen:
                self.seen = True
                self.depth = 1
            elif self.depth:
                self.depth += 1
            return
        if self.depth != 1:
            return
        if tag == "tr":
            if self.row is None:
                self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "br" and self.cell is not None:
            self.cell.append("\n")

    def handle_data(self, data):
        if self.depth == 1 and self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag == "table":
            if self.depth:
                self.depth -= 1
            return
        if self.depth != 1:
            return
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            text = "".join(self.cell).replace("\xa0", " ")
            text = re.sub(r"[ \t\r\f\v]+", " ", text).strip()
            self.row.append(text)
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def calc_table_as_plain_text(html: str) -> str | None:
    """One space per column separator, one line per row, even empty rows.

    Only use a structured table if one really exists in the clipboard.
    Large HTML documents are ignored rather than parsed in the UI thread.
    """
    if not isinstance(html, str) or len(html) > 2_000_000 or "<table" not in html.lower():
        return None
    parser = _FirstClipboardTable()
    parser.feed(html)
    if not parser.rows:
        return None
    return "\n".join(" ".join(row) for row in parser.rows)
