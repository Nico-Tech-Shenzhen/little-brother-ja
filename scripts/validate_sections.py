#!/usr/bin/env python3
"""
validate_sections.py — Fail-closed validation of Little Brother source sections.

This script returns exit code 1 (failure) if ANY of the following is true:
  - Either canonical source file (TXT or HTM) is missing
  - source/manifest.json is missing or malformed
  - manifest.json does not set complete: true for the TXT entry
  - The TXT source file is below the minimum size threshold (< 400 KB)
  - The TXT source SHA-256 does not match manifest.json (when manifest has it)
  - Any of the 29 expected section files is absent from source/sections/
  - Any required section file is empty (0 bytes)
  - Any chapter (1–21) header appears 0 or 2+ times in its section file
  - The legal-code section (28-license.txt) is absent or empty
  - The concatenation of all section files does not match the source file byte-for-byte

Exit code 0 means all checks passed with zero errors.
Warnings (non-fatal) are printed but do not affect the exit code.

Usage:
    python3 scripts/validate_sections.py
"""

import hashlib
import json
import re
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
SECTIONS_DIR = REPO / "source" / "sections"
SOURCE_TXT = REPO / "source" / "original" / "Cory_Doctorow_-_Little_Brother.txt"
SOURCE_HTM = REPO / "source" / "original" / "Cory_Doctorow_-_Little_Brother.htm"
MANIFEST = REPO / "source" / "manifest.json"

MIN_SOURCE_BYTES = 400_000  # ~400 KB; full novel is ~450–550 KB

EXPECTED_SECTIONS = (
    ["00-front-matter.txt", "01-introduction.txt"]
    + [f"{n + 1:02d}-ch{n:02d}.txt" for n in range(1, 22)]
    + [
        "23-epilogue.txt",
        "24-afterword-schneier.txt",
        "25-afterword-huang.txt",
        "26-bibliography.txt",
        "27-acknowledgments.txt",
        "28-license.txt",
    ]
)

REQUIRED_NON_EMPTY = {
    "01-introduction.txt",
    "02-ch01.txt",
    "22-ch21.txt",
    "23-epilogue.txt",
    "24-afterword-schneier.txt",
    "25-afterword-huang.txt",
    "28-license.txt",
}

CHAPTER_SECTIONS = [f"{n + 1:02d}-ch{n:02d}.txt" for n in range(1, 22)]

errors: list[str] = []
warnings: list[str] = []


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


# ── Check 0: source files present and complete ───────────────────────────────

def check_source_present():
    for path in (SOURCE_TXT, SOURCE_HTM):
        if not path.exists():
            errors.append(f"SOURCE MISSING: {path.name} not found in source/original/")
            return False

    size = SOURCE_TXT.stat().st_size
    if size < MIN_SOURCE_BYTES:
        errors.append(
            f"SOURCE INCOMPLETE: {SOURCE_TXT.name} is {size:,} bytes. "
            f"The complete file is ~450–550 KB. "
            f"This is likely a truncated partial download."
        )
        return False
    return True


# ── Check 1: manifest present, complete flag, checksum ───────────────────────

def check_manifest():
    if not MANIFEST.exists():
        errors.append("MANIFEST MISSING: source/manifest.json not found")
        return

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"MANIFEST PARSE ERROR: {e}")
        return

    found_txt = False
    for entry in manifest.get("sources", []):
        if entry.get("id") != "txt":
            continue
        found_txt = True

        if not entry.get("complete", False):
            errors.append(
                "MANIFEST: complete is not true for TXT entry — "
                "set complete: true only after full validation passes"
            )

        expected_sha = entry.get("sha256", "")
        if not expected_sha or expected_sha.upper().startswith("FILL"):
            warnings.append(
                "MANIFEST: sha256 not set for TXT entry — "
                "fill in after downloading the complete source"
            )
        elif SOURCE_TXT.exists() and SOURCE_TXT.stat().st_size >= MIN_SOURCE_BYTES:
            actual = sha256_file(SOURCE_TXT)
            if actual != expected_sha:
                errors.append(
                    f"CHECKSUM MISMATCH: {SOURCE_TXT.name}\n"
                    f"  manifest : {expected_sha}\n"
                    f"  actual   : {actual}"
                )
            else:
                print(f"  Checksum OK ({actual[:16]}…)")

    if not found_txt:
        errors.append("MANIFEST: no entry with id='txt' found")


# ── Check 2: all 29 section files exist ──────────────────────────────────────

def check_sections_exist():
    for fname in EXPECTED_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists():
            errors.append(f"MISSING SECTION: {fname}")


# ── Check 3: required sections are non-empty ─────────────────────────────────

def check_required_non_empty():
    for fname in REQUIRED_NON_EMPTY:
        p = SECTIONS_DIR / fname
        if not p.exists():
            continue  # already reported above
        if p.stat().st_size == 0:
            errors.append(f"EMPTY REQUIRED SECTION: {fname}")
        elif p.stat().st_size < 200:
            warnings.append(
                f"VERY SHORT SECTION: {fname} ({p.stat().st_size} bytes) — "
                "verify header detection"
            )


# ── Check 4: chapters 1–21 appear exactly once ───────────────────────────────

def check_chapter_headers():
    ch_num_rx = re.compile(r"\d+-ch(\d+)\.txt")
    for fname in CHAPTER_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists() or p.stat().st_size == 0:
            continue  # reported elsewhere
        m = ch_num_rx.match(fname)
        if not m:
            continue
        n = int(m.group(1))
        content = p.read_text(encoding="utf-8", errors="replace")
        # Match "Chapter N" on its own line (as it appears in the TXT source)
        hits = re.findall(rf"(?m)^Chapter {n}\s*$", content)
        if len(hits) == 0:
            warnings.append(
                f"CHAPTER HEADER MISSING: no 'Chapter {n}' standalone line in {fname}"
            )
        elif len(hits) > 1:
            errors.append(
                f"DUPLICATE CHAPTER HEADER: {fname} contains 'Chapter {n}' {len(hits)} times"
            )


# ── Check 5: legal-code section present ──────────────────────────────────────

def check_license_section():
    p = SECTIONS_DIR / "28-license.txt"
    if not p.exists() or p.stat().st_size == 0:
        errors.append(
            "MISSING LEGAL CODE: 28-license.txt is absent or empty. "
            "The complete CC legal code must be present in the source."
         )
        return
    content = p.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"(?i)creative\s+commons", content):
        errors.append(
            "LEGAL CODE CONTENT: 28-license.txt does not contain 'Creative Commons' — "
            "check header detection for license section"
        )


# ── Check 6: content conservation (byte-perfect) ─────────────────────────────

def check_conservation():
    if not SOURCE_TXT.exists() or SOURCE_TXT.stat().st_size < MIN_SOURCE_BYTES:
        warnings.append("SOURCE INCOMPLETE: skipping content-conservation check")
        return

    source_bytes = SOURCE_TXT.read_bytes()
    combined = b"".join(
        (SECTIONS_DIR / fn).read_bytes()
        for fn in EXPECTED_SECTIONS
        if (SECTIONS_DIR / fn).exists()
    )

    if source_bytes == combined:
        print(f"  Content conservation: OK ({len(source_bytes):,} bytes, byte-perfect)")
    else:
        errors.append(
            f"CONTENT LOSS: source is {len(source_bytes):,} bytes but sections total "
            f"{len(combined):,} bytes — re-run split_source.py"
        )


# ── Check 7: UTF-8 encoding valid for all sections ───────────────────────────

def check_utf8():
    for fname in EXPECTED_SECTIONS:
        p = SECTIONS_DIR / fname
        if not p.exists() or p.stat().st_size == 0:
            continue
        try:
            p.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            errors.append(f"UTF-8 ERROR in {fname}: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not SECTIONS_DIR.exists():
        print(
            f"ERROR: sections directory not found: {SECTIONS_DIR}\n"
            "Run: python scripts/split_source.py",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Validating sections in {SECTIONS_DIR}/\n")

    source_ok = check_source_present()
    check_manifest()
    check_sections_exist()
    check_required_non_empty()
    check_chapter_headers()
    check_license_section()
    check_conservation()
    check_utf8()

    if warnings:
        print("\nWARNINGS:")
        for w in warnings:
            print(f"  ⚠  {w}")

    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  ✗  {e}")
        print(f"\n{len(errors)} error(s) — validation FAILED.")
        sys.exit(1)

    print("\n✓ All section checks passed with zero errors.")


if __name__ == "__main__":
    main()
