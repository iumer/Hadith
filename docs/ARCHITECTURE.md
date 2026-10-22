# Architecture

## High-level

```
┌─────────────────────────────────────────────┐
│  Expo app (iOS + Android)                   │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐  │
│  │  UI     │→ │ Content  │→ │ SQLite     │  │
│  │ screens │  │ services │  │ quran.db   │  │
│  │         │  │          │  │ hadith.db  │  │
│  └────┬────┘  └──────────┘  └────────────┘  │
│       │                                     │
│       ▼                                     │
│  Report queue (AsyncStorage / SQLite)       │
└───────────────┬─────────────────────────────┘
                │ sync when online
                ▼
        Reports API (later) → review dashboard
```

## Repo layout (target)

```
mockup/                 # Design prototype (Vite) — already started
docs/                   # This documentation
app/                    # Expo app (to create)
  src/
    screens/            # Name, Feeling, Subs, Threads, Reading
    components/         # CardFan, ReportSheet, …
    content/            # mood catalog + loaders
    db/                 # open quran/hadith DBs
    reports/            # queue + sync
  assets/
data/                   # corpora + built DBs (existing)
hadith/                 # Python index pipeline (existing)
quran/                  # Python index pipeline (existing)
moods/                  # Curated mood → refs → explainers (existing)
```

## Content pipeline

1. **Authoring:** `moods/{mood}/{sub}.txt` holds curated references + pastoral text.
2. **Build step (CI / script):** parse mood files → `moods.catalog.json` (ids, refs, copy).
3. **Runtime:** app loads catalog; for each ref, fetch Arabic/English from on-device DB **or** embed full card JSON at build time for v1 simplicity.

**v1 recommendation:** bake a `passages.json` from mood files at build time (fast, offline, simple). Keep SQLite search for a later “Search” feature.

## Navigation

React Navigation (native stack):

`Name → Feeling → Subcategories → Threads → Reading`

Reading keeps subcategory thread list in params/context for Prev/Next.

## Reports

```ts
type Report = {
  id: string
  createdAt: string
  platform: 'ios' | 'android'
  appVersion: string
  passageRef: string
  passageId: string
  moodId: string
  subId: string
  reasons: string[]
  note?: string
}
```

- Write locally first.
- Flush to `POST /reports` when network available (endpoint TBD).
- Until backend exists: export JSON from a debug screen / upload to a private bucket.

## Design system

- Fonts: Fraunces (display) + Nunito (UI) — match mockup.
- Tokens: calm dawn palette in CSS/RN StyleSheet or Tamagui/unistyles later.
- Motion: Reanimated + Moti or RN Animated; spring configs from mockup.

## Environments

| Env | Purpose |
|---|---|
| Local Mac | Daily iOS device runs, Expo Go / dev client |
| Cloud agent / CI | Android APK artifacts, lint, typecheck, catalog build |
| EAS (optional later) | Cloud iOS when you have paid Apple Developer |

## Security / integrity

- Reports are untrusted user input — sanitize on server.
- Do not ship secrets in the app; API keys via EAS secrets if needed.
- Religious content is read-only in the client; edits go through repo PRs.
