"""Build the SQLite FTS5 search database from ``data/corpus/quran``."""
from __future__ import annotations

import gzip
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# Reuse the same Arabic/English normalisation as the hadith package.
from hadith.normalize import normalize_arabic, normalize_english, stem_arabic

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus" / "quran"
DEFAULT_DB = Path(os.environ.get("QURAN_DB", ROOT / "data" / "build" / "quran.db"))
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE surahs (
    number INTEGER PRIMARY KEY, name_ar TEXT, name_en TEXT, name_en_translation TEXT,
    revelation TEXT, ayah_count INTEGER, page_start INTEGER, page_end INTEGER,
    juz_start INTEGER, juz_end INTEGER
);
CREATE TABLE pages (
    number INTEGER PRIMARY KEY, surah_start INTEGER, ayah_start INTEGER,
    ayah_count INTEGER, juz INTEGER
);
CREATE TABLE juzs (
    number INTEGER PRIMARY KEY, surah_start INTEGER, ayah_start INTEGER
);
CREATE TABLE ayahs (
    id INTEGER PRIMARY KEY, uid TEXT UNIQUE, surah INTEGER, ayah INTEGER,
    text_ar TEXT, text_en TEXT, text_ur TEXT,
    page INTEGER, juz INTEGER, ruku INTEGER, hizb_quarter INTEGER, manzil INTEGER,
    sajda INTEGER, surah_en TEXT, surah_ar TEXT
);
CREATE INDEX ayahs_ref ON ayahs(surah, ayah);
CREATE INDEX ayahs_page ON ayahs(page);
CREATE INDEX ayahs_juz ON ayahs(juz);
CREATE VIRTUAL TABLE fts_en USING fts5(
    text, surah, content='', tokenize='porter unicode61 remove_diacritics 2'
);
CREATE VIRTUAL TABLE fts_ar USING fts5(
    text, stem, surah, urdu, content='', tokenize='unicode61 remove_diacritics 2'
);
"""


def build_index(db_path: Path = DEFAULT_DB, corpus: Path = CORPUS, verbose: bool = True) -> Path:
    log = (lambda *a: print(*a, file=sys.stderr, flush=True)) if verbose else (lambda *a: None)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = db_path.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;" + SCHEMA)
    index = json.loads((corpus / "index.json").read_text(encoding="utf-8"))
    t0 = time.time()

    for s in index["surahs"]:
        con.execute("INSERT INTO surahs VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (s["number"], s["name_ar"], s["name_en"], s["name_en_translation"],
                     s["revelation"], s["ayah_count"], s["page_start"], s["page_end"],
                     s["juz_start"], s["juz_end"]))
    for p in index["pages"]:
        con.execute("INSERT INTO pages VALUES (?,?,?,?,?)",
                    (p["number"], p["surah_start"], p["ayah_start"], p["ayah_count"], p["juz"]))
    for j in index["juzs"]:
        con.execute("INSERT INTO juzs VALUES (?,?,?)",
                    (j["number"], j["surah_start"], j["ayah_start"]))

    surah_en = {s["number"]: s["name_en"] for s in index["surahs"]}
    surah_ar = {s["number"]: s["name_ar"] for s in index["surahs"]}
    rows, en_rows, ar_rows = [], [], []
    with gzip.open(corpus / "ayahs.jsonl.gz", "rt", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            a = json.loads(line)
            rows.append((i, a["uid"], a["surah"], a["ayah"], a["text_ar"], a["text_en"], a["text_ur"],
                         a["page"], a["juz"], a["ruku"], a["hizb_quarter"], a["manzil"],
                         int(a["sajda"]), surah_en[a["surah"]], surah_ar[a["surah"]]))
            if a["text_en"]:
                en_rows.append((i, normalize_english(a["text_en"]),
                                normalize_english(surah_en[a["surah"]])))
            ar = normalize_arabic(a["text_ar"] or "")
            ar_rows.append((i, ar, stem_arabic(normalize_arabic(a["text_ar"] or "", drop_formulas=True)),
                            normalize_arabic(surah_ar[a["surah"]]),
                            normalize_arabic(a["text_ur"] or "")))
    con.executemany("INSERT INTO ayahs VALUES (" + ",".join("?" * 15) + ")", rows)
    con.executemany("INSERT INTO fts_en (rowid, text, surah) VALUES (?,?,?)", en_rows)
    con.executemany("INSERT INTO fts_ar (rowid, text, stem, surah, urdu) VALUES (?,?,?,?,?)", ar_rows)
    con.execute("INSERT INTO fts_en(fts_en) VALUES ('optimize')")
    con.execute("INSERT INTO fts_ar(fts_ar) VALUES ('optimize')")
    con.executemany("INSERT INTO meta VALUES (?,?)", [
        ("schema_version", str(SCHEMA_VERSION)),
        ("built_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
        ("ayah_count", str(len(rows))),
        ("mushaf", json.dumps(index["mushaf"])),
        ("editions", json.dumps(index["editions"], ensure_ascii=False)),
    ])
    con.commit()
    con.execute("VACUUM")
    con.close()
    tmp.replace(db_path)
    log(f"[quran-index] wrote {db_path} ({db_path.stat().st_size / 1e6:.1f} MB, "
        f"{len(rows)} ayahs, {time.time() - t0:.0f}s)")
    return db_path


if __name__ == "__main__":
    build_index(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB)
