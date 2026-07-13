#!/usr/bin/env python3
"""
split_source.py — Split the official Little Brother TXT source into sections.

Produces one file per section in source/sections/:
    00-front-matter.txt          License notice and READ THIS FIRST
    01-introduction.txt          Cory Doctorow's Introduction (if present)
    02-ch01.txt                  Chapter 1
    03-ch02.txt                  Chapter 2
    ...
    22-ch21.txt                  Chapter 21
    23-epilogue.txt              Epilogue (if present)
    24-afterword-schneier.txt    Afterword by Bruce Schneier
    25-afterword-huang.txt       Afterword by Andrew "bunnie" Huang
    26-bibliography.txt          Bibliography (if present)
    27-acknowledgments.txt       Acknowledgments (if present)

Usage:
    python3 scripts/split_source.py [--source path/to/file.txt]

The default source file is:
    source/original/Cory_Doctorow_-_Little_Brother.txt

Rules:
  - All original text, paragraph order, emphasis markers, links, and section
    boundaries are preserved exactly. No normalization or rewriting.
  - Chapter bookstore dedications are kept as part of the chapter text.
  - Empty sections (no content between two headers) are written as empty files
    so that validate_sections.py can flag them.
  - The script is idempotent: running it again overwrites output files.
"""

import re
import sys
import argparse
import pathlib

# ── Configuration ────────────────────────────────────────────────────────────

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO / "source" / "original" / "Cory_Doctorow_-_Little_Brother.txt"
SECTIONS_DIR = REPO / "source" / "sections"

# Section definitions: (output_filename, list_of_header_patterns)
# Patterns are matched case-insensitively against stripped lines.
# The FIRST pattern in each list that matches a line triggers that section.
# Order matters: more specific patterns must come before broader ones.

SECTION_MAP = [
    ("00-front-matter.txt", [
        r"^little brother\s*$",
        r"^cory doctorow\s*$",
        r"^read this first\s*$",
        r"^&&&\s*$",
    ]),
    ("01-introduction.txt", [
        r"^introduction\s*$",
        r"^a note from the author\s*$",
        r"^foreword\s*$",
    ]),
]

# Chapters 1–21
for _n in range(1, 22):
    SECTION_MAP.append((
        f"{_n + 1:02d}-ch{_n:02d}.txt",
        [
            rf"^chapter {_n}\b",
            rf"^chapter {_n}[:\s]",
        ],
    ))

SECTION_MAP += [
    ("23-epilogue.txt", [
        r"^epilogue\s*$",
        r"^epilogue[:\s]",
    ]),
    ("24-afterword-schneier.txt", [
        r"^afterword\s+by\s+bruce\s+schneier",
        r"^bruce\s+schneier",
    ]),
    ("25-afterword-huang.txt", [
        r"^afterword\s+by\s+andrew",
        r"^afterword\s+by\s+bunnie",
        r"^andrew\s+[\"']?bunnie[\"']?\s+huang",
    ]),
    ("26-bibliography.txt", [
        r"^bibliography\s*$",
        r"^references\s*$",
        r"^further\s+reading\s*$",
    ]),
    ("27-acknowledgments.txt", [
        r"^acknowledgment",
        r"^acknowledgement",
        r"^thanks\s*$",
    ]),
]


def compile_patterns(section_map):
    """Return list of (filename, compiled_regex_list) pairs."""
    compiled = []
    for fname, patterns in section_map:
        compiled.append((fname, [re.compile(p, re.IGNORECASE) for p in patterns]))
    return compiled


def detect_section(line: str, compiled_map):
    """Return (index, filename) of the section this line starts, or None."""
    stripped = line.strip()
    if not stripped:
        return None
    for idx, (fname, regexes) in enumerate(compiled_map):
        for rx in regexes:
            if rx.match(stripped):
                return idx, fname
    return None


def split_source(source_path: pathlib.Path) -> dict:
    """
    Split source_path into sections.
    Returns a dict {filename: list_of_lines}.
    """
    if not source_path.exists():
        print(f"ERROR: Source file not found: {source_path}", file=sys.stderr)
        print(
            "Download the full source file first:\n"
            "  curl -L -o source/original/Cory_Doctorow_-_Little_Brother.txt \\\n"
            "       http://craphound.com/littlebrother/Cory_Doctorow_-_Little_Brother.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    compiled_map = compile_patterns(SECTION_MAP)
    all_fnames = [fname for fname, _ in SECTION_MAP]

    # Initialize buckets
    buckets = {fname: [] for fname in all_fnames}
    current_section = "00-front-matter.txt"

    lines = source_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

    for line in lines:
        result = detect_section(line, compiled_map)
        if result is not None:
            idx, fname = result
            # Only advance forward; never go backwards
            current_idx = all_fnames.index(current_section)
            if idx > current_idx:
                current_section = fname
                # Include the header line in the new section
                buckets[current_section].append(line)
                continue
        buckets[current_section].append(line)

    return buckets


def write_sections(buckets: dict):
    SECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for fname, lines in buckets.items():
        out = SECTIONS_DIR / fname
        content = "".join(lines)
        out.write_text(content, encoding="utf-8")
        written.append((fname, len(lines), len(content)))
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=DEFAULT_SOURCE,
        help=f"Path to source TXT file (default: {DEFAULT_SOURCE})",
    )
    args = parser.parse_args()

    print(f"Source: {args.source}")
    print(f"Output: {SECTIONS_DIR}/\n")

    buckets = split_source(args.source)
    written = write_sections(buckets)

    total_lines = 0
    empty = []
    for fname, n_lines, n_bytes in written:
        status = "OK" if n_lines > 0 else "EMPTY"
        print(f"  [{status:5s}] {fname:40s}  {n_lines:6d} lines  {n_bytes:8d} bytes")
        total_lines += n_lines
        if n_lines == 0:
            empty.append(fname)

    print(f"\nTotal: {len(written)} sections, {total_lines} lines")

    if empty:
        print(f"\nWARNING: {len(empty)} empty section(s) — source may be truncated or "
              "section headers not recognized:")
        for e in empty:
            print(f"  {e}")
        print("\nRun with the FULL source file to populate all sections.")
        sys.exit(1)
    else:
        print("\n✓ All sections written.")


if __name__ == "__main__":
    main()
