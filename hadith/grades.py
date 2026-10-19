"""Classify free-text hadith gradings into a small set of classes."""
from __future__ import annotations

import re

from .normalize import fold_latin, normalize_arabic

CLASSES = ("sahih", "hasan", "daif", "mawdu")
RANK = {"sahih": 4, "hasan": 3, None: 2, "daif": 1, "mawdu": 0}

# Preferred grader when several are available (most cited, most complete).
GRADER_PRIORITY = ["Al-Albani", "al-Albani", "الألباني", "Shuaib Al Arnaut", "شعيب الأرنؤوط",
                   "Zubair Ali Zai", "Ahmad Muhammad Shakir", "Bashar Awad Maarouf",
                   "Abu Ghuddah", "Muhammad Muhyi Al-Din Abdul Hamid", "Muhammad Fouad Abd al-Baqi",
                   "Salim al-Hilali", "Husayn Salim Asad", "al-Dhahabi", "الذهبي", "al-A'zami"]

_EN_PATTERNS = [
    ("mawdu", r"mawdu|maudu|fabricat|forged|la asla"),
    ("hasan_sahih", r"hasan\s*sahih"),
    ("daif", r"da'?if|daeef|dhaif|weak|munkar|shadh|matruk|batil|mudtarib|mursal|munqati"),
    ("sahih", r"sahih|saheeh|authentic|agreed upon|bukhari and muslim"),
    ("hasan", r"hasan|good"),
]
_AR_PATTERNS = [
    ("mawdu", r"موضوع|مكذوب|لا اصل له|باطل"),
    ("daif", r"ضعيف|منكر|شاذ|واه|متروك|ساقط|كذاب|مضطرب|منقطع|مرسل"),
    ("sahih", r"صحيح|علي شرط|متفق عليه|ثقات"),
    ("hasan", r"حسن"),
]


def classify(grade: str | None) -> str | None:
    """Map a grading string to sahih / hasan / daif / mawdu (or None if unknown).

    The earliest matching keyword wins, so "Isnaad Daif, but the hadith is
    Sahih" is treated as weak-chain (conservative) while "Hasan Sahih" is sahih.
    """
    if not grade:
        return None
    if re.search(r"[\u0600-\u06FF]", grade):
        g = normalize_arabic(grade)
        pats = _AR_PATTERNS
        if "لم يتكلم عليه" in g and not re.search("صحيح|حسن|ضعيف", g):
            return None
    else:
        g = fold_latin(grade)
        pats = _EN_PATTERNS
    best = None
    for cls, pat in pats:
        m = re.search(pat, g)
        if m and (best is None or m.start() < best[1]):
            best = (cls, m.start())
    if not best:
        return None
    return "sahih" if best[0] == "hasan_sahih" else best[0]


def pick(grades: list[dict]) -> tuple[str | None, str | None]:
    """Choose the headline grade: (class, "Grade (Grader)")."""
    if not grades:
        return None, None
    def prio(g):
        name = g.get("grader") or ""
        for i, p in enumerate(GRADER_PRIORITY):
            if p.lower() in name.lower():
                return i
        return len(GRADER_PRIORITY)
    for g in sorted(grades, key=prio):
        cls = classify(g.get("grade"))
        if cls:
            label = g["grade"].strip()
            if g.get("grader"):
                label = f"{label} ({g['grader']})"
            return cls, label
    g = grades[0]
    return None, (g.get("grade") or "").strip() or None
