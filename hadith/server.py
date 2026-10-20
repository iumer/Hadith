"""Minimal JSON HTTP API (stdlib only) - a backend for a web/mobile/desktop front-end.

GET /api/search?q=...&collection=bukhari&collection=muslim&authentic=1&grade=sahih&limit=10&offset=0&lang=auto&group=1&semantic=1
GET /api/hadith/<collection>/<number>
GET /api/uid/<collection:number>
GET /api/page/<collection>/<volume>/<page>
GET /api/collections
GET /api/collections/<collection>/books
GET /api/collections/<collection>/chapters[?book=N]
GET /api/collections/<collection>/books/<book>?limit=50&offset=0
GET /api/stats
"""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from .cite import short_citation
from .search import HadithIndex


def _with_citation(h: dict | None) -> dict | None:
    if h is not None:
        h = dict(h)
        h["citation"] = short_citation(h)
    return h


def make_handler(ix: HadithIndex):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *a):
            sys.stderr.write("[api] " + fmt % a + "\n")

        def _send(self, code: int, obj) -> None:
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _col(self, name: str) -> str:
            slug = ix.resolve_collection(unquote(name))
            if not slug:
                raise LookupError(f"unknown collection {name!r}")
            return slug

        def do_GET(self):  # noqa: N802
            u = urlparse(self.path)
            qs = parse_qs(u.query)
            one = lambda k, d=None: qs.get(k, [d])[0]  # noqa: E731
            parts = [unquote(p) for p in u.path.strip("/").split("/") if p]
            try:
                if parts[:2] == ["api", "search"]:
                    q = one("q", "")
                    cols = [self._col(c) for c in qs.get("collection", [])] or None
                    r = ix.search(q, collections=cols, authentic_only=one("authentic") in ("1", "true"),
                                  grades=qs.get("grade"), language=one("lang", "auto"),
                                  limit=min(int(one("limit", 10)), 100), offset=int(one("offset", 0)),
                                  group=one("group", "1") not in ("0", "false"),
                                  require_english=one("english") in ("1", "true"),
                                  explain=one("explain") in ("1", "true"),
                                  semantic=False if one("semantic") in ("0", "false") else None)
                    d = r.to_dict()
                    for h in d["hits"]:
                        h["citation"] = short_citation(h)
                    return self._send(200, d)
                if parts[:2] == ["api", "hadith"] and len(parts) == 4:
                    h = ix.get(self._col(parts[2]), parts[3])
                    return self._send(200 if h else 404, _with_citation(h) or {"error": "not found"})
                if parts[:2] == ["api", "uid"] and len(parts) == 3:
                    h = ix.get_uid(parts[2])
                    return self._send(200 if h else 404, _with_citation(h) or {"error": "not found"})
                if parts[:2] == ["api", "page"] and len(parts) == 5:
                    rows = ix.by_page(self._col(parts[2]), int(parts[3]), int(parts[4]))
                    return self._send(200, [_with_citation(h) for h in rows])
                if parts == ["api", "collections"]:
                    return self._send(200, ix.collections())
                if parts[:2] == ["api", "collections"] and len(parts) >= 4:
                    slug = self._col(parts[2])
                    if parts[3] == "books" and len(parts) == 4:
                        return self._send(200, ix.books(slug))
                    if parts[3] == "books" and len(parts) == 5:
                        rows = ix.book_hadiths(slug, parts[4], min(int(one("limit", 50)), 500), int(one("offset", 0)))
                        return self._send(200, [_with_citation(h) for h in rows])
                    if parts[3] == "chapters":
                        return self._send(200, ix.chapters(slug, one("book")))
                if parts == ["api", "stats"]:
                    return self._send(200, ix.stats())
                return self._send(404, {"error": "unknown endpoint", "doc": __doc__})
            except LookupError as e:
                return self._send(404, {"error": str(e)})
            except ValueError as e:
                return self._send(400, {"error": str(e)})

    return Handler


def serve(db=None, host: str = "127.0.0.1", port: int = 8765, semantic: bool | None = None) -> None:
    ix = HadithIndex(db, semantic=semantic)
    srv = ThreadingHTTPServer((host, port), make_handler(ix))
    print(f"hadith API on http://{host}:{port}/api/search?q=patience", file=sys.stderr)
    srv.serve_forever()
