#!/usr/bin/env python3
"""
validate_sections.py — Verify the split source sections for Little Brother.

Checks:
  1. All expected section files exist in source/sections/.
  2. Chapters 1–21 are present exactly once.
  3. No section file is empty (which would indicate truncation or a missed header).
  4. No source content has disappeared: total character count of all sections equals
     the total character count of the TXT source file (within 1% tolerance for
     line-ending normalization).
  5. SHA-256 of source/original/Cory_Doctorow_-_Little_Brother.txt matches
     manifest.json's full_sha256 field (if that field is filled in).
  6. UTF-8 encoding is valid for all section files.

Usage:
    python3 scripts/validate_sections.py
"""

import hashlib
import json
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
SECTIONS_DIR = REPO / "source" / "sections"
SOURCE_TXT = REPO / "source" / "original" / "Cory_Doctorow_-_Little_Brother.txt"
MANIFEST = REPO / "source" / "manifest.json"

EXPECTED_SECTIONS = [
    "00-front-matter.txt",
    "01-introduction.txt",
] + [f"{n + 1:02d}-ch{n:02d}.txt" for n in range(1, 22)] + [
    "23-epilogue.txt",
    "24-afterword-schneier.txt",
    "25-afterword-huang.txt",
    "26-bibliography.txt",
    "27-acknowledgments.txt",
]

CHAPTER_SECTIONS = [f"{n + 1:02d}-ch{n:02d}.txt" for n in range(1, 22)]

errors: list[str] = []
warnings: list[str] = []


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def check_expected_sections():
    """Check 1: all expected sections exist."""
    for fname in EXPECTED_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists():
            errors.append(f"MISSING section: {fname}")


def check_chapters_once():
    """Check 2: chapters 1–21 present exactly once."""
    import re as _re
    ch_num_rx = _re.compile(r"\d+-ch(\d+)\.txt")
    for fname in CHAPTER_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists():
            continue  # Already caught above
        if p.stat().st_size == 0:
            continue  # Empty sections reported by check_no_empty_sections
        m = ch_num_rx.match(fname)
        if not m:
            continue
        n = str(int(m.group(1)))   # e.g. "1", "10", "21"
        content = p.read_text(encoding="utf-8", errors="replace")
        hits = _re.findall(rf"(?im)^chapter\s+{n}\b", content)
        if len(hits) == 0:
            warnings.append(f"CHAPTER-HEADER MISSING in {fname}: no 'Chapter {n}' line found")
        elif len(hits) > 1:
            errors.append(f"DUPLICATE chapter header in {fname}: found {len(hits)} occurrences")


def check_no_empty_sections():
    """Check 3: no section file is empty."""
    for fname in EXPECTED_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists():
            continue  # Already caught
        if p.stat().st_size == 0:
            errors.append(f"EMPTY section: {fname} (0 bytes — source may be truncated)")
        elif p.stat().st_size < 100:
            warnings.append(
                f"VERY SHORT section: {fname} ({p.stat().st_size} bytes) — "
                "check that header was detected correctly"
            )


def check_no_content_lost():
    """Check 4: total section content ≈ source TXT content."""
    if not SOURCE_TXT.exists():
        warnings.append(f"Source TXT not found at {SOURCE_TXT} — skipping content-loss check")
        return

    source_chars = len(SOURCE_TXT.read_text(encoding="utf-8", errors="replace"))
    section_chars = 0
    for fname in EXPECTED_SECTIONS:
        p = SECTIONS_DIR / fname
        if p.exists():
            section_chars += len(p.read_text(encoding="utf-8", errors="replace"))

    if source_chars == 0:
        warnings.append("Source TXT is empty — cannot verify content conservation")
        return

    diff_pct = abs(source_chars - section_chars) / source_chars * 100
    if diff_pct > 1.0:
        errors.append(
            f"CONTENT LOSS: source has {source_chars} chars, "
            f"sections total {section_chars} chars "
            f"({diff_pct:.1f}% difference > 1% tolerance)"
        )
    else:
        print(
            f"  Content conservation: source {source_chars} chars, "
            f"sections {section_chars} chars ({diff_pct:.2f}% diff — OK)"
        )


def check_source_checksum():
    """Check 5: source SHA-256 matches manifest (if manifest has full_sha256)."""
    if not MANIFEST.exists():
        warnings.append("manifest.json not found — skipping checksum check")
        return
    if not SOURCE_TXT.exists():
        warnings.append("Source TXT not found — skipping checksum check")
        return

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"manifest.json parse error: {e}")
        return

    for entry in manifest.get("sources", []):
        if entry.get("id") == "txt":
            expected = entry.get("full_sha256", "")
            if not expected or expected.startswith("FILL_IN"):
                warnings.append(
                    "manifest.json full_sha256 not yet set — "
                    "fill in after downloading the complete source file"
                )
                return
            actual = sha256_file(SOURCE_TXT)
            if actual != expected:
                errors.append(
                    f"CHECKSUM MISMATCH for {SOURCE_TXT.name}:\n"
                    f"  expected: {expected}\n"
                    f"  actual:   {actual}"
                )
            else:
                print(f"  Checksum OK: {actual[:16]}…")


def check_utf8_encoding():
    """Check 6: all section files are valid UTF-8."""
    for fname in EXPECTED_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists():
            continue
        try:
            p.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            errors.append(f"UTF-8 ERROR in {fname}: {e}")


def main():
    if not SECTIONS_DIR.exists():
        print(
            f"ERROR: sections directory not found: {SECTIONS_DIR}\n"
            "Run: python scripts/split_source.py",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Validating sections in {SECTIONS_DIR}/\n")

    check_expected_sections()
    check_chapters_once()
    check_no_empty_sections()
    check_no_content_lost()
    check_source_checksum()
    check_utf8_encoding()

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  ⚠  {w}")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  ✗  {e}")
        print(f"\n{len(errors)} error(s) found.")
        sys.exit(1)
    if not errors:
        if not warnings:
            print("\u2713 All section checks passed.")
        else:
            print(f"\n\u2713 Passed with {len(warnings)} warning(s).")


if __name__ == "__main__":
    main()
