#!/usr/bin/env python3
"""
validate_links.py
Check that all image references in docs/**/*.md point to files that exist.
VitePress convention: /images/foo.png => docs/public/images/foo.png

Usage: python3 scripts/validate_links.py
"""
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"
PUBLIC_DIR = DOCS_DIR / "public"

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\((/[^)#\s]+)")

errors: list[str] = []
warnings: list[str] = []


def resolve_vitepress_path(src: str) -> Path:
    """Resolve a VitePress URL path to a filesystem path."""
    stripped = src.lstrip("/")
    public_candidate = PUBLIC_DIR / stripped
    if public_candidate.exists():
        return public_candidate
    docs_candidate = DOCS_DIR / stripped
    if docs_candidate.exists():
        return docs_candidate
    docs_md = (DOCS_DIR / stripped).with_suffix(".md")
    if docs_md.exists():
        return docs_md
    return public_candidate


def check_file(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    rel = md_path.relative_to(REPO_ROOT)

    # Image refs
    for alt, src in IMG_RE.findall(text):
        if src.startswith("http"):
            continue
        if src.startswith("/"):
            resolved = resolve_vitepress_path(src)
        else:
            resolved = (md_path.parent / src).resolve()

        if not resolved.exists():
            errors.append(
                f"{rel}: broken image '{src}' "
                f"(expected at {resolved.relative_to(REPO_ROOT)})"
            )

    # Internal markdown links (absolute paths only)
    for text_content, href in LINK_RE.findall(text):
        href_path = href.split("#")[0]
        if not href_path or href_path.startswith("http"):
            continue
        resolved = resolve_vitepress_path(href_path)
        if not resolved.exists():
            warnings.append(f"{rel}: unresolved link '{href}'")


def main():
    md_files = list(DOCS_DIR.rglob("*.md"))
    print(f"Checking {len(md_files)} markdown files ...\n")

    for f in sorted(md_files):
        check_file(f)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  ⚠  {w}")
        print()

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ✗  {e}")
        print(f"\n{len(errors)} error(s) found.")
        sys.exit(1)
    else:
        print(f"✓ All links OK  ({len(warnings)} warning(s))")


if __name__ == "__main__":
    main()
