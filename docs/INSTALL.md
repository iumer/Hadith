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

**Direct download (~90 MB):**  
https://github.com/iumer/Hadith/releases/download/android-preview-2026-10-22/HeartThreads-preview.apk

Release page: https://github.com/iumer/Hadith/releases/tag/android-preview-2026-10-22

1. Open the link on the phone (or download on a computer and send the file).
2. Allow **Install unknown apps** for the browser/Files if asked.
3. Install → open → enter a name → test swipe / pull-down / back.

No Expo Go required for APK testers.

## After every update

| Platform | What you do |
|---|---|
| iOS | `git pull` + `npm install` + `npx expo start` again |
| Android | Install the **new** APK over the old one |
