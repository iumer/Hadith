# Product overview

Working title: **Mood & Light** (final app name TBD).

A calm mobile app that greets the user by name, asks how they feel, and guides them through **mood → subcategory → reference threads → reading**, with Quran and Hadith content drawn from our indexed corpora.

## User journey

1. **Name** — “What should we call you?”
2. **Feeling** — “Assalamoalikum {name}” + **card fan**: swipe left/right to browse, **pull down** to open with a reveal animation (no double-tap).
3. **Subcategories** — e.g. Sad → Sorrow, Grief, Loneliness…
4. **Threads** — list of **references only** (e.g. `Quran 12:86`, `Sahih al-Bukhari 5641`).
5. **Reading** — full Arabic, English, meaning, reflection; **Previous / Next** across threads; **Report** for quality feedback.

## Content sources (already in repo)

| Asset | Location | Notes |
|---|---|---|
| Mood structure | `moods/*/*.txt` | 8 moods, subcategory files with full cards |
| Hadith index | `hadith/`, `data/corpus/`, `data/build/hadith.db` | SQLite FTS5 |
| Quran index | `quran/`, `data/corpus/quran/`, `data/build/quran.db` | SQLite FTS5 |

## Design direction (locked for v1 mockup)

- **Primary picker:** card fan — swipe browse, pull-down open + curtain reveal.
- **Background:** calm dawn wash (cream → soft sky/mint), not candy blobs.
- **Motion:** springy, clean; respects reduced-motion in the web mockup.

Interactive mockup: `mockup/`. Expo app: `app/` (Milestone 1).
