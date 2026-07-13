#!/usr/bin/env python3
"""
check_translation_batch.py — Read-only validation harness for Little Brother
Japanese translation sections.

Translation status levels (in ascending order of completeness):
  not_started   File is a placeholder; no content checks are applied.
  pilot         Early trial translation; light checks only (status + footer).
  draft         Full translation in progress; all checks applied.
  reviewed      Translation reviewed; all checks applied.
  complete      Translation finalised; all checks applied.

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
from typing import List, Optional, Tuple

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

# Status levels — lower index = less complete
STATUS_LEVELS = ["not_started", "pilot", "draft", "reviewed", "complete"]


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

MARKDOWN_FOOTNOTE_RE = re.compile(r"\[\^")
TOP_CREDIT_RE = re.compile(
    r"^\s*\*?(?:原著|著者|著作権|出版|本翻訳|日本語訳)[::：]",
    re.MULTILINE,
)
BARE_URL_JP_RE = re.compile(
    r"https?://[^\s\)\]>\"\']+[　-鿿＀-￯]"
)


def _read_frontmatter_status(lines: List[str]) -> Optional[str]:
    """Extract translation_status value from YAML frontmatter. Returns None if absent."""
    in_fm = False
    for i, line in enumerate(lines[:30]):
        if i == 0 and line.strip() == "---":
            in_fm = True
            continue
        if in_fm and line.strip() == "---":
            break
        if in_fm:
            m = re.match(r"translation_status:\s*(\S+)", line)
            if m:
                return m.group(1).strip()
    return None


def check_target(t: Target, issues: List[Tuple], summary: List[Tuple]):
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

    # ── Determine translation status ─────────────────────────────────────────
    status = _read_frontmatter_status(lines)

    if status is None:
        issues.append((tag, "NO-STATUS", "No translation_status field in frontmatter"))
        # Cannot determine skip level; fall through with all checks
        status = "draft"  # treat as needing full check
    elif status not in STATUS_LEVELS:
        issues.append((tag, "BAD-STATUS",
                       f"Unknown translation_status: {status!r} "
                       f"(valid: {', '.join(STATUS_LEVELS)})"))
        status = "draft"

    summary.append((tag, status))

    # not_started: file is a placeholder — skip ALL content checks
    if status == "not_started":
        return

    # ── Checks that apply to pilot and above ─────────────────────────────────

    # footer
    if "<small>" not in text:
        issues.append((tag, "NO-FOOTER", "Missing <small> attribution footer"))

    # ── Checks that apply to draft and above ─────────────────────────────────

    if status in ("draft", "reviewed", "complete"):

        # top credit block in first 30 lines of body (after frontmatter)
        head = "\n".join(lines[:30])
        for mm in TOP_CREDIT_RE.finditer(head):
            lineno = head[:mm.start()].count("\n") + 1
            issues.append((tag, "TOP-CREDIT",
                           f"Line ~{lineno}: credit block in first 30 lines — "
                           f"{mm.group().strip()[:60]}"))

        # Markdown footnote syntax
        for i, line in enumerate(lines, 1):
            if MARKDOWN_FOOTNOTE_RE.search(line):
                issues.append((tag, "MD-FOOTNOTE",
                               f"Line {i}: Markdown footnote [^ — {line[:80]}"))

        # bare URL followed by Japanese
        for i, line in enumerate(lines, 1):
            if BARE_URL_JP_RE.search(line):
                issues.append((tag, "BARE-URL",
                               f"Line {i}: bare URL + Japanese — {line[:100]}"))

        # Marcus pronoun check (chapters only)
        if t.kind == "chapter":
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
    summary: List[Tuple] = []

    ch_count = sum(1 for t in targets if t.kind == "chapter")
    sec_count = sum(1 for t in targets if t.kind == "section")
    desc = []
    if ch_count:
        desc.append(f"{ch_count} chapter(s)")
    if sec_count:
        desc.append(f"{sec_count} section(s)")
    print(f"Checking {', '.join(desc)}...\n")

    for t in targets:
        check_target(t, issues, summary)

    # ── Status summary ────────────────────────────────────────────────────────
    counts = {s: 0 for s in STATUS_LEVELS}
    for _tag, st in summary:
        if st in counts:
            counts[st] += 1

    print("Translation status summary:")
    for level in STATUS_LEVELS:
        if counts[level] or level in ("not_started", "draft", "complete"):
            print(f"  {level:12s}: {counts[level]}")
    print()

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
