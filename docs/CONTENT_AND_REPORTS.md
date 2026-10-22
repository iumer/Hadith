# Content & reports

## Mood content

- **Source of truth:** `moods/{mood}/{subcategory}.txt`
- Each file is a sequence of passage cards separated by `────` rules.
- Fields we parse: title/reference, Arabic, English, Meaning, Reflection.

### Threads screen rule

Show **only**:
- Kind badge — `Quran` | `Hadith`
- Reference string — e.g. `Quran 12:86`, `Sahih al-Bukhari 5641`

No preview blurb on the threads list. Full text appears only on the reading screen.

## Reading screen

Order:
1. Badge + reference title  
2. Arabic  
3. English translation  
4. Meaning  
5. Reflection  
6. Previous / Next (+ progress)

## Report reasons (v1)

Users may multi-select:

1. Issue in the reference (wrong book / number)  
2. Reference differs from the original book  
3. The translation is not correct  
4. The Arabic text looks incorrect  
5. The explanation / meaning is not correct  
6. The reflection feels off or misleading  
7. Something else  

Optional free-text note.

Reports are used internally to fix catalog/copy; they are not public comments.

## Improving from reports

1. Triage weekly dump.  
2. Fix mood file or index data in a PR.  
3. Rebuild catalog → ship app update.  
