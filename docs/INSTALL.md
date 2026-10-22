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

Download **`HeartThreads-preview.apk`** from the Cursor agent Artifacts (~90 MB) → open on phone → allow unknown apps → Install.

No Expo Go required for APK testers.

## After every update

| Platform | What you do |
|---|---|
| iOS | `git pull` + `npm install` + `npx expo start` again |
| Android | Install the **new** APK over the old one |
