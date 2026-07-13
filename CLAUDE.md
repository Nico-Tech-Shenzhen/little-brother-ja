# CLAUDE.md — Little Brother 日本語訳

## Operational rules

1. **Always read `TRANSLATION_GUIDE.md` before any translation work.**
2. **Always consult `glossary.tsv` before translating technical or recurring terms.**
3. **Work and report in English** to reduce token usage. Japanese is required only for
   translated book content and public-facing Japanese pages (`docs/ja/`, `docs/index.md`).
   See **§ Operational language** below for the full rule.
4. **Never commit or push** to any remote unless explicitly instructed by the user.
5. **Do not call a section complete** unless all of the following are done:
   - Source section file exists in `source/sections/` and was produced by `scripts/split_source.py`
   - Translation written from the section source text (not from memory or assumptions)
   - `python scripts/validate_sections.py` passes with zero errors
   - Frontmatter field `translation_status` is accurate
6. **Do not re-state the full guide in reports.** Only report deviations, TODOs, errors,
   and quantitative results (word counts, validation output).
7. **Source files are in `source/original/`.** Never attempt to re-download them from the
   internet during a translation session. If a file is missing or corrupt, alert the user.
8. **`/lb-rule-update` edits only `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and/or `glossary.tsv`.**
   It must not edit translated section files or retranslate content unless explicitly instructed.
9. **`/lb-postcheck` and `/lb-full-recheck` are review-only.** They must not rewrite translated
   prose unless the user explicitly requests a separate fix task.

## Operational language

Use **English** for all workflow and development operations.

**Always English:**
- Claude reports, progress summaries, and explanations of changed files
- Validation and build result summaries
- Suggested commit messages and actual git commit messages
- Branch names, PR titles, and PR descriptions
- TODO comments that are not reader-facing
- Internal notes about source sections, validation, and build results

**Always Japanese:**
- Translated book content (`docs/ja/*.md`)
- Japanese reader-facing site text (homepage, credits, nav labels)
- Japanese headings and body text inside translated pages
- Japanese examples that intentionally belong in the translation

**Commit messages must be in English.**

Good:
```
trans: add Chapter 1 Japanese translation (draft)
fix: standardize pronoun usage in ch03
guide: update Marcus voice rules
docs: update site index links
```

Bad (do not use Japanese in commit messages):
```
第1章の日本語訳を追加
マーカスの語りを修正
```

## Book structure

*Little Brother* has the following sections. Translate in order, one section at a time.

| File | Section |
|------|---------|
| `source/sections/00-front-matter.txt` | License notice, READ THIS FIRST |
| `source/sections/01-introduction.txt` | Cory Doctorow's Introduction |
| `source/sections/02-ch01.txt` | Chapter 1 |
| `source/sections/03-ch02.txt` | Chapter 2 |
| … | … |
| `source/sections/22-ch21.txt` | Chapter 21 |
| `source/sections/23-epilogue.txt` | Epilogue |
| `source/sections/24-afterword-schneier.txt` | Afterword by Bruce Schneier |
| `source/sections/25-afterword-huang.txt` | Afterword by Andrew "bunnie" Huang |
| `source/sections/26-bibliography.txt` | Bibliography |
| `source/sections/27-acknowledgments.txt` | Acknowledgments |
| `source/sections/28-license.txt` | Complete Creative Commons legal code (not translated) |

**Chapters end at 21.** Do not create `docs/ja/ch22.md` or beyond.  
Each chapter maps to `docs/ja/chNN.md` (e.g. `docs/ja/ch01.md`).  
Non-chapter sections use descriptive names (e.g. `docs/ja/epilogue.md`).

## Standard section translation workflow

Use this sequence for every section. Vary only if the user specifies otherwise.

**Step 1 — Verify repo state**
```
cd D:\little-brother-ja && git status && git log --oneline -3
```
Confirm clean working tree and correct HEAD before touching any file.

**Step 2 — Read project files**
Read in this order (required before any translation):
1. `TRANSLATION_GUIDE.md` — rules, style, checklist
2. `CHARACTERS.md` — character voices and name conventions
3. `glossary.tsv` — term dictionary
4. `docs/.vitepress/config.mts` — sidebar (to see existing entries)

**Step 3 — Read the source section**
```
source/sections/NN-<name>.txt
```
Translate **only from the section source file**, never from memory.

**Step 4 — Translate**
Write `docs/ja/<slug>.md`:
- Frontmatter: `title`, `translation_status: draft`
- For chapters: frontmatter title `'第N章 タイトル'`
- Content translated per `TRANSLATION_GUIDE.md` and `CHARACTERS.md`
- `<small>` attribution footer at the bottom of every page
- Always write Japanese files with `path.write_bytes(text.encode('utf-8'))` — never the Edit tool

**Step 5 — Update navigation**
Add the new page to the appropriate sidebar group in `docs/.vitepress/config.mts`
and to the reading list in `docs/index.md`.
Write both with `write_bytes(content.encode('utf-8'))`.

**Step 6 — Validate**
```
python scripts/validate_sections.py
python scripts/validate_links.py
```
Zero errors required before marking a section complete.
Run `npm run docs:build` on Windows to check the VitePress build.

**Step 7 — Report**
Report in English only. Include:
- Files changed + line/byte counts
- Source section used
- validate_sections.py and validate_links.py output (full)
- Any deviations from TRANSLATION_GUIDE.md, TODOs, or unresolved issues
- PowerShell commit command (do not commit yourself):
  ```powershell
  git add docs/ja/chNN.md docs/.vitepress/config.mts docs/index.md
  git commit -m "trans: translate chapter N — Chapter Title (draft)"
  ```

## Claude Code commands and skills

Slash commands are registered as thin wrappers in `.claude/commands/*.md`.
Each wrapper delegates to the matching `.claude/skills/lb-*/SKILL.md` for the full procedure.

| Command | Purpose |
|---------|---------|
| `/lb-bootstrap` | Verify setup: source files, sections, scripts, VitePress build |
| `/lb-translate <section>` | Translate a section end-to-end |
| `/lb-postcheck <section>` | Review a translated section without rewriting |
| `/lb-full-recheck` | Revalidate all translated sections against latest rules |
| `/lb-rule-update <description>` | Update TRANSLATION_GUIDE.md / CHARACTERS.md / glossary.tsv only |

**`/lb-rule-update` is rule/glossary-only.** It must not edit translated section files.  
**`/lb-postcheck` and `/lb-full-recheck` are review-only.** They must not rewrite prose.

### Validation harness

```bash
python scripts/split_source.py              # (re-)split source into sections
python scripts/validate_sections.py         # confirm all sections present + checksums
python scripts/validate_links.py            # check internal links in docs/ja/
```

`npm run docs:build` must be run on Windows (cannot run in Linux sandbox).

## Potential future hooks

- **PreToolUse hook**: block `git push` from Claude.
- **Stop hook**: suggest running `/lb-postcheck` or `/lb-full-recheck` after a
  translation session completes.
