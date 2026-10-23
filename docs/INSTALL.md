# Simple install (iOS + Android)

Full handoff + history: **[`../summary.md`](../summary.md)** (start at section 1).

## iPhone (Mac + Expo Go)

```bash
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app"
git checkout cursor/app-interactive-mockup-db55
git pull origin cursor/app-interactive-mockup-db55
cd app
npm install
npx expo start
```

Install **Expo Go** on the iPhone → same Wi‑Fi → scan the QR.

## Android (direct APK)

**Stable download link (same forever — share this once):**  
https://github.com/iumer/Hadith/releases/download/android-preview/HeartThreads-preview.apk  
Also kept up to date (older link some testers have):  
https://github.com/iumer/Hadith/releases/download/android-preview-2026-10-22/HeartThreads-preview.apk

Release page: https://github.com/iumer/Hadith/releases/tag/android-preview

Every new Android build **replaces the file at that same URL** (`scripts/publish_android_apk.sh`). You do not need a new link for testers.

1. Open the link on the phone (or download on a computer and send the file).
2. Allow **Install unknown apps** for the browser/Files if asked.
3. Install → open → enter a name → test swipe / pull-down / back.

No Expo Go required for APK testers.

## Reports token (once per Mac)

The Report button writes to `REPORTS.md` in the private repo `iumer/sakinah-feedback`.
Builds need `app/.env.local` (git-ignored, see `app/.env.example`) with a fine-grained GitHub
token limited to that repo (Contents: Read and write). Without it, reports are only kept on
the phone. After creating or changing it, restart `npx expo start`.

## After every update

| Platform | What you do |
|---|---|
| iOS | `git pull` + `npm install` + `npx expo start` again |
| Android | Re-download the **same** link above and install over the old app |

### Agent: publish a new APK without changing the link

```bash
# after assembleRelease
./scripts/publish_android_apk.sh app/android/app/build/outputs/apk/release/app-release.apk
```
