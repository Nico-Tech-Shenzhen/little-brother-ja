# Skill: lb-postcheck

Review already-translated sections. Read-only — do not rewrite prose.

## Steps

1. **Read current rules**
   Read `TRANSLATION_GUIDE.md`, `CHARACTERS.md`, and `glossary.tsv`.
   Ignore prior chat history — evaluate only against the current rules.

2. **Run validation**
   ```bash
   python3 scripts/check_translation_batch.py <target>
   python3 scripts/validate_links.py
   ```
   Report full output.

3. **Qualitative review**
   For each target file, read `docs/ja/<slug>.md` and check:
   - Marcus uses 「僕」 as narrator, not 「私」
   - No paragraphs, sentences, or bookstore dedications omitted
   - Handles preserved: w1n5t0n, M1k3y, Xnet, DarkNet, ParanoidLinux
   - Setting is 2008 San Francisco (no modernization)
   - Voice sounds like a teenager, not an adult memoirist
   - Technical terms match `glossary.tsv`
   - `<small>` attribution footer present
   - No "公式日本語版" or "公認翻訳" anywhere

4. **Report (English only)**
   Group by file and severity:
   - **Must fix**: errors that violate core rules (omissions, wrong pronoun, broken footer)
   - **Should fix**: style deviations, terminology mismatches
   - **Optional**: minor style improvements

   Do NOT rewrite prose. List issues only.
   If user wants fixes applied, they must request a separate fix task.
