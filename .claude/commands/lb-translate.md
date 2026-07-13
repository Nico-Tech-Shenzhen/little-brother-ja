Translate a section of *Little Brother* into Japanese.

**Argument:** section identifier passed after the command name.
Examples: `ch01` | `ch05` | `ch01-ch05` | `introduction` | `epilogue` | `afterword-schneier` | `afterword-huang`

**Chapters end at 21. Do not create ch22.md or beyond.**

**Instructions:**
1. Read `.claude/skills/lb-translate/SKILL.md` for the full procedure.
2. Follow `CLAUDE.md`, `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and `glossary.tsv`.
3. Use the standard section translation workflow in `CLAUDE.md`.
4. Use **English** for all reports, logs, TODOs, and commit messages.
5. Use **Japanese** only for translated reader-facing content in `docs/ja/`.
6. Never commit or push. Never create ch22.md or beyond.
7. Run `python scripts/check_translation_batch.py <target>` after translating.
