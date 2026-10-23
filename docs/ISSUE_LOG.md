# Issue & suggestion log

Living list. Status: `open` | `fixed-pending-device` | `verified-device` | `wontfix`.

Last agent test surface: Expo web + Vite mockup (cloud browser).  
Last updated: 2026-10-23 (Asia/Karachi). Agent test surface for this round: Expo Go on iOS Simulator (iPhone 17 Pro Max, iOS 27). Full audit: `docs/AUDIT_2026-10-23.md`.

---

## Open / in progress

| ID | Source | Summary | Status | Evidence |
|---|---|---|---|---|
| I-001 | User Mac build | `react-native-screens` 4.30 + Xcode 27 `UIBarMinimization` compile fail | fixed-pending-device | Pinned `4.29.0`; Mac native build succeeded |
| I-002 | User Mac Metro | Missing `babel-preset-expo` → Metro `transformFile` red screen | fixed-pending-device | Added dep; Expo Go sim showed Assalamoalikum + cards |
| I-003 | User process | Local `package.json` dirty from Expo prebuild blocks `git pull` | open | Need pull helper / document `git checkout -- app/package.json` |
| I-004 | User request | Install/test on physical iPhone + Android | open | Expo Go QR path given; APK requested |
| I-005 | Agent protocol | Cloud agent has no iOS/Android simulator | open | Use Expo web + mockup for gate; you verify devices |
| I-006 | User both platforms | Swipe L/R feels stiff — cards don’t slide with finger | fixed-pending-device | Continuous `scroll` shared value follows finger |
| I-007 | User both platforms | Pull-down cuts mid-expand → sudden next page | fixed-pending-device | Pull to max → 820ms reveal → then navigate |
| I-008 | User both platforms | After Read→back→back, stuck on giant card, gestures dead | fixed-pending-device | Remount fan on focus + reset shared values |
| I-009 | User request | Android APK for testers | fixed-pending-device | Sakinah 0.2.0 (versionCode 2) built on the Mac 2026-10-23 and published to the same stable URL; same signing cert as 0.1.0 so it installs as an update |
| I-010 | Agent web QA | CardFan Pan gestures ignore mouse on Expo web — blocked smoke | verified-agent | Web Prev/Next/Open; Playwright hard-refresh smoke **PASS** (steps 1–9); see `qa-web-retest-*.png` |
| I-011 | Agent audit | 33 Quran cards showed English cut off at the first `"` (e.g. 39:53 showed only `Say,`) | fixed-pending-device | New `scripts/build_catalog.py`; 0 truncated cards. Sim: 2:156 full text |
| I-012 | Agent audit | Hadith English showed the wrong sentence (Bukhari 1283/1303/2908, Muslim 923a/2307a, Tirmidhi 2517) or only a narrator line (Ibn Majah 3818, Nasa'i 5453) | fixed-pending-device | `EN_FIX` overrides in `expand_mood_files.py`. Sim: Bukhari 1283, Nasa'i 5453 |
| I-013 | Agent audit | Weak (da'if) hadith Abu Dawud 1518 used ×3; Nawawi 19 ungraded ×3 | fixed-pending-device | Replaced with Tirmidhi 3524 / 3505 / Ibn Hibban 972; Nawawi 19 → Tirmidhi 2516. Build now fails on any non-sahih/hasan hadith |
| I-014 | Agent audit | Arabic words broken across lines (stray space after tanween, ~40 cards); Arabic used Latin font | fixed-pending-device | Build strips the space; Amiri Quran (ayahs) + Amiri (hadith) |
| I-015 | Agent audit | Mood names wrapped mid-word ("Overwhe/lmed"); text bleed on back cards; fan pinned to bottom, pull ran off-screen; unlabeled count badges | fixed-pending-device | `CardFan.tsx` — sim screenshots |
| I-016 | Agent audit | Read: Next/Previous kept old scroll position | fixed-pending-device | `scrollTo(0)` on index change — sim verified |
| I-017 | Agent audit | Report: keyboard hid note + Submit; backdrop tap discarded report; reports lacked passageId/mood/sub/platform/version | fixed-pending-device | KeyboardAvoidingView, first backdrop tap only dismisses keyboard, full payload — sim verified in AsyncStorage |
| I-018 | Agent audit | Name not saved; needed double-tap on Continue with keyboard up | fixed-pending-device | AsyncStorage `hadith.name.v1`; relaunch skips Name — sim verified |
| I-019 | User request | Authenticity bar on hadith pages | fixed-pending-device | `GradeBar.tsx`: Sahih full green, Hasan ¾ light green, Da'if amber, Mawdu' red; tap for graders + "scholars differ" |
| I-020 | Agent audit | `expo lint` reports 22 React Compiler errors in `CardFan.tsx` (Reanimated `.value` writes) | open | Pre-existing pattern; needs `useSharedValue` refactor or rule override |
| I-021 | User request | Cards too small; swipe/pull instructions read like captions | fixed-pending-device | 172×236 cards; "Swipe to browse" pill above, dark "↓ Pull Sad down to open" pill below ("Release to open" when armed) |
| I-022 | User request | Tapping a card did nothing | fixed-pending-device | Tap (or ~4.5s idle) makes the card tug/wiggle + "Pull me down" bubble; tapping a side card brings it to front |
| I-023 | User both platforms | Pull-to-open animation broke midway | fixed-pending-device | Card now expands into a full-screen tile (iOS ease curve, 560ms) and Subs fades in on the same tint; haptics on threshold/open |
| I-024 | User both platforms | Read→back→back showed the opened mood as a giant tile, then it shrank | fixed-pending-device | Fan resets only after the next screen covers it; on return the card just settles. Sim verified |
| I-025 | User request | Arabic → Urdu → English for every passage, authentic translations only | fixed-pending-device | Quran: Junagarhi (UR) + Saheeh International (EN). Hadith: source Urdu/English excerpts; `build_catalog.py` fails if any shown text is not verbatim from the source |
| I-026 | User request | Swipe left/right on Read pages to change passage, keep iOS edge swipe-back | fixed-pending-device | Pan with 28pt edge exclusion (both edges on Android). Sim verified both |
| I-027 | User request | Name asked again after relaunch | fixed-pending-device | App reads saved name before choosing first screen; Feeling has no back-to-name (long-press the greeting to change name) |
| I-028 | User request | Catalog had fragments (e.g. Peaceful 89:29, 89:30 as 3-word cards); Quran must be complete ayat in context, hadith complete sayings | fixed-pending-device | Full recheck: ayah ranges (e.g. 89:27-30, 2:155-157, 26:61-62) shown as one card; hadith slices widened to include the question/story; off-context picks replaced (65:2 divorce, 8:46 battle, 3:154, 76:10, 33:35, 4:59, Bukhari 6472/24/2443); no repeats inside a mood. 148 passages, all source-verified |

## Suggestions (from user / agent)

| ID | Suggestion | Notes |
|---|---|---|
| S-001 | Agent must screenshot issues + fixes before “done” | Protocol in `AGENT_QA_PROTOCOL.md` |
| S-002 | Keep issue list; retest every build | This file |
| S-003 | Prefer Expo Go on device for smoke; native `run:ios --device` for full gestures | Reanimated/gestures more reliable on dev build |

## Closed (reference)

_(none yet marked verified-device)_
