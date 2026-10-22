# Issue & suggestion log

Living list. Status: `open` | `fixed-pending-device` | `verified-device` | `wontfix`.

Last agent test surface: Expo web + Vite mockup (cloud browser).  
Last updated: 2026-10-22 (Asia/Karachi).

---

## Open / in progress

| ID | Source | Summary | Status | Evidence |
|---|---|---|---|---|
| I-001 | User Mac build | `react-native-screens` 4.30 + Xcode 27 `UIBarMinimization` compile fail | fixed-pending-device | Pinned `4.29.0`; Mac native build succeeded |
| I-002 | User Mac Metro | Missing `babel-preset-expo` → Metro `transformFile` red screen | fixed-pending-device | Added dep; Expo Go sim showed Assalamoalikum + cards |
| I-003 | User process | Local `package.json` dirty from Expo prebuild blocks `git pull` | open | Need pull helper / document `git checkout -- app/package.json` |
| I-004 | User request | Install/test on physical iPhone + Android | open | Expo Go QR path given; device sign-off pending user |
| I-005 | Agent protocol | Cloud agent has no iOS/Android simulator | open | Use Expo web + mockup for gate; you verify devices |

## Suggestions (from user / agent)

| ID | Suggestion | Notes |
|---|---|---|
| S-001 | Agent must screenshot issues + fixes before “done” | Protocol in `AGENT_QA_PROTOCOL.md` |
| S-002 | Keep issue list; retest every build | This file |
| S-003 | Prefer Expo Go on device for smoke; native `run:ios --device` for full gestures | Reanimated/gestures more reliable on dev build |

## Closed (reference)

_(none yet marked verified-device)_
