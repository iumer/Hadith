# Setup & builds (Mac + cloud + APK)

How we develop and how **you** get installs on iPhone and Android.

## Roles

| Who | Where | Responsibility |
|---|---|---|
| **You** | MacBook M1 + Xcode | Daily iOS device builds (free Apple ID) |
| **Agent / CI** | Cloud Linux | Code, Android APK artifacts, docs, content pipeline |
| **EAS (later)** | Expo cloud | Optional iOS cloud builds after paid Apple Developer |

---

## One-time setup on your Mac

1. Install **Xcode** (already have) and open once to accept license.
2. Install **Node 20+** (nvm or official installer).
3. Install CocoaPods if prompted: `sudo gem install cocoapods` (or via Homebrew).
4. Clone the repo and use the Expo app folder (after Milestone 1):
   ```bash
   git clone <repo-url>
   cd app
   npm install
   ```
5. Connect iPhone via cable, trust the computer, enable Developer Mode (iOS 16+).
6. In Xcode → Settings → Accounts: add your **Apple ID** (free is OK for personal device).

### Run on your iPhone (weekly)

Free provisioning expires ~7 days — rebuild weekly:

```bash
cd app
npm install
npx expo start          # Expo Go / tunnel for quick checks
npx expo run:ios --device   # native build on your iPhone
```

Or open `ios/*.xcworkspace` in Xcode → select your iPhone → Run.

If signing errors appear: Xcode → Signing & Capabilities → Team = your personal team → unique Bundle ID.

---

## Android APK (you download to phone)

Cloud/CI produces an APK; you install it (allow “unknown apps” for the browser/files app).

### Option A — Expo EAS preview (recommended later)

```bash
npm i -g eas-cli
eas login
eas build -p android --profile preview
```

EAS gives a URL → open on phone → install APK.

### Option B — Local/CI Gradle assemble

```bash
npx expo prebuild --platform android
cd android && ./gradlew assembleRelease
# APK: android/app/build/outputs/apk/release/app-release.apk
```

### Option C — Agent attaches APK

On each Milestone 1+ push, I can:
1. Build APK in cloud
2. Put it in GitHub Actions artifacts or a release asset  
3. Send you the download link

**You:** download → install → smoke-test.

---

## Cloud agent workflow (me)

1. Work on feature branches `cursor/...-db55`.
2. Keep mockup + docs + (soon) `app/` in sync via PRs.
3. Run `npm` typecheck/lint; build Android when requested.
4. Never need your Apple password; iOS signing stays on your Mac until EAS + paid account.

---

## Suggested `eas.json` (when Expo exists)

```json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "android": { "buildType": "apk" },
      "distribution": "internal"
    },
    "production": {}
  }
}
```

- **preview** → APK for your Android phone  
- **development** → optional custom dev client  
- **production** → store binaries later  

---

## Weekly rhythm (while on free Apple ID)

| Day | Action |
|---|---|
| After I push | You `git pull` on Mac |
| Same day | `npx expo run:ios --device` |
| Same day | Download fresh APK if Android changed |
| ~Day 7 | iOS install expires → rebuild on Mac |

---

## Checklist before first device test

- [ ] Mockup approved  
- [ ] Expo app scaffolded  
- [ ] Bundle ID chosen (e.g. `com.yourname.moodlight`)  
- [ ] Mac run succeeds once  
- [ ] APK installs once  
- [ ] Report button writes a local sample report  
