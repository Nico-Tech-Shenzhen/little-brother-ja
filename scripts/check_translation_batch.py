#!/usr/bin/env python3
"""
check_translation_batch.py — Read-only validation harness for Little Brother
Japanese translation sections.

Usage:
    python3 scripts/check_translation_batch.py 1
    python3 scripts/check_translation_batch.py 1 5
    python3 scripts/check_translation_batch.py 1-5
    python3 scripts/check_translation_batch.py epilogue
    python3 scripts/check_translation_batch.py all

Book structure:
    Chapters 1–21   →  docs/ja/ch01.md … ch21.md
    epilogue        →  docs/ja/epilogue.md
    introduction    →  docs/ja/introduction.md
    afterword-schneier  →  docs/ja/afterword-schneier.md
    afterword-huang     →  docs/ja/afterword-huang.md
    bibliography    →  docs/ja/bibliography.md
    acknowledgments →  docs/ja/acknowledgments.md
"""

import re
import sys
import pathlib
from dataclasses import dataclass
from typing import List, Tuple, Set

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS_JA = REPO / "docs" / "ja"

MAX_CHAPTER = 21

NON_CHAPTER_SECTIONS = [
    "introduction",
    "epilogue",
    "afterword-schneier",
    "afterword-huang",
    "bibliography",
    "acknowledgments",
]


@dataclass
class Target:
    kind: str       # 'chapter' or 'section'
    ident: object   # int for chapter, str slug for section

    @property
    def tag(self):
        if self.kind == "chapter":
            return f"ch{self.ident:02d}"
        return self.ident

    @property
    def path(self):
        return DOCS_JA / f"{self.tag}.md"


def _chapter_targets(a: int, b: int) -> List[Target]:
    a = max(1, a)
    b = min(MAX_CHAPTER, b)
    return [Target("chapter", n) for n in range(a, b + 1)]


def parse_args(argv: List[str]) -> List[Target]:
    args = argv[1:]
    if not args or args == ["all"]:
        chapters = _chapter_targets(1, MAX_CHAPTER)
        sections = [Target("section", s) for s in NON_CHAPTER_SECTIONS]
        return chapters + sections

    targets: List[Target] = []
    i = 0
    while i < len(args):
        tok = args[i]
        # Named section
        if tok in NON_CHAPTER_SECTIONS:
            targets.append(Target("section", tok))
            i += 1
            continue
        # Pure digit: chapter N
        if re.fullmatch(r"\d+", tok):
            n = int(tok)
            if i + 1 < len(args) and re.fullmatch(r"\d+", args[i + 1]):
                targets.extend(_chapter_targets(n, int(args[i + 1])))
                i += 2
                continue
            targets.extend(_chapter_targets(n, n))
            i += 1
            continue
        # N-M range
        m = re.fullmatch(r"(\d+)-(\d+)", tok)
        if m:
            targets.extend(_chapter_targets(int(m.group(1)), int(m.group(2))))
            i += 1
            continue
        print(f"WARNING: unrecognised argument {tok!r} — skipped", file=sys.stderr)
        i += 1

    return targets


# ── check patterns ─────────────────────────────────────────────────────────

MOJIBAKE_RE = re.compile(r"[^\x00-\x7F　-鿿豈-﫿＀-￯ -~ -ÿĀ-ɏ]")
MARKDOWN_FOOTNOTE_RE = re.compile(r"\[\^")
TOP_CREDIT_RE = re.compile(
    r"^\s*\*?(?:原著|著者|著作権|出版|本翻訳|日本語訳)[::：]",
    re.MULTILINE,
)
BARE_URL_JP_RE = re.compile(
    r"https?://[^\s\)\]>\"\']+[　-鿿＀-￯]"
)


def check_target(t: Target, issues: List[Tuple]):
    tag = t.tag
    path = t.path

    if not path.exists():
        issues.append((tag, "MISSING", f"File not found: {path}"))
        return

    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        issues.append((tag, "MOJIBAKE", f"UTF-8 decode error: {e}"))
        return

    lines = text.splitlines()

    # 1 — check translation_status in frontmatter
    fm_end = 0
    in_fm = False
    has_status = False
    for i, line in enumerate(lines[:30]):
        if i == 0 and line.strip() == "---":
            in_fm = True
            continue
        if in_fm and line.strip() == "---":
            fm_end = i
            break
        if in_fm and "translation_status" in line:
            has_status = True
    if not has_status:
        issues.append((tag, "NO-STATUS",
                       "No translation_status field in frontmatter"))

    # 2 — top credit block in first 30 lines
    head = "\n".join(lines[:30])
    for mm in TOP_CREDIT_RE.finditer(head):
        lineno = head[:mm.start()].count("\n") + 1
        issues.append((tag, "TOP-CREDIT",
                       f"Line ~{lineno}: credit block in first 30 lines — "
                       f"{mm.group().strip()[:60]}"))

    # 3 — attribution footer present
    if "<small>" not in text:
        issues.append((tag, "NO-FOOTER",
                       "Missing <small> attribution footer"))

    # 4 — Markdown footnote syntax
    for i, line in enumerate(lines, 1):
        if MARKDOWN_FOOTNOTE_RE.search(line):
            issues.append((tag, "MD-FOOTNOTE",
                           f"Line {i}: Markdown footnote [^ — {line[:80]}"))

    # 5 — bare URL followed by Japanese
    for i, line in enumerate(lines, 1):
        if BARE_URL_JP_RE.search(line):
            issues.append((tag, "BARE-URL",
                           f"Line {i}: bare URL + Japanese — {line[:100]}"))

    # 6 — Marcus first-person check: look for 私 as narrator (red flag)
    if t.kind == "chapter":
        # Heuristic: 私は appearing more than 5 times may indicate wrong pronoun
        watashi_count = text.count("私は")
        boku_count = text.count("僕は")
        if watashi_count > 5 and boku_count < watashi_count:
            issues.append((tag, "PRONOUN",
                           f"「私は」 ({watashi_count}×) outnumbers 「僕は」 ({boku_count}×) — "
                           "check narrator pronoun (should be 僕 for Marcus)"))


def main():
    argv = sys.argv
    if len(argv) < 2 or argv[1:] == ["all"]:
        targets = parse_args(["script", "all"])
    else:
        targets = parse_args(argv)

    if not targets:
        print("No targets to check.")
        sys.exit(0)

    issues: List[Tuple] = []

    ch_count = sum(1 for t in targets if t.kind == "chapter")
    sec_count = sum(1 for t in targets if t.kind == "section")
    desc = []
    if ch_count:
        desc.append(f"{ch_count} chapter(s)")
    if sec_count:
        desc.append(f"{sec_count} section(s)")
    print(f"Checking {', '.join(desc)}...\n")

    for t in targets:
        check_target(t, issues)

    if issues:
        print("=" * 60)
        print("ISSUES FOUND")
        print("=" * 60)
        for tag, kind, msg in issues:
            print(f"  [{kind}] {tag}: {msg}")
        print()

    if not issues:
        print("✓ All checks passed.")
    else:
        serious = [i for i in issues if i[1] not in ("NO-STATUS",)]
        print(f"Total issues: {len(issues)}  ({len(serious)} serious)")

    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
