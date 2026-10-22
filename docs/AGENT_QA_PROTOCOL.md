# Agent QA protocol (mandatory)

Before calling any task **done**, the agent must complete this loop on the **agent’s own test surface**, then hand off for your iOS/Android devices.

## Gate before “done”

1. Open the app on the agent test surface (Expo web and/or Vite mockup — see limits below).
2. Walk the full happy path with **real catalog content** from `app/src/content/catalog.json` (moods corpus), not invented placeholder strings.
3. Press **every** interactive control on that path (back, cards, rows, prev/next, report options, submit/cancel).
4. Try to break it (empty name, pull without release, rapid swipe, report with no selection, next on last item, etc.).
5. Read Metro / terminal / browser console errors; fix before claiming done.
6. Run whatever build/check is available here (`tsc`, mockup `npm run build`, Expo web start).
7. Attach **screenshots of issues found** and **screenshots after fixes**.
8. Do **not** say “should work now” / “try again” as a substitute for proof.

## Issue & suggestion log

All user-reported issues and change requests are tracked in `docs/ISSUE_LOG.md`.  
Every build/test pass starts by refreshing that list, retesting prior items, then testing new work.

## Environment limits (honest)

| Surface | Available in cloud agent VM? |
|---|---|
| Vite mockup (browser) | Yes |
| Expo web (browser) | Yes |
| iOS Simulator (Xcode) | **No** — Linux VM, no Xcode |
| Android Emulator | **No** unless separately provisioned |
| Your physical iPhone / Android | **You** — after agent gate passes |

After the agent gate passes, you re-verify on **your** iOS and Android. Agent does not claim device sign-off.

## Content source for this app

This product uses **Hadith/Quran mood catalog** (`moods/` → `catalog.json`), not bank/transaction PDFs.  
“Real data” here means curated corpus passages, not synthetic UI lorem.
