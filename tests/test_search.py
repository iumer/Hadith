"""End-to-end tests against the built index (skipped when data/build/hadith.db is absent)."""
import unittest

from hadith.cite import page_ref, short_citation, to_markdown
from hadith.index import DEFAULT_DB

from .relevance_cases import CASES

HAVE_DB = DEFAULT_DB.exists()


@unittest.skipUnless(HAVE_DB, "run `python -m hadith setup` first")
class SearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from hadith.search import HadithIndex
        cls.ix = HadithIndex()

    def test_reference_lookup(self):
        for q, uid in [("bukhari 1", "bukhari:1"), ("Sahih Muslim 8", "muslim:8a"), ("abu dawud #4031", "abudawud:4031"),
                       ("صحيح البخاري 1", "bukhari:1"), ("riyad as-salihin 1", "riyadussalihin:1"),
                       ("muslim intro-1", "muslim:intro-1")]:
            r = self.ix.search(q)
            self.assertEqual(r.kind, "reference", q)
            self.assertEqual(r.hits[0].hadith["uid"], uid, q)

    def test_page_lookup(self):
        r = self.ix.search("bukhari vol 1 page 6")
        self.assertEqual(r.kind, "page")
        self.assertEqual([h.hadith["number"] for h in r.hits][:2], ["1", "2"])
        self.assertEqual(self.ix.by_page("muslim", 1, 37)[0]["number"], "8a")

    def test_reference_fields(self):
        h = self.ix.get("bukhari", "1")
        self.assertEqual((h["volume"], h["page"]), (1, 6))
        self.assertEqual(h["book_en"], "Revelation")
        self.assertTrue(h["chapter_en"] and h["chapter_ar"] and h["text_ar"] and h["text_en"])
        self.assertEqual(h["grade"], "sahih")

    def test_books_and_chapters(self):
        books = self.ix.books("bukhari")
        self.assertEqual(len(books), 97)
        self.assertEqual(books[0]["name_en"], "Revelation")
        self.assertTrue(all(b["number"] != "0" for b in books))
        self.assertGreater(len(self.ix.chapters("bukhari", "2")), 30)
        self.assertEqual(len(self.ix.collections()), 20)

    def test_filters(self):
        r = self.ix.search("fasting", authentic_only=True, limit=20)
        self.assertTrue(all(h.hadith["grade"] in ("sahih", "hasan") for h in r.hits))
        r = self.ix.search("fasting", collections=["abudawud"], limit=10)
        self.assertTrue(r.hits and all(h.hadith["collection"] == "abudawud" for h in r.hits))

    def test_relevance(self):
        hits = 0
        misses = []
        for q, expected in CASES:
            r = self.ix.search(q, limit=5)
            got = {h.hadith["uid"] for h in r.hits} | {a["uid"] for h in r.hits for a in h.also_in}
            ok = bool(r.hits) if expected is None else bool(got & expected)
            hits += ok
            if not ok:
                misses.append(q)
        self.assertGreaterEqual(hits / len(CASES), 0.85, f"misses: {misses}")

    def test_bad_input_is_safe(self):
        for q in ['"', "AND OR NOT", "*", "()", "", "   ", "NEAR(a b)"]:
            self.ix.search(q)

    def test_citation(self):
        h = self.ix.get("muslim", "8a")
        self.assertEqual(page_ref(h), "vol. 1, pp. 36-38")
        self.assertTrue(short_citation(h).startswith("Sahih Muslim 8a"))
        md = to_markdown(h)
        self.assertIn("The Book of Faith", md)
        self.assertIn("Chapter", md)


if __name__ == "__main__":
    unittest.main()
