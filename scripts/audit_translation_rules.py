#!/usr/bin/env python3
"""
audit_translation_rules.py — Structural checks for Little Brother translation rule files.

Checks:
  glossary.tsv      — column structure, duplicates, PLACEHOLDER/TODO markers, whitespace
  TRANSLATION_GUIDE.md — duplicate headings, [TODO] markers, repeated bullets, obsolete
                         credit wording, references to missing files/commands
  CHARACTERS.md     — same checks as TRANSLATION_GUIDE.md; pronoun contradiction detection

Exit codes:
  0  — no errors (warnings only or all clean)
  1  — structural errors found

Semantic contradiction detection is a responsibility of the Claude skill, not this script.
"""

import re
import sys
import pathlib
from collections import defaultdict, Counter

REPO = pathlib.Path(__file__).resolve().parent.parent

GLOSSARY     = REPO / "glossary.tsv"
GUIDE        = REPO / "TRANSLATION_GUIDE.md"
CHARACTERS   = REPO / "CHARACTERS.md"

KNOWN_COMMANDS = {
    "/lb-bootstrap", "/lb-translate", "/lb-postcheck",
    "/lb-full-recheck", "/lb-rule-update", "/lb-rule-audit",
}

KNOWN_RULE_FILES = {
    "TRANSLATION_GUIDE.md", "CHARACTERS.md", "glossary.tsv",
    "CLAUDE.md",
}

OBSOLETE_CREDIT_STRINGS = [
    "公式日本語版", "公認翻訳", "正規翻訳", "非公式日本語訳",
    "日本語訳*: 高須正和",   # old single-author credit line pattern
]

PRONOUN_MAP = {
    "Marcus": ["僕"],
    "Doctorow": ["私"],
    "Cory Doctorow": ["私"],
}

errors   = []
warnings = []


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def err(location: str, msg: str):
    errors.append(f"  [ERROR] {location}: {msg}")

def warn(location: str, msg: str):
    warnings.append(f"  [WARN]  {location}: {msg}")


def _norm_key(s: str) -> str:
    """Case-fold + strip punctuation for fuzzy duplicate detection."""
    return re.sub(r"[^a-z0-9぀-鿿]", "", s.lower())


# ─────────────────────────────────────────────────────────────────────────────
# glossary.tsv
# ─────────────────────────────────────────────────────────────────────────────

def check_glossary():
    if not GLOSSARY.exists():
        err("glossary.tsv", "File not found")
        return

    raw = GLOSSARY.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as e:
        err("glossary.tsv", f"UTF-8 decode error: {e}")
        return

    lines = text.splitlines()
    if not lines:
        err("glossary.tsv", "File is empty")
        return

    header = lines[0]
    if header != "source_term\tja_term\tnote":
        err("glossary.tsv line 1", f"Header mismatch — got: {header!r}")

    seen_source: dict[str, int] = {}          # exact source_term → first line
    seen_norm:   dict[str, tuple] = {}        # normalised → (term, first line)
    seen_notes:  dict[str, int] = {}          # exact note → first line
    ja_by_source: dict[str, list] = defaultdict(list)  # source → [ja_terms]

    for lineno, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue

        # Detect accidental space separation instead of tabs
        if "\t" not in line:
            err(f"glossary.tsv line {lineno}",
                f"No tab separator — may be space-separated: {line[:80]!r}")
            continue

        cols = line.split("\t")
        if len(cols) != 3:
            err(f"glossary.tsv line {lineno}",
                f"Expected 3 tab-separated columns, got {len(cols)}: {line[:80]!r}")
            continue

        src, ja, note = cols

        # Leading/trailing whitespace
        for i, (col_name, col_val) in enumerate([("source_term", src), ("ja_term", ja), ("note", note)]):
            if col_val != col_val.strip():
                err(f"glossary.tsv line {lineno}",
                    f"Leading/trailing whitespace in {col_name}: {col_val!r}")

        # Empty required columns
        if not src.strip():
            err(f"glossary.tsv line {lineno}", "Empty source_term")
            continue
        if not ja.strip():
            err(f"glossary.tsv line {lineno}",
                f"Empty ja_term for source_term={src!r}")

        # Exact duplicate source_term
        if src in seen_source:
            err(f"glossary.tsv line {lineno}",
                f"Duplicate source_term {src!r} (first seen line {seen_source[src]})")
        else:
            seen_source[src] = lineno

        # Case-insensitive / punctuation-normalised duplicates (warn only)
        nk = _norm_key(src)
        if nk in seen_norm and seen_norm[nk][0] != src:
            warn(f"glossary.tsv line {lineno}",
                 f"Near-duplicate of {seen_norm[nk][0]!r} (line {seen_norm[nk][1]}): {src!r}")
        else:
            seen_norm[nk] = (src, lineno)

        # Conflicting ja_term for same source_term — collect all renderings
        ja_by_source[src].append((ja.strip(), lineno))

        # Exact duplicate note
        if note.strip() and note.strip() in seen_notes:
            warn(f"glossary.tsv line {lineno}",
                 f"Exact duplicate note (also line {seen_notes[note.strip()]}): {note[:60]!r}")
        elif note.strip():
            seen_notes[note.strip()] = lineno

        # Unresolved markers
        for marker in ("PLACEHOLDER", "[TODO]", "TODO:"):
            if marker in note:
                warn(f"glossary.tsv line {lineno}",
                     f"Unresolved marker {marker!r} in note for {src!r}")
        if "[TODO]" in ja or "PLACEHOLDER" in ja:
            err(f"glossary.tsv line {lineno}",
                f"Unresolved marker in ja_term for {src!r}: {ja!r}")

    # Conflicting ja renderings for same source_term
    for src, entries in ja_by_source.items():
        if len(entries) > 1:
            unique_ja = set(j for j, _ in entries)
            if len(unique_ja) > 1:
                err("glossary.tsv",
                    f"Conflicting ja_term for {src!r}: {sorted(unique_ja)}")


# ─────────────────────────────────────────────────────────────────────────────
# Markdown rule files (TRANSLATION_GUIDE.md and CHARACTERS.md)
# ─────────────────────────────────────────────────────────────────────────────

def check_markdown_file(path: pathlib.Path):
    label = path.name

    if not path.exists():
        err(label, "File not found")
        return

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        err(label, f"UTF-8 decode error: {e}")
        return

    lines = text.splitlines()

    # Duplicate headings
    heading_re = re.compile(r"^(#{1,6})\s+(.+)$")
    seen_headings: dict[str, int] = {}
    for lineno, line in enumerate(lines, 1):
        m = heading_re.match(line)
        if m:
            heading_text = m.group(2).strip()
            key = heading_text.lower()
            if key in seen_headings:
                warn(label,
                     f"Duplicate heading {heading_text!r} at line {lineno} "
                     f"(first seen line {seen_headings[key]})")
            else:
                seen_headings[key] = lineno

    # Visible [TODO] markers
    for lineno, line in enumerate(lines, 1):
        if re.search(r"\[TODO\]", line) and not line.strip().startswith("<!--"):
            err(label, f"Line {lineno}: visible [TODO] marker: {line[:80]}")

    # Repeated identical bullet rules
    bullet_re = re.compile(r"^[-*]\s+(.+)$")
    bullet_texts: dict[str, int] = {}
    for lineno, line in enumerate(lines, 1):
        m = bullet_re.match(line.strip())
        if m:
            bullet_key = m.group(1).strip().lower()
            if bullet_key in bullet_texts:
                warn(label,
                     f"Line {lineno}: repeated bullet rule (first line {bullet_texts[bullet_key]}): "
                     f"{m.group(1)[:60]!r}")
            else:
                bullet_texts[bullet_key] = lineno

    # Duplicate canonical examples (blockquote lines)
    bq_re = re.compile(r"^>\s+(.+)$")
    bq_texts: dict[str, int] = {}
    for lineno, line in enumerate(lines, 1):
        m = bq_re.match(line)
        if m:
            bq_key = m.group(1).strip()
            if bq_key in bq_texts:
                warn(label,
                     f"Line {lineno}: duplicate blockquote/example (first line {bq_texts[bq_key]}): "
                     f"{bq_key[:60]!r}")
            else:
                bq_texts[bq_key] = lineno

    # Obsolete credit wording
    # Skip lines that are rules *about* avoiding the phrase (negation context)
    # and lines in the canonical footer template (which correctly uses 「〜ではありません」).
    NEGATION_MARKERS = ("never use", "do not", "no \"", "ではありません", "使わない", "使用しない")
    for lineno, line in enumerate(lines, 1):
        line_lower = line.lower()
        if any(neg in line_lower for neg in NEGATION_MARKERS):
            continue
        for obsolete in OBSOLETE_CREDIT_STRINGS:
            if obsolete in line:
                warn(label,
                     f"Line {lineno}: possibly obsolete credit wording {obsolete!r}: "
                     f"{line[:80]}")
                break

    # References to commands that do not exist
    command_re = re.compile(r"`(/lb-\S+)`")
    for lineno, line in enumerate(lines, 1):
        for match in command_re.finditer(line):
            cmd = match.group(1)
            if cmd not in KNOWN_COMMANDS:
                warn(label, f"Line {lineno}: reference to unknown command {cmd!r}")

    # References to rule files that do not exist
    rule_ref_re = re.compile(r"`([A-Z][A-Z_]+\.(?:md|tsv))`")
    for lineno, line in enumerate(lines, 1):
        for match in rule_ref_re.finditer(line):
            ref = match.group(1)
            if ref not in KNOWN_RULE_FILES:
                if not (REPO / ref).exists():
                    warn(label, f"Line {lineno}: reference to possibly missing file {ref!r}")


def check_characters_pronouns():
    """
    Mechanically detectable pronoun contradiction:
    If the file assigns 「僕」 to a character also assigned 「私」 in the same character block.
    Only checks named characters in PRONOUN_MAP for known violations.
    """
    label = "CHARACTERS.md"
    if not CHARACTERS.exists():
        return

    text = CHARACTERS.read_text(encoding="utf-8")

    # Look for Marcus being assigned 私
    if re.search(r"Marcus.*?「私」", text, re.DOTALL):
        # Only flag if it looks like a pronoun assignment, not a contrast/exception context
        for m in re.finditer(r"(Marcus[^#\n]{0,100}「私」)", text):
            ctx = m.group(1)
            if "not" not in ctx.lower() and "never" not in ctx.lower() and "avoid" not in ctx.lower():
                warn(label, f"Possible 私 pronoun assigned to Marcus: {ctx[:80]!r}")

    # Look for Doctorow being assigned 僕
    if re.search(r"Doctorow.*?「僕」", text, re.DOTALL):
        for m in re.finditer(r"(Doctorow[^#\n]{0,100}「僕」)", text):
            ctx = m.group(1)
            if "not" not in ctx.lower() and "never" not in ctx.lower():
                warn(label, f"Possible 僕 pronoun assigned to Doctorow: {ctx[:80]!r}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("audit_translation_rules.py")
    print("=" * 60)
    print()

    print("── glossary.tsv ──")
    check_glossary()

    print("── TRANSLATION_GUIDE.md ──")
    check_markdown_file(GUIDE)

    print("── CHARACTERS.md ──")
    check_markdown_file(CHARACTERS)
    check_characters_pronouns()

    print()
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(w)
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(e)
        print()
        print(f"Result: {len(errors)} error(s), {len(warnings)} warning(s) — FAIL")
        sys.exit(1)
    else:
        n = len(warnings)
        if n:
            print(f"Result: 0 errors, {n} warning(s) — PASS (warnings only)")
        else:
            print("Result: ✓ All structural checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
