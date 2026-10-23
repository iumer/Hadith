# Content & reports

## Mood content

- **Source of truth:** `moods/{mood}/{subcategory}.txt`
- Each file is a sequence of passage cards separated by `────` rules.
- Fields we parse: title/reference, Arabic, Urdu, English, Meaning, Reflection.

### Selection rules

- **Quran:** always whole ayahs. When one ayah only makes sense with its neighbours, use a
  range in `file_refs.json` (e.g. `Quran 89:27-30`); it is shown as one card with ayah
  markers. Skip ayahs whose context (rulings, battles) would confuse a reader in that mood.
- **Hadith:** a complete saying. If the Prophet's ﷺ words answer a question or end a story,
  include the question or story. Sahih/hasan only.
- No passage twice inside the same mood.

### Translations (authentic sources only)

| | Urdu | English |
|---|---|---|
| Quran | Muhammad Junagarhi | Saheeh International |
| Hadith | Urdu edition in `hadith.db` (fawazahmed0/hadith-api) | sunnah.com translation in `hadith.db` |

Nothing is paraphrased. When the automatic extraction picks the wrong sentence, pin the
Prophet's ﷺ words in `EN_SLICE` / `UR_SLICE` / `AR_SLICE` in `scripts/expand_mood_files.py`
as a (first words, last words) slice of the source. `build_catalog.py` refuses to build if any
shown Arabic/Urdu/English is not a verbatim excerpt of its source. Hadith without an Urdu
translation in the source cannot be used (Bukhari 5641, Nasa'i 5453, Ibn Hibban 972 and
Adab al-Mufrad 245 were replaced for this reason).

### Rebuilding the app catalog

```bash
python -m hadith setup                 # once: builds data/build/hadith.db
python scripts/expand_mood_files.py    # moods/_meta/file_refs.json → moods/*/*.txt
python scripts/build_catalog.py        # moods/*/*.txt → app/src/content/catalog.json
```

- To change which passages appear, edit `moods/_meta/file_refs.json` (and add
  Meaning/Reflection for new refs in `moods/_meta/explanations.json`).
- If the automatic quote extraction picks the wrong sentence for a hadith, pin the
  Prophet's ﷺ words in `EN_FIX` / `AR_FIX` in `scripts/expand_mood_files.py`.
- `build_catalog.py` attaches each hadith's grade from `hadith.db` and **fails the build**
  if any hadith is not sahih or hasan, or if any card has empty Arabic or English.

### Authenticity (hadith only)

| Grade | Label | Bar |
|---|---|---|
| Sahih | Authentic | Full, green |
| Hasan | Good | ¾, light green |
| Da'if | Weak | ⅓, amber (not shipped) |
| Mawdu' | Fabricated | red (not shipped) |

Bukhari and Muslim are shown as "In Sahih al-Bukhari / Sahih Muslim". Other collections
credit the grader (usually al-Albani). When graders disagree the bar says "scholars differ"
and the info sheet lists each grader's verdict. The Quran is not graded.

### Threads screen rule

Show **only**:
- Kind badge — `Quran` | `Hadith`
- Reference string — e.g. `Quran 12:86`, `Sahih al-Bukhari 5641`

No preview blurb on the threads list. Full text appears only on the reading screen.

## Reading screen

Order:
1. Badge + reference title (+ authenticity bar for hadith)  
2. Arabic  
3. Urdu translation  
4. English translation  
5. Meaning  
6. Reflection  
7. Previous / Next (+ progress); swipe left/right in the middle of the screen to page

## Report reasons (v1)

Users may multi-select:

1. Issue in the reference (wrong book / number)  
2. Reference differs from the original book  
3. The translation is not correct  
4. The Arabic text looks incorrect  
5. The explanation / meaning is not correct  
6. The reflection feels off or misleading  
7. Something else  

Optional free-text note.

Reports are appended to **one file**: `REPORTS.md` in the private repo
[iumer/sakinah-feedback](https://github.com/iumer/sakinah-feedback). Each entry records the passage,
mood › sub, reasons, note, the name the user entered, device (name · maker · model), OS,
app version, public IP (via api.ipify.org) and local IP. The sheet tells users this is sent.

- Code: `app/src/reports.ts`. If sending fails (offline, no token) the report is queued on the
  phone (`hadith.reports.pending.v1`) and sent with the next report.
- Token: a fine-grained GitHub token with **Contents: Read and write on iumer/sakinah-feedback only**,
  in `app/.env.local` (git-ignored; see `app/.env.example`). It is embedded in builds, so it must
  never have access to any other repo.

Reports are used internally to fix catalog/copy; they are not public comments.

## Improving from reports

1. Triage weekly dump.  
2. Fix mood file or index data in a PR.  
3. Rebuild catalog → ship app update.  
