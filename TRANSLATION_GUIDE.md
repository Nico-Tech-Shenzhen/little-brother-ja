# Translation Guide — Little Brother 日本語訳

See `CLAUDE.md` for operational rules. This guide covers substance.

## Project scope

Japanese translation of:

> *Little Brother*  
> Author: Cory Doctorow  
> Original publisher: Tor Books, New York (2008)  
> License: Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported  
> Free download: https://craphound.com/littlebrother/download/

The Japanese translation is also released under **CC BY-NC-SA 3.0**.

## Attribution requirements (mandatory in every chapter file)

Every `docs/ja/*.md` file must include the following visible footer `<small>` block:

```html
<small>
*原著*: *Little Brother* © 2008 Cory Doctorow<br>
*出版*: Tor Books<br>
*日本語訳・レビュー*: ニコ技深圳コミュニティ / 高須正和（@tks） — [https://takasumasakazu.net](https://takasumasakazu.net) — CC BY-NC-SA 3.0<br>
*注記*: 本翻訳は、原著の Creative Commons ライセンス条件に従って公開する翻訳であり、出版社による公式日本語版ではありません。
</small>
```

Never use the phrases "公式日本語版" or "公認翻訳" or "正規翻訳".  
Do not describe this as "非公式日本語訳" in the footer — use "高須正和による日本語訳".

## Translation priorities

Apply in order when rules conflict.

**1. Japanese reader clarity comes first.**  
Translate so a Japanese reader familiar with tech culture can follow without decoding
English-shaped prose. If a technical concept needs explanation, explain the function
first, then give the formal term.

**2. Preserve Marcus's voice.**  
The target voice is a fast-talking, sarcastic, technically knowledgeable 17-year-old
American boy — smart, passionate about civil liberties, occasionally immature.
He is NOT an adult memoirist. He is NOT an academic. He sounds like himself.
Use 「僕」 for Marcus's first-person narration. Prefer short declarative sentences,
colloquial phrasing, and teen rhythm.

**3. Technical accuracy still matters.**  
Do not simplify by changing meaning. Preserve all technical facts, protocol names,
product names, hacker slang (when identifiable), and source order.

**4. Translate meaning and voice, not English syntax.**  
Rebuild sentences in natural Japanese. Do not carry over English noun chains, passive
abstractions, or hedged constructions when they obscure the point.

## Voice guidance

### Marcus Yallow (narrator, Chapters 1–21 and Epilogue)

Marcus is the first-person narrator. His voice is:
- Colloquial, fast-paced, opinionated
- Technically precise when explaining computers, cryptography, gaming, civil liberties
- Emotionally raw when dealing with fear, detention, loyalty, politics
- Occasionally self-aware and meta ("You're probably wondering how I ended up here")
- Never academic, never stiff

Use 「僕」 throughout. Avoid 「私」.  
Use plain-form contractions and short sentences. Prefer 「だ／だった」 prose.  
Do not smooth out Marcus's teenage opinions into adult measured prose.

**Register:** Casual but not childish. Educated but not formal.  
**Rhythm:** Short sentences. Exclamatory when Marcus is excited. Terse when scared.

### Other characters (dialogue)

Dialogue voices are specified in `CHARACTERS.md`. Do not flatten all characters to the
same register. Consult `CHARACTERS.md` before translating dialogue scenes.

**Placeholder policy:** Until first pilot translation is complete, `CHARACTERS.md`
holds placeholders. Add character voice details as you encounter them in the text.

### Cory Doctorow's Introduction

First-person author voice. More measured than Marcus, but still personal and direct.
Not academic. Treat as adult non-fiction personal essay.  
Use 「私」 or no pronoun depending on context.

### Bruce Schneier's Afterword

Professional security expert writing an informed opinion essay. Clear, authoritative,
non-alarmist. More formal than Doctorow's introduction.  
Use appropriate formal Japanese for public essay style.

### Andrew "bunnie" Huang's Afterword

Hardware hacker and maker. Practical, hands-on, direct. Similar register to bunnie's
own writing in *Hacking the Xbox* — essay-like, slightly warmer than Schneier.

## Core translation rules

- **Faithful**: Translate every paragraph. Do not summarize, condense, or skip content.
- **Complete**: Do not omit paragraphs, sentences, dialogue, bookstore dedications, or
  any structural element.
- **Preserve structure**: Keep chapter-opening bookstore dedications verbatim structure;
  translate their content.
- **No invented text**: If source text is unclear, mark with `<!-- TODO: verify: [desc] -->`.
- **Preserve order**: Keep all paragraphs in original order. Do not reorganize.
- **Consult glossary.tsv** before translating technical or recurring terms.
- **Katakana** for established loanwords; kanji compounds where natural.

## What to preserve verbatim (no translation)

- Username handles: `w1n5t0n`, `M1k3y`, `Xnet`, `DarkNet`, etc.
- URLs and email addresses
- Brand names: Xbox, PlayStation, Linux, ParanoidLinux, OpenBSD
- Product names and model numbers
- Chapter-opening bookstore names (translate only the surrounding context)
- Technical protocol names: TLS, SSH, Tor, ARPAnet, etc.
- Cryptographic term abbreviations: AES, RSA, SHA-1, etc. (expand on first use)
- Code snippets, terminal output, file names
- Song titles and band names (translate surrounding text, preserve title)

## Setting preservation rule

The novel is set in **San Francisco, 2008**. Do not silently modernize:
- Technology (no smartphones with the current meaning, Twitter was new, etc.)
- Political context (post-9/11 America, DHS surveillance state)
- Services, products, platforms
- Terminology from the period

If a 2008 reference is confusing for a 2020s Japanese reader, add a short translator's
note in a clearly marked HTML comment, but preserve the original text.

## First-person pronoun

Use **「僕」** (not 「私」, not 「俺」) for Marcus's narration throughout.

Exceptions:
- Other characters' first-person dialogue: use the character-appropriate pronoun
  from `CHARACTERS.md`
- Doctorow's Introduction: use 「私」 or omit as natural
- Afterwords: see voice guidance above

## Sentence construction

**Rebuild sentences; do not mirror English syntax.**

- Split long English sentences at natural pauses.
- "and / but / since / while / hence" chains → separate Japanese sentences.
- Resolve ambiguous pronouns from context.
- Do not omit 「僕は」 when a long sentence becomes ambiguous about who is acting.
- Put context/topic before predicate.
- Cause/effect: put reason first when it aids readability.

Marcus's narration often uses rhetorical questions, direct address ("you"), and
mid-paragraph asides. Preserve these structural moves in Japanese.

**Direct address to reader** ("You're probably wondering…"):
Render as 「きっと〜と思ってるだろう」 or similar. Do not flatten to impersonal prose.

## Marcus's sentence rhythm — avoid translation-shaped endings

Marcus's English narration often uses patterns like `X, and that makes me Y` or
`X, which means I'm one of the most Y`. In Japanese, these risk producing
「〜ということを意味する」 or 「〜ということになる」 — which sound like translated prose,
not Marcus's voice.

Rules:
- Split long explanatory English sentences when a short declarative sequence gives Marcus more force.
- Avoid literal explanatory endings such as 「〜ということを意味する」 when Marcus would state the point directly.
- `X, and that makes me Y` may become `Xだ。つまりYってことだ` when the context calls for punch.
- Do not mechanically apply 「ってことだ」 in every paragraph — reserve it for chapter openings and punch lines.
- Chapter openings and punch lines deserve especially strong, concise rhythm.

Good example (Ch. 1 pilot opening):
> 僕はサンフランシスコのミッション地区にあるセザール・チャベス高校の3年生だ。つまり、世界でもっとも監視されている人間の一人ってことだ。

See also Marcus-specific rhythm note in `CHARACTERS.md`.

## Verify agency after rebuilding sentences

When rebuilding English sentences in Japanese, verify who acts on whom:
- Do not preserve English surface grammar when it changes agency, possession, or control.
- `have a jailer` in this context means being assigned or subjected to a jailer, not hiring one.
  Japanese: 「看守につかれる」 (to be saddled with / subjected to a jailer).
- Check transitive/intransitive and active/passive relationships after every rebuild.
- After rebuild, recheck: does the Japanese subject do what the English subject does?

## Do not infer sibling age or birth order

English `brother` and `sister` are not age-marked. Rules:
- Never add 「兄」「弟」「姉」「妹」 unless the source text or established context confirms age order.
- Default to 「兄弟」「姉妹」 or restructure the sentence.
- 「家族」 may be used only when the exact sibling relationship is not important and Japanese
  reads more naturally; report the loss of specificity when it matters.
- Do not infer age, rank, gender, family order, or any relationship detail beyond the source.

## Parse compressed coordination and idioms before translating

When a sentence contains compressed or humorous coordination, identify the grammatical role
of each element before translating:
- Do not invent groups of people when the source coordinates two reasons, standards, or judgments.
- Translate the intended proposition, not the apparent English noun sequence.
- Recheck parallel constructions for scope and attachment.

Good example (Ch. 1 pilot — two reasons/standards, not two types of person):
> 賢いやり方も、衛生面でも、真ん中を選ぶのが正解だ。

## Preserve vivid metaphor without Japanese tautology

- Preserve vivid, grotesque, humorous, or excessive metaphors rather than softening or abstracting them.
- After preserving the image, remove any semantic redundancy introduced in Japanese.
- Tautology to avoid: 「穴の開いた傷口」 — a wound with a hole is redundant; 「ぽっかり開いた傷口」 expresses the image cleanly.
- Preserve insult strength unless Japanese comprehension genuinely requires adjustment.

## Translate perception expressions by function, not word-by-word

- For visual conspicuousness: 「嫌でも目につく」「いやでも目に入る」
- For cognitive obviousness: 「いやでもわかる」
- Avoid unnatural collocations such as 「痛いくらいにわかった」 when the intended meaning is visual (something is conspicuous to the eye).
- Split overloaded descriptions when Japanese rhythm improves from doing so.
- `painfully obvious` is context-dependent: confirm whether the source is about vision, cognition, or social awareness before choosing a rendering.

## Avoid redundant synonym glosses

- Do not write 「ハンドル（ハンドルネーム）」 — choose one established Japanese term.
- Parentheses should add information (the English original, an abbreviation expansion, or a context note), not repeat the same meaning in different words.
- On first mention, use the term from `glossary.tsv`; add the English form in parentheses only when the English itself carries meaning for the reader.

## Locative precision

- Distinguish 「学校で」 / 「校内で」 (at/inside school) from 「学校周辺で」 (in the school's vicinity/neighborhood).
- Resolve English prepositions and broad locative phrases according to the actual scope described in the source.
- When an action takes place within the school building or institution, use 「学校で」 or 「校内で」.

## Technical vocabulary policy

Always check `glossary.tsv` first. If a term is missing, add it before translating.

**Decision rules:**
- Prefer the Japanese term from `glossary.tsv`.
- Security/crypto terms: expand abbreviation on first mention, use abbreviation after.
- Hacker culture terms: check whether the English term itself is part of the meaning.
  If so, keep English in parentheses on first use.
- Do not overload sentences with parenthetical glosses.

**First mention pattern:** Japanese term（English term）  
**After first mention:** Japanese term alone

## Bookstore dedications

Each chapter in *Little Brother* opens with the name of a real (or fictional) bookstore
and a short dedication. These must be:
- Preserved in structure (bookstore name + dedication text)
- Bookstore names kept in English
- Dedication text translated into Japanese
- Formatted consistently across chapters

Example format:
```markdown
> **[Borderlands Books, San Francisco CA](http://www.borderlands-books.com/)**
>
> 書店主、アラン・バティスト。彼と彼の仲間たちが守ろうとしていること、そしていつも歓迎してくれることに感謝を込めて。
```

## Translator notes

Keep translator notes **rare and clearly marked**.

Use HTML comment for internal TODO:
```html
<!-- TODO: TN — [reason for note] -->
```

Use visible note block only when the reader genuinely needs context:
```markdown
> [!NOTE]
> 訳注：[短い説明]
```

Do not add translator notes for technology, culture, or vocabulary that a Japanese
reader familiar with tech and internet culture would already know.

## Chapter-dedication voice — distinct from Marcus

Each chapter opens with a dedication written by **Cory Doctorow**, not by Marcus Yallow.
These dedications are personal, conversational authorial asides — written in the first person
but from Doctorow's adult perspective, not Marcus's teenage narrator voice.

Rules:
- Use 「私」 (not 「僕」) where a first-person pronoun is needed, or omit the subject naturally.
- Voice: warm, personal, adult essay — not Marcus's fast-paced teen narration.
- Keep the same structural notes as novel prose (see Bookstore dedications section below).
- Do NOT smooth into formal Japanese; Doctorow's dedication voice is personal and direct.

## Marcus's authority-mocking "tell" — pragmatic function rule (confirmed by Ch. 1 pilot)

In the English source, Marcus says "sir" to authority figures when he is deliberately mocking
them through exaggerated politeness. He calls this his "tell" — a poker term for an
involuntary reveal.

**The reusable rule: translate the pragmatic function, not a fixed word.**
- Marcus mocks authority by deliberately switching to conspicuously polite language.
- Preserve this behavior: the reader must feel that Marcus is mocking the person through exaggerated politeness.
- The specific Japanese form depends on authority figure and context: 「先生」, another appropriate title, a polite sentence ending, or a shift in the entire dialogue register.
- Use forms such as 「〜ますよ」「〜ていただければ」 — polite but not stiff.
- Do not make Marcus sound like a business letter; avoid 「〜いたします」 alone.
- Do not fix "sir" as a single mandatory Japanese word. Confirm the appropriate form from each scene.
- This behavior applies to teachers, police, DHS staff, and any authority figure where the source shows mocking politeness.
- Japanese dialogue punctuation: use 「〜ですよ、先生」 with a comma before the vocative, not a period that splits it into a separate utterance.

Example (Ch. 1 pilot, confirmed):
> 「何の話か説明していただければ、すぐに真剣に受け止めますよ、先生」

The follow-up narration must make the "tell" explicit:
> 権力を振りかざす相手をからかうとき、僕はいつもわざと丁寧な言葉を使う。これが僕のテルだ。

See Marcus's character entry in `CHARACTERS.md` for the recurring behavior note.

## LLM translation checklist

Before marking any section complete, verify all items:

1. Marcus's voice sounds like a fast-talking teenage hacker, not an adult memoirist.
2. 「僕」 used for Marcus's first-person narration throughout.
3. No paragraphs, sentences, dialogue lines, or bookstore dedications omitted.
4. No text invented; unclear source marked with TODO comment.
5. Technical terms follow `glossary.tsv`; expand on first use.
6. No unnecessary katakana jargon; use natural Japanese equivalents.
7. Ambiguous pronouns resolved to explicit nouns.
8. Verbatim-preserve items (handles, URLs, protocol names) preserved exactly.
9. Setting is 2008 San Francisco; no modernization of technology or politics.
10. Bookstore dedication preserved in structure and translated in content.
11. `<small>` attribution footer present at bottom.
12. No "公式日本語版", "公認翻訳", "正規翻訳" in any text.
13. Direct address to reader ("you") preserved as appropriate Japanese.
14. validate_sections.py passes zero errors.
15. validate_links.py passes zero errors.
16. Frontmatter title and translation_status are accurate.
17. No credit/license block under the chapter title; attribution is footer-only.
18. UTF-8 encoding with no mojibake or replacement characters.
