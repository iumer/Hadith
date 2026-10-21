"""Download pinned Quran sources into ``data/raw/quran``."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

from .catalog import ALQURAN_META_URL, EDITIONS, FAWAZ_COMMIT

ROOT = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("QURAN_RAW_DIR", ROOT / "data" / "raw" / "quran"))


def _fetch(url: str, dest: Path, retries: int = 4) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    delay = 4
    for attempt in range(retries + 1):
        try:
            tmp = dest.with_suffix(dest.suffix + ".part")
            req = urllib.request.Request(url, headers={"User-Agent": "quran-index/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            tmp.rename(dest)
            return
        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"failed to download {url}: {e}") from e
            time.sleep(delay)
            delay *= 2


def edition_path(lang: str) -> Path:
    return RAW / "editions" / f"{EDITIONS[lang]['slug']}.json"


def meta_path() -> Path:
    return RAW / "alquran-meta.json"


def download_all(verbose: bool = True) -> None:
    log = (lambda *a: print(*a, file=sys.stderr, flush=True)) if verbose else (lambda *a: None)
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "editions").mkdir(exist_ok=True)
    log(f"[quran] fawaz commit {FAWAZ_COMMIT}")
    for lang, ed in EDITIONS.items():
        dest = edition_path(lang)
        log(f"[quran] {ed['slug']} -> {dest}")
        _fetch(ed["url"], dest)
    log(f"[quran] meta -> {meta_path()}")
    _fetch(ALQURAN_META_URL, meta_path())
    # Sanity: each edition must have 6236 ayahs.
    for lang in EDITIONS:
        n = len(json.loads(edition_path(lang).read_text(encoding="utf-8"))["quran"])
        if n != 6236:
            raise RuntimeError(f"{lang} edition has {n} ayahs, expected 6236")
    log("[quran] download complete")


if __name__ == "__main__":
    download_all()
