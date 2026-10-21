"""Quran search engine (SQLite FTS5 + Reciprocal Rank Fusion).

1. **Reference lookup** – ``2:255``, ``al-baqarah 255``, ``surah 2 ayah 255``,
   ``page 6``, ``juz 30``.
2. **Normalisation** – same Arabic/English folding as the hadith package.
3. **Retrieval** – FTS5 BM25 over English translation, Arabic text/stems, Urdu.
4. **Fusion** – Reciprocal Rank Fusion, then term-coverage re-rank.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from hadith.normalize import (fold_latin, is_arabic, normalize_arabic, normalize_english,
                              stem_arabic_word)

from .index import DEFAULT_DB

EN_STOPWORDS = set("""
a an the of and or to in on at for from by with about as is are was were be been being it its this that these
those i me my we our you your he him his she her they them their what which who whom whose when where why how
all any both each few more most other some such no nor not only own same so than too very can will just should
now do does did doing have has had having would could may might must shall into over under again further then
once here there up down out off above below between through during before after quran koran verse ayah surah
show give find about regarding concerning related relating allah god lord
""".split())
AR_STOPWORDS = set(normalize_arabic(w) for w in """
في من على عن الى إلى ان أن إن ما لا لم لن هو هي هم ثم او أو قد كان قال قرآن القران سورة اية آية ذلك هذا هذه التي الذي
""".split())
URDU_LETTERS = set("ٹڈڑںےۓہھگکی")

REF_COLON = re.compile(r"^\s*(\d{1,3})\s*[:：]\s*(\d{1,3})\s*$")
REF_SURAH_AYAH = re.compile(
    r"^\s*(?:surah|sura|سورة)?\s*(?P<surah>[\w\u0600-\u06FF\-']+?)\s+"
    r"(?:ayah|aya|verse|ayat|آية|آيت|آیہ)?\s*(?P<ayah>\d{1,3})\s*$",
    re.I,
)
REF_PAGE = re.compile(r"^\s*(?:page|p\.?|صفحة|صفحہ)\s*(\d{1,3})\s*$", re.I)
REF_JUZ = re.compile(r"^\s*(?:juz|para|جزء|پارہ)\s*(\d{1,2})\s*$", re.I)


@dataclass
class Hit:
    ayah: dict
    score: float
    signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = dict(self.ayah)
        d["score"] = round(self.score, 5)
        if self.signals:
            d["signals"] = self.signals
        return d


@dataclass
class SearchResponse:
    query: str
    kind: str                       # "reference" | "page" | "juz" | "search"
    hits: list[Hit]
    total_candidates: int = 0

    def to_dict(self) -> dict:
        return {"query": self.query, "kind": self.kind, "total_candidates": self.total_candidates,
                "hits": [h.to_dict() for h in self.hits]}


def _fts_quote(term: str) -> str:
    return '"' + term.replace('"', " ") + '"'


class QuranIndex:
    def __init__(self, db_path: str | Path | None = None):
        path = Path(db_path or DEFAULT_DB)
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found - run `python -m quran setup` (or `python -m quran index`) first")
        self.con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self._surahs = {r["number"]: dict(r) for r in self.con.execute("SELECT * FROM surahs ORDER BY number")}
        self._alias: list[tuple[str, int]] = []
        for n, s in self._surahs.items():
            names = {str(n), s["name_en"], s["name_ar"], s["name_en_translation"] or ""}
            # Common short forms: "baqarah", "al-baqarah", "fatiha", "faatiha"
            en = fold_latin(s["name_en"] or "")
            names.add(en)
            short = re.sub(r"^(al|an|ar|as|at|ad)-?", "", en).strip()
            names.add(short)
            for variant in (en, short):
                names.add(self._loose_latin(variant))
            for name in names:
                if not name:
                    continue
                nrm = self._norm_name(name)
                self._alias.append((nrm, n))
                compact = nrm.replace(" ", "")
                if compact != nrm:
                    self._alias.append((compact, n))
        self._alias.sort(key=lambda x: -len(x[0]))

    @staticmethod
    def _loose_latin(s: str) -> str:
        """Collapse common transliteration variants (faatiha→fatiha, yaseen→yasin)."""
        s = fold_latin(s).replace("-", " ")
        s = re.sub(r"ee", "i", s)
        s = re.sub(r"oo", "u", s)
        s = re.sub(r"([aeiou])\1+", r"\1", s)
        return s

    @staticmethod
    def _norm_name(s: str) -> str:
        if is_arabic(s):
            return normalize_arabic(s)
        s = QuranIndex._loose_latin(s)
        s = re.sub(r"[^a-z0-9 ]", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        # Drop trailing h often optional in transliteration (fatihah → fatiha).
        if len(s) > 3 and s.endswith("h") and s[-2] in "aeiou":
            s = s[:-1]
        return s

    def surahs(self) -> list[dict]:
        return list(self._surahs.values())

    def resolve_surah(self, name: str) -> int | None:
        if name.isdigit():
            n = int(name)
            return n if n in self._surahs else None
        nrm = self._norm_name(name)
        candidates = {nrm, nrm.replace(" ", "")}
        for alias, num in self._alias:
            if alias in candidates:
                return num
        # Prefix / contains for longer names
        for alias, num in self._alias:
            if len(nrm) >= 4 and any(c in alias or alias in c for c in candidates):
                return num
        return None

    def _row(self, r: sqlite3.Row) -> dict:
        d = dict(r)
        d["ref"] = f"{d['surah']}:{d['ayah']}"
        d["citation"] = f"Quran {d['surah']}:{d['ayah']}"
        if d.get("surah_en"):
            d["citation_long"] = f"Quran {d['surah_en']} {d['ayah']} ({d['surah']}:{d['ayah']})"
        d["sajda"] = bool(d.get("sajda"))
        return d

    def get(self, surah: int | str, ayah: int) -> dict | None:
        s = self.resolve_surah(str(surah)) if not isinstance(surah, int) else surah
        if s is None:
            return None
        r = self.con.execute("SELECT * FROM ayahs WHERE surah=? AND ayah=?", (s, ayah)).fetchone()
        return self._row(r) if r else None

    def surah_ayahs(self, surah: int | str, limit: int = 0, offset: int = 0) -> list[dict]:
        s = self.resolve_surah(str(surah)) if not isinstance(surah, int) else surah
        if s is None:
            return []
        q = "SELECT * FROM ayahs WHERE surah=? ORDER BY ayah"
        args: list = [s]
        if limit:
            q += " LIMIT ? OFFSET ?"
            args += [limit, offset]
        return [self._row(r) for r in self.con.execute(q, args)]

    def by_page(self, page: int) -> list[dict]:
        return [self._row(r) for r in self.con.execute(
            "SELECT * FROM ayahs WHERE page=? ORDER BY surah, ayah", (page,))]

    def by_juz(self, juz: int, limit: int = 0, offset: int = 0) -> list[dict]:
        q = "SELECT * FROM ayahs WHERE juz=? ORDER BY surah, ayah"
        args: list = [juz]
        if limit:
            q += " LIMIT ? OFFSET ?"
            args += [limit, offset]
        return [self._row(r) for r in self.con.execute(q, args)]

    def page_info(self, page: int) -> dict | None:
        r = self.con.execute("SELECT * FROM pages WHERE number=?", (page,)).fetchone()
        return dict(r) if r else None

    def stats(self) -> dict:
        meta = {r["key"]: r["value"] for r in self.con.execute("SELECT * FROM meta")}
        return {
            "ayah_count": int(meta.get("ayah_count", 0)),
            "surah_count": len(self._surahs),
            "page_count": self.con.execute("SELECT COUNT(*) FROM pages").fetchone()[0],
            "juz_count": self.con.execute("SELECT COUNT(*) FROM juzs").fetchone()[0],
            "built_at": meta.get("built_at"),
            "mushaf": json.loads(meta.get("mushaf", "{}")),
            "editions": json.loads(meta.get("editions", "{}")),
        }

    # ------------------------------------------------------------------ search
    def search(self, query: str, *, language: str = "auto", surah: int | str | None = None,
               juz: int | None = None, page: int | None = None, limit: int = 10,
               offset: int = 0, explain: bool = False) -> SearchResponse:
        q = (query or "").strip()
        if not q:
            return SearchResponse(query=q, kind="search", hits=[])

        # Structural shortcuts
        m = REF_COLON.match(q)
        if m:
            hit = self.get(int(m.group(1)), int(m.group(2)))
            return SearchResponse(query=q, kind="reference",
                                  hits=[Hit(hit, 1.0)] if hit else [])
        m = REF_PAGE.match(q)
        if m:
            rows = self.by_page(int(m.group(1)))
            return SearchResponse(query=q, kind="page",
                                  hits=[Hit(r, 1.0) for r in rows[offset:offset + limit]],
                                  total_candidates=len(rows))
        m = REF_JUZ.match(q)
        if m:
            rows = self.by_juz(int(m.group(1)))
            return SearchResponse(query=q, kind="juz",
                                  hits=[Hit(r, 1.0) for r in rows[offset:offset + limit]],
                                  total_candidates=len(rows))
        m = REF_SURAH_AYAH.match(q)
        if m:
            s = self.resolve_surah(m.group("surah"))
            if s is not None:
                hit = self.get(s, int(m.group("ayah")))
                return SearchResponse(query=q, kind="reference",
                                      hits=[Hit(hit, 1.0)] if hit else [])

        surah_n = None
        if surah is not None:
            surah_n = self.resolve_surah(str(surah)) if not isinstance(surah, int) else surah

        lang = language if language != "auto" else self._detect_lang(q)
        terms_en, terms_ar = self._analyse(q, lang)
        ranked = self._retrieve(terms_en, terms_ar, lang, surah_n, juz, page)
        scored = self._rerank(ranked, terms_en, terms_ar, q)
        total = len(scored)
        hits = [Hit(a, sc, sig if explain else {}) for a, sc, sig in scored[offset:offset + limit]]
        return SearchResponse(query=q, kind="search", hits=hits, total_candidates=total)

    def _detect_lang(self, q: str) -> str:
        if any(c in URDU_LETTERS for c in q):
            return "ur"
        if is_arabic(q):
            return "ar"
        return "en"

    def _analyse(self, q: str, lang: str) -> tuple[list[str], list[str]]:
        if lang == "en":
            en = [t for t in normalize_english(q).split() if t not in EN_STOPWORDS and len(t) > 1]
            return en, []
        ar_raw = normalize_arabic(q)
        ar = [t for t in ar_raw.split() if t not in AR_STOPWORDS and len(t) > 1]
        stems = [stem_arabic_word(t) for t in ar]
        if lang == "ur":
            return [], ar  # Urdu lives in fts_ar.urdu; same tokens after folding
        return [], list(dict.fromkeys(ar + stems))

    def _retrieve(self, terms_en: list[str], terms_ar: list[str], lang: str,
                  surah: int | None, juz: int | None, page: int | None) -> dict[int, list[tuple[str, float]]]:
        """Return rowid -> [(list_name, rank), ...]."""
        lists: dict[str, list[int]] = {}
        if terms_en:
            phrase = " ".join(terms_en)
            lists["en_phrase"] = self._fts_en(f'"{phrase}"', surah, juz, page)
            if len(terms_en) > 1:
                lists["en_and"] = self._fts_en(" ".join(_fts_quote(t) for t in terms_en), surah, juz, page)
            lists["en_or"] = self._fts_en(" OR ".join(_fts_quote(t) for t in terms_en), surah, juz, page)
        if terms_ar:
            phrase = " ".join(terms_ar)
            col = "urdu" if lang == "ur" else "text"
            lists["ar_phrase"] = self._fts_ar(f'{col}:"{phrase}"', surah, juz, page)
            lists["ar_or"] = self._fts_ar(
                " OR ".join(f"{col}:{_fts_quote(t)}" for t in terms_ar), surah, juz, page)
            if lang != "ur":
                lists["ar_stem"] = self._fts_ar(
                    " OR ".join(f"stem:{_fts_quote(t)}" for t in terms_ar), surah, juz, page)
        ranked: dict[int, list[tuple[str, float]]] = {}
        for name, ids in lists.items():
            for i, rid in enumerate(ids):
                ranked.setdefault(rid, []).append((name, float(i)))
        return ranked

    def _filter_sql(self, surah: int | None, juz: int | None, page: int | None) -> tuple[str, list]:
        clauses, args = [], []
        if surah is not None:
            clauses.append("a.surah=?"); args.append(surah)
        if juz is not None:
            clauses.append("a.juz=?"); args.append(juz)
        if page is not None:
            clauses.append("a.page=?"); args.append(page)
        where = (" AND " + " AND ".join(clauses)) if clauses else ""
        return where, args

    def _fts_en(self, match: str, surah, juz, page, k: int = 200) -> list[int]:
        where, args = self._filter_sql(surah, juz, page)
        sql = (f"SELECT f.rowid FROM fts_en f JOIN ayahs a ON a.id=f.rowid "
               f"WHERE fts_en MATCH ?{where} ORDER BY bm25(fts_en) LIMIT ?")
        try:
            return [r[0] for r in self.con.execute(sql, [match, *args, k])]
        except sqlite3.OperationalError:
            return []

    def _fts_ar(self, match: str, surah, juz, page, k: int = 200) -> list[int]:
        where, args = self._filter_sql(surah, juz, page)
        sql = (f"SELECT f.rowid FROM fts_ar f JOIN ayahs a ON a.id=f.rowid "
               f"WHERE fts_ar MATCH ?{where} ORDER BY bm25(fts_ar) LIMIT ?")
        try:
            return [r[0] for r in self.con.execute(sql, [match, *args, k])]
        except sqlite3.OperationalError:
            return []

    def _rerank(self, ranked: dict[int, list[tuple[str, float]]],
                terms_en: list[str], terms_ar: list[str], raw_q: str
                ) -> list[tuple[dict, float, dict]]:
        if not ranked:
            return []
        k = 60
        fused: list[tuple[int, float, dict]] = []
        for rid, entries in ranked.items():
            rrf = sum(1.0 / (k + rank + 1) for _, rank in entries)
            fused.append((rid, rrf, {"lists": [n for n, _ in entries]}))
        fused.sort(key=lambda x: -x[1])
        # Fetch rows for top candidates
        ids = [rid for rid, _, _ in fused[:400]]
        rows = {r["id"]: self._row(r) for r in self.con.execute(
            f"SELECT * FROM ayahs WHERE id IN ({','.join('?' * len(ids))})", ids)}
        en_set = set(terms_en)
        ar_set = set(terms_ar)
        out = []
        for rid, rrf, sig in fused:
            a = rows.get(rid)
            if not a:
                continue
            cov = 0.0
            if en_set:
                blob = normalize_english((a.get("text_en") or "") + " " + (a.get("surah_en") or ""))
                toks = set(blob.split())
                cov = len(en_set & toks) / max(1, len(en_set))
            if ar_set:
                blob = normalize_arabic((a.get("text_ar") or "") + " " + (a.get("text_ur") or ""))
                toks = set(blob.split())
                cov = max(cov, len(ar_set & toks) / max(1, len(ar_set)))
            phrase_bonus = 0.0
            nq = normalize_english(raw_q) if en_set else normalize_arabic(raw_q)
            if nq and len(nq.split()) >= 2:
                hay = normalize_english(a.get("text_en") or "") if en_set else normalize_arabic(a.get("text_ar") or "")
                if nq in hay:
                    phrase_bonus = 0.25
            score = rrf * (1.0 + 0.35 * cov) + phrase_bonus
            # Mild prior: shorter famous ayahs (Ayat al-Kursi etc.) already win on phrase;
            # boost early Madinan surahs slightly for equal scores — skip, keep lexical.
            sig = {**sig, "coverage": round(cov, 3), "rrf": round(rrf, 5)}
            out.append((a, score, sig))
        out.sort(key=lambda x: -x[1])
        return out
