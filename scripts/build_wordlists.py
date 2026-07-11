#!/usr/bin/env python3
"""Derive spawndir's adjective and noun word lists from public-domain sources.

This is the exact pipeline that produced ``words/adjectives.txt`` and
``words/nouns.txt``. It reconstructs the lists from two public-domain sources:

1. **Moby Part-of-Speech II** (Grady Ward, public domain, Jan 2001)
   Project Gutenberg eBook #3203. ``mobypos.txt`` — 233,356 entries in the
   form ``word\\POS`` where POS is one or more single-letter codes:
   ``A`` adjective, ``N`` noun, ``V``/``v`` verb, ``t``/``i``/``h``/``p``/``P``
   other. See SOURCES.md for full attribution.

2. **Google 10,000 Most Common English Words** (first20hours, public domain)
   Derived from Google's Trillion Word Corpus. Used as a frequency filter so
   generated directory names use recognizable vocabulary.

Pipeline
--------
1. Parse ``mobypos.txt`` (latin-1 encoded). Keep alphabetic words of 4–10 chars.
2. Adjectives = POS code contains ``A`` but not ``N`` or ``V``.
   Nouns      = POS code contains ``N`` but not ``A`` or ``V``.
3. Drop any word that ever appears *capitalized* in Moby (proper nouns are
   stored capitalized; common nouns/adjectives are lowercase). A word kept must
   appear *only* in lowercase form.
4. Intersect with the Google frequency list (compared case-insensitively).
5. Title-case, sort, and write one word per line to ``words/{adjectives,nouns}.txt``.

Reproducibility
---------------
Source files are cached next to this script (``scripts/.cache/``). If absent,
they are downloaded. Override every path on the CLI; see ``--help``.

    python3 scripts/build_wordlists.py
    python3 scripts/build_wordlists.py --moby /tmp/mobypos.txt --common /tmp/common.txt

The expected output is 545 adjectives and 1919 nouns.
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

MOBY_URL = "https://www.gutenberg.org/files/3203/files/mobypos.txt"
COMMON_URL = (
    "https://raw.githubusercontent.com/first20hours/google-10000-english/"
    "master/google-10000-english-no-swears.txt"
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "words"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"


def ensure_source(path: Path, url: str) -> Path:
    """Return ``path``, downloading from ``url`` into the cache if it is missing."""
    if path.exists():
        return path
    cached = CACHE_DIR / path.name
    if cached.exists():
        return cached
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"downloading {url} -> {cached}", file=sys.stderr)
    urllib.request.urlretrieve(url, cached)
    return cached


def parse_moby(moby_path: Path):
    """Yield ``(word, pos_code)`` tuples, one per Moby entry."""
    with moby_path.open(encoding="latin-1") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if "\\" not in line:
                continue
            word, code = line.rsplit("\\", 1)
            word = word.strip()
            if word.isalpha() and 4 <= len(word) <= 10:
                yield word, code.strip()


def load_common(common_path: Path) -> set[str]:
    with common_path.open() as f:
        return {line.strip().lower() for line in f if line.strip()}


def build_lists(moby_path: Path, common_path: Path):
    """Return ``(adjectives, nouns)`` as sorted, title-cased lists."""
    entries = list(parse_moby(moby_path))

    # Map each lowercase word to the set of capitalisations it appears under.
    # A word that is ever capitalised in Moby is treated as a proper noun.
    cases: dict[str, set[bool]] = {}
    for word, _code in entries:
        cases.setdefault(word.lower(), set()).add(word[0].isupper())

    common = load_common(common_path)

    adj: set[str] = set()
    noun: set[str] = set()
    for word, code in entries:
        seen = cases.get(word.lower(), set())
        if True in seen or False not in seen:
            continue  # appears capitalised (proper noun) — skip
        wl = word.lower()
        if "A" in code and "N" not in code and "V" not in code:
            adj.add(wl)
        if "N" in code and "A" not in code and "V" not in code:
            noun.add(wl)

    def titlecase_sorted(words):
        return sorted(w[0].upper() + w[1:] for w in (words & common))

    return titlecase_sorted(adj), titlecase_sorted(noun)


def write_list(path: Path, words) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(words) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--moby", type=Path, default=Path("mobypos.txt"),
                    help="path to mobypos.txt (downloaded if absent)")
    ap.add_argument("--common", type=Path, default=Path("google-10000-english-no-swears.txt"),
                    help="path to the Google frequency list (downloaded if absent)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="output directory for the word lists")
    args = ap.parse_args()

    moby_path = ensure_source(args.moby, MOBY_URL)
    common_path = ensure_source(args.common, COMMON_URL)

    adjectives, nouns = build_lists(moby_path, common_path)
    write_list(args.out / "adjectives.txt", adjectives)
    write_list(args.out / "nouns.txt", nouns)

    print(f"adjectives: {len(adjectives)} -> {args.out / 'adjectives.txt'}")
    print(f"nouns:      {len(nouns)} -> {args.out / 'nouns.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
