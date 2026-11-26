#!/usr/bin/env python3
"""Turn the GROBID TEI XML served by OpenAlex into plain text.

Two shapes exist in the archive: most files are TEI with
<TEI><teiHeader/><text><body>, while an older minority wraps a lowercase <tei>
inside <html><body> with the sections directly under <text>. Element names are
matched case-insensitively, and the bibliography is dropped because reference
lists are noise for embedding and extraction.
"""
import gzip
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SKIP = {"teiheader", "listbibl"}
BLOCK = {"div", "p", "head", "item", "l", "cell", "row", "figure", "table", "note"}


def extract_text(raw):
    """XML bytes (optionally gzipped) to normalised plain text."""
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    root = ET.fromstring(raw)
    body = _find(root, "text")
    out = []
    _walk(body if body is not None else root, out)
    text = "".join(out)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _local(tag):
    return tag.rsplit("}", 1)[-1].lower()


def _find(node, name):
    if _local(node.tag) == name:
        return node
    for child in node:
        found = _find(child, name)
        if found is not None:
            return found
    return None


def _walk(node, out):
    name = _local(node.tag)
    if name in SKIP:
        if node.tail:
            out.append(node.tail)
        return
    block = name in BLOCK
    if block:
        out.append("\n")
    if node.text:
        out.append(node.text)
    for child in node:
        _walk(child, out)
    if block:
        out.append("\n")
    if node.tail:
        out.append(node.tail)


def _self_check():
    upper = (
        b'<?xml version="1.0"?><TEI xmlns="http://www.tei-c.org/ns/1.0">'
        b"<teiHeader><title>HEADERNOISE</title></teiHeader>"
        b"<text><body><div><head>Intro</head><p>Hello <hi>world</hi>.</p></div></body>"
        b"<back><listBibl><bibl>REFNOISE</bibl></listBibl></back></text></TEI>"
    )
    text = extract_text(upper)
    assert "Hello world." in text and "Intro" in text, text
    assert "HEADERNOISE" not in text and "REFNOISE" not in text, text

    lower = (
        b"<html><body><tei><text><div><head>Intro</head>"
        b"<p>Lower case shape.</p></div></text></tei></body></html>"
    )
    assert "Lower case shape." in extract_text(lower)

    assert extract_text(gzip.compress(upper)) == text
    print("tei_text self-check OK")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _self_check()
    else:
        for arg in sys.argv[1:]:
            body = extract_text(Path(arg).read_bytes())
            print(f"{arg}: {len(body)} chars, {len(body.split())} words")
