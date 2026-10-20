"""Build the SQLite search database from ``data/corpus``.

Tables
------
collections   one row per book collection (metadata, edition, authenticity)
books         kitab divisions with hadith counts and printed page ranges
chapters      bab divisions
hadiths       every hadith with full reference data and texts
fts_en        FTS5 (porter) over English text / chapter / book / narrator
fts_ar        FTS5 over normalised Arabic text, light stems, Arabic headings, Urdu

The database is a single portable file usable from Python, Node, Swift,
Kotlin, etc.  (any SQLite build with FTS5).
"""
from __future__ import annotations

import gzip
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

from .normalize import normalize_arabic, normalize_english, stem_arabic

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "corpus"
DEFAULT_DB = Path(os.environ.get("HADITH_DB", ROOT / "data" / "build" / "hadith.db"))
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE collections (
    slug TEXT PRIMARY KEY, position INTEGER, name_en TEXT, name_ar TEXT, author_en TEXT, author_ar TEXT,
    died_ah INTEGER, authenticity TEXT, grp TEXT, description TEXT, edition TEXT, volumes INTEGER,
    hadith_count INTEGER, with_english INTEGER, with_arabic INTEGER, with_urdu INTEGER,
    with_page INTEGER, with_grade INTEGER, grade_counts TEXT, sources TEXT, sunnah_slug TEXT, aliases TEXT
);
CREATE TABLE books (
    id INTEGER PRIMARY KEY, collection TEXT, number TEXT, position INTEGER, name_en TEXT, name_ar TEXT,
    hadith_count INTEGER, first TEXT, last TEXT, volume_start INTEGER, page_start INTEGER,
    volume_end INTEGER, page_end INTEGER
);
CREATE TABLE chapters (
    id INTEGER PRIMARY KEY, collection TEXT, book_number TEXT, number TEXT, position INTEGER,
    name_en TEXT, name_ar TEXT, hadith_count INTEGER, first TEXT, volume INTEGER, page INTEGER
);
CREATE TABLE hadiths (
    id INTEGER PRIMARY KEY, uid TEXT UNIQUE, collection TEXT, seq INTEGER, number TEXT, alt_number TEXT,
    book_number TEXT, book_en TEXT, book_ar TEXT, chapter_number TEXT, chapter_en TEXT, chapter_ar TEXT,
    in_book_ref TEXT, narrator_en TEXT, text_en TEXT, text_ar TEXT, text_ur TEXT,
    grade TEXT, grade_text TEXT, grades TEXT, volume INTEGER, page INTEGER, volume_end INTEGER,
    page_end INTEGER, print_number TEXT, url TEXT, matn_key TEXT
);
CREATE INDEX hadiths_ref ON hadiths(collection, number);
CREATE INDEX hadiths_book ON hadiths(collection, book_number, seq);
CREATE INDEX hadiths_page ON hadiths(collection, volume, page);
CREATE INDEX books_c ON books(collection, position);
CREATE INDEX chapters_c ON chapters(collection, book_number, position);
CREATE VIRTUAL TABLE fts_en USING fts5(
    text, chapter, book, narrator, content='', tokenize='porter unicode61 remove_diacritics 2'
);
CREATE VIRTUAL TABLE fts_ar USING fts5(
    text, stem, chapter, urdu, content='', tokenize='unicode61 remove_diacritics 2'
);
"""


def _matn_key(text_ar: str | None) -> str | None:
    """Tail of the normalised Arabic text: the matn usually follows the isnad,
    so the ending identifies the same hadith across collections."""
    if not text_ar:
        return None
    t = normalize_arabic(text_ar, drop_formulas=True)
    return t[-220:] if t else None


def build_index(db_path: Path = DEFAULT_DB, corpus: Path = CORPUS, verbose: bool = True) -> Path:
    log = (lambda *a: print(*a, file=sys.stderr, flush=True)) if verbose else (lambda *a: None)
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = db_path.with_suffix(".tmp")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;" + SCHEMA)
    index = json.loads((corpus / "collections.json").read_text(encoding="utf-8"))
    t0 = time.time()
    hid = 0
    for pos, (slug, info) in enumerate(index.items()):
        con.execute(
            "INSERT INTO collections VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (slug, pos, info["name_en"], info["name_ar"], info["author_en"], info["author_ar"], info["died_ah"],
             info["authenticity"], info["group"], info["description"], info["edition"], info["volumes"],
             info["hadith_count"], info["with_english"], info["with_arabic"], info["with_urdu"],
             info["with_page"], info["with_grade"], json.dumps(info["grade_counts"]),
             json.dumps(info["sources"]), info["sunnah_slug"], json.dumps(info["aliases"], ensure_ascii=False)))
        for i, b in enumerate(info["books"]):
            con.execute("INSERT INTO books (collection, number, position, name_en, name_ar, hadith_count, first, last,"
                        " volume_start, page_start, volume_end, page_end) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (slug, b["number"], i, b["name_en"], b["name_ar"], b["hadith_count"], b["first"], b["last"],
                         b["volume_start"], b["page_start"], b["volume_end"], b["page_end"]))
        for i, ch in enumerate(info["chapters"]):
            con.execute("INSERT INTO chapters (collection, book_number, number, position, name_en, name_ar,"
                        " hadith_count, first, volume, page) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (slug, ch["book_number"], ch["number"], i, ch["name_en"], ch["name_ar"],
                         ch["hadith_count"], ch["first"], ch["volume"], ch["page"]))
        rows, en_rows, ar_rows = [], [], []
        with gzip.open(corpus / f"{slug}.jsonl.gz", "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                hid += 1
                rows.append((hid, r["uid"], slug, r["seq"], r["number"], r["alt_number"], r["book_number"],
                             r["book_en"], r["book_ar"], r["chapter_number"], r["chapter_en"], r["chapter_ar"],
                             r["in_book_ref"], r["narrator_en"], r["text_en"], r["text_ar"], r["text_ur"],
                             r["grade"], r["grade_text"], json.dumps(r["grades"], ensure_ascii=False),
                             r["volume"], r["page"], r["volume_end"], r["page_end"], r["print_number"], r["url"],
                             _matn_key(r["text_ar"])))
                if r["text_en"] or r["chapter_en"] or r["book_en"]:
                    en_rows.append((hid, normalize_english(r["text_en"] or ""),
                                    normalize_english(r["chapter_en"] or ""),
                                    normalize_english(r["book_en"] or ""),
                                    normalize_english(r["narrator_en"] or "")))
                ar = normalize_arabic(r["text_ar"] or "")
                ar_rows.append((hid, ar, stem_arabic(normalize_arabic(r["text_ar"] or "", drop_formulas=True)),
                                normalize_arabic(" ".join(x for x in (r["chapter_ar"], r["book_ar"]) if x)),
                                normalize_arabic(r["text_ur"] or "")))
        con.executemany("INSERT INTO hadiths VALUES (" + ",".join("?" * 27) + ")", rows)
        con.executemany("INSERT INTO fts_en (rowid, text, chapter, book, narrator) VALUES (?,?,?,?,?)", en_rows)
        con.executemany("INSERT INTO fts_ar (rowid, text, stem, chapter, urdu) VALUES (?,?,?,?,?)", ar_rows)
        log(f"[index] {slug}: {len(rows)} hadith ({time.time() - t0:.0f}s)")
    con.execute("INSERT INTO fts_en(fts_en) VALUES ('optimize')")
    con.execute("INSERT INTO fts_ar(fts_ar) VALUES ('optimize')")
    con.executemany("INSERT INTO meta VALUES (?,?)", [
        ("schema_version", str(SCHEMA_VERSION)), ("built_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
        ("hadith_count", str(hid))])
    con.commit()
    con.execute("VACUUM")
    con.close()
    tmp.replace(db_path)
    log(f"[index] wrote {db_path} ({db_path.stat().st_size / 1e6:.0f} MB, {hid} hadith)")
    return db_path


if __name__ == "__main__":
    build_index(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB)
