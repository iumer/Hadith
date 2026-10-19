"""Text normalisation shared by the indexer and the search engine.

The same functions must be used at index time and at query time, otherwise
Arabic queries typed without diacritics will not match vocalised text.
"""
from __future__ import annotations

import re
import unicodedata

# Harakat, tanwin, shadda, sukun, superscript alef, Quranic annotation marks.
_AR_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u08D3-\u08FF]")
_AR_TATWEEL = "\u0640"
_AR_MAP = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ٲ": "ا", "ٳ": "ا",
    "ى": "ي", "ئ": "ي", "ی": "ي",
    "ؤ": "و",
    "ة": "ه", "ۃ": "ه", "ہ": "ه", "ھ": "ه",
    "ے": "ي", "ں": "ن",
    "ك": "ك", "ک": "ك", "گ": "ك",
    "ء": "",
    "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
    "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
    "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
    "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
})
_NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)
_SPACES = re.compile(r"\s+")
_OPENITI_NOISE = re.compile(r"PageV\d+P\d+|ms\d+|@MATN@|\[ص:\s*\d+\]")

# Honorific formulas are extremely frequent and carry no topical meaning.
_AR_FORMULAS = [
    "صلي الله عليه وسلم", "صلي الله عليه وعلي اله وسلم", "رضي الله عنهما",
    "رضي الله عنها", "رضي الله عنهم", "رضي الله عنه", "عليه السلام",
    "عز وجل", "تبارك وتعالي", "سبحانه وتعالي",
]


def strip_arabic_diacritics(text: str) -> str:
    return _AR_DIACRITICS.sub("", text).replace(_AR_TATWEEL, "")


def normalize_arabic(text: str, drop_formulas: bool = False) -> str:
    """Diacritic-free, orthographically normalised Arabic suitable for matching."""
    if not text:
        return ""
    text = _OPENITI_NOISE.sub(" ", text)
    text = strip_arabic_diacritics(text)
    text = text.translate(_AR_MAP)
    text = _NON_WORD.sub(" ", text)
    text = _SPACES.sub(" ", text).strip()
    if drop_formulas:
        for f in _AR_FORMULAS:
            text = text.replace(f, " ")
        text = _SPACES.sub(" ", text).strip()
    return text


def fold_latin(text: str) -> str:
    """Lowercase and strip accents / transliteration marks (ʿ ʾ ` ' ā ī ū)."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[`'’‘ʿʾ\u02bb\u02bc]", "", text)
    return text.lower()


def normalize_english(text: str) -> str:
    if not text:
        return ""
    text = text.replace("(ﷺ)", " ").replace("ﷺ", " ")
    text = fold_latin(text)
    text = re.sub(r"\(\s*(pbuh|saw|sas|p\.b\.u\.h\.?)\s*\)", " ", text)
    text = _NON_WORD.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def clean_display(text: str, openiti: bool = False) -> str:
    """Tidy whitespace in source text for display without changing wording."""
    if not text:
        return ""
    if openiti:
        text = _OPENITI_NOISE.sub(" ", text)
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    return text.strip()


def is_arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    ar = sum(1 for c in letters if "\u0600" <= c <= "\u06FF" or "\u0750" <= c <= "\u077F")
    return ar / len(letters) > 0.5


_AR_PREFIXES = ("وال", "فال", "بال", "كال", "لل", "ال")
_AR_SUFFIXES = ("ها", "ان", "ات", "ون", "ين", "يه", "ه", "ي")


def stem_arabic_word(w: str) -> str:
    """Light stemmer (Larkey's light10) on a normalised Arabic word."""
    if len(w) > 3 and w[0] == "و":
        w = w[1:]
    for p in _AR_PREFIXES:
        if w.startswith(p) and len(w) - len(p) >= 2:
            w = w[len(p):]
            break
    for s in _AR_SUFFIXES:
        if len(w) - len(s) >= 2 and w.endswith(s):
            w = w[: -len(s)]
    return w


def stem_arabic(text_normalized: str) -> str:
    return " ".join(stem_arabic_word(w) for w in text_normalized.split())


def char_ngrams(text: str, n: int = 4) -> set[str]:
    t = text.replace(" ", "")
    return {t[i:i + n] for i in range(max(0, len(t) - n + 1))}
