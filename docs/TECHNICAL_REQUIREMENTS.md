# Technical requirements

## Platforms

| Platform | Target | Distribution for testing |
|---|---|---|
| iOS | iPhone (iOS 15+) | Local install from your M1 Mac + Xcode (free Apple ID; weekly re-sign) |
| Android | API 24+ | Downloadable **APK** from CI / EAS / agent artifact |

**Framework:** Expo (React Native) + TypeScript.

## Functional requirements

### Core flow
- [ ] Capture and persist display name locally.
- [ ] Show greeting + mood card fan (8 moods from `moods/`).
- [ ] Pull-card interaction: tap to focus, tap again / “Reveal” to open.
- [ ] Subcategory list per mood.
- [ ] **Threads screen:** references only (Quran / Hadith badge + citation).
- [ ] **Reading screen:** Arabic, English, Meaning, Reflection.
- [ ] Previous / Next + progress indicator across threads in that subcategory.
- [ ] Offline-first: ship SQLite DBs (or a packaged subset) on device.

### Report / feedback
- [ ] **Report** on reading screen.
- [ ] Multi-select reasons, e.g.:
  - Issue in the reference (wrong book / number)
  - Reference differs from the original book
  - Translation is not correct
  - Arabic text looks incorrect
  - Explanation / meaning is not correct
  - Reflection feels off or misleading
  - Something else (+ optional note)
- [ ] Store reports (device queue + sync to backend when online).
- [ ] Include metadata: app version, passage id/ref, mood/sub path, timestamp, platform.

### Non-functional
- Smooth 60fps interactions on mid-range phones.
- Dark/light: start with calm light theme from mockup; dark later optional.
- Accessibility: Dynamic Type where reasonable; reduced motion; large tap targets.
- No account required for v1 reading; reports can be anonymous.

## Data requirements

- Mood taxonomy and curated refs stay editable as text/JSON in repo.
- Full passage bodies resolved from `quran.db` / `hadith.db` (or pre-baked JSON for v1 speed).
- Citations must match index numbers (Bukhari 5641, Quran 2:255, etc.).

## Out of scope for v1

- Full semantic search UI
- User accounts / social
- Push notifications
- App Store / Play production release (comes after internal testing)

## Success criteria for first internal build

1. Install on your iPhone from Mac.
2. Install APK on Android without a store.
3. Complete flow Name → Mood → Sub → Thread → Read → Report.
4. Report payload visible in logs / admin dump.
