# Milestones

Phased plan from mockup → installable iOS + Android builds.

---

## Milestone 0 — Design lock

**Goal:** Agree UI flow and visuals.

- [x] Interactive mockup (`mockup/`)
- [x] Card fan + calm background
- [x] Swipe L/R to browse · **pull down** to open (no double-tap)
- [x] Reveal curtain animation into next screen
- [x] Threads = references only
- [x] Reading + Previous/Next
- [x] Report multi-select sheet
- [x] Locked for Expo build (pull-down + swipe)

**Exit:** Written OK from you on screens + report reasons.

---

## Milestone 1 — Expo skeleton *(in progress)*

**Goal:** Expo app runs on your iPhone and an Android emulator/APK.

**I do (cloud):**
- [x] Scaffold Expo (TypeScript + React Navigation)
- [x] Port theme + screens (Name → Feeling/CardFan → Subs → Threads → Read)
- [x] CardFan: swipe L/R + pull-down reveal (Reanimated + Gesture Handler)
- [x] Bundle mood catalog from `moods/`
- [x] Report sheet → local AsyncStorage queue
- [x] Wire `eas.json` preview APK profile
- [ ] GitHub Action for Android APK (next)
- [x] Document Mac commands for iOS device run

**You do (Mac):**
- Install Xcode CLT, Node, Watchman (if needed)
- `cd app && npm install && npx expo run:ios --device` with free Apple ID
- Confirm app launches on iPhone

**Deliverable:** Assalamoalikum + pull-down moods on your phone + APK link.

---

## Milestone 2 — Content wiring

**Goal:** Real moods → subs → threads → reading from curated data.

**I do:**
- Build script: `moods/**/*.txt` → `passages.json` / catalog
- Implement full navigation + CardFan in RN
- Threads list (refs only) + Reading with Prev/Next
- Bundle content offline

**You do:** Spot-check 5–10 passages vs original books.

**Deliverable:** Complete read path with real content.

---

## Milestone 3 — Reports

**Goal:** Collect multi-select reports.

**I do:**
- Report sheet UI (ported from mockup)
- Local queue + JSON export / temporary sync endpoint
- Simple admin view or weekly dump of reports

**You do:** File a few test reports from device.

**Deliverable:** Reports you can open and act on.

---

## Milestone 4 — Polish & stability

**Goal:** Feels release-candidate for friends/family testing.

- Performance pass, empty states, error toasts
- Reduced motion, larger text
- Icon + splash (name still TBD)
- Crash-free smoke on iOS + Android

**Deliverable:** Weekly iOS rebuild + APK for testers.

---

## Milestone 5 — Store readiness *(later)*

Requires paid Apple Developer ($99/yr) + Play Console.

- EAS production profiles
- Privacy text, content attribution / licences
- TestFlight + internal Play track

---

## Suggested order of coding (Milestone 1–2 detail)

1. `npx create-expo-app` in `app/`
2. Navigation + 5 screens (placeholders)
3. Theme tokens from mockup
4. CardFan component (Reanimated)
5. Catalog build from `moods/`
6. Threads + Reading
7. Report sheet + local store
8. Android CI APK
9. Mac iOS runbook verified by you
