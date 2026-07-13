Revalidate all existing translated Japanese sections against the latest rules.

**The novel has chapters 1–21. There is no Chapter 22.**

**Argument (optional):** `all`, a range `ch01-ch21`, a section name, or combinations.
Examples: *(no argument)* | `all` | `ch01-ch21` | `epilogue` | `ch10-ch21 epilogue`

**Instructions:**
1. Read `.claude/skills/lb-full-recheck/SKILL.md` for the full procedure.
2. Read the current `CLAUDE.md`, `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and `glossary.tsv` — ignore prior chat history.
3. Run `python3 scripts/check_translation_batch.py all` (or the requested range).
4. Run `python3 scripts/validate_links.py`.
5. Perform qualitative review against `TRANSLATION_GUIDE.md` and `CHARACTERS.md`.
6. **Review only.** Do **not** retranslate or edit `docs/ja/*.md` unless the user explicitly requests a separate fix task.
7. Report in **English**, grouped by file and severity.
