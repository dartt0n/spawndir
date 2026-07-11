# Sources

spawndir embeds word lists from the following public-domain and freely-licensed sources. The adjective and noun lists can be regenerated from the original sources with `scripts/build_wordlists.py` (see [Reproduction](#reproduction) below).

## Moby Part-of-Speech II

- **Author**: Grady Ward
- **License**: Public Domain (granted by author, January 2001)
- **Source**: Project Gutenberg eBook #3203 - https://www.gutenberg.org/ebooks/3203
- **File**: `mobypos.txt` - 233,356 entries with part-of-speech codes
- **Usage**: Parsed to extract adjectives (code contains 'A', not 'N'/'V') and nouns (code contains 'N', not 'A'/'V'), filtered to alphabetic words of 4–10 characters that appear ONLY in lowercase form in the source (excludes proper nouns). Then intersected with the Google frequency list below to retain only common English words. Output: `words/adjectives.txt`, `words/nouns.txt`.

## Google 10,000 Most Common English Words

- **Author**: first20hours
- **License**: Public Domain (unlicensed)
- **Source**: https://github.com/first20hours/google-10000-english
- **File**: `google-10000-english-no-swears.txt` — 9,894 words ranked by frequency
- **Derived from**: Google's Trillion Word Corpus via n-gram frequency analysis
- **Usage**: Used as a frequency filter - only Moby POS words appearing in this list are retained, ensuring generated directory names use recognizable vocabulary.

## Colors and Suffixes

- **Source**: Hand-curated from common English vocabulary (independently compiled).
- **License**: CC0 (public domain dedication). No copyright applies to simple lists of common words.

## Reproduction

The `words/adjectives.txt` and `words/nouns.txt` lists are produced by `scripts/build_wordlists.py`, which downloads the two public-domain source files above (caching them under `scripts/.cache/`) and runs the documented extraction pipeline. The script is deterministic — it reproduces the committed lists byte-for-byte (545 adjectives, 1919 nouns).

`words/colors.txt` and `words/suffixes.txt` are **not** script-generated: they are hand-curated static lists authored directly in the repository (see "Colors and Suffixes" above). There is no source dataset or processing step to reproduce.

```sh
python3 scripts/build_wordlists.py
```
