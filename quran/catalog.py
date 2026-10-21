"""Pinned sources for the Quran text, translations and structural metadata."""
from __future__ import annotations

# fawazahmed0/quran-api — editions served from jsDelivr at a fixed commit.
FAWAZ_COMMIT = "93e6f64925ae76273520d636fcaaf061129f2316"
FAWAZ_BASE = f"https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@{FAWAZ_COMMIT}"

# alquran.cloud — surah names, Madani mushaf page / juz / ruku anchors.
ALQURAN_META_URL = "https://api.alquran.cloud/v1/meta"

EDITIONS = {
    "ar": {
        "slug": "ara-quranuthmanihaf",
        "name": "Uthmani (Hafs)",
        "author": "King Fahd Complex / Quran Complex",
        "language": "ar",
        "url": f"{FAWAZ_BASE}/editions/ara-quranuthmanihaf.min.json",
    },
    "en": {
        "slug": "eng-ummmuhammad",
        "name": "Saheeh International",
        "author": "Umm Muhammad (Saheeh International)",
        "language": "en",
        "url": f"{FAWAZ_BASE}/editions/eng-ummmuhammad.min.json",
    },
    "ur": {
        "slug": "urd-muhammadjunagar",
        "name": "Muhammad Junagarhi",
        "author": "Muhammad Junagarhi",
        "language": "ur",
        "url": f"{FAWAZ_BASE}/editions/urd-muhammadjunagar.min.json",
    },
}

# Madani mushaf (King Fahd Complex style): 604 pages, 30 juz, 114 surahs, 6236 ayahs.
MUSHAF = {
    "name_en": "Madani Mushaf (Hafs 'an 'Asim)",
    "pages": 604,
    "juz": 30,
    "surahs": 114,
    "ayahs": 6236,
}
