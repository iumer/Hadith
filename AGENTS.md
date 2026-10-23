# Agent entrypoint

1. Checkout **`cursor/app-interactive-mockup-db55`** (active mobile-app work).
2. Read **[`summary.md`](./summary.md)** end-to-end.
3. Follow **[`docs/AGENT_QA_PROTOCOL.md`](./docs/AGENT_QA_PROTOCOL.md)** and update **[`docs/ISSUE_LOG.md`](./docs/ISSUE_LOG.md)**.
4. Install notes: **[`docs/INSTALL.md`](./docs/INSTALL.md)**.

## Stable Android APK URL (do not create new links)

https://github.com/iumer/Hadith/releases/download/android-preview/HeartThreads-preview.apk  
Also kept up to date (older link some testers have):  
https://github.com/iumer/Hadith/releases/download/android-preview-2026-10-22/HeartThreads-preview.apk

After `assembleRelease`, publish in place:

```bash
./scripts/publish_android_apk.sh app/android/app/build/outputs/apk/release/app-release.apk
```

The script updates **both** release links on every build. Keep sharing the same URLs with testers.
