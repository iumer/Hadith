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
    "Tirmidhi 2346": ("Whoever among you wakes up", "gathered for him"),
    "Bukhari 6384": ("O `Abdullah bin Qais! Say", "for it is one of the treasures of Paradise"),
    "Muslim 2577a": ("O My servants, all of you are astray", "I shall guide you"),
    "Tirmidhi 2020": ("Teach me something", "Do not get angry"),
    "Bukhari 1283": ("The Prophet (ﷺ) passed by a woman", "stroke of a calamity"),
    "Bukhari 1303": ("`Abdur Rahman bin `Auf said", "grieved by your separation"),
    "Muslim 923a": ("what Allah had taken belonged to Him", "seek reward from Allah"),
    "Muslim 918a": ("If any Muslim who suffers", "better than it in exchange"),
    "Bukhari 2908": ("The 'Prophet was the best", "Don't be afraid! Don't be afraid!"),
    "Tirmidhi 2517": ("O Messenger of Allah! Shall I tie it", "Tie it and rely(upon Allah)"),
    "Ibn Majah 3882": ("The Messenger of Allah (ﷺ) taught me", "anything with Him)"),
    "Muslim 2573": ("Never a believer", "expiated for him"),
    "Muslim 2593": ("A'isha, verily Allah is kind", "besides it (kindness)"),
    "Muslim 2610": ("I know of a wording", "Satan the accursed"),
    "Abu Dawud 4777": ("If anyone suppresses anger", "maidens he wishes"),
    "Abu Dawud 4782": ("When one of you becomes angry", "should lie down"),
    "Tirmidhi 3524": ("O Living, O Self-Sustaining", "astaghīth)"),
    "Tirmidhi 3505": ("The supplication of Dhun-Nun", "Allah responds to him"),
    "Abu Dawud 2774": ("When anything came", "gratitude to Allah"),
    "Bukhari 39": ("Religion is very easy", "last hours of the nights"),
    "Bukhari 6465": ("What deeds are loved most", "within your ability"),
    "Tirmidhi 3540": ("O son of Adam! Verily", "nearly as great as it"),
    "Muslim 2664": ("A strong believer", "for the Satan"),
    "Bukhari 4563": ("Allah is Sufficient for us and He Is", "(of affairs, for us)"),
    "Ibn Majah 4216": ("Which of the people is best", "rancor or envy in it"),
    "Bukhari 2441": ("Allah will bring a believer near", "forgive them for you today"),
    "Muslim 132a": ("Verily we perceive in our minds", "the faith manifest"),
}
AR_SLICE = {
    "Tirmidhi 2346": ("مَنْ أَصْبَحَ مِنْكُمْ", "حِيزَتْ لَهُ الدُّنْيَا"),
    "Bukhari 6384": ("يَا عَبْدَ اللَّهِ بْنَ قَيْسٍ", "كُنُوزِ الْجَنَّةِ ‏"),
    "Muslim 2577a": ("يَا عِبَادِي كُلُّكُمْ ضَالٌّ", "أَهْدِكُمْ"),
    "Tirmidhi 2020": ("عَلِّمْنِي شَيْئًا", "لاَ تَغْضَبْ"),
    "Bukhari 1283": ("مَرَّ النَّبِيُّ", "الصَّدْمَةِ الأُولَى"),
    "Bukhari 1303": ("فَقَالَ لَهُ عَبْدُ الرَّحْمَنِ", "لَمَحْزُونُونَ"),
    "Bukhari 2908": ("كَانَ النَّبِيُّ", "لَمْ تُرَاعُوا لَمْ تُرَاعُوا"),
    "Tirmidhi 2517": ("يَا رَسُولَ اللَّهِ أَعْقِلُهَا", "اعْقِلْهَا وَتَوَكَّلْ"),
    "Tirmidhi 3505": ("دَعْوَةُ ذِي النُّونِ", "اسْتَجَابَ اللَّهُ لَهُ"),
    "Muslim 918a": ("مَا مِنْ مُسْلِمٍ", "إِلاَّ أَخْلَفَ اللَّهُ لَهُ خَيْرًا مِنْهَا"),
    "Abu Dawud 2774": ("كَانَ إِذَا جَاءَهُ", "شَاكِرًا لِلَّهِ"),
    "Bukhari 6465": ("سُئِلَ النَّبِيُّ", "مَا تُطِيقُونَ"),
    "Bukhari 4563": ("حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ", "وَنِعْمَ الْوَكِيلُ"),
    "Ibn Majah 4216": ("أَىُّ النَّاسِ أَفْضَلُ", "وَلاَ حَسَدَ"),
    "Bukhari 2441": ("إِنَّ اللَّهَ يُدْنِي", "أَغْفِرُهَا لَكَ الْيَوْمَ"),
    "Muslim 132a": ("إِنَّا نَجِدُ فِي أَنْفُسِنَا", "صَرِيحُ الإِيمَانِ"),
    "Ibn Majah 3882": ("عَلَّمَنِي رَسُولُ اللَّهِ", "لاَ أُشْرِكُ بِهِ شَيْئًا"),
}
UR_SLICE = {
    "Bukhari 6384": ("عبداللہ بن قیس کہو", "ایک خزانہ ہے"),
    "Muslim 2577a": ("میرے بندو! تم سب کے سب گمراہ ہو", "میں تمہیں ہدایت دوں گا"),
    "Abu Dawud 3330": ("ان دونوں کے درمیان", "حرام میں پھنس گیا"),
    "Abu Dawud 4777": ("جس نے اپنا غصہ", "جسے چاہے چن لے"),
    "Abu Dawud 4782": ("جب تم میں سے کسی کو غصہ", "ورنہ پھر لیٹ جائے"),
    "Bukhari 24": ("اس کو اس کے حال پر رہنے دو", "ایمان ہی کا ایک حصہ ہے"),
    "Bukhari 2443": ("اپنے بھائی کی مدد کرو", "ظالم ہو یا مظلوم"),
    "Bukhari 2447": ("ظلم قیامت کے دن", "اندھیرے ہوں گے"),
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
    "Tirmidhi 2032": ("اے اسلام لانے والے", "اگرچہ وہ اپنے گھر کے اندر ہو"),
    "Tirmidhi 2344": ("اگر تم لوگ اللہ پر توکل", "آسودہ واپس آتے ہیں"),
    "Tirmidhi 2499": ("سارے انسان خطاکار ہیں", "توبہ کرنے والے ہیں"),
    "Tirmidhi 2516": ("اے لڑکے!", "صحیفے خشک ہو گئے ہیں"),
    "Tirmidhi 3452": ("میں ایک ایسا کلمہ جانتا ہوں", "راندے ہوئے شیطان سے"),
    "Tirmidhi 3489": ("اے اللہ! میں تجھ سے ہدایت", "بے نیازی چاہتا ہوں"),
    "Tirmidhi 3505": ("ذوالنون ( یونس", "اس کی دعا قبول فرمائے گا"),
    "Tirmidhi 3524": ("اے زندہ اور ہمیشہ", "مدد چاہتا ہوں"),
    "Tirmidhi 3537": ("اللہ اپنے بندے کی توبہ", "خر خر کی آواز نہ آنے لگے"),
    "Tirmidhi 766": ("روزہ دار کے لیے", "اپنے رب سے ملے گا"),
    "Muslim 2963a": ("جب تم میں سے کوئی شخص اس کی طرف دیکھے", "اسے فضیلت حاصل ہے"),
    "Abu Dawud 2774": ("نبی اکرم صلی اللہ علیہ وسلم کے پاس جب کوئی خوشی", "سجدہ میں گر پڑتے"),
    "Muslim 2734a": ("اللہ تعالیٰ اس بات پر", "اللہ کی حمد کرے"),
    "Muslim 918a": ("کوئی مسلمان نہیں جسے مصیبت پہنچے", "بہتر بدل عطا فرمادیتا ہے"),
    "Bukhari 6407": ("اس شخص کی مثال", "زندہ اور مردہ جیسی ہے"),
    "Bukhari 39": ("بیشک دین آسان ہے", "مدد حاصل کرو"),
    "Bukhari 6465": ("کون سا عمل اللہ کے نزدیک", "جتنی طاقت ہے"),
    "Tirmidhi 3540": ("اللہ کہتا ہے", "مغفرت لے کر آؤں گا"),
    "Muslim 2664": ("طاقت ور مومن", "کو کھول دیتا ہے"),
    "Bukhari 4563": ("کلمہ «حسبنا", "بہترین کام بنانے والا ہے"),
    "Muslim 2564c": ("اللہ تعالیٰ تمہاری صورتوں", "اعمال کی طرف دیکھتا ہے"),
    "Muslim 2582": ("قیامت کے دن تم سب", "پورا پورا لیا جائے گا"),
    "Ibn Majah 4216": ("لوگوں میں سب سے بہتر کون ہے", "نہ کینہ اور نہ حسد"),
    "Bukhari 2441": ("اللہ تعالیٰ مومن کو اپنے نزدیک", "آج بھی میں تیری مغفرت کرتا ہوں"),
    "Muslim 2749": ("اس ذات کی قسم", "ان کی مغفرت فرمائے"),
    "Muslim 2588": ("صدقے نے مال میں", "اس کا مقام بلند کر دیتا ہے"),
    "Tirmidhi 2518": ("اس چیز کو چھوڑ دو", "شک میں مبتلا کرتا ہے"),
    "Muslim 132a": ("ہم اپنے دلوں میں ایسی چیزیں", "یہی صریح ایمان ہے"),
    "Bukhari 3276": ("تم میں سے کسی کے پاس شیطان", "شیطانی خیال کو چھوڑ دے"),
    "Tirmidhi 2346": ("تم میں سے جس نے بھی صبح کی", "پوری دنیا سمیٹ دی گئی"),
    "Tirmidhi 2020": ("مجھے کچھ سکھائیے", "غصہ مت کرو"),
    "Tirmidhi 2517": ("اللہ کے رسول! کیا میں اونٹ", "پھر توکل کرو"),
    "Bukhari 1283": ("نبی کریم صلی اللہ علیہ وسلم کا گزر", "اس وقت کرنا چاہیے"),
    "Bukhari 1303": ("تو عبدالرحمٰن بن عوف", "جدائی سے غمگین ہیں"),
    "Bukhari 2908": ("نبی کریم صلی اللہ علیہ وسلم سب سے زیادہ خوبصورت", "ڈرو مت"),
    "Ibn Majah 3882": ("رسول اللہ صلی اللہ علیہ وسلم نے مجھے یہ کلمات", "شریک نہیں ٹھہراتی"),
}


def source_slice(ref: str, text: str, first: str, last: str) -> str:
    # NFC: some Urdu sources store آ as alef + madda; it renders identically
    text = unicodedata.normalize("NFC", re.sub(r"\s+", " ", text or ""))
    first, last = unicodedata.normalize("NFC", first), unicodedata.normalize("NFC", last)
    i = text.find(first)
    j = text.rfind(last, i)
    if i < 0 or j < 0:
        sys.exit(f"{ref}: slice ({first!r} … {last!r}) not found in source text")
    out = text[i : j + len(last)]
    if re.search(r"[\u0600-\u06FF]", out):
        out = re.sub(r"\s+", " ", re.sub(r'[\u200f"{}]|‏\.‏', "", out))
    out = out.replace('""', "").strip(' "“”')
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


AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def join_ayahs(ayahs: list[dict]) -> dict:
    """One card for a passage of consecutive ayahs, each followed by its number."""
    if len(ayahs) == 1:
        return ayahs[0]
    first, last = ayahs[0], ayahs[-1]
    return {
        **first,
        "ref": f"{first['surah']}:{first['ayah']}-{last['ayah']}",
        "text_ar": " ".join(f"{x['text_ar'].strip()} ﴿{str(x['ayah']).translate(AR_DIGITS)}﴾" for x in ayahs),
        "text_ur": " ".join(f"({x['ayah']}) {x['text_ur'].strip()}" for x in ayahs),
        "text_en": " ".join(f"({x['ayah']}) {x['text_en'].strip()}" for x in ayahs),
    }


def format_quran(d: dict, meaning: str, reflection: str) -> str:
    s, a = d["surah"], d.get("ref", f"{d['surah']}:{d['ayah']}").split(":")[1]
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
        s, rng = line.split()[1].split(":")
        lo, _, hi = rng.partition("-")
        ayahs = [qx.get(int(s), n) for n in range(int(lo), int(hi or lo) + 1)]
        return "quran", join_ayahs(ayahs) if all(ayahs) else None
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
