# Heart Threads / Hadith project — handoff summary

**Audience:** humans installing the app + any AI agent continuing the work.  
**Last updated:** 2026-10-23 (Asia/Karachi)  
**Working branch for the mobile app:** `cursor/app-interactive-mockup-db55`  
**PR:** https://github.com/iumer/Hadith/pull/3  
**Preferred Mac project folder:**  
`/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app`

---

## 1. Simple install (updated build)

You only need to install something **new** when we ship a new JS/native build. For this round:

| Platform | What you install | How |
|---|---|---|
| **iPhone** | **Expo Go** (App Store) + this project’s JS | Mac runs Metro; phone scans QR |
| **Android** | **Direct APK** (no Expo Go required for testers) | Download APK → open → install |

You do **not** need a paid Apple Developer account for Expo Go smoke tests.  
Free Apple ID + Xcode is only needed if you use `npx expo run:ios` (native binary).

---

### A) iPhone — Mac + Expo Go (recommended for you now)

**One-time**

1. On iPhone: install **Expo Go** from the App Store.
2. On Mac, open Terminal:

```bash
mkdir -p "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app"
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app"
```

3. If the repo is not cloned yet:

```bash
git clone https://github.com/iumer/Hadith.git .
```

4. Get the latest app branch and deps:

```bash
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app"
git fetch origin
git checkout cursor/app-interactive-mockup-db55
git pull origin cursor/app-interactive-mockup-db55
cd app
npm install
```

**Every time you want the updated app**

```bash
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app"
git pull origin cursor/app-interactive-mockup-db55
cd app
npm install
npx expo start
```

- Phone and Mac on the **same Wi‑Fi**.
- In the Terminal QR: scan with **Camera** (or Expo Go).
- Enter a name → you should see **Assalamoalikum …** and the mood cards.
- **Swipe** left/right to browse; **pull down** on the front card to open.

**If `git pull` complains about local changes** (common after Expo prebuild):

```bash
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app"
git checkout -- app/package.json
git pull origin cursor/app-interactive-mockup-db55
```

**If Metro shows a red “babel-preset-expo” screen:** run `npm install` inside `app/` again (dep is already in the branch).

**Optional — native iOS binary (not required for Expo Go):**

```bash
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app/app"
npx expo run:ios
```

We pin `react-native-screens@4.29.0` for Xcode 27 (`UIBarMinimization`). If native folders are dirty: `rm -rf ios && npx expo run:ios`.

---

### B) Android — direct APK (share with testers)

Yes: for Android we give a **ready `.apk`**. Testers do **not** need a Mac or Expo Go.

**Stable download link (same forever — share once with testers):**  
https://github.com/iumer/Hadith/releases/download/sakinah/Sakinah.apk  
Older links (still updated with every build): https://github.com/iumer/Hadith/releases/download/android-preview/HeartThreads-preview.apk · https://github.com/iumer/Hadith/releases/download/android-preview-2026-10-22/HeartThreads-preview.apk

Release page: https://github.com/iumer/Hadith/releases/tag/android-preview

New builds **overwrite that same file** via `./scripts/publish_android_apk.sh` — no new link to redistribute.

**On the Android phone**

1. Open the download link (or send the file via WhatsApp/Drive).
2. Allow **Install unknown apps** for Files/Chrome if asked.
3. Install → open → enter name → test swipe / pull-down / back from a hadith or verse.

**When we push another Android update:** re-download the **same** URL and install over the old app. No App Store.

---

### What to verify after install (both platforms)

1. Swipe left/right — cards should **move with your finger** (not jump only at release).
2. Pull down — card should go **all the way** through the reveal, then the next screen.
3. Open a hadith/verse → Back → Back to the big cards — fan should still swipe/pull (not stuck).

Track status in `docs/ISSUE_LOG.md` (I-006, I-007, I-008 = fixed in code, pending your device check).

---

## 2. What this project is

Working product name in code: **Heart Threads** (product docs also say Mood & Light; final name TBD).

**User journey**

1. Name  
2. Feeling — Assalamoalikum + **card fan** (swipe browse, pull-down open)  
3. Subcategories  
4. Threads — reference list only (`Quran …` / `Hadith …`)  
5. Read — Arabic, English, meaning, reflection + Report  

**Content today in the app:** curated offline catalog baked into  
`app/src/content/catalog.json` (**8 moods · 37 subs · 148 passages**), built from `moods/**/*.txt` by `scripts/build_catalog.py`.
Every hadith carries its authenticity grade; only sahih/hasan hadith are shipped.  
Full Quran/Hadith SQLite search DBs exist in the repo for later “Search”; v1 reading path does **not** open those DBs at runtime yet.

---

## 3. Repo map (where things live)

```
hadith/          Python hadith corpus + FTS5 search CLI/API
quran/           Python Quran corpus + FTS5 search
data/            raw + corpus + built DBs (hadith.db, quran.db, …)
moods/           Curated mood → subcategory .txt cards (source of truth for app copy)
scripts/         e.g. expand_mood_files.py (citations → full cards via indexes)
mockup/          Vite + Framer Motion phone mockup (design lock)
app/             Expo / React Native app (ship this)
docs/            Product, architecture, QA, setup
summary.md       THIS FILE — agent handoff + install
tests/           Python tests for search/index
```

---

## 4. Chronology — what we did and why (beginning → now)

Read this section top-to-bottom if you are a new agent.

### Phase A — Hadith corpus & index

**Why:** Need citable, searchable hadith with book/chapter/grade/page, not scraped snippets.

**What:**

- Merged a large multi-collection corpus (~98k hadith, 20 collections) into a portable pipeline.
- Built **SQLite FTS5** index (`data/build/hadith.db`) via `python -m hadith setup`.
- Hybrid bilingual search (EN/AR/UR), reference parsers (`bukhari 1`, vol/page), optional semantic embeddings.
- CLI + JSON API (`python -m hadith serve`).
- Printed edition volume/page via OpenITI/Shamela alignment where available.

**Key entrypoints:** `hadith/`, root `README.md`, `python -m hadith …`

### Phase B — Quran corpus & index

**Why:** Mood threads mix Quran ayahs and hadith; need the same offline-quality lookup.

**What:**

- Quran corpus with Madani page index, surah/ayah, juz/ruku, Arabic + Saheeh International EN + Junagarhi UR.
- SQLite FTS5 (`data/build/quran.db`) and search APIs under `quran/`.

### Phase C — Mood authoring (txt cards)

**Why:** The app is pastoral/mood-first, not a raw search UI. Humans curate which refs appear under each feeling.

**What:**

- Structure: `moods/{mood}/{subcategory}.txt` (8 moods: happy, confident, sad, overwhelmed, anxious, angry, shame-guilt, confused).
- First pass: citation lists per subcategory.
- Then **expanded** into full cards: Arabic, English, meaning, reflection — using the indexes (`scripts/expand_mood_files.py` + `moods/_meta/`).
- Product rule: Threads screen shows **references only**; full text only on Read.

### Phase D — Interactive mockup

**Why:** Lock UX before native work (especially gestures).

**What:**

- `mockup/` Vite app: name → card fan → subs → threads → read → report sheet.
- Explored picker concepts; **locked** on card fan: swipe L/R, **pull down to open** (no double-tap), curtain reveal.
- Calm dawn visual language (cream / soft sky), not candy UI.

### Phase E — Expo mobile app

**Why:** Ship on real phones (iOS via user’s Mac, Android via APK).

**What:**

- Scaffolded Expo app in `app/` (RN + React Navigation + Reanimated + Gesture Handler).
- Ported screens and `CardFan`.
- Bundled `catalog.json` from moods for offline v1.
- Report sheet → AsyncStorage queue (`hadith.reports.v1`).
- Docs: `docs/PRODUCT_OVERVIEW.md`, `ARCHITECTURE.md`, `SETUP_AND_BUILDS.md`, `MILESTONES.md`, `CONTENT_AND_REPORTS.md`.

### Phase F — Mac build friction fixes

**Why:** User hit real Xcode/Metro blockers.

**What:**

- Pin `react-native-screens@4.29.0` (Xcode 27 `UIBarMinimization` break on 4.30) — I-001.
- Add `babel-preset-expo` so Metro transforms — I-002.
- Document clone path under Desktop “Hadith app” (spaces in path) — I-003 hygiene.

### Phase G — Card fan bugfixes (user report, both platforms)

**Why:** Stiff swipe, cut pull animation, stuck giant card after back.

**What (in `app/src/components/CardFan.tsx` + `FeelingScreen.tsx`):**

| Issue | Fix |
|---|---|
| I-006 Swipe stiff | Continuous `scroll` shared value follows finger |
| I-007 Pull cuts mid-way | Pull to max → 820ms reveal → **then** navigate |
| I-008 Stuck after back | Remount fan on focus (`fanEpoch`) + reset shared values |
| I-010 Web mouse can’t Pan | Web-only Prev / Open / Next; Open/browse use live `scroll` |

Mockup kept aligned conceptually with the same interaction model.

### Phase H — Agent QA + Android APK

**Why:** Cloud agent has no iOS/Android simulators; user needs shareable Android build.

**What:**

- `docs/AGENT_QA_PROTOCOL.md` + living `docs/ISSUE_LOG.md`.
- Expo web + Playwright smoke for navigation/back path (gestures still need device).
- Release APK: `HeartThreads-preview.apk` (~90MB) under cloud artifacts.

### Phase I — Full audit + content/UI fix round (2026-10-23)

**Why:** User asked for a full UI / functionality / content audit, then fixes, plus an authenticity indicator.

**What:**

- Audit report: `docs/AUDIT_2026-10-23.md` (19 UI, 8 functional issues; 53 content entries with current vs suggested cards).
- New `scripts/build_catalog.py` (the catalog previously came from a one-off step that truncated English at the first `"`).
- Fixed wrong/empty hadith English via `EN_FIX`; replaced weak Abu Dawud 1518 and ungraded Nawawi 19.
- New `GradeBar` on hadith pages (Sahih / Hasan / Da'if / Mawdu' with grader + "scholars differ" sheet).
- UI: Amiri fonts for Arabic, card fan layout/titles, scroll reset, report keyboard + full payload, saved name, label cleanups.
- **Not yet applied:** the passage *replacement* suggestions in the audit (sections 5 / entries marked REPLACE/MERGE/ADD) — waiting on scholar review.

### Phase J — Home feel + Urdu round (2026-10-23)

- Card fan: bigger cards, instruction pills, tap/idle "Pull me down" hint, card-to-screen open animation, clean return.
- Read: Arabic → Urdu → English (authentic, verbatim-checked), swipe to page, edge swipe-back kept.
- Name asked only on first launch.

---

## 5. Current milestone status

See `docs/MILESTONES.md`.

| Milestone | Status |
|---|---|
| M0 Design lock (mockup) | Done |
| M1 Expo skeleton + device installs | **In progress** — code + APK ready; device sign-off pending |
| M2 Content wiring from moods → catalog | Largely done for offline catalog; keep regenerating when moods change |
| M3 Reports | UI + local queue done; sync/admin later |
| M4 Polish | Not started |
| M5 Stores | Later (paid Apple + Play) |

---

## 6. Important constraints (do not ignore)

1. **Gestures:** Browse = swipe; open = **pull down** (not tap-tap). Reveal must finish before navigation.
2. **Threads list:** references only — no blurb previews.
3. **Real catalog data** — do not ship fake lorem passages.
4. **Agent proof:** screenshots / issue log; no “should work” without evidence (`docs/AGENT_QA_PROTOCOL.md`).
5. **Cloud agent** cannot run iOS Simulator or Android Emulator — gate on Expo web/mockup; **user** verifies devices.
6. **Branches:** `cursor/<name>-db55`; app PR branch is `cursor/app-interactive-mockup-db55` (base chain toward `main` via earlier index branches).
7. **No transaction PDFs** / unrelated deliverables.

---

## 7. How to continue (next agent checklist)

1. Read `docs/ISSUE_LOG.md` and this file.
2. Work on `cursor/app-interactive-mockup-db55` (or branch off it with `cursor/…-db55`).
3. After mood edits: `python scripts/expand_mood_files.py && python scripts/build_catalog.py` (see `docs/CONTENT_AND_REPORTS.md`).
4. Retest CardFan: swipe continuity, full pull reveal, back-from-Read not stuck.
5. For Android tester builds: `cd app/android && ./gradlew assembleRelease` (with Android SDK), copy APK to `/opt/cursor/artifacts/HeartThreads-preview.apk`.
6. For iOS: user uses Expo Go + `npx expo start` on Mac (section 1).
7. Update `docs/ISSUE_LOG.md` statuses when the user confirms devices.
8. Do **not** claim device-fixed until `verified-device`.

### Likely next features

- Wire optional in-app **Search** against `hadith.db` / `quran.db` (architecture already sketched).
- Run `scripts/build_catalog.py` in CI.
- Apply the reviewed content replacements from `docs/AUDIT_2026-10-23.md`.
- GitHub Action for APK artifacts.
- Report sync endpoint / weekly dump.

---

## 8. Quick commands cheat sheet

```bash
# Python indexes
python -m hadith setup
python -m hadith search patience -n 5
python -m quran …          # see quran package / root README

# Expand mood citations (needs built indexes)
python scripts/expand_mood_files.py

# Mockup
cd mockup && npm install && npm run dev

# Expo app
cd app && npm install && npx expo start

# Android release APK
cd app/android && ./gradlew assembleRelease
```

---

## 9. Related docs

| Doc | Use |
|---|---|
| `README.md` | Hadith/Quran index CLI details |
| `docs/PRODUCT_OVERVIEW.md` | Product intent |
| `docs/ARCHITECTURE.md` | Target app architecture |
| `docs/SETUP_AND_BUILDS.md` | Longer Mac/EAS notes |
| `docs/ISSUE_LOG.md` | Living bugs |
| `docs/AUDIT_2026-10-23.md` | Full UI/function/content audit + content suggestions |
| `docs/AGENT_QA_PROTOCOL.md` | How agents must QA |
| `docs/CONTENT_AND_REPORTS.md` | Mood txt + report reasons |
| `app/README.md` | Expo app short readme |
| `app/AGENTS.md` | App-local agent notes |

---

*End of handoff. Prefer updating this file when a phase completes so the next agent stays oriented.*
