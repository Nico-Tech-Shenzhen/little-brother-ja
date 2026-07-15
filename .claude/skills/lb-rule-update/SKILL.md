# Skill: lb-rule-update

Update translation rules, character voices, and/or glossary entries only.
**Never edit translated section files (`docs/ja/*.md`). Never retranslate.**

---

## Canonical file policy (single source of truth)

| Information type | Canonical location |
|---|---|
| General Japanese prose, syntax, ambiguity, metaphor, translation-process rules | `TRANSLATION_GUIDE.md` |
| Character-specific voice, pronoun, dialogue register, recurring behavior | `CHARACTERS.md` |
| Stable source term → Japanese rendering | `glossary.tsv` |
| Context-dependent term | `glossary.tsv` with a concise context note |
| Term mapping + general prose principle | Mapping in `glossary.tsv`; principle in `TRANSLATION_GUIDE.md` — do not duplicate the full explanation |
| Character-specific use of a general term | Mapping in `glossary.tsv`; character behavior in `CHARACTERS.md` |

**Do not copy the same full rule into two files.**
Cross-reference with a single line when needed.

---

## Feedback classification

An exact correction is **not** automatically a project-wide rule.
Only generalise when the principle will plausibly recur in future chapters.

---

## Conflict-resolution policy

Before editing, read **all three** canonical rule files in full.

Precedence when rules conflict:
1. Current explicit user instruction
2. Existing project-wide translation priorities (§ Translation priorities in `TRANSLATION_GUIDE.md`)
3. Character-specific voice rule (`CHARACTERS.md`)
4. Context-specific glossary note (`glossary.tsv` note column)
5. General glossary mapping (`glossary.tsv` ja_term)
6. Older examples and existing translated prose

Resolution rules:
- Prefer the current explicit user decision.
- Merge compatible rules; replace obsolete rules rather than retaining parallel alternatives.
- If the conflict cannot be resolved from available evidence, report `needs_human_decision` and stop.
- Never silently choose between two materially different translations without explaining.

---

## Rule-efficiency policy

- **Search before adding.** If a rule or entry exists, merge or strengthen it.
- Merge overlapping rules; delete obsolete examples when superseded.
- Prefer one general rule + one strong example over several near-duplicate examples.
- Do not store chapter-specific prose as a general rule.
- Do not turn every corrected sentence into a glossary entry.
- Keep glossary notes concise (one or two sentences).
- Keep long rationale in `TRANSLATION_GUIDE.md`; character evidence in `CHARACTERS.md`.
- Preserve nuance when consolidation would change meaning.

---

## Steps

### Step 1 — Read current state
Read `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and `glossary.tsv` in full.

### Step 2 — Plan changes
For each item of feedback: check whether an existing rule or entry already covers it.
- Merge or strengthen the existing entry when possible; do not duplicate.
- Distinguish reusable rules (generalise) from one-off corrections (local fix only).

### Step 3 — Apply changes (rule files only)

**glossary.tsv**: `source_term\tja_term\tnote` (tab-separated, 3 columns)
**TRANSLATION_GUIDE.md**: add to the most relevant existing section.
**CHARACTERS.md**: add to the character's existing entry.

**Do not edit `docs/ja/*.md` or any other file.**

### Step 4 — Run validation
```bash
python3 scripts/validate_links.py
python3 scripts/audit_translation_rules.py
```
Include full output.

### Step 5 — Report (English only)

Summary:
- Files changed; rules merged/replaced/added; glossary rows added/modified/deleted
- Contradictions found and resolved; unresolved conflicts flagged as `needs_human_decision`
- Confirmation: `No docs/ja/*.md files were edited`
- `git diff -- TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv`
- PowerShell commit:
  ```powershell
  git add TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv
  git commit -m "guide: <short description>"
  ```
