# Skill: lb-rule-audit

Periodic maintenance audit of the translation rule system.
**Never edit translated section files (`docs/ja/*.md`).**

Invocation:
```
/lb-rule-audit [all|terminology|voice]
```
Default scope: `all`.

---

## Scope definitions

| Scope | What is checked |
|---|---|
| `terminology` | `glossary.tsv` — duplicates, conflicting renderings, stale entries, PLACEHOLDER markers |
| `voice` | `CHARACTERS.md` — pronoun consistency, contradictions, stale PLACEHOLDERs, conflicting dialogue rules |
| `all` | Both of the above, plus `TRANSLATION_GUIDE.md` — duplicate rules, obsolete examples, cross-file conflicts |

---

## Canonical file policy (same as lb-rule-update)

| Information type | Canonical location |
|---|---|
| General prose, syntax, ambiguity, metaphor, process rules | `TRANSLATION_GUIDE.md` |
| Character voice, pronoun, dialogue register, recurring behavior | `CHARACTERS.md` |
| Stable source term → Japanese rendering | `glossary.tsv` |
| Context-dependent term | `glossary.tsv` with a concise context note |
| Term mapping + general principle | Mapping in `glossary.tsv`; principle in `TRANSLATION_GUIDE.md` |
| Character-specific use of general term | `glossary.tsv` + `CHARACTERS.md` |

**Do not copy the same full rule into two files.**

---

## Conflict-resolution policy (same as lb-rule-update)

Precedence:
1. Current explicit user instruction
2. Project-wide translation priorities
3. Character-specific voice rule
4. Context-specific glossary note
5. General glossary mapping
6. Older examples and existing translated prose

- Merge compatible rules; replace obsolete with current.
- If irresolvable from evidence, report `needs_human_decision`.
- Never silently choose between materially different translations.

---

## Rule-efficiency policy (same as lb-rule-update)

- Search before adding. Merge overlapping rules.
- Delete obsolete examples when superseded.
- Prefer one general rule + one strong example over several near-duplicates.
- Keep glossary notes concise; rationale in `TRANSLATION_GUIDE.md`.
- Preserve nuance when consolidation would change meaning.

---

## Steps

### Step 1 — Read all rule files in full
Read `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and `glossary.tsv` completely.

### Step 2 — Run structural audit script
```bash
python3 scripts/audit_translation_rules.py
```
Record all errors and warnings.

### Step 3 — Semantic audit

For each scope in {terminology, voice} (per invocation):

**terminology (glossary.tsv):**
- Identify entries marked PLACEHOLDER or with unresolved TODO
- Identify near-duplicate source terms that should be merged
- Identify context-dependent terms not marked as such in the note
- Identify entries where ja_term contradicts a rule in TRANSLATION_GUIDE.md
- Identify entries displaced from their canonical file
- Identify entries that should be removed because they are trivial, overly specific, or no longer needed

**voice (CHARACTERS.md + TRANSLATION_GUIDE.md):**
- Check for contradictory pronoun assignments for the same character
- Check for duplicate or near-duplicate dialogue rules
- Check for rules that claim a fixed rendering for a context-dependent term
- Check for examples in CHARACTERS.md that belong in TRANSLATION_GUIDE.md and vice versa
- Check for PLACEHOLDER entries where evidence now exists

**all (adds TRANSLATION_GUIDE.md):**
- Duplicate or near-duplicate headings
- Redundant rule sections
- Rules that have been superseded by a later user decision and not removed
- Cross-file conflicts (e.g., a glossary mapping that contradicts a TRANSLATION_GUIDE rule)
- Obsolete command references (commands that no longer exist)
- Obsolete credit wording

### Step 4 — Apply changes (rule files only)

For each issue found, determine: resolve / flag / no-action.

**Resolve** (edit the canonical file):
- Merge duplicate rules
- Remove obsolete examples
- Correct misplaced content (move to canonical file; cross-reference)
- Mark stale PLACEHOLDERs or remove if confirmed

**Flag** (`needs_human_decision`):
- Semantic contradictions that cannot be resolved without a translation judgment
- Cases where two equally valid renderings exist

**No-action**:
- Warnings that are informational only
- Deliberate redundancy that preserves nuance

**Do not edit `docs/ja/*.md` under any circumstances.**

### Step 5 — Run validation
```bash
python3 scripts/validate_links.py
python3 scripts/audit_translation_rules.py
```
Include full output.

### Step 6 — Report (English only)

Include:
- Structural audit script output (full)
- Issues found, classified: resolved / flagged / no-action
- Rules merged, replaced, removed
- Glossary rows modified or removed
- Contradictions resolved (explain how)
- Unresolved conflicts: `needs_human_decision`
- Explicit confirmation: `No docs/ja/*.md files were edited`
- `git diff -- TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv`
- PowerShell commit:
  ```powershell
  git add TRANSLATION_GUIDE.md CHARACTERS.md glossary.tsv
  git commit -m "guide: <short description of audit changes>"
  ```
