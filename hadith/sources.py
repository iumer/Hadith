"""Download the raw sources (pinned to exact commits) into ``data/raw``."""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from .catalog import (COLLECTIONS, FAWAZ_INFO_URL, FAWAZ_URL, HADITHJSON_URL, LK_COMMIT,
                      LK_REPO)

ROOT = Path(__file__).resolve().parent.parent
RAW = Path(os.environ.get("HADITH_RAW_DIR", ROOT / "data" / "raw"))


def _fetch(url: str, dest: Path, retries: int = 4) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    delay = 4
    for attempt in range(retries + 1):
        try:
            tmp = dest.with_suffix(dest.suffix + ".part")
            req = urllib.request.Request(url, headers={"User-Agent": "hadith-index/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            tmp.rename(dest)
            return
        except Exception as e:  # network hiccups
            if attempt == retries:
                raise RuntimeError(f"failed to download {url}: {e}") from e
            time.sleep(delay)
            delay *= 2


def fawaz_path(edition: str) -> Path:
    return RAW / "fawaz" / f"{edition}.json"


def hadithjson_path(rel: str) -> Path:
    return RAW / "hadith-json" / rel


def openiti_path(filename: str) -> Path:
    return RAW / "openiti" / filename


def lk_dir() -> Path:
    return RAW / "LK-Hadith-Corpus"


def download_all(verbose: bool = True) -> None:
    log = (lambda *a: print(*a, file=sys.stderr)) if verbose else (lambda *a: None)
    _fetch(FAWAZ_INFO_URL, RAW / "fawaz" / "info.json")
    for c in COLLECTIONS:
        log(f"[sources] {c.slug}")
        if c.fawaz:
            for lang in c.fawaz_languages:
                ed = f"{lang}-{c.fawaz}"
                _fetch(FAWAZ_URL.format(edition=ed), fawaz_path(ed))
        if c.hadithjson:
            _fetch(HADITHJSON_URL.format(path=c.hadithjson), hadithjson_path(c.hadithjson))
        if c.openiti:
            _fetch(c.openiti.url, openiti_path(c.openiti.filename))
    d = lk_dir()
    if not (d / ".git").exists():
        log("[sources] LK-Hadith-Corpus")
        subprocess.run(["git", "clone", "-q", LK_REPO, str(d)], check=True)
    subprocess.run(["git", "-C", str(d), "checkout", "-q", LK_COMMIT], check=True)


if __name__ == "__main__":
    download_all()
