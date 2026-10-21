"""Merge Arabic + translations + Madani page/juz metadata into ``data/corpus/quran``."""
from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

from . import sources
from .catalog import EDITIONS, MUSHAF

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus" / "quran"


def _page_map(meta: dict) -> dict[tuple[int, int], dict]:
    """Build (surah, ayah) -> {page, juz, ruku, hizb_quarter, manzil, sajda} from page starts.

    alquran.cloud meta gives the *first* ayah of each page/juz/ruku. Fill forward.
    """
    pages = meta["data"]["pages"]["references"]          # index 0 = page 1
    juzs = meta["data"]["juzs"]["references"]
    rukus = meta["data"]["rukus"]["references"]
    hizbs = meta["data"]["hizbQuarters"]["references"]
    manzils = meta["data"]["manzils"]["references"]
    sajdas = { (s["surah"], s["ayah"]): s.get("recommended", False)
               for s in meta["data"]["sajdas"]["references"] }

    # Expand page starts into a dense map by walking all ayahs in order later.
    starts = {
        "page": [(i + 1, r["surah"], r["ayah"]) for i, r in enumerate(pages)],
        "juz": [(i + 1, r["surah"], r["ayah"]) for i, r in enumerate(juzs)],
        "ruku": [(i + 1, r["surah"], r["ayah"]) for i, r in enumerate(rukus)],
        "hizb_quarter": [(i + 1, r["surah"], r["ayah"]) for i, r in enumerate(hizbs)],
        "manzil": [(i + 1, r["surah"], r["ayah"]) for i, r in enumerate(manzils)],
    }
    return {"starts": starts, "sajdas": sajdas}


def _assign(starts: list[tuple[int, int, int]], surah: int, ayah: int) -> int:
    """Largest start whose (surah, ayah) <= current position."""
    cur = 1
    for num, s, a in starts:
        if (s, a) <= (surah, ayah):
            cur = num
        else:
            break
    return cur


def build(download: bool = True) -> None:
    log = lambda *a: print(*a, file=sys.stderr, flush=True)
    if download:
        sources.download_all()
    CORPUS.mkdir(parents=True, exist_ok=True)

    editions = {lang: json.loads(sources.edition_path(lang).read_text(encoding="utf-8"))["quran"]
                for lang in EDITIONS}
    meta = json.loads(sources.meta_path().read_text(encoding="utf-8"))
    pm = _page_map(meta)
    surah_refs = meta["data"]["surahs"]["references"]

    # Index each edition by (chapter, verse).
    by = {}
    for lang, rows in editions.items():
        by[lang] = {(r["chapter"], r["verse"]): r["text"] for r in rows}

    ayahs = []
    for r in editions["ar"]:
        s, v = r["chapter"], r["verse"]
        text_ar = (r["text"] or "").lstrip("\ufeff")
        text_en = by["en"].get((s, v), "")
        text_ur = by["ur"].get((s, v), "")
        page = _assign(pm["starts"]["page"], s, v)
        juz = _assign(pm["starts"]["juz"], s, v)
        ruku = _assign(pm["starts"]["ruku"], s, v)
        hizb = _assign(pm["starts"]["hizb_quarter"], s, v)
        manzil = _assign(pm["starts"]["manzil"], s, v)
        sajda = (s, v) in pm["sajdas"]
        ayahs.append({
            "uid": f"{s}:{v}",
            "surah": s,
            "ayah": v,
            "text_ar": text_ar,
            "text_en": text_en or None,
            "text_ur": text_ur or None,
            "page": page,
            "juz": juz,
            "ruku": ruku,
            "hizb_quarter": hizb,
            "manzil": manzil,
            "sajda": sajda,
        })

    # Surah summaries with page ranges.
    surahs = []
    for ref in surah_refs:
        n = ref["number"]
        rows = [a for a in ayahs if a["surah"] == n]
        surahs.append({
            "number": n,
            "name_ar": ref["name"],
            "name_en": ref["englishName"],
            "name_en_translation": ref["englishNameTranslation"],
            "revelation": ref["revelationType"],
            "ayah_count": ref["numberOfAyahs"],
            "page_start": rows[0]["page"],
            "page_end": rows[-1]["page"],
            "juz_start": rows[0]["juz"],
            "juz_end": rows[-1]["juz"],
        })

    # Pages index: which ayahs start each page (already in meta) + counts.
    pages = []
    for i, r in enumerate(meta["data"]["pages"]["references"], 1):
        rows = [a for a in ayahs if a["page"] == i]
        pages.append({
            "number": i,
            "surah_start": r["surah"],
            "ayah_start": r["ayah"],
            "ayah_count": len(rows),
            "juz": rows[0]["juz"] if rows else None,
        })

    with gzip.open(CORPUS / "ayahs.jsonl.gz", "wt", encoding="utf-8", compresslevel=9) as f:
        for a in ayahs:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    index = {
        "mushaf": MUSHAF,
        "editions": {lang: {"slug": e["slug"], "name": e["name"], "author": e["author"]}
                     for lang, e in EDITIONS.items()},
        "sources": {
            "fawaz_commit": __import__("quran.catalog", fromlist=["FAWAZ_COMMIT"]).FAWAZ_COMMIT,
            "alquran_meta": "https://api.alquran.cloud/v1/meta",
        },
        "surah_count": len(surahs),
        "ayah_count": len(ayahs),
        "page_count": len(pages),
        "surahs": surahs,
        "pages": pages,
        "juzs": [{"number": i + 1, "surah_start": r["surah"], "ayah_start": r["ayah"]}
                 for i, r in enumerate(meta["data"]["juzs"]["references"])],
    }
    (CORPUS / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"[quran] wrote {len(ayahs)} ayahs, {len(surahs)} surahs, {len(pages)} pages -> {CORPUS}")


if __name__ == "__main__":
    build(download="--no-download" not in sys.argv)
