"""Optional semantic (embedding) retrieval layer.

Needs ``sentence-transformers`` (``pip install -r requirements-semantic.txt``).
Without it, or without the embeddings file, search runs purely lexically.

The model is multilingual (English / Arabic / Urdu share one vector space), so a
question in English also finds Arabic-only hadith, and paraphrases ("who is a true
Muslim") reach the wording of the text ("A Muslim is the one who avoids harming...").

Files:  data/build/embeddings.npy  float16 [N, dim], row i = hadiths.id i+1
        data/build/embeddings.json {"model": ..., "count": N, "dim": dim}
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import threading
import time
from pathlib import Path

from .index import DEFAULT_DB

MODEL = os.environ.get("HADITH_EMBED_MODEL", "intfloat/multilingual-e5-small")
MAX_CHARS = 900


def emb_paths(db_path: Path) -> tuple[Path, Path]:
    db_path = Path(db_path)
    return db_path.with_name("embeddings.npy"), db_path.with_name("embeddings.json")


def _matn(text_ar: str) -> str:
    """Drop most of the isnad: keep from the first quotation of the Prophet when marked."""
    for mark in ("«", "قال رسول الله", "أن رسول الله", "أن النبي", "قال النبي"):
        i = text_ar.find(mark)
        if 0 <= i < len(text_ar) - 40:
            return text_ar[i:]
    return text_ar[-MAX_CHARS:]


def fingerprint(con: sqlite3.Connection) -> str:
    import hashlib
    h = hashlib.sha1()
    for (uid,) in con.execute("SELECT uid FROM hadiths ORDER BY id"):
        h.update(uid.encode() + b"\n")
    return h.hexdigest()


def passage(row: sqlite3.Row) -> str:
    if row["text_en"]:
        head = row["chapter_en"] or row["book_en"] or ""
        body = re.sub(r"^Narrated [^:]{1,80}:\s*", "", row["text_en"])
    else:
        head = row["chapter_ar"] or row["book_ar"] or ""
        body = _matn(row["text_ar"] or "")
    return f"passage: {head}. {body}"[:MAX_CHARS]


def available() -> bool:
    try:
        import numpy  # noqa: F401
        import sentence_transformers  # noqa: F401
        return True
    except ImportError:
        return False


def _load_model(name: str):
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(name, device=os.environ.get("HADITH_EMBED_DEVICE", "cpu"))
    m.max_seq_length = 256
    return m


def build_embeddings(db_path: Path = DEFAULT_DB, model: str = MODEL, batch: int = 64) -> Path:
    import numpy as np
    out, meta = emb_paths(db_path)
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    n = con.execute("SELECT MAX(id) FROM hadiths").fetchone()[0]
    m = _load_model(model)
    dim = m.get_sentence_embedding_dimension()
    part = out.with_suffix(".part.npy")
    # Resumable: rows already encoded are kept in a memory-mapped work file.
    done_file = out.with_suffix(".progress")
    start = int(done_file.read_text()) if done_file.exists() and part.exists() else 0
    mm = np.lib.format.open_memmap(part, mode="r+" if start else "w+", dtype=np.float16, shape=(n, dim))
    t0 = time.time()
    rows = con.execute("SELECT id, text_en, text_ar, chapter_en, chapter_ar, book_en, book_ar FROM hadiths "
                       "WHERE id > ? ORDER BY id", (start,))
    chunk = []
    last = start
    while True:
        r = rows.fetchone()
        if r is not None:
            chunk.append(r)
        if chunk and (len(chunk) >= batch * 8 or r is None):
            vecs = m.encode([passage(x) for x in chunk], batch_size=batch, normalize_embeddings=True)
            for x, v in zip(chunk, vecs):
                mm[x["id"] - 1] = v
            last = chunk[-1]["id"]
            mm.flush()
            done_file.write_text(str(last))
            rate = (last - start) / (time.time() - t0)
            print(f"[embed] {last}/{n}  {rate:.0f}/s  eta {(n - last) / rate / 60:.1f} min", file=sys.stderr, flush=True)
            chunk = []
        if r is None:
            break
    del mm
    part.replace(out)
    done_file.unlink(missing_ok=True)
    meta.write_text(json.dumps({"model": model, "count": n, "dim": dim, "fingerprint": fingerprint(con)}))
    return out


class SemanticIndex:
    def __init__(self, db_path: Path, con: sqlite3.Connection | None = None):
        import numpy as np
        out, meta = emb_paths(db_path)
        info = json.loads(meta.read_text())
        if con is not None and info.get("fingerprint") != fingerprint(con):
            raise ValueError("embeddings were built for a different index; rerun `python -m hadith embed`")
        self.model_name = info["model"]
        self.matrix = np.load(out, mmap_mode="r")
        self._model = None
        self._np = np
        self._lock = threading.Lock()

    @classmethod
    def try_open(cls, db_path: Path, con: sqlite3.Connection | None = None) -> "SemanticIndex | None":
        out, meta = emb_paths(db_path)
        if not (out.exists() and meta.exists() and available()):
            return None
        try:
            return cls(db_path, con)
        except Exception as e:  # corrupt/missing files must not break lexical search
            print(f"[semantic] disabled: {e}", file=sys.stderr)
            return None

    @property
    def model(self):
        if self._model is None:
            self._model = _load_model(self.model_name)
            if not hasattr(self, "_dense"):
                self._dense = self._np.asarray(self.matrix, dtype=self._np.float32)
        return self._model

    def query(self, text: str, top: int = 300) -> list[tuple[int, float]]:
        np = self._np
        with self._lock:
            q = self.model.encode(["query: " + text], normalize_embeddings=True)[0].astype(np.float32)
        sims = self._dense @ q
        idx = np.argpartition(-sims, min(top, len(sims) - 1))[:top]
        idx = idx[np.argsort(-sims[idx])]
        return [(int(i) + 1, float(sims[i])) for i in idx]


if __name__ == "__main__":
    build_embeddings(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DB)
