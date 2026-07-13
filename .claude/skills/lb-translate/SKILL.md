# Skill: lb-translate

Translate a section of Little Brother into Japanese end-to-end.

## Arguments

Accepts any of:
- `ch01` through `ch21` — a single chapter
- `ch01-ch05` — a chapter range
- `introduction` — Cory Doctorow's introduction
- `epilogue` — the epilogue
- `afterword-schneier` — Bruce Schneier's afterword
- `afterword-huang` — Andrew "bunnie" Huang's afterword
- `bibliography` — bibliography
- `acknowledgments` — acknowledgments

## Steps

**Step 1 — Verify repo state**
```bash
git status && git log --oneline -3
```
Confirm clean working tree.

**Step 2 — Read project files (required before any translation)**
Read in this order:
1. `CLAUDE.md`
2. `TRANSLATION_GUIDE.md`
3. `CHARACTERS.md`
4. `glossary.tsv`
5. `docs/.vitepress/config.mts` (check existing sidebar entries)

**Step 3 — Locate and read the source section**
Find the relevant file in `source/sections/`:
- ch01 → `source/sections/02-ch01.txt`
- ch02 → `source/sections/03-ch02.txt`
- (pattern: file index = chapter number + 1, zero-padded to 2 digits)
- introduction → `source/sections/01-introduction.txt`
- epilogue → `source/sections/23-epilogue.txt`
- afterword-schneier → `source/sections/24-afterword-schneier.txt`
- afterword-huang → `source/sections/25-afterword-huang.txt`
- bibliography → `source/sections/26-bibliography.txt`
- acknowledgments → `source/sections/27-acknowledgments.txt`

If the section file is empty, the source is likely truncated. Alert the user and stop.

**Step 4 — Translate**
Write `docs/ja/<slug>.md`. Always use Python `write_bytes(text.encode('utf-8'))`.

Frontmatter for chapters:
```yaml
---
title: '第N章 タイトル'
translation_status: draft
---
```

Frontmatter for other sections:
```yaml
---
title: 'セクション名'
translation_status: draft
---
```

Apply all rules from `TRANSLATION_GUIDE.md` and `CHARACTERS.md`:
- 「僕」 for Marcus's narration
- Preserve bookstore dedications in structure
- Preserve handles: w1n5t0n, M1k3y, Xnet, DarkNet, ParanoidLinux
- Do not summarize, condense, or omit any content
- Include `<small>` attribution footer at bottom

**Step 5 — Update navigation**
Add entry to the appropriate sidebar group in `docs/.vitepress/config.mts`.
Update reading list in `docs/index.md`.
Use Python `write_bytes(content.encode('utf-8'))` for both files.

**Step 6 — Validate**
```bash
python3 scripts/check_translation_batch.py <target>
python3 scripts/validate_links.py
```
Zero errors required.

**Step 7 — Report (English only)**
Include:
- Files created/modified + byte counts
- Source section used
- Full validation output
- Any deviations, TODOs, or unresolved issues
- PowerShell commit command:
  ```powershell
  git add docs/ja/<slug>.md docs/.vitepress/config.mts docs/index.md
  git commit -m "trans: translate <section> (draft)"
  ```
