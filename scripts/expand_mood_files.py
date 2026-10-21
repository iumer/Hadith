#!/usr/bin/env python3
"""Expand moods/*/*.txt citation lists into full Arabic/English + meaning cards."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from hadith.search import HadithIndex
from quran.search import QuranIndex

MOODS = ROOT / "moods"
EXPLAIN_PATH = MOODS / "_meta" / "explanations.json"
SNAP_PATH = MOODS / "_meta" / "file_refs.json"

COLL = {
    "Bukhari": "bukhari",
    "Muslim": "muslim",
    "Tirmidhi": "tirmidhi",
    "Abu Dawud": "abudawud",
    "Nasa'i": "nasai",
    "Ibn Majah": "ibnmajah",
    "Adab al-Mufrad": "adab",
    "Nawawi 40": "nawawi40",
}

EN_FIX = {
    "Tirmidhi 2020": "Do not get angry.",
}
AR_FIX = {
    "Tirmidhi 2020": "لَا تَغْضَبْ",
}


def extract_matn(ar: str) -> str:
    if not ar:
        return ""
    quotes = re.findall(r"‏\s*\"‏\s*(.*?)\s*‏\"‏", ar, re.S)
    if not quotes:
        quotes = re.findall(r"«(.*?)»", ar, re.S)
    if quotes:
        quotes = [re.sub(r"\s+", " ", x).strip() for x in quotes if x.strip()]
        return max(quotes, key=len)
    m = re.search(r"قال رسول الله[^«\"]*[«\"](.*?)[»\"]", ar, re.S)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return re.sub(r"\s+", " ", ar).strip()


def extract_en(en: str) -> str:
    if not en:
        return ""
    ms = re.findall(r"[“\"]([^“\"]{10,})[”\"]", en)
    if ms:
        t = max(ms, key=len).strip().rstrip(".")
        return t + "."
    m = re.search(r"(?:said|saying)\s*[:，,]?\s*[“\"]?(.*)", en, re.I | re.S)
    if m:
        t = m.group(1).strip().strip('"“”').rstrip(".")
        return t + "."
    return en.strip().rstrip(".") + "."


def narrator_line(d: dict) -> str:
    n = (d.get("narrator_en") or "").strip().rstrip(":")
    if n:
        # Some sources already store a full lead-in ("Abu Hurairah narrated that…").
        if re.search(r"\bnarrated that\b|\breported that\b|\bsaid that\b", n, re.I) or len(n) > 48:
            base = n[0].upper() + n[1:] if n else n
        elif re.match(r"^(Narrated|It was narrated)", n, re.I) or "reported" in n.lower():
            base = n
        else:
            base = "Narrated " + n
        if "رضي الله" not in base:
            base = base + " (رضي الله عنه/عنهم)"
        return base + ":"
    en = d.get("text_en") or ""
    m = re.match(r"^((?:Narrated|It was narrated)[^.:]+|[\w `'.-]+ reported[^.]*?)", en)
    if m:
        return m.group(1).rstrip(":") + " (رضي الله عنه/عنهم):"
    return "It is narrated:"


def book_line(d: dict) -> str | None:
    num, en, ar = d.get("book_number"), d.get("book_en"), d.get("book_ar")
    if not en and not ar:
        return None
    if num not in (None, "", 0, "0"):
        if en and ar and ar != en:
            return f"Book {num}: {en} ({ar})"
        return f"Book {num}: {en or ar}"
    if en and ar and ar != en:
        return f"{en} ({ar})"
    return en or ar


def format_hadith(ref: str, d: dict, meaning: str, reflection: str) -> str:
    title = f"{d.get('collection_name_en') or ref.split()[0]} {d['number']}"
    parts = [title, ""]
    bl = book_line(d)
    if bl:
        parts += [bl, ""]
    parts += [narrator_line(d), "", "The Prophet Muhammad ﷺ said:", ""]
    ar = AR_FIX.get(ref) or extract_matn(d.get("text_ar") or "")
    en = EN_FIX.get(ref) or extract_en(d.get("text_en") or "")
    en = en.strip().strip("“”\"")
    if ar:
        parts += ["Arabic:", "", ar, ""]
    parts += ["English Translation:", "", f"“{en}”", ""]
    parts += ["Meaning ❤️", "", meaning.strip(), ""]
    parts += ["Reflection", "", reflection.strip(), ""]
    ref_line = f"Reference: {d.get('collection_name_en') or ref.split()[0]} {d['number']}"
    if d.get("book_en"):
        ref_line += f", Book of {d['book_en']}."
    else:
        ref_line += "."
    parts.append(ref_line)
    return "\n".join(parts).rstrip() + "\n"


def format_quran(d: dict, meaning: str, reflection: str) -> str:
    s, a = d["surah"], d["ayah"]
    surah = d.get("surah_en") or ""
    parts = [f"Quran {s}:{a}", ""]
    if surah:
        ar_name = d.get("surah_ar") or ""
        parts += [f"Surah {surah}" + (f" ({ar_name})" if ar_name else ""), ""]
    parts += ["Arabic:", "", (d.get("text_ar") or "").strip(), ""]
    parts += ["English Translation:", "", f"“{(d.get('text_en') or '').strip()}”", ""]
    parts += ["Meaning ❤️", "", meaning.strip(), ""]
    parts += ["Reflection", "", reflection.strip(), ""]
    parts.append(f"Reference: Quran {s}:{a}" + (f", Surah {surah}." if surah else "."))
    return "\n".join(parts).rstrip() + "\n"


def parse_ref_line(line: str, hx: HadithIndex, qx: QuranIndex):
    if line.startswith("Quran "):
        s, a = map(int, line.split()[1].split(":"))
        return "quran", qx.get(s, a)
    for name, slug in sorted(COLL.items(), key=lambda x: -len(x[0])):
        if line.startswith(name + " "):
            return "hadith", hx.get(slug, line[len(name) + 1 :])
    raise KeyError(line)


def snapshot_refs() -> dict[str, list[str]]:
    if SNAP_PATH.exists():
        return json.loads(SNAP_PATH.read_text(encoding="utf-8"))
    data: dict[str, list[str]] = {}
    for p in sorted(MOODS.rglob("*.txt")):
        if "_meta" in p.parts:
            continue
        lines = [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            continue
        if lines[0].startswith("Quran ") or any(lines[0].startswith(k) for k in COLL):
            data[str(p.relative_to(MOODS))] = lines
    if not data:
        sys.exit("no citation-only mood files found to expand")
    SNAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAP_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"snapshotted {len(data)} files -> {SNAP_PATH}")
    return data


def main() -> None:
    explain = json.loads(EXPLAIN_PATH.read_text(encoding="utf-8"))
    lists = snapshot_refs()
    hx, qx = HadithIndex(semantic=False), QuranIndex()
    missing: list[str] = []
    for rel, ref_list in lists.items():
        blocks = []
        for ref in ref_list:
            if ref not in explain:
                missing.append(f"{rel}: {ref} (no explanation)")
                continue
            kind, d = parse_ref_line(ref, hx, qx)
            if not d:
                missing.append(f"{rel}: {ref} (not in index)")
                continue
            m, r = explain[ref]["meaning"], explain[ref]["reflection"]
            if kind == "quran":
                blocks.append(format_quran(d, m, r))
            else:
                blocks.append(format_hadith(ref, d, m, r))
        out = ("\n" + ("─" * 40) + "\n\n").join(blocks)
        (MOODS / rel).write_text(out + ("\n" if out and not out.endswith("\n") else ""), encoding="utf-8")
        print(f"wrote {rel} ({len(ref_list)} entries)")
    if missing:
        print("MISSING:")
        print("\n".join("  " + m for m in missing))
        sys.exit(1)
    print("done")


if __name__ == "__main__":
    main()
