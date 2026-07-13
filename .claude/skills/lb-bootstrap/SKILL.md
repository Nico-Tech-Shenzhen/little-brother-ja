# Skill: lb-bootstrap

Verify the Little Brother translation repository is correctly set up.

## Steps

1. **Check project files exist**
   Confirm these files are present. Report any missing:
   - `CLAUDE.md`
   - `TRANSLATION_GUIDE.md`
   - `CHARACTERS.md`
   - `glossary.tsv`
   - `CONTENT-LICENSE.md`
   - `source/manifest.json`
   - `scripts/split_source.py`
   - `scripts/validate_sections.py`
   - `scripts/validate_links.py`
   - `scripts/check_translation_batch.py`
   - `docs/.vitepress/config.mts`
   - `.github/workflows/deploy.yml`
   - `package.json`

2. **Check source files**
   - Confirm `source/original/Cory_Doctorow_-_Little_Brother.txt` exists.
   - Confirm `source/original/Cory_Doctorow_-_Little_Brother.htm` exists.
   - Report file sizes. If either file is < 500 KB, warn that it is likely truncated.
   - Check `source/manifest.json` for `partial_download: true` entries and report them.

3. **Check sections**
   - If `source/sections/` is empty or missing, run:
     ```bash
     python3 scripts/split_source.py
     ```
   - Run:
     ```bash
     python3 scripts/validate_sections.py
     ```
   - Report full output.

4. **Check links**
   ```bash
   python3 scripts/validate_links.py
   ```
   Report full output.

5. **Report**
   - List of project files: present / missing
   - Source file status: size, partial-download warning if applicable
   - split_source.py output (if run)
   - validate_sections.py output
   - validate_links.py output
   - Suggested next step (e.g. download full source, run `/lb-translate ch01`)
