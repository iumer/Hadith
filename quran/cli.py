"""Command line interface: ``python -m quran <command>``.

Pipeline:  download -> build (data/corpus/quran) -> index (data/build/quran.db)
``setup`` runs ``index`` (and ``build``/``download`` if the corpus is missing).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ix(args):
    from .search import QuranIndex
    return QuranIndex(args.db)


def _dump(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def _fmt_ayah(a: dict, *, arabic: bool, english: bool, urdu: bool, max_chars: int) -> str:
    head = f"Quran {a.get('surah_en') or a['surah']} {a['ayah']} ({a['surah']}:{a['ayah']})"
    loc = f"  Madani p. {a['page']}, juz {a['juz']}"
    if a.get("sajda"):
        loc += "  [sajda]"
    parts = [head + loc]
    def clip(t: str) -> str:
        if max_chars and len(t) > max_chars:
            return t[: max_chars - 1] + "…"
        return t
    if arabic and a.get("text_ar"):
        parts.append(clip(a["text_ar"]))
    if english and a.get("text_en"):
        parts.append(clip(a["text_en"]))
    if urdu and a.get("text_ur"):
        parts.append(clip(a["text_ur"]))
    return "\n".join(parts)


def _print_hits(args, hits):
    for i, h in enumerate(hits, 1):
        a = h.ayah if hasattr(h, "ayah") else h
        score = getattr(h, "score", None)
        prefix = f"[{i}] "
        if score is not None and getattr(args, "explain", False):
            prefix = f"[{i} score={score:.4f}] "
        if args.format == "markdown":
            print(f"### {prefix}{a.get('citation_long') or a.get('citation')}\n")
            if not args.no_arabic and a.get("text_ar"):
                print(f"> {a['text_ar']}\n")
            if not args.no_english and a.get("text_en"):
                print(a["text_en"] + "\n")
            if args.urdu and a.get("text_ur"):
                print(a["text_ur"] + "\n")
            print(f"*Madani mushaf p. {a['page']}, juz {a['juz']}*\n")
        else:
            print(prefix + _fmt_ayah(
                a, arabic=not args.no_arabic, english=not args.no_english,
                urdu=args.urdu, max_chars=args.max_chars or 0))
            print()


def cmd_download(args):
    from .sources import download_all
    download_all()


def cmd_build(args):
    from .build import build
    build(download=not args.no_download)


def cmd_index(args):
    from .index import DEFAULT_DB, build_index
    build_index(Path(args.db or DEFAULT_DB))


def cmd_setup(args):
    from .index import CORPUS, DEFAULT_DB, build_index
    if not (CORPUS / "index.json").exists():
        from .build import build
        build(download=True)
    db = Path(args.db or DEFAULT_DB)
    if db.exists() and not args.force:
        print(f"{db} already exists (use --force to rebuild)", file=sys.stderr)
        return
    build_index(db)


def cmd_search(args):
    ix = _ix(args)
    surah = None
    if args.surah:
        surah = ix.resolve_surah(args.surah)
        if surah is None:
            sys.exit(f"unknown surah: {args.surah}")
    r = ix.search(" ".join(args.query), language=args.lang, surah=surah, juz=args.juz,
                  page=args.page, limit=args.limit, offset=args.offset, explain=args.explain)
    if args.format == "json":
        return _dump(r.to_dict())
    print(f"# {r.kind}: {r.query!r} — {len(r.hits)} shown of {r.total_candidates or len(r.hits)} candidates\n")
    _print_hits(args, r.hits)


def cmd_get(args):
    ix = _ix(args)
    # Accept "2:255" as a single arg, or surah + ayah.
    if args.ayah is None and ":" in args.surah:
        s, a = args.surah.split(":", 1)
        hit = ix.get(s, int(a))
    elif args.ayah is None:
        sys.exit("usage: get <surah> <ayah>   or   get <surah>:<ayah>")
    else:
        hit = ix.get(args.surah, int(args.ayah))
    if not hit:
        sys.exit("not found")
    if args.format == "json":
        return _dump(hit)
    _print_hits(args, [hit])


def cmd_page(args):
    ix = _ix(args)
    rows = ix.by_page(args.page)
    if args.format == "json":
        return _dump(rows)
    if not rows:
        sys.exit("no ayahs on that page")
    info = ix.page_info(args.page)
    print(f"# Madani page {args.page}  (juz {info['juz'] if info else '?'}, "
          f"{len(rows)} ayahs)\n")
    _print_hits(args, rows)


def cmd_juz(args):
    ix = _ix(args)
    rows = ix.by_juz(args.juz, limit=args.limit, offset=args.offset)
    if args.format == "json":
        return _dump(rows)
    print(f"# Juz {args.juz} — showing {len(rows)}\n")
    _print_hits(args, rows)


def cmd_surah(args):
    ix = _ix(args)
    n = ix.resolve_surah(args.surah)
    if n is None:
        sys.exit(f"unknown surah: {args.surah}")
    meta = ix._surahs[n]
    rows = ix.surah_ayahs(n, limit=args.limit, offset=args.offset)
    if args.format == "json":
        return _dump({"surah": meta, "ayahs": rows})
    print(f"# {meta['name_en']} ({meta['name_ar']}) — {meta['ayah_count']} ayahs, "
          f"pp. {meta['page_start']}–{meta['page_end']}, juz {meta['juz_start']}–{meta['juz_end']}\n")
    _print_hits(args, rows)


def cmd_surahs(args):
    ix = _ix(args)
    rows = ix.surahs()
    if args.format == "json":
        return _dump(rows)
    for s in rows:
        print(f"{s['number']:>3}  {s['name_en']:<18} {s['name_ar']:<14} "
              f"{s['ayah_count']:>3} ayahs  pp. {s['page_start']:>3}–{s['page_end']:<3}  "
              f"juz {s['juz_start']}–{s['juz_end']}  {s['revelation']}")


def cmd_stats(args):
    _dump(_ix(args).stats())


def main(argv=None):
    p = argparse.ArgumentParser(prog="quran", description="Search and cite the Quran (Madani mushaf).")
    p.add_argument("--db", help="path to quran.db (default data/build/quran.db or $QURAN_DB)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def out_opts(sp):
        sp.add_argument("--format", choices=["text", "markdown", "json"], default="text")
        sp.add_argument("--no-arabic", action="store_true")
        sp.add_argument("--no-english", action="store_true")
        sp.add_argument("--urdu", action="store_true", help="also print the Urdu translation")
        sp.add_argument("--max-chars", type=int, default=0, help="truncate quoted texts")

    sub.add_parser("download", help="fetch pinned Arabic + EN/UR editions and mushaf meta").set_defaults(fn=cmd_download)
    sp = sub.add_parser("build", help="merge sources into data/corpus/quran")
    sp.add_argument("--no-download", action="store_true")
    sp.set_defaults(fn=cmd_build)
    sub.add_parser("index", help="build the SQLite search index").set_defaults(fn=cmd_index)
    sp = sub.add_parser("setup", help="create the index if missing")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(fn=cmd_setup)

    sp = sub.add_parser("search", help="keyword / phrase / reference search (English, Arabic, Urdu)")
    sp.add_argument("query", nargs="+")
    sp.add_argument("-n", "--limit", type=int, default=10)
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--surah", help="restrict to a surah (name or number)")
    sp.add_argument("--juz", type=int)
    sp.add_argument("--page", type=int, help="restrict to a Madani mushaf page")
    sp.add_argument("--lang", choices=["auto", "en", "ar", "ur"], default="auto")
    sp.add_argument("--explain", action="store_true")
    out_opts(sp)
    sp.set_defaults(fn=cmd_search)

    sp = sub.add_parser("get", help="fetch one ayah: get 2 255   or   get 2:255")
    sp.add_argument("surah")
    sp.add_argument("ayah", nargs="?")
    out_opts(sp)
    sp.set_defaults(fn=cmd_get)

    sp = sub.add_parser("page", help="ayahs on a Madani mushaf page: page 6")
    sp.add_argument("page", type=int)
    out_opts(sp)
    sp.set_defaults(fn=cmd_page)

    sp = sub.add_parser("juz", help="ayahs in a juz (optionally limited)")
    sp.add_argument("juz", type=int)
    sp.add_argument("-n", "--limit", type=int, default=20)
    sp.add_argument("--offset", type=int, default=0)
    out_opts(sp)
    sp.set_defaults(fn=cmd_juz)

    sp = sub.add_parser("surah", help="read a surah: surah baqarah   or   surah 2")
    sp.add_argument("surah")
    sp.add_argument("-n", "--limit", type=int, default=0, help="0 = all ayahs")
    sp.add_argument("--offset", type=int, default=0)
    out_opts(sp)
    sp.set_defaults(fn=cmd_surah)

    sp = sub.add_parser("surahs", help="list all 114 surahs with page/juz ranges")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(fn=cmd_surahs)

    sub.add_parser("stats", help="index statistics").set_defaults(fn=cmd_stats)

    args = p.parse_args(argv)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        args.fn(args)
    except FileNotFoundError as e:
        sys.exit(str(e))
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
