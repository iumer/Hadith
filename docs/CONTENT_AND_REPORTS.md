# Content & reports

## Mood content

- **Source of truth:** `moods/{mood}/{subcategory}.txt`
- Each file is a sequence of passage cards separated by `────` rules.
- Fields we parse: title/reference, Arabic, English, Meaning, Reflection.

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
1. Badge + reference title  
2. Arabic  
3. English translation  
4. Meaning  
5. Reflection  
6. Previous / Next (+ progress)

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

Each report is stored in AsyncStorage (`hadith.reports.v1`) as
`{id, createdAt, platform, appVersion, passageRef, passageId, moodId, subId, reasons, note?}`.

Reports are used internally to fix catalog/copy; they are not public comments.

## Improving from reports

1. Triage weekly dump.  
2. Fix mood file or index data in a PR.  
3. Rebuild catalog → ship app update.  
