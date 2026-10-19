"""Monotonic alignment of two orderings of the same hadith collection.

Different digitisations of a book split, merge and number hadiths slightly
differently.  We align a *primary* sequence (the one whose numbering we cite)
with a *secondary* sequence (e.g. an OpenITI printed edition carrying volume
and page numbers) using Arabic text similarity, using shared hadith numbers
as anchors where available.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .normalize import char_ngrams, normalize_arabic


@dataclass
class AlignItem:
    key: object            # caller's identifier
    text: str              # Arabic text
    number: str | None = None


def _features(text: str, limit: int = 1200) -> set[str]:
    t = normalize_arabic(text, drop_formulas=True)
    if len(t) > limit:
        t = t[: limit // 2] + " " + t[-limit // 2:]
    return char_ngrams(t, 4)


def similarity(a: set[str], b: set[str]) -> float:
    """Overlap coefficient: robust when one side carries extra commentary."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    return inter / min(len(a), len(b)) * (0.5 + 0.5 * min(len(a), len(b)) / max(len(a), len(b)))


def _shingles(text: str) -> set[str]:
    w = normalize_arabic(text, drop_formulas=True).split()
    return {w[i] + " " + w[i + 1] for i in range(len(w) - 1)}


def match_global(primary: Sequence[AlignItem], secondary: Sequence[AlignItem], *,
                 threshold: float = 0.6, candidates: int = 25, max_df: int = 150
                 ) -> dict[object, tuple[object, float]]:
    """Order-independent best match for each primary item (inverted index on
    word bigrams, very common bigrams such as isnad formulae ignored)."""
    import collections
    index: dict[str, list[int]] = collections.defaultdict(list)
    sf = [_features(s.text) for s in secondary]
    for j, s in enumerate(secondary):
        for g in _shingles(s.text):
            index[g].append(j)
    pairs: list[tuple[float, int, int]] = []
    for i, p in enumerate(primary):
        sh = _shingles(p.text)
        hits: collections.Counter = collections.Counter()
        for g in sh:
            lst = index.get(g)
            if lst and len(lst) <= max_df:
                hits.update(lst)
        if not hits:
            continue
        pf = _features(p.text)
        for j, _ in hits.most_common(candidates):
            sc = similarity(pf, sf[j])
            if p.number and secondary[j].number == p.number:
                sc += 0.05
            if sc >= threshold:
                pairs.append((sc, i, j))
    # Greedy one-to-one assignment, best pairs first: books repeat hadiths
    # verbatim, and each repetition should land on its own record.
    pairs.sort(key=lambda t: (-t[0], abs(t[1] - t[2])))
    used_p: set[int] = set()
    used_s: set[int] = set()
    out: dict[object, tuple[object, float]] = {}
    for sc, i, j in pairs:
        if i in used_p or j in used_s:
            continue
        used_p.add(i)
        used_s.add(j)
        out[primary[i].key] = (secondary[j].key, min(sc, 1.0))
    return out


def align(primary: Sequence[AlignItem], secondary: Sequence[AlignItem], *,
          window: int = 40, threshold: float = 0.6, number_threshold: float = 0.5,
          use_numbers: bool = True) -> dict[object, tuple[object, float]]:
    """Return {primary.key: (secondary.key, score)} for confidently matched items.

    Several primary items may map to the same secondary item (a printed
    edition sometimes groups chains that a translation splits), but the
    mapping never goes backwards by more than a few records.
    """
    pf = [_features(p.text) for p in primary]
    sf = [_features(s.text) for s in secondary]
    num_index: dict[str, int] = {}
    if use_numbers:
        for j, s in enumerate(secondary):
            if s.number and s.number not in num_index:
                num_index[s.number] = j

    out: dict[object, tuple[object, float]] = {}
    j = 0
    m = len(secondary)
    for i, p in enumerate(primary):
        if not pf[i]:
            continue
        best_j, best = -1, 0.0
        if use_numbers and p.number and p.number in num_index:
            k = num_index[p.number]
            sc = similarity(pf[i], sf[k])
            if sc >= number_threshold:
                best_j, best = k, sc
        if best_j < 0:
            # Collections repeat hadiths almost verbatim, so prefer the
            # nearest good candidate over a marginally better distant one.
            lo = max(0, j - 3)
            hi = min(m, j + window)
            best_adj = -1.0
            for k in range(lo, hi):
                sc = similarity(pf[i], sf[k])
                adj = sc - 0.01 * abs(k - (j + 1))
                if sc >= threshold and adj > best_adj:
                    best_j, best, best_adj = k, sc, adj
            if best_j < 0:
                # Re-synchronise after a long run of unmatched material.
                for k in range(hi, min(m, j + window * 8)):
                    sc = similarity(pf[i], sf[k])
                    adj = sc - 0.001 * (k - j)
                    if sc >= threshold + 0.25 and adj > best_adj:
                        best_j, best, best_adj = k, sc, adj
                if best_j < 0:
                    continue
        out[p.key] = (secondary[best_j].key, best)
        j = best_j
    return out
