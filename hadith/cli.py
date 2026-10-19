"""Command line interface: ``python -m hadith <command>``.

Pipeline:  download -> build (data/corpus) -> index (data/build/hadith.db)
``setup`` runs ``index`` (and ``build``/``download`` if the corpus is missing).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import cite


def _ix(args):
    from .search import HadithIndex
    return HadithIndex(args.db)


def _dump(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def _print_hits(args, hits, also=True):
    for i, h in enumerate(hits, 1):
        d = h.hadith if hasattr(h, "hadith") else h
        also_in = getattr(h, "also_in", None) if also else None
        kw = dict(arabic=not args.no_arabic, english=not args.no_english, urdu=args.urdu,
                  max_chars=args.max_chars or None, also_in=also_in)
        if args.format == "markdown":
            print(cite.to_markdown(d, **kw))
        else:
            print(f"[{i}] " + cite.to_text(d, **kw))


def cmd_download(args):
    from .sources import download_all
    download_all()


def cmd_build(args):
    from .build import build
    build(args.collections or None, download=not args.no_download)


def cmd_index(args):
    from .index import DEFAULT_DB, build_index
    build_index(Path(args.db or DEFAULT_DB))


def cmd_setup(args):
    from .index import CORPUS, DEFAULT_DB, build_index
    if not (CORPUS / "collections.json").exists():
        from .build import build
        build(None, download=True)
    db = Path(args.db or DEFAULT_DB)
    if db.exists() and not args.force:
        print(f"{db} already exists (use --force to rebuild)", file=sys.stderr)
        return
    build_index(db)


def cmd_search(args):
    ix = _ix(args)
    cols = None
    if args.collection:
        cols = []
        for c in args.collection:
            slug = ix.resolve_collection(c)
            if not slug:
                sys.exit(f"unknown collection: {c}")
            cols.append(slug)
    r = ix.search(" ".join(args.query), collections=cols, authentic_only=args.authentic,
                  grades=args.grade, language=args.lang, limit=args.limit, offset=args.offset,
                  group=not args.no_group, require_english=args.english_only, explain=args.explain)
    if args.format == "json":
        return _dump(r.to_dict())
    print(f"# {r.kind}: {r.query!r} — {len(r.hits)} shown of {r.total_candidates or len(r.hits)} candidates\n")
    _print_hits(args, r.hits)


def _resolve(ix, name):
    slug = ix.resolve_collection(name)
    if not slug:
        sys.exit(f"unknown collection: {name}  (see `python -m hadith collections`)")
    return slug


def cmd_get(args):
    ix = _ix(args)
    h = ix.get(_resolve(ix, args.collection), args.number)
    if not h:
        sys.exit("not found")
    if args.format == "json":
        return _dump(h)
    _print_hits(args, [h])


def cmd_page(args):
    ix = _ix(args)
    rows = ix.by_page(_resolve(ix, args.collection), args.volume, args.page)
    if args.format == "json":
        return _dump(rows)
    if not rows:
        sys.exit("no hadith recorded on that page")
    _print_hits(args, rows)


def cmd_collections(args):
    ix = _ix(args)
    cols = ix.collections()
    if args.format == "json":
        return _dump(cols)
    for c in cols:
        print(f"{c['slug']:<16} {c['name_en']:<34} {c['name_ar']:<22} {c['hadith_count']:>6} hadith  "
              f"vols={c['volumes'] or '-':<3} en={c['with_english']:<6} graded={c['with_grade']}")


def cmd_books(args):
    ix = _ix(args)
    rows = ix.books(_resolve(ix, args.collection))
    if args.format == "json":
        return _dump(rows)
    for b in rows:
        pages = ""
        if b["page_start"]:
            pages = f"vol. {b['volume_start']} p. {b['page_start']} – vol. {b['volume_end']} p. {b['page_end']}"
        print(f"{b['number']:>4}  {(b['name_en'] or ''):<48} {(b['name_ar'] or ''):<30} "
              f"{b['hadith_count']:>5} hadith  #{b['first']}–{b['last']}  {pages}")


def cmd_chapters(args):
    ix = _ix(args)
    rows = ix.chapters(_resolve(ix, args.collection), args.book)
    if args.format == "json":
        return _dump(rows)
    for c in rows:
        loc = f"vol. {c['volume']} p. {c['page']}" if c["page"] else ""
        name = c["name_en"] or c["name_ar"] or ""
        if c["name_en"] and c["name_ar"]:
            name = f"{c['name_en']} | {c['name_ar']}"
        print(f"{c['book_number']:>4}.{c['number'] or '-':<6} {name[:110]:<110} {c['hadith_count']:>4}  #{c['first']}  {loc}")


def cmd_book(args):
    ix = _ix(args)
    rows = ix.book_hadiths(_resolve(ix, args.collection), args.book, args.limit, args.offset)
    if args.format == "json":
        return _dump(rows)
    _print_hits(args, rows)


def cmd_stats(args):
    _dump(_ix(args).stats())


def cmd_serve(args):
    from .server import serve
    serve(args.db, args.host, args.port)


def main(argv=None):
    p = argparse.ArgumentParser(prog="hadith", description="Search and cite the major hadith collections.")
    p.add_argument("--db", help="path to hadith.db (default data/build/hadith.db or $HADITH_DB)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def out_opts(sp):
        sp.add_argument("--format", choices=["text", "markdown", "json"], default="text")
        sp.add_argument("--no-arabic", action="store_true")
        sp.add_argument("--no-english", action="store_true")
        sp.add_argument("--urdu", action="store_true", help="also print the Urdu translation")
        sp.add_argument("--max-chars", type=int, default=0, help="truncate quoted texts")

    sub.add_parser("download", help="fetch raw sources (pinned revisions)").set_defaults(fn=cmd_download)
    sp = sub.add_parser("build", help="parse/align sources into data/corpus")
    sp.add_argument("collections", nargs="*")
    sp.add_argument("--no-download", action="store_true")
    sp.set_defaults(fn=cmd_build)
    sub.add_parser("index", help="build the SQLite search index").set_defaults(fn=cmd_index)
    sp = sub.add_parser("setup", help="create the index if missing")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(fn=cmd_setup)

    sp = sub.add_parser("search", help="topic / keyword / reference search (English, Arabic, Urdu)")
    sp.add_argument("query", nargs="+")
    sp.add_argument("-c", "--collection", action="append", help="restrict to collection (repeatable)")
    sp.add_argument("-n", "--limit", type=int, default=5)
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--authentic", action="store_true", help="only sahih/hasan")
    sp.add_argument("--grade", action="append", choices=["sahih", "hasan", "daif", "mawdu"])
    sp.add_argument("--lang", choices=["auto", "en", "ar", "ur"], default="auto")
    sp.add_argument("--english-only", action="store_true", help="only hadith that have an English translation")
    sp.add_argument("--no-group", action="store_true", help="do not fold parallel narrations")
    sp.add_argument("--explain", action="store_true")
    out_opts(sp)
    sp.set_defaults(fn=cmd_search)

    sp = sub.add_parser("get", help="fetch one hadith: get bukhari 1")
    sp.add_argument("collection")
    sp.add_argument("number")
    out_opts(sp)
    sp.set_defaults(fn=cmd_get)

    sp = sub.add_parser("page", help="hadith on a printed page: page bukhari 1 6")
    sp.add_argument("collection")
    sp.add_argument("volume", type=int)
    sp.add_argument("page", type=int)
    out_opts(sp)
    sp.set_defaults(fn=cmd_page)

    sp = sub.add_parser("collections", help="list collections")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(fn=cmd_collections)
    sp = sub.add_parser("books", help="list the books (kitabs) of a collection")
    sp.add_argument("collection")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(fn=cmd_books)
    sp = sub.add_parser("chapters", help="list chapters (babs) of a collection or one book")
    sp.add_argument("collection")
    sp.add_argument("book", nargs="?")
    sp.add_argument("--format", choices=["text", "json"], default="text")
    sp.set_defaults(fn=cmd_chapters)
    sp = sub.add_parser("book", help="read the hadith of one book")
    sp.add_argument("collection")
    sp.add_argument("book")
    sp.add_argument("-n", "--limit", type=int, default=20)
    sp.add_argument("--offset", type=int, default=0)
    out_opts(sp)
    sp.set_defaults(fn=cmd_book)
    sub.add_parser("stats", help="index statistics").set_defaults(fn=cmd_stats)
    sp = sub.add_parser("serve", help="JSON HTTP API")
    sp.add_argument("--host", default="127.0.0.1")
    sp.add_argument("--port", type=int, default=8765)
    sp.set_defaults(fn=cmd_serve)

    args = p.parse_args(argv)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        args.fn(args)
    except FileNotFoundError as e:
        sys.exit(str(e))
    except BrokenPipeError:
        pass
