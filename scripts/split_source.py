#!/usr/bin/env python3
"""
split_source.py — Split the official Little Brother TXT source into 29 sections.

Produces one file per section in source/sections/:

    00-front-matter.txt          License notice, READ THIS FIRST, book header
    01-introduction.txt          Cory Doctorow's Introduction
    02-ch01.txt                  Chapter 1
    03-ch02.txt                  Chapter 2
    ...
    22-ch21.txt                  Chapter 21
    23-epilogue.txt              Epilogue
    24-afterword-schneier.txt    Afterword by Bruce Schneier
    25-afterword-huang.txt       Afterword by Andrew "bunnie" Huang
    26-bibliography.txt          Bibliography
    27-acknowledgments.txt       Acknowledgments
    28-license.txt               Complete Creative Commons legal code

Usage:
    python3 scripts/split_source.py [--source path/to/file.txt]

Default source: source/original/Cory_Doctorow_-_Little_Brother.txt

Content-conservation guarantee:
    The concatenation of all output section files (in order) equals the source
    file byte-for-byte. No characters are added, removed, or altered. Each
    section header line is included in the section it opens. The only
    "normalization" is that the source is read as UTF-8 text and written as
    UTF-8 text; line-ending characters are preserved as-is.

The script exits non-zero if:
    - the source file is missing
    - the source file cannot be decoded as UTF-8
    - any required section header is not detected (indicating an incomplete source)
    - content conservation fails (post-write integrity check)
"""

import re
import sys
import hashlib
import argparse
import pathlib

# ── Configuration ─────────────────────────────────────────────────────────────

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO / "source" / "original" / "Cory_Doctorow_-_Little_Brother.txt"
SECTIONS_DIR = REPO / "source" / "sections"

# Minimum file size required to accept as a complete source (bytes).
# The full novel TXT is ~450–550 KB. Anything under this threshold is partial.
MIN_SOURCE_BYTES = 400_000

# ── Section definitions ───────────────────────────────────────────────────────
# Each entry: (output_filename, list_of_header_regex_patterns)
# Patterns are matched case-insensitively against each stripped line.
# The FIRST line matching any pattern in a group triggers that section.
# Sections are detected in document order; the splitter never moves backward.

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
        [rf"^chapter {_n}\s*$"],
    ))

SECTION_MAP += [
    ("23-epilogue.txt", [
        r"^epilogue\s*$",
    ]),
    ("24-afterword-schneier.txt", [
        r"^afterword\s+by\s+bruce\s+schneier",
    ]),
    ("25-afterword-huang.txt", [
        r"^afterword\s+by\s+andrew",
        r"^afterword\s+by\s+bunnie",
    ]),
    ("26-bibliography.txt", [
        r"^bibliography\s*$",
        r"^further\s+reading\s*$",
    ]),
    ("27-acknowledgments.txt", [
        r"^acknowledgments\s*$",
        r"^acknowledgements\s*$",
    ]),
    ("28-license.txt", [
        r"^creative\s+commons\s+legal\s+code\s*$",
        r"^creative\s+commons\s+attribution.noncommercial.sharealike",
    ]),
]

# Required section headers (these must be detected or the split is considered
# incomplete and the script exits non-zero).
REQUIRED_SECTIONS = {
    "01-introduction.txt",
    "02-ch01.txt",
    "22-ch21.txt",
    "23-epilogue.txt",
    "24-afterword-schneier.txt",
    "25-afterword-huang.txt",
    "28-license.txt",
}


def compile_map(section_map):
    return [(fn, [re.compile(p, re.IGNORECASE) for p in pats])
            for fn, pats in section_map]


def split_source(source_path: pathlib.Path):
    """
    Read source_path and split it into sections.
    Returns dict {filename: str_content}.
    Exits non-zero on any fatal error.
    """
    if not source_path.exists():
        print(
            f"ERROR: Source file not found: {source_path}\n"
            f"\nDownload the complete file:\n"
            f"  curl -L -o '{source_path}' \\\n"
            f"    http://craphound.com/littlebrother/Cory_Doctorow_-_Little_Brother.txt\n"
            f"The complete file is approximately 450–550 KB.",
            file=sys.stderr,
        )
        sys.exit(1)

    size = source_path.stat().st_size
    if size < MIN_SOURCE_BYTES:
        print(
            f"ERROR: Source file is only {size:,} bytes — this looks like a partial/truncated download.\n"
            f"The complete Little Brother TXT is approximately 450–550 KB.\n"
            f"Download the full file from:\n"
            f"  http://craphound.com/littlebrother/Cory_Doctorow_-_Little_Brother.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # Read as bytes then decode so no platform newline conversion occurs.
        # write_bytes() below also bypasses Windows \n→\r\n translation.
        raw_text = source_path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"ERROR: Source file is not valid UTF-8: {e}", file=sys.stderr)
        sys.exit(1)

    compiled = compile_map(SECTION_MAP)
    all_fnames = [fn for fn, _ in SECTION_MAP]
    buckets = {fn: [] for fn in all_fnames}

    current_section = "00-front-matter.txt"
    current_idx = 0

    lines = raw_text.splitlines(keepends=True)
    for line in lines:
        stripped = line.strip()
        # Try to advance to a later section
        matched = False
        if stripped:
            for idx, (fname, regexes) in enumerate(compiled):
                if idx <= current_idx:
                    continue
                for rx in regexes:
                    if rx.match(stripped):
                        current_section = fname
                        current_idx = idx
                        matched = True
                        break
                if matched:
                    break
        buckets[current_section].append(line)

    return {fn: "".join(lines_list) for fn, lines_list in buckets.items()}


def write_sections(buckets: dict):
    SECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for fname, content in buckets.items():
        out = SECTIONS_DIR / fname
        encoded = content.encode("utf-8")
        # write_bytes avoids platform newline conversion (LF→CRLF on Windows).
        out.write_bytes(encoded)
        results.append((fname, len(content.splitlines()), len(encoded)))
    return results


def verify_conservation(source_path: pathlib.Path, all_fnames: list):
    """Post-write check: concatenation of sections == source bytes."""
    source_bytes = source_path.read_bytes()
    combined = b"".join(
        (SECTIONS_DIR / fn).read_bytes()
        for fn in all_fnames
        if (SECTIONS_DIR / fn).exists()
    )
    if source_bytes != combined:
        src_h = hashlib.sha256(source_bytes).hexdigest()[:12]
        comb_h = hashlib.sha256(combined).hexdigest()[:12]
        print(
            f"ERROR: Content conservation check FAILED.\n"
            f"  source SHA256[:12]: {src_h}\n"
            f"  concat SHA256[:12]: {comb_h}\n"
            f"  source size: {len(source_bytes)} bytes\n"
            f"  concat size: {len(combined)} bytes",
            file=sys.stderr,
        )
        sys.exit(1)
    return len(source_bytes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=DEFAULT_SOURCE,
        help=f"Path to source TXT (default: {DEFAULT_SOURCE})",
    )
    args = parser.parse_args()

    print(f"Source : {args.source}")
    print(f"Output : {SECTIONS_DIR}/\n")

    buckets = split_source(args.source)
    results = write_sections(buckets)

    all_fnames = [fn for fn, _ in SECTION_MAP]
    empty = []
    missing_required = []

    for fname, n_lines, n_bytes in results:
        status = "OK" if n_bytes > 0 else "EMPTY"
        req = "*" if fname in REQUIRED_SECTIONS else " "
        print(f"  [{status:5s}]{req} {fname:45s}  {n_lines:6d} lines  {n_bytes:9d} bytes")
        if n_bytes == 0:
            empty.append(fname)
            if fname in REQUIRED_SECTIONS:
                missing_required.append(fname)

    print(f"\nTotal: {len(results)} sections")

    # Content conservation check (hard failure)
    total_bytes = verify_conservation(args.source, all_fnames)
    print(f"Content conservation: OK ({total_bytes:,} bytes round-tripped)")

    if missing_required:
        print(
            f"\nERROR: {len(missing_required)} required section(s) are empty — "
            f"source is likely incomplete:",
            file=sys.stderr,
        )
        for s in missing_required:
            print(f"  {s}", file=sys.stderr)
        sys.exit(1)

    if empty:
        print(f"\nWARNING: {len(empty)} optional section(s) are empty.")

    print("\n✓ Split complete.")


if __name__ == "__main__":
    main()
