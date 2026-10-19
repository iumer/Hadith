"""Merge all sources into one normalised corpus (``data/corpus``).

Output per collection: ``<slug>.jsonl.gz`` with one hadith per line, plus a
``collections.json`` index describing collections, books (kitab) and chapters
(bab) with their printed volume/page ranges.
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
import re
import sys
from pathlib import Path

from . import sources
from .align import AlignItem, align, match_global
from .catalog import COLLECTIONS, Collection
from .glossary import kitab_english
from .grades import pick
from .normalize import clean_display, normalize_arabic
from .openiti import Record, parse

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"

csv.field_size_limit(sys.maxsize)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def fmt_number(x) -> str | None:
    """7 -> "7"; "8.01" -> "8a"; 402.2 -> "402b" (sunnah.com style sub-numbers)."""
    if x is None or x == "":
        return None
    s = str(x)
    if "." in s:
        a, b = s.split(".", 1)
        b = int(b) if b.strip("0") else 0
        if b == 0:
            return str(int(a))
        return f"{int(a)}{chr(96 + b)}" if b <= 26 else f"{int(a)}.{b}"
    return str(int(float(s)))


def _nan(v):
    if v is None:
        return None
    v = str(v).strip()
    return None if v in ("", "nan", "None") else v


def _num(v):
    v = _nan(v)
    if v is None:
        return None
    try:
        return str(int(float(v)))
    except ValueError:
        return v


NARRATOR_RE = re.compile(
    r"^\s*((?:Narrated|It was narrated (?:from|that|by)|It is narrated on the authority of|"
    r"Reported|It has been narrated)\s[^:\"]{2,140}?:)")


def split_narrator(text: str) -> tuple[str | None, str]:
    m = NARRATOR_RE.match(text or "")
    if m and len(m.group(1)) < 150:
        return m.group(1).strip(), text
    return None, text


def _same_english(a: str | None, b: str | None) -> bool:
    from .normalize import char_ngrams, normalize_english
    a, b = normalize_english(a or "")[:400], normalize_english(b or "")[:400]
    if not a or not b:
        return False
    ga, gb = char_ngrams(a, 4), char_ngrams(b, 4)
    return len(ga & gb) / max(1, min(len(ga), len(gb))) >= 0.5


# --------------------------------------------------------------------------- loaders

def load_lk(folder: str) -> list[dict]:
    """LK rows in book order (files are one per kitab: Chapter<N>.csv)."""
    d = sources.lk_dir() / folder
    files = sorted(d.glob("*.csv"), key=lambda f: int(re.sub(r"\D", "", f.stem) or 0))
    rows = []
    for f in files:
        with open(f, encoding="utf-8-sig", newline="") as fh:
            rows.extend(csv.DictReader(fh))
    return rows


def load_openiti(c: Collection) -> list[Record]:
    raw = sources.openiti_path(c.openiti.filename).read_text(encoding="utf-8")
    records = parse(raw, c.openiti.spec())
    if c.openiti.text_grade_regex:
        rx = re.compile(c.openiti.text_grade_regex)
        for r in records:
            m = rx.match(r.text)
            if m:
                r.grade_note = (m.group(1).strip() + ("؛ " + r.grade_note if r.grade_note else ""))
                r.text = r.text[m.end():].strip()
    return records


def attach_print(rec: dict, r: Record, score: float) -> None:
    rec["volume"], rec["page"] = r.volume, r.page
    rec["volume_end"], rec["page_end"] = r.end_volume or r.volume, r.end_page or r.page
    rec["print_number"] = r.number
    rec["print_align_score"] = round(score, 3)
    rec["_print_kitab"] = r.kitab
    if not rec.get("book_ar") and r.kitab:
        rec["book_ar"] = r.kitab
    if not rec.get("chapter_ar") and r.bab:
        rec["chapter_ar"] = r.bab
        rec["chapter_number"] = rec.get("chapter_number") or r.bab_number
    if r.grade_note:
        rec["grades"].extend(split_grade_note(r.grade_note, c_grade_source.get(rec["collection"]) or "Editor"))
    if not rec.get("text_ar") and r.text:
        rec["text_ar"] = r.text


c_grade_source: dict[str, str] = {}

_GRADER_LABELS = [
    ("الألباني", "al-Albani"), ("الالباني", "al-Albani"), ("شعيب", "Shu'ayb al-Arna'ut"),
    ("الذهبي", "al-Dhahabi"), ("الأعظمي", "al-A'zami"), ("الاعظمي", "al-A'zami"),
]


def split_grade_note(note: str, default: str) -> list[dict]:
    """"حكم الألباني: صحيح ؛ حكم شعيب الأرنؤوط: إسناده صحيح" -> one entry per grader."""
    out = []
    for part in [p.strip() for p in note.split(" ؛ ") if p.strip()]:
        label, _, body = part.partition(":")
        if not body.strip() or len(label) > 40:
            label, body = "", part
        grader = None
        for key, name in _GRADER_LABELS:
            if key in label:
                grader = name
                break
        body = body.strip()
        if grader is None:
            m = re.match(r"^قال\s+(?:الشيخ\s+)?(\S+)\s*:\s*", body)
            if m:
                for key, name in _GRADER_LABELS:
                    if key in m.group(1):
                        grader, body = name, body[m.end():]
                        break
        if grader is None:
            grader = default.split(" / ")[0] if " / " in default else default
        out.append({"grader": grader, "grade": body})
    return out


# --------------------------------------------------------------------------- builders

def build_fawaz(c: Collection) -> list[dict]:
    eds = {}
    for lang in c.fawaz_languages:
        eds[lang] = json.loads(sources.fawaz_path(f"{lang}-{c.fawaz}").read_text(encoding="utf-8"))
    meta = eds["eng"]["metadata"] if "eng" in eds else eds["ara"]["metadata"]
    sections = meta.get("sections", {})
    by_lang = {lang: {h["hadithnumber"]: h for h in e["hadiths"]} for lang, e in eds.items()}
    order = [h["hadithnumber"] for h in eds["ara"]["hadiths"]]

    lk_rows = load_lk(c.lk) if c.lk else []

    # fawaz leaves most of Muslim's Muqaddimah empty; LK has it.
    lk_intro = {}
    if c.slug == "muslim":
        lk_intro = {_num(r.get("Hadith_number")): r for r in lk_rows if _num(r.get("Chapter_Number")) == "0"}

    recs = []
    for seq, hn in enumerate(order, 1):
        ar = by_lang["ara"].get(hn, {})
        en = by_lang.get("eng", {}).get(hn, {})
        ur = by_lang.get("urd", {}).get(hn, {})
        text_ar = clean_display(ar.get("text", ""))
        text_en = clean_display(en.get("text", ""))
        lk_row = lk_intro.get(fmt_number(hn)) if lk_intro and ((en or ar).get("reference") or {}).get("book") == 0 else None
        if lk_row and not text_ar and not text_en:
            text_ar = clean_display(_nan(lk_row.get("Arabic_Hadith")) or "")
            text_en = clean_display(_nan(lk_row.get("English_Hadith")) or "")
        if not text_ar and not text_en:
            continue
        ref = (en or ar).get("reference") or {}
        bn = ref.get("book")
        arabic_number = ar.get("arabicnumber", en.get("arabicnumber"))
        if c.slug == "muslim":
            if arabic_number:
                number = fmt_number(arabic_number)
            elif bn == 0 and (not recs or recs[-1]["book_number"] in (None, "0")):
                number = f"intro-{ref.get('hadith', hn)}"
            else:
                # Unnumbered in the source; keep it in the book of its neighbour.
                number = f"seq{fmt_number(hn)}"
                bn = int(recs[-1]["book_number"]) if recs and recs[-1]["book_number"] else bn
                ref = {}
        else:
            number = fmt_number(hn)
        grades = [{"grader": g["name"], "grade": g["grade"]} for g in (en.get("grades") or ar.get("grades") or [])]
        narrator, _ = split_narrator(text_en)
        rec = {
            "collection": c.slug, "seq": seq, "number": number,
            "alt_number": str(fmt_number(hn)) if c.slug == "muslim" else None,
            "book_number": str(bn) if bn is not None else None,
            "book_en": sections.get(str(bn)) or None,
            "book_ar": None,
            "chapter_number": None, "chapter_en": None, "chapter_ar": None,
            "in_book_ref": f"Book {bn}, Hadith {ref.get('hadith')}" if bn is not None and ref.get("hadith") else None,
            "narrator_en": narrator,
            "text_en": text_en or None, "text_ar": text_ar or None,
            "text_ur": clean_display(ur.get("text", "")) or None,
            "grades": grades,
            "_hint": str(int(float(arabic_number))) if arabic_number not in (None, "") else None,
        }
        recs.append(rec)

    if lk_rows:
        P = [AlignItem(key=i, text=r["text_ar"] or "", number=fmt_number(order[r["seq"] - 1]))
             for i, r in enumerate(recs) if r["text_ar"]]
        S = [AlignItem(key=j, text=row.get("Arabic_Hadith") or "", number=_num(row.get("Hadith_number")))
             for j, row in enumerate(lk_rows)]
        m = align(P, S)
        for i, (j, sc) in m.items():
            rec, row = recs[i], lk_rows[j]
            rec["_lk_book_ar"] = _nan(row.get("Chapter_Arabic"))
            rec["chapter_number"] = _num(row.get("Section_Number"))
            rec["chapter_en"] = _nan(row.get("Section_English"))
            rec["chapter_ar"] = _nan(row.get("Section_Arabic"))
            if not rec["narrator_en"]:
                isnad = _nan(row.get("English_Isnad"))
                if isnad and len(isnad) < 150 and (rec["text_en"] or "").startswith(isnad[:20]):
                    rec["narrator_en"] = isnad
        log(f"  LK headings aligned {len(m)}/{len(P)}")

    if c.openiti:
        records = load_openiti(c)
        use_numbers = c.openiti.record_mode != "number_para"
        P = [AlignItem(key=i, text=r["text_ar"] or "", number=r["_hint"])
             for i, r in enumerate(recs) if r["text_ar"]]
        S = [AlignItem(key=j, text=x.text, number=x.number) for j, x in enumerate(records)]
        m = align(P, S, use_numbers=use_numbers)
        for i, (j, sc) in m.items():
            attach_print(recs[i], records[j], sc)
        log(f"  print edition aligned {len(m)}/{len(P)}")
    # One Arabic title per book: LK headings first, then the printed edition.
    votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in recs:
        if r.get("_lk_book_ar"):
            votes[r["book_number"]][r["_lk_book_ar"]] += 3
        if r.get("_print_kitab"):
            votes[r["book_number"]][r["_print_kitab"]] += 1
    for r in recs:
        v = votes.get(r["book_number"])
        if v:
            r["book_ar"] = v.most_common(1)[0][0]
        elif not r.get("book_ar"):
            r["book_ar"] = None
    if c.slug in ("bukhari", "muslim"):
        for r in recs:
            r["grades"].insert(0, {"grader": c.name_en, "grade": "Sahih"})
    return recs


def build_hadithjson(c: Collection) -> list[dict]:
    hj = json.loads(sources.hadithjson_path(c.hadithjson).read_text(encoding="utf-8"))
    chapters = {ch["id"]: ch for ch in hj["chapters"]}
    recs = []
    for seq, h in enumerate(hj["hadiths"], 1):
        ch = chapters.get(h.get("chapterId"), {})
        en = h.get("english") or {}
        narrator = clean_display(en.get("narrator") or "") or None
        text_en = clean_display(en.get("text") or "")
        text_ar = clean_display(h.get("arabic") or "")
        if not text_en and not text_ar:
            continue
        recs.append({
            "collection": c.slug, "seq": seq, "number": str(h.get("idInBook") or seq), "alt_number": None,
            "book_number": str(h.get("chapterId")) if h.get("chapterId") is not None else None,
            "book_en": ch.get("english"), "book_ar": ch.get("arabic"),
            "chapter_number": None, "chapter_en": None, "chapter_ar": None,
            "in_book_ref": None, "narrator_en": narrator,
            "text_en": ((narrator + " " + text_en) if narrator and text_en and not text_en.startswith(narrator) else text_en) or None,
            "text_ar": text_ar or None, "text_ur": None, "grades": [],
        })
    if c.openiti:
        records = load_openiti(c)
        P = [AlignItem(key=i, text=r["text_ar"] or "", number=r["number"]) for i, r in enumerate(recs) if r["text_ar"]]
        S = [AlignItem(key=j, text=x.text, number=x.number) for j, x in enumerate(records)]
        m = align(P, S)
        for i, (j, sc) in m.items():
            attach_print(recs[i], records[j], sc)
        log(f"  print edition aligned {len(m)}/{len(P)}")
    return recs


def build_openiti(c: Collection) -> list[dict]:
    records = load_openiti(c)
    recs = []
    kitab_index: dict[str, int] = {}
    seen_numbers: collections.Counter = collections.Counter()
    bab_counter: dict[str, int] = collections.defaultdict(int)
    last_bab_key = None
    has_kitabs = any(r.kitab for r in records)
    for seq, r in enumerate(records, 1):
        if not r.text:
            continue
        k = r.kitab or ("مقدمة" if has_kitabs else c.name_ar)
        if k not in kitab_index:
            kitab_index[k] = len(kitab_index) + (0 if r.kitab is None else 1)
        bn = str(kitab_index[k])
        bab_key = (bn, r.bab)
        if r.bab and bab_key != last_bab_key:
            bab_counter[bn] += 1
        last_bab_key = bab_key
        num = r.number or str(seq)
        seen_numbers[num] += 1
        if seen_numbers[num] > 1:
            num = f"{num}.{seen_numbers[num]}"
        rec = {
            "collection": c.slug, "seq": seq, "number": num, "alt_number": None,
            "book_number": bn, "book_en": None if has_kitabs else c.name_en, "book_ar": k,
            "chapter_number": r.bab_number or (str(bab_counter[bn]) if r.bab else None),
            "chapter_en": None, "chapter_ar": r.bab,
            "in_book_ref": None, "narrator_en": None,
            "text_en": None, "text_ar": None, "text_ur": None, "grades": [],
        }
        attach_print(rec, r, 1.0)
        recs.append(rec)

    if c.hadithjson:
        hj = json.loads(sources.hadithjson_path(c.hadithjson).read_text(encoding="utf-8"))
        chapters = {ch["id"]: ch for ch in hj["chapters"]}
        H = [h for h in hj["hadiths"] if (h.get("arabic") or "").strip()]
        P = [AlignItem(key=i, text=h["arabic"], number=str(h.get("idInBook"))) for i, h in enumerate(H)]
        S = [AlignItem(key=j, text=r["text_ar"] or "", number=r["print_number"]) for j, r in enumerate(recs)]
        m = match_global(P, S)
        votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        collided = set()
        for i, (j, sc) in sorted(m.items(), key=lambda kv: -kv[1][1]):
            h = H[i]
            en = h.get("english") or {}
            rec = recs[j]
            t = clean_display(en.get("text") or "")
            narr = clean_display(en.get("narrator") or "") or None
            if t and rec["text_en"]:
                collided.add(i)
            if t and not rec["text_en"]:
                rec["text_en"] = (narr + " " + t) if narr and not t.startswith(narr) else t
                rec["narrator_en"] = narr
                rec["en_source_number"] = str(h.get("idInBook"))
                rec["en_align_score"] = round(sc, 3)
            ch = chapters.get(h.get("chapterId"))
            if has_kitabs and ch and ch.get("english"):
                votes[rec["book_number"]][ch["english"]] += 1
        for rec in recs:
            v = votes.get(rec["book_number"])
            if v:
                rec["book_en"] = v.most_common(1)[0][0]
        log(f"  hadith-json aligned {len(m)}/{len(P)} (English attached to {sum(1 for r in recs if r['text_en'])})")
        matched = {i for i in m} - collided
        # Variant wordings ("and in a narration of Muslim ...") that sunnah.com
        # lists separately belong to the preceding hadith in the printed book.
        extra = []
        prev_rec = None
        prev_chapter = None
        attached = 0
        for i, h in enumerate(H):
            en = h.get("english") or {}
            if i in matched:
                prev_rec, prev_chapter = recs[m[i][0]], h.get("chapterId")
                continue
            t = clean_display(en.get("text") or "")
            if not t:
                continue
            narr = clean_display(en.get("narrator") or "") or None
            full = (narr + " " + t) if narr and not t.startswith(narr) else t
            if prev_rec is not None and h.get("chapterId") == prev_chapter and i not in collided:
                prev_rec["text_en"] = (prev_rec["text_en"] + "\n\n" if prev_rec["text_en"] else "") + full
                attached += 1
                continue
            extra.append((h, narr, full))
        if attached:
            log(f"  attached {attached} variant narrations to their parent hadith")
        for h, narr, full in extra:
            ch = chapters.get(h.get("chapterId"), {})
            recs.append({
                "collection": c.slug, "seq": len(records) + int(h.get("idInBook") or 0), "number": f"en-{h.get('idInBook')}",
                "alt_number": None, "book_number": None, "book_en": ch.get("english"), "book_ar": ch.get("arabic"),
                "chapter_number": None, "chapter_en": None, "chapter_ar": None, "in_book_ref": None,
                "narrator_en": narr, "text_en": full,
                "text_ar": clean_display(h.get("arabic") or "") or None, "text_ur": None, "grades": [],
            })
        if extra:
            log(f"  kept {len(extra)} unplaced translated hadith")
    return recs


# --------------------------------------------------------------------------- finalise

def finalise(c: Collection, recs: list[dict]) -> tuple[list[dict], dict]:
    seen: collections.Counter = collections.Counter()
    for r in recs:
        seen[r["number"]] += 1
        if seen[r["number"]] > 1:
            r["number"] = f"{r['number']}-{seen[r['number']]}"
    for r in recs:
        r["uid"] = f"{c.slug}:{r['number']}"
        for k in ("_hint", "_lk_book_ar", "_print_kitab"):
            r.pop(k, None)
        if not r.get("book_en") and r.get("book_ar") and c.slug != "ahmad":
            r["book_en"] = kitab_english(r["book_ar"])
        cls, label = pick(r["grades"])
        r["grade"], r["grade_text"] = cls, label
        if c.sunnah_slug and c.primary == "fawaz" and not str(r["number"]).startswith("intro"):
            r["url"] = f"https://sunnah.com/{c.sunnah_slug}:{r['number']}"
        else:
            r["url"] = None
        for k in ("volume", "page", "volume_end", "page_end", "print_number", "print_align_score"):
            r.setdefault(k, None)

    # Books (kitab) and chapters (bab) with page ranges.
    books: dict[str, dict] = {}
    chapters: dict[tuple, dict] = {}
    for r in recs:
        b = books.setdefault(r["book_number"], {
            "number": r["book_number"], "name_en": r["book_en"], "name_ar": r["book_ar"],
            "hadith_count": 0, "first": r["number"], "last": r["number"],
            "volume_start": None, "page_start": None, "volume_end": None, "page_end": None})
        b["hadith_count"] += 1
        b["last"] = r["number"]
        b["name_en"] = b["name_en"] or r["book_en"]
        b["name_ar"] = b["name_ar"] or r["book_ar"]
        if r["volume"] is not None:
            if b["volume_start"] is None:
                b["volume_start"], b["page_start"] = r["volume"], r["page"]
            b["volume_end"], b["page_end"] = r["volume_end"], r["page_end"]
        if r["chapter_en"] or r["chapter_ar"]:
            key = (r["book_number"], r["chapter_number"], r["chapter_en"] or r["chapter_ar"])
            ch = chapters.setdefault(key, {
                "book_number": r["book_number"], "number": r["chapter_number"],
                "name_en": r["chapter_en"], "name_ar": r["chapter_ar"], "hadith_count": 0,
                "first": r["number"], "volume": r["volume"], "page": r["page"]})
            ch["hadith_count"] += 1
            ch["name_ar"] = ch["name_ar"] or r["chapter_ar"]
            ch["name_en"] = ch["name_en"] or r["chapter_en"]
    info = {
        "slug": c.slug, "name_en": c.name_en, "name_ar": c.name_ar,
        "author_en": c.author_en, "author_ar": c.author_ar, "died_ah": c.died_ah,
        "authenticity": c.authenticity, "group": c.group, "description": c.description,
        "edition": c.openiti.edition if c.openiti else None,
        "volumes": c.openiti.volumes if c.openiti else None,
        "hadith_count": len(recs),
        "with_english": sum(1 for r in recs if r["text_en"]),
        "with_arabic": sum(1 for r in recs if r["text_ar"]),
        "with_urdu": sum(1 for r in recs if r["text_ur"]),
        "with_page": sum(1 for r in recs if r["page"] is not None),
        "with_grade": sum(1 for r in recs if r["grade"]),
        "grade_counts": dict(collections.Counter(r["grade"] or "unknown" for r in recs)),
        "sources": [s for s in ("fawaz" if c.fawaz else None, "hadithjson" if c.hadithjson else None,
                                "lk" if c.lk else None, "openiti" if c.openiti else None) if s],
        "sunnah_slug": c.sunnah_slug, "aliases": list(c.aliases),
        "books": list(books.values()),
        "chapters": list(chapters.values()),
    }
    return recs, info


FIELDS = ["uid", "collection", "seq", "number", "alt_number", "book_number", "book_en", "book_ar",
          "chapter_number", "chapter_en", "chapter_ar", "in_book_ref", "narrator_en",
          "text_en", "text_ar", "text_ur", "grade", "grade_text", "grades",
          "volume", "page", "volume_end", "page_end", "print_number", "print_align_score", "en_source_number", "en_align_score", "url"]


def build(slugs: list[str] | None = None, download: bool = True) -> None:
    if download:
        sources.download_all()
    CORPUS.mkdir(parents=True, exist_ok=True)
    index_path = CORPUS / "collections.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    for c in COLLECTIONS:
        if slugs and c.slug not in slugs:
            continue
        log(f"[build] {c.slug} ({c.primary})")
        c_grade_source[c.slug] = (c.openiti.grade_source if c.openiti else None) or "Editor"
        recs = {"fawaz": build_fawaz, "hadithjson": build_hadithjson, "openiti": build_openiti}[c.primary](c)
        recs, info = finalise(c, recs)
        with gzip.open(CORPUS / f"{c.slug}.jsonl.gz", "wt", encoding="utf-8", compresslevel=9) as f:
            for r in recs:
                f.write(json.dumps({k: r.get(k) for k in FIELDS}, ensure_ascii=False) + "\n")
        index[c.slug] = info
        log(f"  {info['hadith_count']} hadith, {len(info['books'])} books, {len(info['chapters'])} chapters, "
            f"en={info['with_english']} ar={info['with_arabic']} ur={info['with_urdu']} "
            f"page={info['with_page']} graded={info['with_grade']}")
    order = [c.slug for c in COLLECTIONS]
    index = {k: index[k] for k in order if k in index}
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    build(sys.argv[1:] or None)
