"""Parser for OpenITI mARkdown texts (digitised printed Arabic editions).

OpenITI files keep the printed edition's pagination as ``PageVxxPyyy``
markers (volume xx, page yyy).  Two conventions occur in the corpus:

* ``end``:   the marker closes a page (classic OpenITI / JK / mARkdown files);
* ``start``: the marker opens a page (newer Shamela conversions, which also
  emit inline ``[ص: N]`` page breaks and meaningless ``PageV00P000`` markers).

The parser turns a file into a list of :class:`Record` objects, one per hadith
(or per numbered unit), each carrying its printed volume/page, the enclosing
kitab (book) and bab (chapter) headings, and any editor's grading note.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from .normalize import clean_display

PAGE_RE = re.compile(r"PageV(\d+)P(\d+)")
INLINE_PAGE_RE = re.compile(r"\[ص:\s*(\d+)\]")
TOKEN_RE = re.compile(r"PageV\d+P\d+|\[ص:\s*\d+\]")
MS_RE = re.compile(r"\bms\d+\b")
ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
NUM_HEADER_RE = re.compile(r"^\(?\s*(\d+)\s*\)?\s*(?:[-–ـ]\s*)?(.*)$")

GRADE_HEADERS = ("تعليق المحقق", "قال الشيخ الألباني", "حكم الألباني", "قال الألباني",
                 "حكم الحديث", "تعليق شعيب", "قال شعيب", "حكم", "التعليق")
HEADER_TAGS_RE = re.compile(r"^(?:AUTO|CHECK)\s+")


def _preprocess_inline_numbers(raw: str) -> str:
    """Rewrite ``# 12 - text`` records (numbers inline, sometimes glued to the
    previous heading) into the ``### | 12 -`` form, and label grade blocks."""
    raw = re.sub(r"#\s*(\d{1,5}) - (?=\S)", r"\n### | \1 - \n# ", raw)
    raw = re.sub(r"(?m)^# __________L\s*$", "### | [حكم الألباني]", raw)
    raw = re.sub(r"(?m)^# S\s*$", "### | [حكم شعيب الأرنؤوط]", raw)
    raw = re.sub(r"(?m)^# (?:§|Z \(\d+\))\s*$", "", raw)
    return raw.replace("§", "")


@dataclass
class Record:
    number: str | None
    text: str = ""
    volume: int | None = None
    page: int | None = None
    end_volume: int | None = None
    end_page: int | None = None
    kitab: str | None = None
    kitab_number: str | None = None
    bab: str | None = None
    bab_number: str | None = None
    grade_note: str | None = None
    extra_headers: list[str] = field(default_factory=list)


@dataclass
class FileSpec:
    page_style: str = "start"          # "start" or "end"
    # How a hadith record begins.  "number_header": ``### | 12 -`` lines;
    # "dollar": ``### $`` lines (unnumbered); "number_para": ``# 12 -`` paragraphs.
    record_mode: str = "number_header"
    kitab_prefixes: tuple[str, ...] = ("كتاب", "أبواب", "ابواب", "من كتاب", "ومن كتاب")
    bab_prefixes: tuple[str, ...] = ("باب",)
    chapter_prefixes: tuple[str, ...] = ()   # extra prefixes treated as bab (e.g. مسند)
    skip_until: str | None = None            # ignore everything before this literal
    headers_in_text: bool = False            # unknown headings are part of the hadith text


def _iter_body_lines(raw: str) -> Iterable[str]:
    in_header = True
    for line in raw.splitlines():
        if in_header:
            if line.startswith("#META#Header#End#"):
                in_header = False
            continue
        yield line.rstrip()


def _strip_header_text(s: str) -> str:
    s = s.strip().strip("|").strip()
    s = s.strip("()[] ")
    return s


def parse(raw: str, spec: FileSpec) -> list[Record]:
    if spec.record_mode == "number_inline":
        raw = _preprocess_inline_numbers(raw)
        spec = FileSpec(**{**spec.__dict__, "record_mode": "number_header"})
    lines = list(_iter_body_lines(raw))
    if spec.skip_until:
        for i, l in enumerate(lines):
            if spec.skip_until in l:
                lines = lines[i:]
                break

    # Phase 1: flatten into an event stream.
    events: list[tuple] = []   # ("text", str) | ("page", vol, page) | ("ipage", page) | ("hdr", level, text) | ("rec", number)

    def emit_text(s: str):
        pos = 0
        for m in TOKEN_RE.finditer(s):
            if m.start() > pos:
                events.append(("text", s[pos:m.start()]))
            tok = m.group(0)
            pm = PAGE_RE.fullmatch(tok)
            if pm:
                events.append(("page", int(pm.group(1)), int(pm.group(2))))
            else:
                events.append(("ipage", int(INLINE_PAGE_RE.fullmatch(tok).group(1))))
            pos = m.end()
        if pos < len(s):
            events.append(("text", s[pos:]))

    for line in lines:
        if not line.strip():
            continue
        if line.startswith("### $"):
            if spec.record_mode == "dollar":
                events.append(("rec", None))
                emit_text(" " + line[5:])
                continue
            line = "### |" + line[5:]
        if line.startswith("###"):
            body = MS_RE.sub("", line[3:]).strip()
            level = len(body) - len(body.lstrip("|"))
            body = body.lstrip("|").strip()
            # A header may itself be only a page token.
            if TOKEN_RE.fullmatch(body.strip()):
                emit_text(body)
                continue
            # Page markers embedded in headers.
            for m in TOKEN_RE.finditer(body):
                emit_text(m.group(0))
            body = TOKEN_RE.sub("", body).strip()
            events.append(("hdr", level, body))
            continue
        if line.startswith("# "):
            content = line[2:]
            if spec.record_mode == "number_para":
                m = re.match(r"^\s*(\d+)\s*-\s*$", content.translate(ARABIC_DIGITS))
                if m:
                    events.append(("rec", m.group(1)))
                    continue
            events.append(("text", "\n"))
            emit_text(content)
            continue
        if line.startswith("~~"):
            emit_text(" " + line[2:])
            continue
        if line.startswith("#"):
            emit_text(line.lstrip("#"))
            continue
        emit_text(" " + line)

    # Phase 2: resolve the printed page in effect at every event index.
    n = len(events)
    page_at: list[tuple[int | None, int | None]] = [(None, None)] * n
    if spec.page_style == "start":
        # Shamela emits a record's *starting* page after the record, so a
        # PageV marker may lag behind an inline [ص: N] break that preceded it.
        # Pages never decrease within a volume, so keep the maximum.
        vol, pg = None, None
        for i, ev in enumerate(events):
            if ev[0] == "page" and ev[1] > 0:
                if ev[1] != vol:
                    vol, pg = ev[1], ev[2]
                else:
                    pg = max(pg or 0, ev[2])
            elif ev[0] == "ipage" and vol is not None:
                pg = max(pg or 0, ev[1])
            page_at[i] = (vol, pg)
    else:
        nxt: tuple[int | None, int | None] = (None, None)
        for i in range(n - 1, -1, -1):
            ev = events[i]
            if ev[0] == "page" and ev[1] > 0:
                nxt = (ev[1], ev[2])
            page_at[i] = nxt
        # Text after the final marker sits on the page following it.
        last = None
        for i, ev in enumerate(events):
            if ev[0] == "page" and ev[1] > 0:
                last = (ev[1], ev[2] + 1)
            if page_at[i] == (None, None) and last:
                page_at[i] = last

    # Phase 3: build records.
    records: list[Record] = []
    cur: Record | None = None
    kitab = kitab_no = bab = bab_no = None
    buf: list[str] = []
    grade_mode = False
    grade_buf: list[str] = []

    def close():
        nonlocal cur, buf, grade_buf, grade_mode
        if cur is not None:
            cur.text = clean_display(MS_RE.sub("", "".join(buf)), openiti=True)
            if grade_buf:
                g = clean_display(MS_RE.sub("", " ".join(grade_buf)), openiti=True)
                g = re.sub(r":\s*\d+\s*-\s*", ": ", g)
                cur.grade_note = g or None
            records.append(cur)
        cur, buf, grade_buf, grade_mode = None, [], [], False

    def start(number: str | None, idx: int):
        nonlocal cur
        close()
        v, p = page_at[idx]
        cur = Record(number=number, volume=v, page=p, kitab=kitab, kitab_number=kitab_no,
                     bab=bab, bab_number=bab_no)

    for i, ev in enumerate(events):
        kind = ev[0]
        if kind == "rec":
            # In "start" style the next text event carries the page; use the
            # page in effect at the record marker which is the same thing.
            start(ev[1], i + 1 if i + 1 < n else i)
            continue
        if kind == "text":
            if cur is not None:
                (grade_buf if grade_mode else buf).append(ev[1])
                v, p = page_at[i]
                if v is not None and ev[1].strip():
                    cur.end_volume, cur.end_page = v, p
                if cur.volume is None and v is not None:
                    cur.volume, cur.page = v, p
            continue
        if kind in ("page", "ipage"):
            continue
        # Header.
        _, level, body = ev
        text = HEADER_TAGS_RE.sub("", _strip_header_text(body))
        norm = text.translate(ARABIC_DIGITS)
        if spec.record_mode == "number_header":
            m = re.fullmatch(r"\(?\s*(\d+)\s*\)?\s*[-–ـ]?\s*", norm)
            if m:
                start(m.group(1), i + 1 if i + 1 < n else i)
                continue
        if cur is not None and len(text) < 60 and any(g in text for g in GRADE_HEADERS):
            grade_mode = True
            label = re.sub(r"[\[\]:]", " ", text).strip()
            grade_buf.append((" ؛ " if grade_buf else "") + label + ": ")
            continue
        m = NUM_HEADER_RE.match(norm)
        num, rest = (m.group(1), m.group(2).strip()) if m and m.group(2) else (None, norm)
        rest_clean = rest.strip(" -–ـ:()")
        if rest_clean.startswith(spec.kitab_prefixes):
            close()
            kitab, kitab_no = clean_display(rest_clean, openiti=True), num
            bab = bab_no = None
            continue
        if rest_clean.startswith(spec.bab_prefixes) or (spec.chapter_prefixes and rest_clean.startswith(spec.chapter_prefixes)):
            close()
            bab, bab_no = clean_display(rest_clean, openiti=True), num
            continue
        if cur is not None and text:
            if spec.headers_in_text:
                (grade_buf if grade_mode else buf).append(" " + text + " ")
            else:
                cur.extra_headers.append(text)
    close()
    return records
