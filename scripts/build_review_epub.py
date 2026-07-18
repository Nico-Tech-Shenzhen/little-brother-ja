#!/usr/bin/env python3
"""Build the Japanese Little Brother review EPUB using only the standard library."""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import shutil
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "dist" / "little-brother-ja-review.epub"
TITLE = "Little Brother 日本語訳 レビュー版"
AUTHOR = "Cory Doctorow"
TRANSLATOR = "日本語訳・レビュー: ニコ技深圳コミュニティ / 高須正和（@tks）"

SECTIONS = [
    ("front-matter", "表紙・ライセンス表記"),
    ("introduction", "著者まえがき"),
    *[(f"ch{i:02d}", f"第{i}章") for i in range(1, 22)],
    ("epilogue", "エピローグ"),
    ("afterword-schneier", "あとがき — Bruce Schneier"),
    ("afterword-huang", 'あとがき — Andrew "bunnie" Huang'),
    ("bibliography", "参考文献"),
    ("acknowledgments", "謝辞"),
]


def strip_source_wrappers(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)
    text = re.sub(r"\n?<small>\s*.*?</small>\s*\Z", "\n", text, flags=re.S | re.I)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return text.strip() + "\n"


def inline(text: str) -> str:
    tokens: list[str] = []

    def hold(fragment: str) -> str:
        tokens.append(fragment)
        return f"\x00{len(tokens) - 1}\x00"

    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", lambda m: hold(f"<code>{m.group(1)}</code>"), text)
    text = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)|(?<!_)_([^_\n]+?)_(?!_)", lambda m: f"<em>{m.group(1) or m.group(2)}</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^\s)]+)(?:\s+[\"'][^\"']*[\"'])?\)",
        lambda m: hold(f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>'),
        text,
    )
    text = text.replace("  \n", "<br />\n")
    for index, token in enumerate(tokens):
        text = text.replace(f"\x00{index}\x00", token)
    return text


def markdown_to_xhtml(markdown: str) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    quote: list[str] = []
    list_kind: str | None = None

    def flush_paragraph() -> None:
        if paragraph:
            output.append(f"<p>{inline('\n'.join(paragraph))}</p>")
            paragraph.clear()

    def flush_quote() -> None:
        if quote:
            parts = [inline(part) for part in quote]
            output.append("<blockquote>" + "".join(f"<p>{part}</p>" for part in parts) + "</blockquote>")
            quote.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(f"</{list_kind}>")
            list_kind = None

    for raw in lines + [""]:
        line = raw.rstrip()
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        item = re.match(r"^\s*([-+*]|\d+\.)\s+(.+)$", line)
        if line.startswith(">"):
            flush_paragraph(); close_list()
            content = re.sub(r"^>\s?", "", line)
            if content:
                quote.append(content)
            continue
        flush_quote()
        if heading:
            flush_paragraph(); close_list()
            level = len(heading.group(1))
            output.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
        elif item:
            flush_paragraph()
            wanted = "ol" if item.group(1)[0].isdigit() else "ul"
            if list_kind != wanted:
                close_list(); output.append(f"<{wanted}>"); list_kind = wanted
            output.append(f"<li>{inline(item.group(2))}</li>")
        elif re.fullmatch(r"\s*([-*_])(?:\s*\1){2,}\s*", line):
            flush_paragraph(); close_list(); output.append("<hr />")
        elif not line.strip():
            flush_paragraph(); close_list()
        else:
            close_list(); paragraph.append(line)
    return "\n".join(output)


def xhtml_document(title: str, body: str, body_class: str = "section") -> str:
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja" lang="ja">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body class="{body_class}">{body}</body></html>'''


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))


def build(output: Path) -> None:
    missing = [slug for slug, _ in SECTIONS if not (ROOT / "docs" / "ja" / f"{slug}.md").is_file()]
    if missing:
        raise SystemExit("Missing Japanese section(s): " + ", ".join(missing))

    book_id = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, TITLE + '|' + AUTHOR)}"
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with tempfile.TemporaryDirectory(prefix="little-brother-epub-") as tmp:
        root = Path(tmp)
        oebps = root / "OEBPS"
        write_text(root / "mimetype", "application/epub+zip")
        write_text(root / "META-INF" / "container.xml", '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''')
        write_text(oebps / "style.css", '''@charset "UTF-8";
html { writing-mode: horizontal-tb; -epub-writing-mode: horizontal-tb; }
body { font-family: serif; line-height: 1.75; margin: 5%; }
h1 { font-size: 1.65em; margin-top: 0; } h2 { font-size: 1.3em; }
blockquote { margin: 1em 1.2em; padding-left: .8em; border-left: .18em solid #999; }
a { text-decoration: underline; } .section { break-before: page; page-break-before: always; }
.title-page { text-align: center; } .notice { margin-top: 3em; text-align: left; }
''')

        title_body = f'''<section epub:type="titlepage" xmlns:epub="http://www.idpf.org/2007/ops">
<h1>{html.escape(TITLE)}</h1><p>{html.escape(AUTHOR)}</p><p>{html.escape(TRANSLATOR)}</p>
<div class="notice"><h2>レビュー版について</h2><p>本書はレビュー用のドラフト版です。翻訳は校正・レビューにより変更される場合があります。</p>
<h2>ライセンス</h2><p>原著 <em>Little Brother</em> © 2008 Cory Doctorow / Tor Books</p>
<p>原著および本日本語訳は、クリエイティブ・コモンズ 表示—非営利—継承 3.0 非移植（CC BY-NC-SA 3.0）の条件で提供されます。</p>
<p><a href="https://creativecommons.org/licenses/by-nc-sa/3.0/">CC BY-NC-SA 3.0</a></p></div></section>'''
        write_text(oebps / "title.xhtml", xhtml_document(TITLE, title_body, "title-page"))

        for slug, label in SECTIONS:
            source = (ROOT / "docs" / "ja" / f"{slug}.md").read_text(encoding="utf-8")
            body = markdown_to_xhtml(strip_source_wrappers(source))
            write_text(oebps / f"{slug}.xhtml", xhtml_document(label, body))

        nav_items = "".join(f'<li><a href="{slug}.xhtml">{html.escape(label)}</a></li>' for slug, label in SECTIONS)
        nav = f'''<nav epub:type="toc" id="toc" xmlns:epub="http://www.idpf.org/2007/ops"><h1>目次</h1><ol><li><a href="title.xhtml">タイトル・権利表記</a></li>{nav_items}</ol></nav>'''
        write_text(oebps / "nav.xhtml", xhtml_document("目次", nav, "toc"))

        ncx_points = ['<navPoint id="title" playOrder="1"><navLabel><text>タイトル・権利表記</text></navLabel><content src="title.xhtml"/></navPoint>']
        for order, (slug, label) in enumerate(SECTIONS, 2):
            ncx_points.append(f'<navPoint id="{slug}" playOrder="{order}"><navLabel><text>{html.escape(label)}</text></navLabel><content src="{slug}.xhtml"/></navPoint>')
        write_text(oebps / "toc.ncx", f'''<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1"><head><meta name="dtb:uid" content="{book_id}"/></head><docTitle><text>{html.escape(TITLE)}</text></docTitle><navMap>{''.join(ncx_points)}</navMap></ncx>''')

        manifests = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>', '<item id="css" href="style.css" media-type="text/css"/>', '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>', '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>']
        manifests += [f'<item id="{slug}" href="{slug}.xhtml" media-type="application/xhtml+xml"/>' for slug, _ in SECTIONS]
        spine = ['<itemref idref="title"/>'] + [f'<itemref idref="{slug}"/>' for slug, _ in SECTIONS]
        opf = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="ja" prefix="dcterms: http://purl.org/dc/terms/">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="bookid">{book_id}</dc:identifier><dc:title>{html.escape(TITLE)}</dc:title><dc:creator>{AUTHOR}</dc:creator><dc:contributor>{html.escape(TRANSLATOR)}</dc:contributor><dc:language>ja</dc:language><dc:rights>CC BY-NC-SA 3.0; draft review edition</dc:rights><meta property="dcterms:modified">{modified}</meta></metadata>
<manifest>{''.join(manifests)}</manifest><spine toc="ncx">{''.join(spine)}</spine></package>'''
        write_text(oebps / "content.opf", opf)

        output.parent.mkdir(parents=True, exist_ok=True)
        temporary_output = output.with_suffix(".epub.tmp")
        with zipfile.ZipFile(temporary_output, "w") as archive:
            archive.write(root / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
            for path in sorted(root.rglob("*")):
                if path.is_file() and path.name != "mimetype":
                    archive.write(path, path.relative_to(root).as_posix(), compress_type=zipfile.ZIP_DEFLATED)
        temporary_output.replace(output)


def validate(epub: Path) -> list[str]:
    errors: list[str] = []
    expected = {"mimetype", "META-INF/container.xml", "OEBPS/content.opf", "OEBPS/nav.xhtml", "OEBPS/toc.ncx", "OEBPS/title.xhtml", "OEBPS/style.css"}
    expected |= {f"OEBPS/{slug}.xhtml" for slug, _ in SECTIONS}
    with zipfile.ZipFile(epub) as archive:
        names = archive.namelist()
        if names[0] != "mimetype" or archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            errors.append("mimetype must be the first, uncompressed ZIP member")
        if archive.read("mimetype") != b"application/epub+zip": errors.append("invalid mimetype")
        missing = expected - set(names)
        if missing: errors.append("missing members: " + ", ".join(sorted(missing)))
        for name in sorted(expected - {"mimetype", "OEBPS/style.css"}):
            try: ET.fromstring(archive.read(name))
            except ET.ParseError as exc: errors.append(f"invalid XML in {name}: {exc}")
        opf = archive.read("OEBPS/content.opf").decode("utf-8")
        nav = archive.read("OEBPS/nav.xhtml").decode("utf-8")
        if TITLE not in opf or AUTHOR not in opf or TRANSLATOR not in opf: errors.append("required metadata is incomplete")
        positions = [nav.find(f'href="{slug}.xhtml"') for slug, _ in SECTIONS]
        if any(pos < 0 for pos in positions) or positions != sorted(positions): errors.append("navigation is missing or out of order")
        for slug, _ in SECTIONS:
            content = archive.read(f"OEBPS/{slug}.xhtml").decode("utf-8")
            if "translation_status:" in content or "<small>" in content: errors.append(f"source wrapper remains in {slug}.xhtml")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", type=Path)
    args = parser.parse_args()
    output = args.validate_only or args.output
    if not args.validate_only: build(output)
    errors = validate(output)
    if errors:
        raise SystemExit("EPUB validation failed:\n- " + "\n- ".join(errors))
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"VALID: {output} ({output.stat().st_size} bytes, {len(SECTIONS)} sections, sha256={digest})")


if __name__ == "__main__":
    main()
