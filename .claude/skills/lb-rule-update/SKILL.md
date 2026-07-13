# Skill: lb-rule-update

Update translation rules, character voices, and/or glossary entries only.
Never edit translated section files. Never retranslate.

## Target files

- `TRANSLATION_GUIDE.md` — style, prose, and process rules
- `CHARACTERS.md` — character voice, pronoun, and name conventions
- `glossary.tsv` — stable term mappings (source_term / ja_term / note)

## Routing rules

| Change type | Target file |
|-------------|------------|
| Stable term → ja_term mapping | `glossary.tsv` |
| Style rule, prose pattern, prohibited phrase | `TRANSLATION_GUIDE.md` |
| Character voice, pronoun, or name transliteration | `CHARACTERS.md` |
| Both a term and its usage context | both `glossary.tsv` and `TRANSLATION_GUIDE.md` |

## Steps

1. **Read current state**
   Read `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and `glossary.tsv` in full.

2. **Check for existing entries**
   Search for the term or rule before adding. Merge or strengthen; do not duplicate.

3. **Apply changes**
   - `glossary.tsv`: add or update a row with tab-separated columns
     `source_term\tja_term\tnote`
   - `TRANSLATION_GUIDE.md` or `CHARACTERS.md`: add to the most relevant section.
     Do not create new top-level sections without reason.

4. **Confirm no chapter files touched**
   List only the rule files that were changed.

5. **Run validation**
   ```bash
   python3 scripts/validate_links.py
   ```
   Report full output.

6. **Report (English only)**
   - What changed and in which file
   - Placement rationale
   - Whether the change requires retroactive fixes in already-translated sections (flag only; do not fix)
   - Confirmation that no `docs/ja/*.md` files were edited
   - `git diff -- TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv`
   - PowerShell commit command:
     ```powershell
     git add TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv
     git commit -m "guide: <short description of change>"
     ```
