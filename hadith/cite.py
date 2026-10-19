"""Human-readable references for a hadith record (as returned by ``HadithIndex``)."""
from __future__ import annotations

import textwrap

GRADE_LABEL = {"sahih": "Sahih (authentic)", "hasan": "Hasan (good)", "daif": "Da'if (weak)",
               "mawdu": "Mawdu' (fabricated)", None: "Not graded in this edition"}


def page_ref(h: dict) -> str | None:
    if not h.get("page"):
        return None
    v, p, ve, pe = h.get("volume"), h["page"], h.get("volume_end"), h.get("page_end")
    vol = f"vol. {v}, " if v else ""
    if pe and (pe != p or (ve and ve != v)):
        if ve and ve != v:
            return f"{vol}p. {p} - vol. {ve}, p. {pe}"
        return f"{vol}pp. {p}-{pe}"
    return f"{vol}p. {p}"


def book_ref(h: dict) -> str | None:
    name = h.get("book_en") or h.get("book_ar")
    if not name:
        return None
    num = h.get("book_number")
    both = h.get("book_en") and h.get("book_ar") and h["book_en"] != h["book_ar"]
    label = f"{h['book_en']} ({h['book_ar']})" if both else name
    return f"Book {num}: {label}" if num not in (None, "") else label


def chapter_ref(h: dict) -> str | None:
    en, ar = h.get("chapter_en"), h.get("chapter_ar")
    if not (en or ar):
        return None
    label = f"{en} ({ar})" if en and ar and en != ar else (en or ar)
    num = h.get("chapter_number")
    return f"Chapter {num}: {label}" if num not in (None, "") else label


def short_citation(h: dict) -> str:
    """One line, e.g. ``Sahih al-Bukhari 1 — Book 1: Revelation — vol. 1, p. 6``."""
    parts = [f"{h.get('collection_name_en') or h['collection']} {h['number']}"]
    if h.get("book_en") or h.get("book_ar"):
        parts.append(h.get("book_en") or h.get("book_ar"))
    pr = page_ref(h)
    if pr:
        parts.append(pr)
    return " — ".join(parts)


def grade_line(h: dict) -> str:
    if h.get("grades"):
        return "; ".join(f"{g['grade']} ({g['grader']})" for g in h["grades"])
    return GRADE_LABEL.get(h.get("grade"), "Not graded")


def reference_block(h: dict) -> list[tuple[str, str]]:
    rows = [("Collection", f"{h.get('collection_name_en')} ({h.get('collection_name_ar')})"),
            ("Hadith number", str(h["number"]) + (f" (also numbered {h['alt_number']})" if h.get("alt_number") else ""))]
    for label, val in (("Book", book_ref(h)), ("Chapter", chapter_ref(h)),
                       ("In-book reference", h.get("in_book_ref"))):
        if val:
            rows.append((label, val))
    pr = page_ref(h)
    if pr:
        rows.append(("Printed edition", f"{pr} — {h.get('edition')}"))
    rows.append(("Grade", grade_line(h)))
    if h.get("url"):
        rows.append(("Online", h["url"]))
    return rows


def to_markdown(h: dict, *, arabic: bool = True, english: bool = True, urdu: bool = False,
                max_chars: int | None = None, also_in: list[dict] | None = None) -> str:
    def cut(t: str) -> str:
        return t if not max_chars or len(t) <= max_chars else t[:max_chars].rsplit(" ", 1)[0] + " …"

    out = [f"### {short_citation(h)}", ""]
    out += [f"- **{k}:** {v}" for k, v in reference_block(h)]
    if also_in:
        out.append("- **Also narrated in:** " + ", ".join(
            f"{a['collection_name_en']} {a['number']}" for a in also_in))
    out.append("")
    if english and h.get("text_en"):
        out += ["> " + line for line in cut(h["text_en"]).splitlines()] + [""]
    if arabic and h.get("text_ar"):
        out += ["> " + line for line in cut(h["text_ar"]).splitlines()] + [""]
    if urdu and h.get("text_ur"):
        out += ["> " + line for line in cut(h["text_ur"]).splitlines()] + [""]
    return "\n".join(out)


def to_text(h: dict, *, width: int = 100, arabic: bool = True, english: bool = True, urdu: bool = False,
            max_chars: int | None = None, also_in: list[dict] | None = None) -> str:
    def cut(t: str) -> str:
        return t if not max_chars or len(t) <= max_chars else t[:max_chars].rsplit(" ", 1)[0] + " …"

    out = [short_citation(h), "-" * min(width, 80)]
    out += [f"{k:>18}: {v}" for k, v in reference_block(h)]
    if also_in:
        out.append(f"{'Also in':>18}: " + ", ".join(f"{a['collection_name_en']} {a['number']}" for a in also_in))
    for flag, key in ((english, "text_en"), (arabic, "text_ar"), (urdu, "text_ur")):
        if flag and h.get(key):
            out.append("")
            out += textwrap.wrap(cut(h[key]), width) if key == "text_en" else [cut(h[key])]
    return "\n".join(out) + "\n"
