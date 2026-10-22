# Heart Threads / Hadith & Quran

## Start here (humans + AI agents)

**Active app branch:** `cursor/app-interactive-mockup-db55`  
**Full handoff (read first):** [`summary.md`](./summary.md)  
**Install (iOS Expo Go + Android APK):** [`docs/INSTALL.md`](./docs/INSTALL.md)

```bash
git clone https://github.com/iumer/Hadith.git
cd Hadith
git checkout cursor/app-interactive-mockup-db55
git pull
```

Then open **`summary.md`** — corpus → moods → mockup → Expo app → card fixes → current status.

**Android APK (stable link, never changes):**  
https://github.com/iumer/Hadith/releases/download/android-preview/HeartThreads-preview.apk

Docs index: [`docs/README.md`](./docs/README.md) · living bugs: [`docs/ISSUE_LOG.md`](./docs/ISSUE_LOG.md)

---

# Hadith & Quran index and search

An indexed, searchable corpus of the major hadith collections **and** the Quran (Madani
mushaf). Every hadith carries a complete reference: collection, hadith number, book
(kitab), chapter (bab), and, where a printed edition is available, the volume and page in
a named edition. It also carries the grading, plus the Arabic text, English translation
and Urdu translation where those exist. Every ayah carries surah/ayah numbers, Madani
page, juz, ruku, and Arabic + Saheeh International English + Junagarhi Urdu.

* **98,239 hadith in 20 collections**, with 646 books and 26,569 chapters.
* **Search** in English, Arabic or Urdu by topic, keyword, phrase or reference. Searches
  such as `bukhari 1`, `muslim 8` or `abu dawud vol 4 page 44` also work. The core uses
  BM25 full-text search with bilingual topic expansion. Optional multilingual embeddings
  add semantic matching.
* **One portable SQLite file** (`data/build/hadith.db`, FTS5), built from pinned upstream
  sources. A mobile, desktop or web app can open it directly.
* The core needs only the **Python standard library**.

```bash
python -m hadith setup                                   # build the index from data/corpus (~40 s)
python -m hadith search patience in hardship -n 5
python -m hadith search "إنما الأعمال بالنيات"
python -m hadith search "ماں کی خدمت"                     # Urdu
python -m hadith search fasting --authentic -c abudawud --format markdown
python -m hadith get bukhari 1
python -m hadith page muslim 1 37                        # vol. 1, p. 37 of the printed edition
python -m hadith books bukhari                           # kitab list with hadith and page ranges
python -m hadith chapters muslim 1                       # babs of Muslim, Book of Faith
python -m hadith serve                                   # JSON API on http://127.0.0.1:8765
```

Optional semantic layer (better for paraphrased questions such as "who is a true muslim"):

```bash
pip install --index-url https://download.pytorch.org/whl/cpu torch
pip install -r requirements-semantic.txt
python -m hadith embed          # ~20 min on 4 CPU cores; writes data/build/embeddings.npy
```

Once `embeddings.npy` exists and `sentence-transformers` can be imported, search uses the
semantic layer automatically. Pass `--no-semantic`, or `semantic=0` in the API, to turn it off.

## Collections

| Collection | Arabic | Compiler | Hadith | Books | Chapters | English | Urdu | Vol./page | Graded | Printed edition used for vol./page | Slug |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| Sahih al-Bukhari | صحيح البخاري | al-Bukhari (d. 256 AH) | 7,580 | 97 | 3,842 | 7,580 | 7,016 | 7,553 | 7,580 | Dar Tawq al-Najat 1422 AH, ed. Zuhayr al-Nasir (Sultaniyya), 9 vols | `bukhari` |
| Sahih Muslim | صحيح مسلم | Muslim (d. 261 AH) | 7,449 | 57 | 1,337 | 7,449 | 7,389 | 7,280 | 7,449 | Dar Ihya' al-Turath al-'Arabi, ed. Fu'ad 'Abd al-Baqi, 5 vols | `muslim` |
| Sunan Abi Dawud | سنن أبي داود | Abu Dawud (d. 275 AH) | 5,272 | 43 | 1,907 | 5,272 | 5,271 | 5,272 | 5,272 | al-Maktaba al-'Asriyya, ed. Muhyi al-Din 'Abd al-Hamid, 4 vols | `abudawud` |
| Jami' at-Tirmidhi | جامع الترمذي | al-Tirmidhi (d. 279 AH) | 3,926 | 49 | 2,208 | 3,926 | 3,868 | 3,913 | 3,890 | Dar Ihya' al-Turath al-'Arabi, ed. Ahmad Shakir et al., 5 vols | `tirmidhi` |
| Sunan an-Nasa'i | سنن النسائي | al-Nasa'i (d. 303 AH) | 5,679 | 51 | 2,309 | 5,679 | 3,870 | 5,677 | 5,671 | Maktab al-Matbu'at al-Islamiyya, ed. Abu Ghudda, 8 vols | `nasai` |
| Sunan Ibn Majah | سنن ابن ماجه | Ibn Majah (d. 273 AH) | 4,340 | 38 | 1,415 | 4,340 | 4,327 | 4,338 | 4,338 | Dar Ihya' al-Kutub al-'Arabiyya, ed. Fu'ad 'Abd al-Baqi, 2 vols | `ibnmajah` |
| Muwatta Malik | موطأ مالك | Malik ibn Anas (d. 179 AH) | 1,829 | 61 | 578 | 1,818 | 1,575 | 1,790 | 1,829 | Dar Ihya' al-Turath al-'Arabi, ed. Fu'ad 'Abd al-Baqi, 2 vols | `malik` |
| Musnad Ahmad | مسند أحمد | Ahmad ibn Hanbal (d. 241 AH) | 27,583 | 33 | 1,216 | 1,341 | – | 27,583 | – | Mu'assasat al-Risala, ed. al-Arna'ut et al., 45 vols | `ahmad` |
| Sunan ad-Darimi | سنن الدارمي | al-Darimi (d. 255 AH) | 3,542 | 25 | 1,366 | – | – | 3,542 | 3,117 | Dar al-Mughni, ed. Husayn Salim Asad, 4 vols | `darimi` |
| Sahih Ibn Khuzaymah | صحيح ابن خزيمة | Ibn Khuzaymah (d. 311 AH) | 3,067 | 8 | 2,097 | – | – | 3,067 | 1,460 | al-Maktab al-Islami, ed. al-A'zami, 4 vols | `ibnkhuzaymah` |
| Sahih Ibn Hibban | صحيح ابن حبان | Ibn Hibban (d. 354 AH) | 7,488 | 59 | 6,948 | – | – | 7,488 | 7,478 | Mu'assasat al-Risala 1414/1993, ed. al-Arna'ut, 18 vols | `ibnhibban` |
| al-Mustadrak | المستدرك على الصحيحين | al-Hakim (d. 405 AH) | 8,812 | 51 | 4 | – | – | 8,812 | 4,153 | Dar al-Kutub al-'Ilmiyya, ed. Mustafa 'Ata, 4 vols | `mustadrak` |
| Riyad as-Salihin | رياض الصالحين | al-Nawawi (d. 676 AH) | 1,896 | 20 | 366 | 1,890 | – | 1,896 | – | Dar Ibn Kathir 1428/2007, ed. al-Fahl | `riyadussalihin` |
| Bulugh al-Maram | بلوغ المرام | Ibn Hajar (d. 852 AH) | 1,580 | 19 | 93 | 1,426 | – | 1,577 | – | Dar al-Falaq 1424 AH, ed. al-Zuhayri | `bulugh` |
| al-Adab al-Mufrad | الأدب المفرد | al-Bukhari (d. 256 AH) | 1,342 | 1 | 631 | 1,319 | – | 1,342 | 1,331 | Dar al-Basha'ir, ed. Fu'ad 'Abd al-Baqi (al-Albani's grades) | `adab` |
| Shama'il Muhammadiyya | الشمائل المحمدية | al-Tirmidhi (d. 279 AH) | 406 | 1 | 56 | 393 | – | 406 | – | al-Maktaba al-Tijariyya, ed. al-Julaymi | `shamail` |
| Mishkat al-Masabih | مشكاة المصابيح | al-Tabrizi (d. 741 AH) | 6,326 | 30 | 196 | 4,426 | – | 6,326 | 4,595 | al-Maktab al-Islami 1985, ed. al-Albani, 3 vols | `mishkat` |
| Forty Hadith of al-Nawawi | الأربعون النووية | al-Nawawi (d. 676 AH) | 42 | 1 | – | 42 | – | – | – | – | `nawawi40` |
| Forty Hadith Qudsi | الأربعون القدسية | (compilation) | 40 | 1 | – | 40 | – | – | – | – | `qudsi40` |
| Forty Hadith of Shah Waliullah | أربعون الشاه ولي الله | Shah Wali Allah (d. 1176 AH) | 40 | 1 | – | 40 | – | – | – | – | `shahwaliullah40` |

**Authenticity.** The two *Sahihs* (Bukhari, Muslim) are treated as sahih throughout. The
other collections carry per-hadith grades from the sources:

* Abu Dawud, Tirmidhi, Nasa'i, Ibn Majah: al-Albani, Zubair 'Ali Za'i, Shakir and others.
* Malik: Salim al-Hilali.
* Ibn Hibban: al-Albani and al-Arna'ut.
* Mustadrak: al-Dhahabi's *Talkhis*.
* Ibn Khuzaymah: al-A'zami.
* Darimi: Husayn Asad.
* Mishkat and al-Adab al-Mufrad: al-Albani.

Each hadith keeps every grade it was given, in `grades`. `grade` is the normalised class
(`sahih` / `hasan` / `daif` / `mawdu`), chosen by grader priority with al-Albani first.
`authentic_only` / `--authentic` keeps sahih and hasan only. The source edition of Musnad
Ahmad has no grades.

## Reference model

| Field | Meaning |
|---|---|
| `number` | The standard citation number, e.g. `bukhari 1`, `muslim 8a` (sunnah.com style sub-numbers for Muslim's repeated chains; `alt_number` = the running number), `muslim intro-5` for the Muqaddima |
| `book_number`, `book_en`, `book_ar` | Kitab (for Musnad Ahmad: the musnad of a Companion group) |
| `chapter_number`, `chapter_en`, `chapter_ar` | Bab / tarjama |
| `in_book_ref` | e.g. "Book 1, Hadith 1" (sunnah.com in-book numbering) |
| `volume`, `page`, `volume_end`, `page_end` | Location in the printed edition named in `collections.edition` |
| `print_number` | The number printed in that edition (if it differs) |
| `grades`, `grade`, `grade_text` | All grades, the normalised class, a display string |
| `text_ar`, `text_en`, `text_ur`, `narrator_en` | Texts |
| `url` | sunnah.com link (Six Books, Malik, the Forty) |

How volume and page were obtained: the Arabic text of every hadith was aligned against
the OpenITI/Shamela digitisation of the printed edition. The digitisations carry
`PageVxxPyyy` and `[ص: N]` page markers. Alignment uses character 4-gram similarity, a
number hint, and a monotonic window with a re-sync search. Spot checks:

* Bukhari 1: vol. 1, p. 6
* Muslim 8a: vol. 1, pp. 36–38
* Abu Dawud 1: vol. 1, p. 1
* Tirmidhi 1: vol. 1, p. 5

`print_align_score` in the corpus records the confidence of each match.

## Search algorithm (`hadith/search.py`)

1. **Reference parser.** Recognises collection names and aliases in English and Arabic,
   followed by a number (`8`, `8a`, `intro-3`) or by `vol V page P`. These go to a direct
   lookup.
2. **Query analysis.** Detects the script, normalises the text (diacritics; alef, ya and
   ta-marbuta variants; Urdu letter forms), removes stopwords, and light-stems Arabic.
3. **Expansion.**
   * A bilingual thesaurus of about 140 topics (`glossary.TOPICS`) maps "fasting" to
     sawm, siyam, صوم, صيام and so on.
   * Urdu words (`URDU_TERMS`) map to the same topics.
   * English synonym groups (`EN_SYNONYMS`) treat deeds/actions, dua/supplication and
     similar words as the same term.

   As a result, English queries reach Arabic-only books, and Arabic or Urdu queries reach
   English translations.
4. **Retrieval.** Several FTS5 BM25 lists, with chapter titles weighted three times body
   text:
   * exact phrase
   * all terms
   * all terms with synonyms
   * "all but one term" (soft AND), weighted by IDF so that dropping a common word costs
     less than dropping a rare one
   * chapter heading match
   * any term plus expansions
   * Arabic exact surface forms, light stems and headings
   * the Urdu translation
   * optionally, the top 300 by embedding cosine similarity
5. **Reciprocal Rank Fusion** with k = 30 and a weight per list.
6. **Re-ranking:**
   * IDF-weighted term coverage of the stored text
   * bonuses for phrase presence and for matches in the chapter heading
   * an authenticity factor: sahih 1.15, hasan 1.06, unknown 1.0, da'if 0.78, mawdu' 0.45
   * a mild collection prior: Bukhari, then Muslim, then the Sunan
   * damping of repeated hits from the same chapter, so the first page stays diverse
7. **Folding of parallel narrations.** Hits whose matn (the normalised tail of the Arabic
   text) overlaps by 60% or more are grouped. The representative is the hadith from the
   highest-ranked collection, at its first occurrence. The others appear under `also_in`,
   e.g. *Bukhari 1, also Muslim 1907a, Abu Dawud 2201, Nasa'i 75…*.

`tests/relevance_cases.py` holds 20 topic queries with hadith that are expected on the
first page. Lexical search alone finds 19 of the 20.

## Python API

```python
from hadith.search import HadithIndex
from hadith.cite import to_markdown

ix = HadithIndex()                         # data/build/hadith.db or $HADITH_DB
r = ix.search("kindness to neighbours", authentic_only=True, limit=5)
for hit in r.hits:
    print(to_markdown(hit.hadith, also_in=hit.also_in, max_chars=400))

ix.get("muslim", "8")                      # -> muslim 8a
ix.by_page("bukhari", 1, 6)                # hadith printed on vol. 1, p. 6
ix.books("tirmidhi"); ix.chapters("tirmidhi", "1")
ix.book_hadiths("bukhari", "2", limit=20)
```

HTTP (`python -m hadith serve`):

* `/api/search?q=…&collection=bukhari&authentic=1&limit=10`
* `/api/hadith/bukhari/1`
* `/api/page/muslim/1/37`
* `/api/collections`, `/api/collections/bukhari/books`, `/api/collections/bukhari/books/2`,
  `/api/collections/bukhari/chapters?book=2`
* `/api/stats`

All responses are JSON with CORS enabled.

## Building an app on this

* **Data.** Ship `hadith.db` (about 320 MB; about 100 MB zipped). It is plain SQLite with
  FTS5, which is available in Android's SQLite, iOS/macOS, `sql.js`/wa-sqlite in the
  browser, Electron/Node (`better-sqlite3`), Flutter (`sqflite`/`sqlite3`) and
  React-Native (`op-sqlite`).
* **Smaller builds.** To shrink the file, drop the `text_ur` column, or rebuild with a
  subset of collections via `python -m hadith build bukhari muslim …`.
* **Porting the search.** The logic is about 450 lines and relies only on SQL plus the
  normalisation functions in `hadith/normalize.py`, which are pure string maps. It ports
  directly to Kotlin, Swift, Dart or TypeScript. Alternatively, run `python -m hadith serve`
  (or wrap `HadithIndex` in FastAPI) as the backend.
* **Semantic search** needs the embedding model. On a server, use the model as is. On a
  device, export `multilingual-e5-small` to ONNX (about 120 MB, or about 30 MB
  int8-quantised) and do a dot product against `embeddings.npy` (98k × 384 float16, 75 MB).

## Rebuilding from the sources

```bash
python -m hadith download     # pinned revisions -> data/raw (~600 MB)
python -m hadith build        # parse + align -> data/corpus/*.jsonl.gz (committed)
python -m hadith index        # -> data/build/hadith.db
python -m unittest tests.test_core tests.test_search
```

Sources, each pinned to a commit in `hadith/catalog.py`:

* [fawazahmed0/hadith-api](https://github.com/fawazahmed0/hadith-api): Arabic, English and
  Urdu texts with sunnah.com numbering and grades for the Six Books, Malik and the Forty.
* [AhmedBaset/hadith-json](https://github.com/AhmedBaset/hadith-json): English for Ahmad,
  the anthologies and Mishkat.
* [LK Hadith Corpus](https://github.com/ShathaTm/LK-Hadith-Corpus): bilingual chapter
  (bab) headings for the Six Books.
* [OpenITI](https://github.com/OpenITI) (digitised Shamela and JK editions): the printed
  editions, giving volume, page, kitab and bab, and the editors' grades.

Check each project's licence before redistributing the data in a published app.

## Quran

* **6,236 ayahs**, 114 surahs, 604 Madani mushaf pages, 30 juz.
* Arabic (Uthmani Hafs), English (Saheeh International), Urdu (Muhammad Junagarhi).
* Structural metadata from [alquran.cloud](https://alquran.cloud): page, juz, ruku,
  hizb quarter, manzil, sajda.
* One portable SQLite file (`data/build/quran.db`, ~7 MB, FTS5). Same normalisation as
  the hadith package.

```bash
python -m quran setup                                    # download + build + index
python -m quran search patience -n 5
python -m quran search "الله لا اله الا هو"
python -m quran search "صبر" --urdu
python -m quran get 2:255                                # Ayat al-Kursi
python -m quran get baqarah 255
python -m quran page 1                                   # Madani mushaf page
python -m quran surah fatiha
python -m quran surahs                                   # page/juz ranges
python -m quran juz 30 -n 10
```

```python
from quran.search import QuranIndex

ix = QuranIndex()                        # data/build/quran.db or $QURAN_DB
ix.get(2, 255)
ix.search("throne", limit=5)
ix.by_page(42)                           # Madani page containing 2:255
ix.surah_ayahs("ikhlas")
```

Rebuild:

```bash
python -m quran download     # pinned fawazahmed0/quran-api commit + alquran.cloud meta
python -m quran build        # -> data/corpus/quran/ (committed)
python -m quran index        # -> data/build/quran.db
```

Editions are pinned in `quran/catalog.py` (fawazahmed0/quran-api commit
`93e6f649…`). Check upstream licences before redistributing in a published app.

## Limitations

* Translations are those of the sources (mostly the sunnah.com translations). Arabic-only
  collections (Darimi, Ibn Khuzaymah, Ibn Hibban, Mustadrak, most of Ahmad) are searched
  in Arabic, through the English→Arabic topic expansion, or semantically.
* Around 1–3% of hadith in the fawaz-based collections could not be aligned to the
  printed edition, and so have no volume or page. Some editions (Muslim, Ibn Majah)
  are paginated continuously across volumes, as in the print.
* Chapter numbers follow the sources and are not always sequential. Chapter names are
  authoritative.
* Quran page numbers follow the standard Madani (King Fahd Complex) mushaf. Other printed
  layouts (Indo-Pak 15-line, etc.) differ.
