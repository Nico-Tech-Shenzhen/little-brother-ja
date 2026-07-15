Update translation rules in `TRANSLATION_GUIDE.md`, character voice in `CHARACTERS.md`,
and/or glossary entries in `glossary.tsv`.
**Never edit translated section content. Never retranslate.**

**Argument:** free-form description of the rule, character voice, or term change.

**Instructions:**
1. Read `.claude/skills/lb-rule-update/SKILL.md` for the full procedure.
2. Follow `CLAUDE.md` operational rules.
3. Edit **only** `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and/or `glossary.tsv`
   (unless user explicitly names another non-translation rule file).
   - Stable term mappings → `glossary.tsv`
   - Style / prose / voice / process rules → `TRANSLATION_GUIDE.md`
   - Character voice, pronoun, name conventions → `CHARACTERS.md`
   - Term + usage context → both files; do not duplicate the explanation
4. Check for existing entries first. Merge or strengthen; do not duplicate.
5. **Never** edit `docs/ja/*.md` or any translated section file.
6. **Never** retranslate.
7. Run `python3 scripts/validate_links.py` and `python3 scripts/audit_translation_rules.py`;
   include full output.
8. Show `git diff -- TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv`.
9. Report in **English**: what changed, placement rationale,
   confirmation that no section files were edited, validation result, PowerShell commit command.
