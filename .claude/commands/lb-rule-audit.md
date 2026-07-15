Audit and consolidate translation rules across `TRANSLATION_GUIDE.md`, `CHARACTERS.md`,
and `glossary.tsv`.
**Never edit translated section content. Never retranslate.**

**Optional scope argument:** `all` (default), `terminology`, or `voice`

**Instructions:**
1. Read `.claude/skills/lb-rule-audit/SKILL.md` for the full procedure.
2. Follow `CLAUDE.md` operational rules.
3. Edit **only** `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and/or `glossary.tsv`
   (unless the user explicitly names another non-translation rule file).
   Never edit `docs/ja/*.md` or any other reader-facing file.
4. Default scope is `all` when no argument is given.
5. Run `python3 scripts/audit_translation_rules.py` and include full output.
6. Report in **English**: contradictions found and resolved, rules merged/replaced/removed,
   glossary entries modified, explicit confirmation that no translated files were edited,
   PowerShell commit command.
