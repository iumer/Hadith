"""Hadith search engine.

Algorithm (all steps run inside one SQLite file, so the same logic ports to a
mobile/desktop app):

1. **Reference lookup** – queries such as ``bukhari 1``, ``muslim:8a``,
   ``abu dawud 4031`` or ``bukhari vol 1 page 6`` are answered directly.
2. **Query analysis** – detect script (Latin / Arabic / Urdu), normalise
   (diacritics, alef/ya/ta-marbuta variants), drop stopwords, light-stem Arabic.
3. **Topic expansion** – a bilingual thesaurus (``glossary.TOPICS``) adds
   synonyms and transliterations ("fasting" → sawm, siyam, صوم, صيام …).
   English queries therefore also reach Arabic-only collections, and Arabic
   queries reach the English translations.
4. **Retrieval** – several FTS5 BM25 queries with column weights (chapter
   titles weigh more than body text, since they name the topic):
   exact phrase, all-terms (AND), any-term + expansions (OR), Arabic stems,
   Arabic headings, Urdu.
5. **Fusion** – Reciprocal Rank Fusion over the ranked lists.
6. **Re-ranking** – term coverage, phrase presence, authenticity
   (sahih > hasan > ungraded > da'if > mawdu') and collection rank
   (Bukhari, Muslim, then the Sunan …).
7. **Grouping** – the same hadith narrated in several books (same matn) is
   folded into one result with "also in" references.
"""
from __future__ import annotations

import json
import math
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from .glossary import EN_SYNONYMS, arabic_topic_expansions, expand_query_terms
from .index import DEFAULT_DB
from .normalize import (char_ngrams, fold_latin, is_arabic, normalize_arabic, normalize_english,
                        stem_arabic_word)

EN_STOPWORDS = set("""
a an the of and or to in on at for from by with about as is are was were be been being it its this that these
those i me my we our you your he him his she her they them their what which who whom whose when where why how
all any both each few more most other some such no nor not only own same so than too very can will just should
now do does did doing have has had having would could may might must shall into over under again further then
once here there up down out off above below between through during before after hadith hadiths ahadith narration
narrations narrated tell me show give find about regarding concerning related relating prophet's say said says
saying upon peace blessings muhammad messenger allah's pbuh saw sallallahu alaihi wasallam topic summary
""".split())
AR_STOPWORDS = set(normalize_arabic(w) for w in """
في من على عن الى إلى ان أن إن ما لا لم لن هو هي هم ثم او أو قد كان قال حديث احاديث أحاديث عن ذلك هذا هذه التي الذي
""".split())

COLLECTION_PRIOR = {
    "bukhari": 1.12, "muslim": 1.10, "abudawud": 1.02, "tirmidhi": 1.02, "nasai": 1.02, "ibnmajah": 1.0,
    "malik": 1.0, "ahmad": 0.97, "darimi": 0.96, "ibnkhuzaymah": 0.97, "ibnhibban": 0.97, "mustadrak": 0.94,
    "riyadussalihin": 0.99, "bulugh": 0.98, "adab": 0.98, "shamail": 0.98, "mishkat": 0.96,
    "nawawi40": 1.0, "qudsi40": 1.0, "shahwaliullah40": 0.97,
}
GRADE_FACTOR = {"sahih": 1.15, "hasan": 1.06, None: 1.0, "daif": 0.78, "mawdu": 0.45}
# Priority used to pick the representative of a group of parallel narrations.
GROUP_PRIORITY = ["bukhari", "muslim", "abudawud", "tirmidhi", "nasai", "ibnmajah", "malik", "ahmad",
                  "darimi", "ibnkhuzaymah", "ibnhibban", "mustadrak", "riyadussalihin", "bulugh", "adab",
                  "shamail", "mishkat", "nawawi40", "qudsi40", "shahwaliullah40"]
URDU_LETTERS = set("ٹڈڑںےۓہھگکی")

REF_NUMBER = r"(\d+[a-z]?|intro-\d+|seq\d+|en-\d+)"


@dataclass
class Hit:
    hadith: dict
    score: float
    also_in: list[dict] = field(default_factory=list)
    signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = dict(self.hadith)
        d["score"] = round(self.score, 5)
        d["also_in"] = self.also_in
        if self.signals:
            d["signals"] = self.signals
        return d


@dataclass
class SearchResponse:
    query: str
    kind: str                       # "reference" | "page" | "search"
    hits: list[Hit]
    total_candidates: int = 0
    expansions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"query": self.query, "kind": self.kind, "total_candidates": self.total_candidates,
                "expansions": self.expansions, "hits": [h.to_dict() for h in self.hits]}


def _fts_quote(term: str) -> str:
    return '"' + term.replace('"', " ") + '"'


class HadithIndex:
    def __init__(self, db_path: str | Path | None = None, semantic: bool | None = None):
        """``semantic``: None = use embeddings when installed/built, False = lexical only,
        True = require them."""
        path = Path(db_path or DEFAULT_DB)
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found - run `python -m hadith setup` (or `python -m hadith index`) first")
        self.con = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self._collections = {r["slug"]: dict(r) for r in self.con.execute(
            "SELECT * FROM collections ORDER BY position")}
        self._alias: list[tuple[str, str]] = []
        for slug, c in self._collections.items():
            names = {slug, c["name_en"], c["name_ar"]} | set(json.loads(c["aliases"] or "[]"))
            for n in names:
                if n:
                    self._alias.append((self._norm_name(n), slug))
        self._alias.sort(key=lambda x: -len(x[0]))
        self._idf_cache: dict[tuple, float] = {}
        self._n_docs: dict[str, int] = {}
        self.semantic = None
        if semantic is not False:
            from .semantic import SemanticIndex
            self.semantic = SemanticIndex.try_open(path, self.con)
            if semantic and self.semantic is None:
                raise RuntimeError("semantic search requested but embeddings/sentence-transformers are missing "
                                   "(pip install -r requirements-semantic.txt; python -m hadith embed)")

    # ------------------------------------------------------------------ metadata
    @staticmethod
    def _norm_name(s: str) -> str:
        if is_arabic(s):
            return normalize_arabic(s)
        s = fold_latin(s).replace("-", " ")
        s = re.sub(r"[^a-z0-9 ]", "", s)
        s = re.sub(r"\b(sahih|sunan|jami|al|as|an|at|ad|ibn|the)\b", lambda m: m.group(0), s)
        return re.sub(r"\s+", " ", s).strip()

    def collections(self) -> list[dict]:
        return list(self._collections.values())

    def collection(self, slug: str) -> dict | None:
        return self._collections.get(slug)

    def resolve_collection(self, name: str) -> str | None:
        n = self._norm_name(name)
        for alias, slug in self._alias:
            if n == alias:
                return slug
        for alias, slug in self._alias:
            if alias and (n.startswith(alias) or alias.startswith(n)) and len(n) >= 3:
                return slug
        return None

    def books(self, collection: str) -> list[dict]:
        return [dict(r) for r in self.con.execute(
            "SELECT * FROM books WHERE collection=? ORDER BY position", (collection,))]

    def chapters(self, collection: str, book_number: str | None = None) -> list[dict]:
        if book_number is None:
            q, a = "SELECT * FROM chapters WHERE collection=? ORDER BY position", (collection,)
        else:
            q, a = "SELECT * FROM chapters WHERE collection=? AND book_number=? ORDER BY position", (collection, str(book_number))
        return [dict(r) for r in self.con.execute(q, a)]

    def _row(self, r: sqlite3.Row) -> dict:
        d = dict(r)
        d["grades"] = json.loads(d["grades"] or "[]")
        d.pop("matn_key", None)
        c = self._collections.get(d["collection"], {})
        d["collection_name_en"] = c.get("name_en")
        d["collection_name_ar"] = c.get("name_ar")
        d["edition"] = c.get("edition")
        return d

    def get(self, collection: str, number: str) -> dict | None:
        r = self.con.execute("SELECT * FROM hadiths WHERE collection=? AND number=?",
                             (collection, str(number))).fetchone()
        if r is None and re.fullmatch(r"\d+", str(number)):
            # "muslim 8" -> first sub-number 8a; also try print/alternate numbers.
            r = (self.con.execute("SELECT * FROM hadiths WHERE collection=? AND number GLOB ? ORDER BY seq LIMIT 1",
                                  (collection, f"{number}[a-z]")).fetchone()
                 or self.con.execute("SELECT * FROM hadiths WHERE collection=? AND alt_number=?",
                                     (collection, str(number))).fetchone())
        return self._row(r) if r else None

    def get_uid(self, uid: str) -> dict | None:
        r = self.con.execute("SELECT * FROM hadiths WHERE uid=?", (uid,)).fetchone()
        return self._row(r) if r else None

    def by_page(self, collection: str, volume: int, page: int) -> list[dict]:
        rows = self.con.execute(
            "SELECT * FROM hadiths WHERE collection=? AND volume=? AND page<=? AND COALESCE(page_end,page)>=? "
            "ORDER BY seq", (collection, volume, page, page)).fetchall()
        return [self._row(r) for r in rows]

    def book_hadiths(self, collection: str, book_number: str, limit: int = 50, offset: int = 0) -> list[dict]:
        rows = self.con.execute(
            "SELECT * FROM hadiths WHERE collection=? AND book_number=? ORDER BY seq LIMIT ? OFFSET ?",
            (collection, str(book_number), limit, offset)).fetchall()
        return [self._row(r) for r in rows]

    def chapter_hadiths(self, collection: str, book_number: str, chapter_number: str) -> list[dict]:
        rows = self.con.execute(
            "SELECT * FROM hadiths WHERE collection=? AND book_number=? AND chapter_number=? ORDER BY seq",
            (collection, str(book_number), str(chapter_number))).fetchall()
        return [self._row(r) for r in rows]

    def stats(self) -> dict:
        tot = self.con.execute("SELECT COUNT(*) FROM hadiths").fetchone()[0]
        meta = dict(self.con.execute("SELECT key, value FROM meta").fetchall())
        return {"hadith_count": tot, "collections": len(self._collections), **meta}

    # ------------------------------------------------------------------ references
    def parse_reference(self, query: str):
        q = query.strip()
        m = re.match(r"^(.+?)\s*(?:vol(?:ume)?\.?|v\.?|ج|جلد)\s*(\d+)\s*[,/ ]\s*(?:p(?:age)?\.?|ص|صفحه)?\s*(\d+)\s*$", q, re.I)
        if m:
            slug = self.resolve_collection(m.group(1))
            if slug:
                return ("page", slug, int(m.group(2)), int(m.group(3)))
        m = re.match(r"^(.+?)\s*(?:#|:|no\.?|number|hadith|رقم)?\s*" + REF_NUMBER + r"\s*$", q, re.I)
        if m:
            slug = self.resolve_collection(m.group(1))
            if slug:
                return ("ref", slug, m.group(2).lower())
        return None

    # ------------------------------------------------------------------ search
    def search(self, query: str, *, collections: list[str] | None = None, authentic_only: bool = False,
               grades: list[str] | None = None, language: str = "auto", limit: int = 10, offset: int = 0,
               group: bool = True, require_english: bool = False, explain: bool = False,
               semantic: bool | None = None) -> SearchResponse:
        ref = self.parse_reference(query)
        if ref:
            if ref[0] == "ref":
                h = self.get(ref[1], ref[2])
                return SearchResponse(query, "reference", [Hit(h, 1.0)] if h else [])
            rows = self.by_page(ref[1], ref[2], ref[3])
            return SearchResponse(query, "page", [Hit(h, 1.0) for h in rows])

        q_is_ar = is_arabic(query) if language == "auto" else language in ("ar", "ur")
        q_is_ur = q_is_ar and any(ch in URDU_LETTERS for ch in query)
        lists: list[tuple[str, float, list[int]]] = []
        expansions: dict = {}
        en_terms: list[str] = []
        ar_terms: list[str] = []
        ar_stems: list[str] = []
        phrase_en = None
        phrase_ar = None
        en_idf: list[float] = []

        if not q_is_ar:
            norm = normalize_english(query)
            en_terms = [t for t in norm.split() if t not in EN_STOPWORDS and len(t) > 1]
            if not en_terms:
                en_terms = [t for t in norm.split() if len(t) > 1]
            exp_en, exp_ar = expand_query_terms(" ".join(en_terms))
            exp_en = [normalize_english(t) for t in exp_en if normalize_english(t) not in en_terms]
            expansions = {"english": exp_en, "arabic": exp_ar}
            if en_terms:
                if len(en_terms) >= 2:
                    phrase_en = " ".join(en_terms)
                    lists.append(("en_phrase", 1.6, self._fts("fts_en", _fts_quote(phrase_en), (1.0, 3.0, 1.0, 0.3))))
                lists.append(("en_all", 1.4, self._fts("fts_en", " AND ".join(_fts_quote(t) for t in en_terms), (1.0, 3.0, 1.0, 0.3))))
                groups = ["(" + " OR ".join(_fts_quote(x) for x in [t] + EN_SYNONYMS.get(t, [])) + ")" for t in en_terms]
                if any(t in EN_SYNONYMS for t in en_terms):
                    lists.append(("en_all_syn", 1.2, self._fts("fts_en", " AND ".join(groups), (1.0, 3.0, 1.0, 0.3))))
                # Chapter titles name the topic of all hadith under them.
                lists.append(("en_heading", 0.9, self._fts("fts_en", "chapter : (" + " AND ".join(groups) + ")", (0.0, 1.0, 0.0, 0.0))))
                idf = [self._idf("fts_en", g) for g in groups]
                en_idf = [x / sum(idf) for x in idf] if sum(idf) else [1 / len(idf)] * len(idf)
                # Soft AND: all terms but one (helps when one query word is absent, e.g. "dua").
                # Dropping a common word costs little, dropping a rare one costs a lot.
                if 3 <= len(groups) <= 5:
                    for i in range(len(groups)):
                        rest = " AND ".join(g for j, g in enumerate(groups) if j != i)
                        w = 1.4 * (1 - en_idf[i]) ** 2
                        lists.append((f"en_most{i}", w, self._fts("fts_en", rest, (1.0, 3.0, 1.0, 0.3), 150)))
                        lists.append((f"en_head_most{i}", w * 0.8, self._fts(
                            "fts_en", "chapter : (" + rest + ")", (0.0, 1.0, 0.0, 0.0), 150)))
                lists.append(("en_any", 0.9, self._fts("fts_en", " OR ".join(_fts_quote(t) for t in en_terms + exp_en), (1.0, 3.0, 1.0, 0.3))))
            if exp_ar:
                stems = list(dict.fromkeys(stem_arabic_word(w) for t in exp_ar for w in t.split()))
                q = "stem : (" + " OR ".join(_fts_quote(s) for s in stems) + ") OR chapter : (" + \
                    " OR ".join(_fts_quote(t) for t in exp_ar) + ")"
                lists.append(("ar_expansion", 0.7, self._fts("fts_ar", q, (1.0, 1.0, 2.5, 0.0))))
        else:
            norm = normalize_arabic(query)
            ar_terms = [t for t in norm.split() if t not in AR_STOPWORDS and len(t) > 1] or norm.split()
            ar_stems = list(dict.fromkeys(stem_arabic_word(t) for t in ar_terms))
            exp_en, exp_ar = arabic_topic_expansions(norm)
            expansions = {"english": exp_en, "arabic": [t for t in exp_ar if t not in ar_terms]}
            if len(ar_terms) >= 2:
                phrase_ar = " ".join(ar_terms)
                lists.append(("ar_phrase", 1.6, self._fts("fts_ar", "text : " + _fts_quote(phrase_ar), (1.0, 1.0, 1.0, 1.0))))
            # Exact surface forms (with/without the article) guard against light-stem collisions
            # such as صبره "heap" vs الصبر "patience".
            forms = ["(" + " OR ".join(_fts_quote(f) for f in _ar_forms(t)) + ")" for t in ar_terms]
            lists.append(("ar_exact", 1.5, self._fts("fts_ar", "text : (" + " AND ".join(forms) + ")", (1.0, 1.0, 1.0, 0.0))))
            lists.append(("ar_heading", 1.1, self._fts("fts_ar", "chapter : (" + " AND ".join(forms) + ")", (0.0, 0.0, 1.0, 0.0))))
            lists.append(("ar_all", 1.2, self._fts("fts_ar", "stem : (" + " AND ".join(_fts_quote(s) for s in ar_stems) + ")", (1.0, 1.0, 1.0, 0.0))))
            any_q = "stem : (" + " OR ".join(_fts_quote(s) for s in ar_stems) + ") OR chapter : (" + \
                    " OR ".join(_fts_quote(t) for t in ar_terms + expansions["arabic"]) + ")"
            lists.append(("ar_any", 0.9, self._fts("fts_ar", any_q, (1.0, 1.0, 2.5, 0.0))))
            # Urdu cannot always be told apart from Arabic (e.g. نماز), so the Urdu
            # translation column is always searched, with more weight when Urdu letters appear.
            uw = 1.3 if q_is_ur else 0.6
            lists.append(("urdu", uw, self._fts("fts_ar", "urdu : (" + " AND ".join(_fts_quote(t) for t in ar_terms) + ")", (0.0, 0.0, 0.0, 1.0))))
            if len(ar_terms) > 1:
                lists.append(("urdu_any", uw * 0.6, self._fts("fts_ar", "urdu : (" + " OR ".join(_fts_quote(t) for t in ar_terms) + ")", (0.0, 0.0, 0.0, 1.0))))
            if expansions["arabic"]:
                ex_stems = list(dict.fromkeys(stem_arabic_word(w) for t in expansions["arabic"] for w in t.split()))
                lists.append(("ar_topic", 0.6, self._fts("fts_ar", "chapter : (" + " OR ".join(
                    _fts_quote(t) for t in expansions["arabic"]) + ") OR stem : (" + " OR ".join(
                    _fts_quote(s) for s in ex_stems) + ")", (1.0, 1.0, 2.5, 0.0))))
            if exp_en:
                lists.append(("en_expansion", 0.6, self._fts("fts_en", " OR ".join(_fts_quote(normalize_english(t)) for t in exp_en), (1.0, 3.0, 1.0, 0.3))))

        sem_rank: dict[int, int] = {}
        if self.semantic is not None and semantic is not False and query.strip():
            sem = self.semantic.query(query.strip(), top=300)
            lists.append(("semantic", 1.4, [i for i, _ in sem]))
            sem_rank = {i: k for k, (i, _) in enumerate(sem)}

        # Reciprocal rank fusion.
        fused: dict[int, float] = {}
        sig: dict[int, dict] = {}
        for name, w, ids in lists:
            for rank, hid in enumerate(ids):
                fused[hid] = fused.get(hid, 0.0) + w / (30 + rank)
                if explain:
                    sig.setdefault(hid, {})[name] = rank + 1
        if not fused:
            return SearchResponse(query, "search", [], 0, expansions)

        cand = sorted(fused, key=fused.get, reverse=True)[:600]
        rows = {}
        for i in range(0, len(cand), 500):
            chunk = cand[i:i + 500]
            for r in self.con.execute(f"SELECT * FROM hadiths WHERE id IN ({','.join('?' * len(chunk))})", chunk):
                rows[r["id"]] = r

        wanted_grades = set(grades or [])
        scored: list[tuple[float, sqlite3.Row]] = []
        en_stems = [{_en_stem(x) for x in [t] + EN_SYNONYMS.get(t, []) if " " not in x} for t in en_terms]
        for hid in cand:
            r = rows.get(hid)
            if r is None:
                continue
            if collections and r["collection"] not in collections:
                continue
            g = r["grade"]
            if authentic_only and g not in ("sahih", "hasan"):
                continue
            if wanted_grades and g not in wanted_grades:
                continue
            if require_english and not r["text_en"]:
                continue
            s = fused[hid]
            # Term coverage and phrase presence on the stored text.
            if en_terms:
                hay = normalize_english(" ".join(x or "" for x in (r["text_en"], r["chapter_en"], r["book_en"])))
                hay_stems = {_en_stem(w) for w in hay.split()}
                cov = sum(wt for alts, wt in zip(en_stems, en_idf) if alts & hay_stems)
                if not r["text_en"]:
                    cov = max(cov, 0.5)
                if sem_rank.get(hid, 999) < 40:
                    cov = max(cov, 0.75)   # a close paraphrase need not share the query words
                s *= 0.5 + 0.5 * cov
                head = {_en_stem(w) for w in normalize_english(r["chapter_en"] or "").split()}
                if head:
                    s *= 1 + 0.3 * sum(wt for alts, wt in zip(en_stems, en_idf) if alts & head)
                if phrase_en and phrase_en in hay:
                    s *= 1.25
            elif ar_terms:
                hay = normalize_arabic(" ".join(x or "" for x in (r["text_ar"], r["chapter_ar"], r["text_ur"])))
                hay_words = set(hay.split())
                hay_stems = {stem_arabic_word(w) for w in hay_words}
                cov = sum(1 for t in ar_stems if t in hay_stems) / len(ar_stems)
                exact = sum(1 for t in ar_terms if hay_words & set(_ar_forms(t))) / len(ar_terms)
                if sem_rank.get(hid, 999) < 40:
                    cov, exact = max(cov, 0.75), max(exact, 0.75)
                s *= (0.55 + 0.45 * cov) * (0.8 + 0.2 * exact)
                if phrase_ar and phrase_ar in hay:
                    s *= 1.25
            s *= GRADE_FACTOR.get(g, 1.0) * COLLECTION_PRIOR.get(r["collection"], 1.0)
            if not q_is_ar and not r["text_en"]:
                s *= 0.85
            scored.append((s, r))
        scored.sort(key=lambda x: -x[0])
        # Diversity: each further hit from the same chapter is damped so one bab
        # does not fill the whole first page.
        seen: dict[tuple, int] = {}
        div = []
        for s, r in scored:
            k = (r["collection"], r["book_number"], r["chapter_en"] or r["chapter_ar"] or r["chapter_number"])
            n = seen.get(k, 0)
            seen[k] = n + 1
            div.append((s * (0.9 ** n), r))
        scored = sorted(div, key=lambda x: -x[0])

        hits: list[Hit] = []
        if group:
            hits = self._group(scored, need=offset + limit)
        else:
            hits = [Hit(self._row(r), s) for s, r in scored[: offset + limit]]
        if explain:
            for h in hits:
                h.signals = sig.get(h.hadith["id"], {})
        return SearchResponse(query, "search", hits[offset: offset + limit], len(scored), expansions)

    def _fts(self, table: str, match: str, weights: tuple, limit: int = 400) -> list[int]:
        w = ",".join(str(x) for x in weights)
        try:
            return [r[0] for r in self.con.execute(
                f"SELECT rowid FROM {table} WHERE {table} MATCH ? ORDER BY bm25({table}, {w}) LIMIT ?",
                (match, limit))]
        except sqlite3.OperationalError:
            return []

    def _idf(self, table: str, match: str) -> float:
        key = (table, match)
        if key not in self._idf_cache:
            if table not in self._n_docs:
                self._n_docs[table] = self.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] or 1
            try:
                df = self.con.execute(f"SELECT COUNT(*) FROM {table} WHERE {table} MATCH ?", (match,)).fetchone()[0]
            except sqlite3.OperationalError:
                df = 0
            self._idf_cache[key] = math.log(1 + self._n_docs[table] / (1 + df))
            if len(self._idf_cache) > 5000:
                self._idf_cache.clear()
        return self._idf_cache[key]

    def _group(self, scored: list[tuple[float, sqlite3.Row]], need: int) -> list[Hit]:
        """Fold parallel narrations (same matn) into one hit."""
        groups: list[dict] = []
        for s, r in scored:
            key = r["matn_key"]
            feats = char_ngrams(key, 4) if key and len(key) > 40 else None
            placed = False
            if feats:
                for g in groups:
                    gf = g["feats"]
                    if gf and len(feats & gf) / min(len(feats), len(gf)) >= 0.6:
                        g["members"].append((s, r))
                        placed = True
                        break
            if not placed:
                groups.append({"feats": feats, "members": [(s, r)], "score": s})
                if len(groups) >= need + 5:
                    break
        out = []
        for g in groups[:need]:
            members = g["members"]
            members.sort(key=lambda m: (GROUP_PRIORITY.index(m[1]["collection"])
                                        if m[1]["collection"] in GROUP_PRIORITY else 99, -m[0]))
            best_s = max(m[0] for m in members)
            # A hadith repeated within one collection is cited at its first occurrence.
            top_c = members[0][1]["collection"]
            same = [m for m in members if m[1]["collection"] == top_c and m[0] >= 0.5 * members[0][0]]
            rep_m = min(same, key=lambda m: m[1]["seq"])
            rep = rep_m[1]
            also = [{"uid": m[1]["uid"], "collection": m[1]["collection"], "number": m[1]["number"],
                     "collection_name_en": self._collections[m[1]["collection"]]["name_en"],
                     "grade": m[1]["grade"]} for m in members if m is not rep_m]
            out.append(Hit(self._row(rep), best_s, also))
        out.sort(key=lambda h: -h.score)
        return out


_AR_CLITICS = ("وال", "فال", "بال", "كال", "لل", "ال", "و", "ف", "ب", "ل")


def _ar_forms(term: str) -> list[str]:
    """Surface variants of a normalised Arabic word: bare, with/without the article and
    common proclitics (و ف ب ل)."""
    base = term
    for p in _AR_CLITICS:
        if base.startswith(p) and len(base) - len(p) >= 3:
            base = base[len(p):]
            break
    definite = ["ال" + base, "وال" + base, "فال" + base, "بال" + base, "لل" + base]
    if "ال" in term[:4] and term.endswith(base):
        # The user wrote the article: keep to definite forms (الصبر ≠ صبر "to tie up").
        return list(dict.fromkeys([term] + definite))
    return list(dict.fromkeys([term, base, "و" + base, "ب" + base, "ل" + base] + definite))


def _en_stem(w: str) -> str:
    for suf in ("ingly", "edly", "ing", "ers", "ies", "ied", "ed", "es", "er", "ly", "s"):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[: -len(suf)] + ("y" if suf in ("ies", "ied") else "")
    return w
