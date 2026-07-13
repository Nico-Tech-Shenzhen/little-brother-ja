# Little Brother 日本語訳

Japanese translation project for *Little Brother* by Cory Doctorow.

- **Repository**: https://github.com/Nico-Tech-Shenzhen/little-brother-ja
- **Site**: https://takasumasakazu.net/little-brother-ja/
- **Translator**: 高須正和 / TAKASU Masakazu (@tks)

## About this project

*Little Brother* is a 2008 science fiction novel by Cory Doctorow, published by Tor Books.
It tells the story of Marcus Yallow, a 17-year-old hacker in San Francisco who is detained
by the Department of Homeland Security after a terrorist attack and subsequently leads a
grassroots resistance using hacker techniques.

The novel is distributed under Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported.
This Japanese translation uses the same license.

This is a fan translation project based on the CC-licensed English edition.
**This is not an officially published Japanese edition.**

## License

- **Book-derived content** (translations): CC BY-NC-SA 3.0
- **Scripts and site configuration**: MIT License

See `CONTENT-LICENSE.md` for full details.

## Source

The original English text is distributed free by Cory Doctorow:

- Download page: https://craphound.com/littlebrother/download/
- Plain text: http://craphound.com/littlebrother/Cory_Doctorow_-_Little_Brother.txt
- HTML: http://craphound.com/littlebrother/Cory_Doctorow_-_Little_Brother.htm

Source files must be placed in `source/original/` before running the split script.
See `source/manifest.json` for checksums and download instructions.

## Repository structure

```
little-brother-ja/
├── CLAUDE.md                    # Claude Code operational rules
├── TRANSLATION_GUIDE.md         # Translation rules and style guide
├── CHARACTERS.md                # Character voice guide
├── glossary.tsv                 # Term dictionary (source_term / ja_term / note)
├── CONTENT-LICENSE.md           # License information
├── README.md                    # This file
├── package.json                 # VitePress build config
├── source/
│   ├── original/                # Official source files (TXT + HTML)
│   ├── sections/                # Split sections (output of split_source.py)
│   └── manifest.json            # URLs, checksums, download instructions
├── docs/
│   ├── index.md                 # Japanese site homepage
│   ├── credits.md               # Credits page
│   ├── license.md               # License page
│   ├── ja/                      # Translated chapter files
│   └── .vitepress/
│       └── config.mts           # VitePress configuration
├── scripts/
│   ├── split_source.py          # Split TXT source into sections
│   ├── validate_sections.py     # Verify all sections exist and are valid
│   └── validate_links.py        # Check internal links in docs/ja/
├── .claude/
│   ├── commands/                # Claude Code slash command wrappers
│   └── skills/                  # Full skill procedure files
└── .github/
    └── workflows/
        └── deploy.yml           # GitHub Pages deployment
```

## Getting started (for translators)

1. Download the full source files (see `source/manifest.json` for instructions)
2. Run `python scripts/split_source.py` to split the source into sections
3. Run `python scripts/validate_sections.py` to confirm all sections are present
4. Install dependencies: `npm install`
5. Read `TRANSLATION_GUIDE.md` and `CHARACTERS.md` before translating
6. Use `/lb-translate ch01` to begin translating Chapter 1

## Getting started (for site build)

```bash
npm install
npm run docs:dev      # local preview
npm run docs:build    # production build
```

## Translation status

No chapters translated yet. Repository is in initial setup state.
