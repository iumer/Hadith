# Heart Threads (Expo)

Mobile app: moods → threads → reading, with **swipe** to browse cards and **pull down** to open (reveal animation).

## Run

```bash
cd app
npm install
npx expo start
```

iPhone (Mac + free Apple ID):

```bash
npx expo run:ios --device
```

Android preview APK (EAS):

```bash
eas build -p android --profile preview
```

## Structure

- `src/content/catalog.json` — curated moods/passages
- `src/components/CardFan.tsx` — swipe L/R + pull-down reveal
- `src/screens/*` — Name, Feeling, Subs, Threads, Read
- Reports saved locally via AsyncStorage (`hadith.reports.v1`)
