import unittest

from hadith.align import AlignItem, align, match_global
from hadith.build import fmt_number
from hadith.grades import classify, pick
from hadith.normalize import is_arabic, normalize_arabic, normalize_english, stem_arabic_word
from hadith.openiti import FileSpec, parse

SAMPLE = """######OpenITI#
#META# 000.SortField :: x
#META#Header#End#

# PageV01P005
### | كتاب الإيمان
### || باب حب الرسول
### | 1 -
# حدثنا فلان عن فلان قال رسول الله صلى الله عليه وسلم لا يؤمن أحدكم [ص: 6] حتى أكون أحب إليه
### | 2 -
# حدثنا آخر قال إنما الأعمال بالنيات
### | [تعليق المحقق]
# إسناده صحيح
# PageV01P007
### | كتاب الصلاة
### | 3 -
# حدثنا ثالث في الصلاة
"""


class NormalizeTest(unittest.TestCase):
    def test_arabic(self):
        self.assertEqual(normalize_arabic("إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ"), "انما الاعمال بالنيات")
        self.assertEqual(normalize_arabic("الصلاة"), "الصلاه")
        self.assertEqual(normalize_arabic("مصطفى"), "مصطفي")

    def test_urdu_letters_fold(self):
        self.assertEqual(normalize_arabic("روزہ"), normalize_arabic("روزه"))

    def test_stem(self):
        self.assertEqual(stem_arabic_word("والصلاه"), "صلا")
        self.assertEqual(stem_arabic_word("المسلمون"), "مسلم")

    def test_english_and_script(self):
        self.assertEqual(normalize_english("Allah's Messenger (ﷺ) said:"), "allahs messenger said")
        self.assertTrue(is_arabic("قال رسول الله"))
        self.assertFalse(is_arabic("patience"))


class OpenITITest(unittest.TestCase):
    def test_start_style_pages_and_headings(self):
        recs = parse(SAMPLE, FileSpec(page_style="start"))
        self.assertEqual([r.number for r in recs], ["1", "2", "3"])
        r1, r2, r3 = recs
        self.assertEqual((r1.volume, r1.page, r1.end_page), (1, 5, 6))
        self.assertEqual(r1.kitab, "كتاب الإيمان")
        self.assertEqual(r1.bab, "باب حب الرسول")
        self.assertIn("إنما الأعمال بالنيات", r2.text)
        self.assertIn("إسناده صحيح", r2.grade_note)
        self.assertEqual((r3.kitab, r3.bab, r3.page), ("كتاب الصلاة", None, 7))

    def test_end_style_pages(self):
        recs = parse(SAMPLE, FileSpec(page_style="end"))
        self.assertEqual(recs[0].page, 7)
        self.assertEqual(recs[2].page, 8)


class AlignTest(unittest.TestCase):
    TEXTS = ["قال رسول الله انما الاعمال بالنيات وانما لكل امري ما نوي",
             "عن ابي هريرة قال قال رسول الله من كان يومن بالله واليوم الاخر فليقل خيرا او ليصمت",
             "عن انس قال النبي لا يومن احدكم حتي يحب لاخيه ما يحب لنفسه",
             "الطهور شطر الايمان والحمد لله تملا الميزان"]

    def test_align_with_shifted_numbers(self):
        P = [AlignItem(key=i, text=t, number=str(i + 1)) for i, t in enumerate(self.TEXTS)]
        S = [AlignItem(key=j, text=t, number=str(j + 10)) for j, t in enumerate(["مقدمة لا علاقة لها"] + self.TEXTS)]
        m = align(P, S)
        self.assertEqual({i: j for i, (j, _) in m.items()}, {0: 1, 1: 2, 2: 3, 3: 4})

    def test_match_global_one_to_one(self):
        P = [AlignItem(key=i, text=t) for i, t in enumerate(self.TEXTS)]
        S = [AlignItem(key=j, text=t) for j, t in enumerate(reversed(self.TEXTS))]
        m = match_global(P, S)
        self.assertEqual({i: j for i, (j, _) in m.items()}, {0: 3, 1: 2, 2: 1, 3: 0})


class GradesTest(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(classify("Hasan Sahih"), "sahih")
        self.assertEqual(classify("Da'if Jiddan"), "daif")
        self.assertEqual(classify("إسناده ضعيف"), "daif")
        self.assertEqual(classify("صحيح لغيره"), "sahih")
        self.assertEqual(classify("حسن"), "hasan")
        self.assertEqual(classify("Maudu"), "mawdu")

    def test_pick_prefers_albani(self):
        cls, text = pick([{"grader": "Zubair Ali Zai", "grade": "Da'if"}, {"grader": "Al-Albani", "grade": "Sahih"}])
        self.assertEqual(cls, "sahih")
        self.assertIn("Albani", text)


class NumberingTest(unittest.TestCase):
    def test_sub_numbers(self):
        self.assertEqual(fmt_number(8.01), "8a")
        self.assertEqual(fmt_number(402.02), "402b")
        self.assertEqual(fmt_number(7), "7")


if __name__ == "__main__":
    unittest.main()
