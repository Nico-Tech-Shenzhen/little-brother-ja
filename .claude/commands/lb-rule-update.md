Update translation rules in `TRANSLATION_GUIDE.md`, character voice in `CHARACTERS.md`,
and/or glossary entries in `glossary.tsv`.
Never edit translated section content. Never retranslate.

**Argument:** free-form description of the rule, character voice, or term change. Examples:
- `Marcus should use 僕 not 私`
- `add ARG (Alternate Reality Game) to glossary`
- `DHS interrogators should have cold, bureaucratic register`
- `bookstore dedication format should use blockquote`

Also triggered by Japanese phrases such as:
- ルールだけ更新 / ルールを追加
- 辞書に追加 / この訳語を登録して
- 本文は修正しない / 再翻訳しない

**Instructions:**
1. Read `.claude/skills/lb-rule-update/SKILL.md` for the full procedure.
2. Follow `CLAUDE.md` operational rules.
3. Edit **only** `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and/or `glossary.tsv`
   (unless user explicitly names another file).
   - Stable term mappings → `glossary.tsv`
   - Style / prose / voice rules → `TRANSLATION_GUIDE.md`
   - Character voice details → `CHARACTERS.md`
   - Both a term and a usage rule → both files
4. Check for existing entries first. Merge or strengthen; do not duplicate.
5. **Never** edit `docs/ja/*.md` or any translated section file.
6. **Never** retranslate.
7. Run `python3 scripts/validate_links.py` and include the full output in your report.
8. Show `git diff -- TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv`.
9. Report in **English**: what changed, placement rationale, confirmation that no
   section files were edited, validation result, and the PowerShell commit command.
