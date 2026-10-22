#!/usr/bin/env python3
"""Expand moods/*/*.txt citation lists into full Arabic/English + meaning cards."""
from __future__ import annotations

import json
import re
import sys
import unicodedata
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
    "Ibn Hibban": "ibnhibban",
}

# Translations must be the published ones, never paraphrased. When the automatic
# extraction picks the wrong quote (a bystander's words, chain notes) these pin the
# Prophet's ﷺ words as a (first words, last words) slice of the source text, so the
# result is always a verbatim excerpt. Arabic and Urdu use the same scheme.
EN_SLICE = {
    "Tirmidhi 2020": ("Do not get angry", "Do not get angry"),
    "Bukhari 52": ("Both legal and illegal", "his religion and his honor"),
    "Bukhari 1283": ("Verily, the patience", "stroke of a calamity"),
    "Bukhari 1303": ("The eyes are shedding tears", "grieved by your separation"),
    "Muslim 923a": ("what Allah had taken belonged to Him", "seek reward from Allah"),
    "Bukhari 2908": ("Don't be afraid! Don't be afraid!", "Don't be afraid!"),
    "Muslim 2307a": ("There was nothing to be afraid of", "nothing to be afraid of"),
    "Tirmidhi 2517": ("Tie it and rely", "(upon Allah)"),
    "Ibn Majah 3818": ("Glad tidings", "record of their deeds"),
    "Ibn Majah 3882": ("Allah! Allahu Rabbi", "anything with Him)"),
    "Muslim 2573": ("Never a believer", "expiated for him"),
    "Muslim 2593": ("A'isha, verily Allah is kind", "besides it (kindness)"),
    "Muslim 2675a": ("I am near to the thought", "I rush towards him"),
    "Muslim 2610": ("I know of a wording", "Satan the accursed"),
    "Abu Dawud 4777": ("If anyone suppresses anger", "maidens he wishes"),
    "Abu Dawud 4782": ("When one of you becomes angry", "should lie down"),
    "Abu Dawud 3330": ("But between them", "what is unlawful"),
    "Ibn Majah 4251": ("Every son of Adam", "those who repent"),
    "Tirmidhi 3524": ("O Living, O Self-Sustaining", "astaghīth)"),
    "Tirmidhi 3505": ("The supplication of Dhun-Nun", "Allah responds to him"),
    "Tirmidhi 2032": ("O you who accepted Islam", "the depth of his house"),
}
AR_SLICE = {
    "Tirmidhi 2020": ("لاَ تَغْضَبْ", "لاَ تَغْضَبْ"),
    "Bukhari 52": ("الْحَلاَلُ بَيِّنٌ", "لِدِيِنِهِ وَعِرْضِهِ"),
    "Muslim 2307a": ("لَمْ تُرَاعُوا", "لَمْ تُرَاعُوا لَمْ تُرَاعُوا"),
    "Tirmidhi 3505": ("دَعْوَةُ ذِي النُّونِ", "اسْتَجَابَ اللَّهُ لَهُ"),
}
UR_SLICE = {
    "Abu Dawud 3330": ("ان دونوں کے درمیان", "حرام میں پھنس گیا"),
    "Abu Dawud 4777": ("جس نے اپنا غصہ", "جسے چاہے چن لے"),
    "Abu Dawud 4782": ("جب تم میں سے کسی کو غصہ", "ورنہ پھر لیٹ جائے"),
    "Bukhari 1283": ("صبر تو جب صدمہ", "اس وقت کرنا چاہیے"),
    "Bukhari 1303": ("آنکھوں سے آنسو جاری ہیں", "ہم تمہاری جدائی سے غمگین ہیں"),
    "Bukhari 24": ("اس کو اس کے حال پر رہنے دو", "ایمان ہی کا ایک حصہ ہے"),
    "Bukhari 2443": ("اپنے بھائی کی مدد کرو", "ظالم ہو یا مظلوم"),
    "Bukhari 2447": ("ظلم قیامت کے دن", "اندھیرے ہوں گے"),
    "Bukhari 2908": ("ڈرو مت", "ڈرو مت"),
    "Bukhari 52": ("حلال کھلا ہوا ہے", "اپنے دین اور عزت کو بچا لیا"),
    "Bukhari 6065": ("آپس میں بغض نہ رکھو", "سلام کلام چھوڑ کر رہے"),
    "Bukhari 6114": ("پہلوان وہ نہیں ہے", "بے قابو نہ ہو جائے"),
    "Bukhari 6306": ("اے اللہ! تو میرا رب ہے", "کوئی بھی گناہ نہیں معاف کرتا"),
    "Bukhari 6338": ("جب تم میں سے کوئی دعا کرے", "کوئی زبردستی کرنے والا نہیں ہے"),
    "Bukhari 6369": ("اے اللہ! میں تیری پناہ مانگتا ہوں", "لوگوں کے غلبہ سے"),
    "Bukhari 6446": ("تونگری یہ نہیں ہے", "دل غنی ہو"),
    "Bukhari 6472": ("میری امت کے ستر ہزار", "اپنے رب ہی پر بھروسہ رکھتے ہیں"),
    "Bukhari 7405": ("اللہ تعالیٰ فرماتا ہے", "دوڑ کر آ جاتا ہوں"),
    "Ibn Majah 3818": ("مبارکبادی ہے", "کثرت سے استغفار پائے"),
    "Ibn Majah 3882": ("اللہ، اللہ ہی میرا رب ہے", "شریک نہیں ٹھہراتی"),
    "Ibn Majah 4251": ("سارے بنی آدم", "توبہ کرنے والے ہیں"),
    "Muslim 1051": ("غنا مال و اسباب", "دل کی بے نیا زی ہے"),
    "Muslim 1054": ("وہ انسان کا میاب", "قناعت کی تو فیق بخشی"),
    "Muslim 2307a": ("خوف میں مبتلا نہ ہو خوف", "خوف میں مبتلانہ ہو"),
    "Muslim 2558b": ("ایک دوسرے سے بغض نہ رکھو", "تعلق ترک کیے رکھے"),
    "Muslim 2573": ("مومن کو کوئی تکلیف", "گناہوں کو مٹا دیا جاتا ہے"),
    "Muslim 2578": ("ظلم سے بچو", "حلال کر لیا"),
    "Muslim 2593": ("عائشہ! اللہ تعالیٰ نرمی", "اتنا عطا نہیں فرماتا"),
    "Muslim 2609a": ("( کوئی شخص ) پچھاڑ", "قابو میں رکھتا ہے"),
    "Muslim 2610": ("مجھے ایک ایسا کلمہ معلوم ہے", "اعوذبالله من الشيطان الرجيم"),
    "Muslim 2675a": ("اللہ عزوجل فرماتا ہے", "دوڑتا ہوا اس کے پاس جاتا ہوں"),
    "Muslim 2999": ("مومن کا معاملہ عجیب ہے", "اس کے لیے بھلائی ہوتی ہے"),
    "Muslim 923a": ("اللہ ہی کا ہے جو اس نے لے لیا", "اجر وثواب کی طلب گار ہوں"),
    "Tirmidhi 1935": ("آپس میں قطع تعلق نہ کرو", "سلام کلام بند رکھے"),
    "Tirmidhi 2014": ("مظلوم کی دعا سے ڈرو", "کوئی پردہ آڑے نہیں آتا"),
    "Tirmidhi 2020": ("غصہ مت کرو", "غصہ مت کرو"),
    "Tirmidhi 2032": ("اے اسلام لانے والے", "اگرچہ وہ اپنے گھر کے اندر ہو"),
    "Tirmidhi 2344": ("اگر تم لوگ اللہ پر توکل", "آسودہ واپس آتے ہیں"),
    "Tirmidhi 2499": ("سارے انسان خطاکار ہیں", "توبہ کرنے والے ہیں"),
    "Tirmidhi 2516": ("اے لڑکے!", "صحیفے خشک ہو گئے ہیں"),
    "Tirmidhi 2517": ("اسے باندھ دو", "پھر توکل کرو"),
    "Tirmidhi 3452": ("میں ایک ایسا کلمہ جانتا ہوں", "راندے ہوئے شیطان سے"),
    "Tirmidhi 3489": ("اے اللہ! میں تجھ سے ہدایت", "بے نیازی چاہتا ہوں"),
    "Tirmidhi 3505": ("ذوالنون ( یونس", "اس کی دعا قبول فرمائے گا"),
    "Tirmidhi 3524": ("اے زندہ اور ہمیشہ", "مدد چاہتا ہوں"),
    "Tirmidhi 3537": ("اللہ اپنے بندے کی توبہ", "خر خر کی آواز نہ آنے لگے"),
    "Tirmidhi 766": ("روزہ دار کے لیے", "اپنے رب سے ملے گا"),
}


def source_slice(ref: str, text: str, first: str, last: str) -> str:
    # NFC: some Urdu sources store آ as alef + madda; it renders identically
    text = unicodedata.normalize("NFC", re.sub(r"\s+", " ", text or ""))
    first, last = unicodedata.normalize("NFC", first), unicodedata.normalize("NFC", last)
    i = text.find(first)
    j = text.find(last, i + len(first) - len(last) if last in first else i)
    if i < 0 or j < 0:
        sys.exit(f"{ref}: slice ({first!r} … {last!r}) not found in source text")
    out = text[i : j + len(last)].replace('""', "").strip(' "“”')
    return out[0].upper() + out[1:]


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
    ar = source_slice(ref, d.get("text_ar"), *AR_SLICE[ref]) if ref in AR_SLICE else extract_matn(d.get("text_ar") or "")
    en = source_slice(ref, d.get("text_en"), *EN_SLICE[ref]) if ref in EN_SLICE else extract_en(d.get("text_en") or "")
    en = en.strip().strip("“”\"'‘’")
    if ref not in UR_SLICE:
        sys.exit(f"{ref}: add its Urdu matn to UR_SLICE")
    ur = source_slice(ref, d.get("text_ur"), *UR_SLICE[ref])
    if ar:
        parts += ["Arabic:", "", ar, ""]
    parts += ["Urdu Translation:", "", ur, ""]
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
    parts += ["Urdu Translation:", "", (d.get("text_ur") or "").strip(), ""]
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
