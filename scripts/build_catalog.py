#!/usr/bin/env python3
"""Build app/src/content/catalog.json from moods/*/*.txt (the content source of truth).

Each hadith gets its authenticity grade from data/build/hadith.db. Only sahih and
hasan hadith are shipped; anything else fails the build so it gets fixed at the source.

    python -m hadith setup            # once, builds data/build/hadith.db
    python scripts/build_catalog.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOODS = ROOT / "moods"
OUT = ROOT / "app" / "src" / "content" / "catalog.json"
DB = ROOT / "data" / "build" / "hadith.db"

# Display order and card metadata for the eight moods.
MOOD_META = [
    ("happy", "Happy", "Lightness", "#FFE566"),
    ("confident", "Confident", "Steady", "#7DFFB3"),
    ("sad", "Sad", "Tender", "#7EC8FF"),
    ("overwhelmed", "Overwhelmed", "Heavy", "#C4B5FD"),
    ("anxious", "Anxious", "Restless", "#FFB347"),
    ("angry", "Angry", "Heat", "#FF7A8A"),
    ("shame-guilt", "Shame & Guilt", "Weight", "#FFB4A2"),
    ("confused", "Confused", "Fog", "#80E5FF"),
]
SUB_LABELS = {"grateful-blessed": "Grateful & Blessed"}

ALLOWED = {"sahih", "hasan"}
SEPARATOR = re.compile(r"^─{10,}\s*$", re.M)
SECTIONS = ("Arabic:", "English Translation:", "Meaning ❤️", "Reflection", "Reference:")


def fix_arabic(text: str) -> str:
    # The mushaf source has a stray space between tanween and alif, which makes
    # the alif wrap onto its own line on device.
    return re.sub(r"([ࣰ-ًࣲ-ٍ]) (ا)", r"\1\2", text).strip()


def strip_quotes(text: str) -> str:
    # Remove only the one pair of outer curly quotes added by expand_mood_files.py;
    # inner quotes are part of the translation.
    text = text.strip()
    if text.startswith("“") and text.endswith("”"):
        text = text[1:-1].strip()
    # Saheeh International text drops the closing quote at the end of an ayah.
    if text.count('"') % 2:
        text += '"'
    return text


def parse_block(block: str) -> dict:
    lines = block.strip().splitlines()
    title = lines[0].strip()
    body = "\n".join(lines[1:])
    pos = {s: body.find("\n" + s) for s in SECTIONS}
    found = sorted((p, s) for s, p in pos.items() if p >= 0)
    parts: dict[str, str] = {}
    for i, (p, s) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(body)
        parts[s] = body[p + 1 + len(s) : end].strip()
    head = body[: found[0][0]].strip() if found else ""
    source = head.splitlines()[0].strip() if title.startswith("Quran ") and head else ""
    return {
        "title": title,
        "kind": "quran" if title.startswith("Quran ") else "hadith",
        "source": source,
        "arabic": fix_arabic(parts.get("Arabic:", "")),
        "english": strip_quotes(parts.get("English Translation:", "")),
        "meaning": parts.get("Meaning ❤️", ""),
        "reflection": parts.get("Reflection", ""),
    }


def normalize_grade(text: str) -> str | None:
    t = (text or "").lower()
    if "mawdu" in t or "maudu" in t or "موضوع" in t or "fabricat" in t:
        return "mawdu"
    if "daif" in t or "da'if" in t or "ضعيف" in t or "munkar" in t or "weak" in t:
        return "daif"
    if "sahih" in t or "صحيح" in t:
        return "sahih"
    if "hasan" in t or "حسن" in t:
        return "hasan"
    return None


class Grades:
    def __init__(self, db: Path):
        self.db = sqlite3.connect(db)
        self.names = dict(self.db.execute("select name_en, slug from collections"))

    def lookup(self, title: str) -> dict:
        for name, slug in sorted(self.names.items(), key=lambda x: -len(x[0])):
            if title.startswith(name + " "):
                number = title[len(name) + 1 :]
                row = self.db.execute(
                    "select grade, grade_text, grades from hadiths where collection=? and number=?",
                    (slug, number),
                ).fetchone()
                if not row:
                    raise SystemExit(f"{title}: not found in {DB}")
                return self._describe(slug, name, *row)
        raise SystemExit(f"{title}: unknown collection")

    def _describe(self, slug: str, name: str, grade: str, grade_text: str, grades_json: str) -> dict:
        if slug in ("bukhari", "muslim"):
            return {"grade": "sahih", "gradedBy": f"In {name}", "gradings": [], "disputed": False}
        gradings = []
        for g in json.loads(grades_json or "[]"):
            label = normalize_grade(g.get("grade", ""))
            if label:
                gradings.append({"grader": g.get("grader", "").strip(), "grade": label})
        m = re.search(r"\(([^()]*)\)\s*$", grade_text or "")
        graded_by = m.group(1).strip() if m else (gradings[0]["grader"] if gradings else "")
        if graded_by.lower() == "al-albani":
            graded_by = "Al-Albani"
        labels = {g["grade"] for g in gradings}
        disputed = bool(labels & ALLOWED) and bool(labels - ALLOWED)
        return {
            "grade": grade or normalize_grade(grade_text) or "",
            "gradedBy": graded_by,
            "gradings": gradings,
            "disputed": disputed,
        }


def main() -> None:
    if not DB.exists():
        sys.exit(f"{DB} missing — run `python -m hadith setup` first")
    grades = Grades(DB)
    errors: list[str] = []
    moods = []
    for mood_id, label, short, color in MOOD_META:
        subs = []
        for path in sorted((MOODS / mood_id).glob("*.txt")):
            sub_id = path.stem
            items = []
            for i, block in enumerate(SEPARATOR.split(path.read_text(encoding="utf-8"))):
                if not block.strip():
                    continue
                item = parse_block(block)
                if not item["english"] or not item["arabic"]:
                    errors.append(f"{path.relative_to(ROOT)}: {item['title']} has empty Arabic or English")
                if item["kind"] == "hadith":
                    g = grades.lookup(item["title"])
                    if g["grade"] not in ALLOWED:
                        errors.append(f"{path.relative_to(ROOT)}: {item['title']} is graded '{g['grade'] or 'ungraded'}'")
                    item.update(g)
                items.append({"id": f"{mood_id}-{sub_id}-{i}", **{k: v for k, v in item.items() if v != ""}})
            sub_label = SUB_LABELS.get(sub_id, sub_id.replace("-", " ").title())
            subs.append({"id": sub_id, "label": sub_label, "items": items})
        moods.append({"id": mood_id, "label": label, "short": short, "color": color, "subs": subs})

    if errors:
        print("Catalog not written:\n" + "\n".join("  " + e for e in errors))
        sys.exit(1)
    OUT.write_text(json.dumps({"moods": moods}, ensure_ascii=False), encoding="utf-8")
    n = sum(len(s["items"]) for m in moods for s in m["subs"])
    print(f"wrote {OUT.relative_to(ROOT)}: {len(moods)} moods, {sum(len(m['subs']) for m in moods)} subs, {n} passages")


if __name__ == "__main__":
    main()
