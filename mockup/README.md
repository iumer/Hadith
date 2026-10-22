# Mood & Light — Interactive Mockup

Clickable phone mockup of the app flow (design exploration only).

## Flow

1. Enter your name  
2. **Assalamoalikum {name}** — how are you feeling?  
3. **Spinning mood orbit** — drag to spin, hold to speed up, tap a mood  
4. Subcategories for that mood  
5. List of Hadith / Quran references (preview only)  
6. Full reading (Arabic, English, meaning, reflection) with back

Uses the real mood folders and sample passages from `../moods`.

## Run locally

```bash
cd mockup
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). On a phone browser, the mockup goes full-screen.

## Notes

- This is **not** the Expo app yet — only an interactive design prototype.  
- There are **8** moods (happy, confident, sad, overwhelmed, anxious, angry, shame-guilt, confused), matching the folders we created.
