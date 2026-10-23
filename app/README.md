# Heart Threads (Expo)

Mobile app: moods → threads → reading, with **swipe** to browse cards and **pull down** to open (reveal animation).

## Run

```bash
cd app
npm install
npx expo start
```

iPhone / Simulator (Mac + free Apple ID):

```bash
cd "/Users/geovision/Desktop/Developmentt/New Ideas/Hadith app/app"
git pull && npm install
npx expo run:ios
```

Pick your **physical iPhone** when prompted (or an iOS 18 simulator). If the build fails after a dependency change, wipe native folders once: `rm -rf ios && npx expo run:ios`.

Android preview APK (EAS):

```bash
eas build -p android --profile preview
```

## Structure

- `src/content/catalog.json` — curated moods/passages
- `src/components/CardFan.tsx` — swipe L/R + pull-down reveal
- `src/screens/*` — Name, Feeling, Subs, Threads, Read
- Reports saved locally via AsyncStorage (`hadith.reports.v1`)
