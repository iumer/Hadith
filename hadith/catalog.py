"""Catalogue of the hadith collections indexed by this project.

Every collection lists where its data comes from:

* ``fawaz``      – fawazahmed0/hadith-api (Arabic / English / Urdu, grades, standard numbering)
* ``hadithjson`` – AhmedBaset/hadith-json (Arabic / English scraped from sunnah.com)
* ``lk``         – LK Hadith Corpus (Leeds & King Saud Univ.; kitab + bab headings, isnad/matn split)
* ``openiti``    – OpenITI corpus: digitised printed Arabic editions with volume/page markers

``authenticity`` values:

* ``sahih``     – every musnad hadith in the book is accepted as authentic by scholarly consensus
* ``mostly``    – the author intended to collect only authentic hadith, but later critics graded some weaker
* ``graded``    – contains sahih, hasan and da'if material; rely on the per-hadith grades
* ``selection`` – an anthology drawn from the above; per-hadith grades/attributions given where known
"""
from __future__ import annotations

from dataclasses import dataclass, field

OPENITI_RAW = "https://raw.githubusercontent.com/OpenITI/{repo}/{commit}/data/{path}"
OPENITI_COMMITS = {
    "0200AH": "599f22fe249871f602efe2e0ddc801d3742960a3",
    "0250AH": "0cc00c0646c81988c75a3815fe6d9a5fa65ce592",
    "0275AH": "44e1c36738a2bf5c14dafa232a6ae1891e6171cd",
    "0300AH": "01a1544130e0236850ef2698923ad01575c5bd7c",
    "0325AH": "089e665b4958e0f145a46941987fb81cf3dda1b8",
    "0425AH": "3a3c829e55a1e4fb614aa857e0d85f51d6a9f0ee",
    "0750AH": "7c9c84d9f98581470aa2b7f8bee00ae285c5c707",
    "0700AH": "3d8ff4e7b035aaa4ca5dda52c7322645f3401dcf",
    "0875AH": "5835c183b8bbf4ea454d5c1be2b168b669403771",
}
FAWAZ_COMMIT = "df57907be35291c91ad6a6691180e22ca9920784"
FAWAZ_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@" + FAWAZ_COMMIT + "/editions/{edition}.json"
FAWAZ_INFO_URL = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@" + FAWAZ_COMMIT + "/info.json"
HADITHJSON_COMMIT = "70b83d6d21995bb32f8d7271cd75501be5a922a7"
HADITHJSON_URL = "https://raw.githubusercontent.com/AhmedBaset/hadith-json/" + HADITHJSON_COMMIT + "/db/by_book/{path}"
LK_COMMIT = "c45fa64aa40bf1d4a34b9b35359640a583b02881"
LK_REPO = "https://github.com/ShathaTm/LK-Hadith-Corpus.git"


@dataclass
class OpenITISource:
    repo: str
    path: str                     # path below data/
    edition: str                  # human description of the printed edition
    volumes: int | None
    page_style: str = "start"
    record_mode: str = "number_header"
    kitab_prefixes: tuple[str, ...] = ("كتاب", "أبواب", "ابواب", "من كتاب", "ومن كتاب")
    bab_prefixes: tuple[str, ...] = ("باب",)
    chapter_prefixes: tuple[str, ...] = ()
    grade_source: str | None = None   # who wrote the grading notes embedded in this edition
    skip_until: str | None = None
    # Regex whose group(1) is a grade written at the start of each record's text.
    text_grade_regex: str | None = None
    headers_in_text: bool = False

    def spec(self):
        from .openiti import FileSpec
        return FileSpec(page_style=self.page_style, record_mode=self.record_mode,
                        kitab_prefixes=self.kitab_prefixes, bab_prefixes=self.bab_prefixes,
                        chapter_prefixes=self.chapter_prefixes, skip_until=self.skip_until,
                        headers_in_text=self.headers_in_text)

    @property
    def url(self) -> str:
        return OPENITI_RAW.format(repo=self.repo, commit=OPENITI_COMMITS[self.repo], path=self.path)

    @property
    def filename(self) -> str:
        return self.path.rsplit("/", 1)[-1]


@dataclass
class Collection:
    slug: str
    name_en: str
    name_ar: str
    author_en: str
    author_ar: str
    died_ah: int | None
    authenticity: str
    description: str
    primary: str                        # "fawaz" | "hadithjson" | "openiti"
    group: str                          # "kutub_sittah" | "major" | "sahih_extra" | "anthology"
    fawaz: str | None = None            # fawaz collection id
    fawaz_languages: tuple[str, ...] = ("ara", "eng")
    hadithjson: str | None = None       # path below db/by_book/
    lk: str | None = None               # LK folder name
    openiti: OpenITISource | None = None
    sunnah_slug: str | None = None      # sunnah.com URL slug
    aliases: tuple[str, ...] = field(default_factory=tuple)


COLLECTIONS: list[Collection] = [
    Collection(
        slug="bukhari", name_en="Sahih al-Bukhari", name_ar="صحيح البخاري",
        author_en="Muhammad ibn Isma'il al-Bukhari", author_ar="محمد بن إسماعيل البخاري", died_ah=256,
        authenticity="sahih", group="kutub_sittah", primary="fawaz",
        description="Al-Jami' al-Musnad al-Sahih. Regarded as the most authentic book after the Qur'an.",
        fawaz="bukhari", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/bukhari.json", lk="Bukhari", sunnah_slug="bukhari",
        aliases=("bukhari", "sahih bukhari", "al-bukhari", "البخاري"),
        openiti=OpenITISource(
            repo="0275AH", path="0256Bukhari/0256Bukhari.Sahih/0256Bukhari.Sahih.Shamela0001681-ara1",
            edition="Dar Tawq al-Najat, 1422 AH, ed. Muhammad Zuhayr al-Nasir (Sultaniyya print, Fu'ad 'Abd al-Baqi numbering), 9 vols",
            volumes=9, page_style="start"),
    ),
    Collection(
        slug="muslim", name_en="Sahih Muslim", name_ar="صحيح مسلم",
        author_en="Muslim ibn al-Hajjaj al-Naysaburi", author_ar="مسلم بن الحجاج النيسابوري", died_ah=261,
        authenticity="sahih", group="kutub_sittah", primary="fawaz",
        description="Al-Musnad al-Sahih. Second in rank after al-Bukhari; famous for gathering all chains of a hadith in one place.",
        fawaz="muslim", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/muslim.json", lk="Muslim", sunnah_slug="muslim",
        aliases=("muslim", "sahih muslim", "مسلم"),
        openiti=OpenITISource(
            repo="0275AH", path="0261Muslim/0261Muslim.Sahih/0261Muslim.Sahih.Shamela0001727-ara1.mARkdown",
            edition="Dar Ihya' al-Turath al-'Arabi, Beirut, ed. Muhammad Fu'ad 'Abd al-Baqi, 5 vols",
            volumes=5, page_style="end", record_mode="dollar"),
    ),
    Collection(
        slug="abudawud", name_en="Sunan Abi Dawud", name_ar="سنن أبي داود",
        author_en="Abu Dawud Sulayman ibn al-Ash'ath al-Sijistani", author_ar="أبو داود سليمان بن الأشعث السجستاني", died_ah=275,
        authenticity="graded", group="kutub_sittah", primary="fawaz",
        description="One of the four Sunan; focuses on legal (fiqh) hadith. Abu Dawud noted serious weaknesses he knew of.",
        fawaz="abudawud", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/abudawud.json", lk="AbuDaud", sunnah_slug="abudawud",
        aliases=("abu dawud", "abi dawud", "abu daud", "sunan abi dawud", "أبي داود", "ابو داود"),
        openiti=OpenITISource(
            repo="0275AH", path="0275AbuDawudSijistani/0275AbuDawudSijistani.Sunan/0275AbuDawudSijistani.Sunan.Shamela0001726-ara1",
            edition="al-Maktaba al-'Asriyya, Sidon-Beirut, ed. Muhammad Muhyi al-Din 'Abd al-Hamid, 4 vols",
            volumes=4, page_style="start"),
    ),
    Collection(
        slug="tirmidhi", name_en="Jami' at-Tirmidhi", name_ar="جامع الترمذي",
        author_en="Abu 'Isa Muhammad ibn 'Isa al-Tirmidhi", author_ar="أبو عيسى محمد بن عيسى الترمذي", died_ah=279,
        authenticity="graded", group="kutub_sittah", primary="fawaz",
        description="Al-Jami' al-Kabir; al-Tirmidhi grades many hadith himself (sahih, hasan, gharib) and records juristic opinions.",
        fawaz="tirmidhi", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/tirmidhi.json", lk="Tirmizi", sunnah_slug="tirmidhi",
        aliases=("tirmidhi", "tirmizi", "jami tirmidhi", "sunan tirmidhi", "الترمذي"),
        openiti=OpenITISource(
            repo="0300AH", path="0279Tirmidhi/0279Tirmidhi.Sunan/0279Tirmidhi.Sunan.JK000140-ara1.completed",
            edition="Dar Ihya' al-Turath al-'Arabi, Beirut, ed. Ahmad Muhammad Shakir et al., 5 vols",
            volumes=5, page_style="end"),
    ),
    Collection(
        slug="nasai", name_en="Sunan an-Nasa'i", name_ar="سنن النسائي",
        author_en="Ahmad ibn Shu'ayb al-Nasa'i", author_ar="أحمد بن شعيب النسائي", died_ah=303,
        authenticity="graded", group="kutub_sittah", primary="fawaz",
        description="Al-Mujtaba (al-Sunan al-Sughra); considered the Sunan with the fewest weak narrations.",
        fawaz="nasai", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/nasai.json", lk="Nesai", sunnah_slug="nasai",
        aliases=("nasai", "nasa'i", "an-nasai", "sunan nasai", "النسائي"),
        openiti=OpenITISource(
            repo="0325AH", path="0303Nasai/0303Nasai.SunanSughra/0303Nasai.SunanSughra.Shamela0000829-ara1",
            edition="Maktab al-Matbu'at al-Islamiyya, Aleppo, ed. 'Abd al-Fattah Abu Ghudda, 8 vols (+ index)",
            volumes=8, page_style="start"),
    ),
    Collection(
        slug="ibnmajah", name_en="Sunan Ibn Majah", name_ar="سنن ابن ماجه",
        author_en="Muhammad ibn Yazid Ibn Majah al-Qazwini", author_ar="محمد بن يزيد ابن ماجه القزويني", died_ah=273,
        authenticity="graded", group="kutub_sittah", primary="fawaz",
        description="Sixth of the canonical six; contains a notable number of weak narrations, so check grades.",
        fawaz="ibnmajah", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/ibnmajah.json", lk="IbnMaja", sunnah_slug="ibnmajah",
        aliases=("ibn majah", "ibn maja", "sunan ibn majah", "ابن ماجه", "ابن ماجة"),
        openiti=OpenITISource(
            repo="0275AH", path="0273IbnMaja/0273IbnMaja.Sunan/0273IbnMaja.Sunan.Shamela0001198-ara1",
            edition="Dar Ihya' al-Kutub al-'Arabiyya (Faysal 'Isa al-Babi al-Halabi), ed. Muhammad Fu'ad 'Abd al-Baqi, 2 vols",
            volumes=2, page_style="start"),
    ),
    Collection(
        slug="malik", name_en="Muwatta Malik", name_ar="موطأ مالك",
        author_en="Malik ibn Anas", author_ar="مالك بن أنس", died_ah=179,
        authenticity="mostly", group="major", primary="fawaz",
        description="Riwaya of Yahya ibn Yahya al-Laythi. The earliest surviving major hadith-and-fiqh compilation; includes mursal reports and Companions' sayings.",
        fawaz="malik", fawaz_languages=("ara", "eng", "urd"),
        hadithjson="the_9_books/malik.json", sunnah_slug="malik",
        aliases=("muwatta", "muwatta malik", "malik", "الموطأ", "موطأ"),
        openiti=OpenITISource(
            repo="0200AH", path="0179MalikIbnAnas/0179MalikIbnAnas.Muwatta/0179MalikIbnAnas.Muwatta.Shamela0001699-ara1.completed",
            edition="Dar Ihya' al-Turath al-'Arabi, Beirut, ed. Muhammad Fu'ad 'Abd al-Baqi, 2 vols",
            volumes=2, page_style="start", record_mode="number_para"),
    ),
    Collection(
        slug="ahmad", name_en="Musnad Ahmad", name_ar="مسند أحمد",
        author_en="Ahmad ibn Hanbal", author_ar="أحمد بن حنبل", died_ah=241,
        authenticity="graded", group="major", primary="openiti",
        description="The largest of the early musnads (~27,600 hadith arranged by Companion). Full Arabic text; English where sunnah.com has it.",
        hadithjson="the_9_books/ahmed.json", sunnah_slug="ahmad",
        aliases=("musnad ahmad", "ahmad", "musnad", "مسند أحمد", "احمد"),
        openiti=OpenITISource(
            repo="0250AH", path="0241IbnHanbal/0241IbnHanbal.Musnad/0241IbnHanbal.Musnad.Shamela0013157-ara1",
            edition="Mu'assasat al-Risala, ed. Shu'ayb al-Arna'ut, 'Adil Murshid et al., 45 vols",
            volumes=45, page_style="start",
            kitab_prefixes=("مسند", "أول مسند", "بقية مسند", "تمام مسند", "ومن مسند", "من مسند"),
            bab_prefixes=("حديث", "ومن حديث", "بقية حديث", "تمام حديث", "زيادة", "ومما")),
    ),
    Collection(
        slug="darimi", name_en="Sunan ad-Darimi", name_ar="سنن الدارمي",
        author_en="'Abd Allah ibn 'Abd al-Rahman al-Darimi", author_ar="عبد الله بن عبد الرحمن الدارمي", died_ah=255,
        authenticity="graded", group="major", primary="openiti",
        description="Musnad al-Darimi, often counted among the nine books. Arabic with the editor's (Husayn Salim Asad) grade on each hadith.",
        sunnah_slug="darimi",
        aliases=("darimi", "sunan darimi", "الدارمي"),
        openiti=OpenITISource(
            repo="0275AH", path="0255CabdAllahDarimi/0255CabdAllahDarimi.Sunan/0255CabdAllahDarimi.Sunan.Shamela0021795-ara3",
            edition="Dar al-Mughni, Riyadh, ed. Husayn Salim Asad al-Darani, 4 vols",
            volumes=4, page_style="start", grade_source="Husayn Salim Asad"),
    ),
    Collection(
        slug="ibnkhuzaymah", name_en="Sahih Ibn Khuzaymah", name_ar="صحيح ابن خزيمة",
        author_en="Muhammad ibn Ishaq Ibn Khuzaymah", author_ar="محمد بن إسحاق ابن خزيمة", died_ah=311,
        authenticity="mostly", group="sahih_extra", primary="openiti",
        description="One of the works restricted to authentic hadith after the two Sahihs (only the first part survives). Arabic only.",
        aliases=("ibn khuzaymah", "ibn khuzaima", "sahih ibn khuzaymah", "ابن خزيمة"),
        openiti=OpenITISource(
            repo="0325AH", path="0311IbnKhuzaymaNaysaburi/0311IbnKhuzaymaNaysaburi.Sahih/0311IbnKhuzaymaNaysaburi.Sahih.Shamela0001446-ara1",
            edition="al-Maktab al-Islami, Beirut, ed. Muhammad Mustafa al-A'zami, 4 vols",
            volumes=4, page_style="start", grade_source="al-A'zami / al-Albani"),
    ),
    Collection(
        slug="ibnhibban", name_en="Sahih Ibn Hibban", name_ar="صحيح ابن حبان",
        author_en="Muhammad ibn Hibban al-Busti", author_ar="محمد بن حبان البستي", died_ah=354,
        authenticity="mostly", group="sahih_extra", primary="openiti",
        description="Al-Ihsan fi Taqrib Sahih Ibn Hibban (arr. Ibn Balban). Arabic, with al-Arna'ut's and al-Albani's grades.",
        aliases=("ibn hibban", "sahih ibn hibban", "ابن حبان"),
        openiti=OpenITISource(
            repo="0750AH", path="0739CalaDinIbnBalban/0739CalaDinIbnBalban.Ihsan/0739CalaDinIbnBalban.Ihsan.Sham19Y0001734-ara1",
            edition="Mu'assasat al-Risala, Beirut, 2nd ed. 1414/1993, ed. Shu'ayb al-Arna'ut, 18 vols",
            volumes=18, page_style="end", record_mode="number_inline", grade_source="Shu'ayb al-Arna'ut / al-Albani",
            skip_until="### | CHECK المقدمة",
            kitab_prefixes=("كتاب",), bab_prefixes=("باب", "ذكر", "AUTO ذكر")),
    ),
    Collection(
        slug="mustadrak", name_en="Al-Mustadrak 'ala al-Sahihayn", name_ar="المستدرك على الصحيحين",
        author_en="Al-Hakim al-Naysaburi", author_ar="الحاكم النيسابوري", died_ah=405,
        authenticity="graded", group="sahih_extra", primary="openiti",
        description="Hadith al-Hakim judged to meet the conditions of al-Bukhari and/or Muslim; many gradings were revised by al-Dhahabi (Talkhis). Arabic only.",
        aliases=("mustadrak", "hakim", "al-hakim", "المستدرك", "الحاكم"),
        openiti=OpenITISource(
            repo="0425AH", path="0405HakimNaysaburi/0405HakimNaysaburi.Mustadrak/0405HakimNaysaburi.Mustadrak.Shamela0002266-ara1",
            edition="Dar al-Kutub al-'Ilmiyya, Beirut, ed. Mustafa 'Abd al-Qadir 'Ata, 4 vols",
            volumes=4, page_style="start", grade_source="al-Dhahabi (Talkhis)"),
    ),
    Collection(
        slug="riyadussalihin", name_en="Riyad as-Salihin", name_ar="رياض الصالحين",
        author_en="Yahya ibn Sharaf al-Nawawi", author_ar="يحيى بن شرف النووي", died_ah=676,
        authenticity="selection", group="anthology", primary="openiti",
        description="Al-Nawawi's thematic anthology of hadith on character, worship and manners, drawn mostly from the Sahihs and Sunan.",
        hadithjson="other_books/riyad_assalihin.json", sunnah_slug="riyadussalihin",
        aliases=("riyad", "riyadh", "riyad as salihin", "riyadh us saliheen", "رياض الصالحين"),
        openiti=OpenITISource(
            repo="0700AH", path="0676Nawawi/0676Nawawi.RiyadSalihin/0676Nawawi.RiyadSalihin.Shamela0002348-ara5",
            edition="Dar Ibn Kathir, Damascus-Beirut, 1428/2007, ed. Mahir Yasin al-Fahl, 1 vol",
            volumes=1, page_style="start"),
    ),
    Collection(
        slug="bulugh", name_en="Bulugh al-Maram", name_ar="بلوغ المرام",
        author_en="Ibn Hajar al-'Asqalani", author_ar="ابن حجر العسقلاني", died_ah=852,
        authenticity="selection", group="anthology", primary="openiti",
        description="Ibn Hajar's compendium of legal (ahkam) hadith with source attributions and many gradings.",
        hadithjson="other_books/bulugh_almaram.json", sunnah_slug="bulugh",
        aliases=("bulugh", "bulugh al maram", "بلوغ المرام"),
        openiti=OpenITISource(
            repo="0875AH", path="0852IbnHajarCasqalani/0852IbnHajarCasqalani.BulughMaram/0852IbnHajarCasqalani.BulughMaram.Shamela0009111-ara1",
            edition="Dar al-Falaq, Riyadh, 7th ed. 1424 AH, ed. Samir ibn Amin al-Zuhayri, 1 vol",
            volumes=1, page_style="start", headers_in_text=True),
    ),
    Collection(
        slug="adab", name_en="Al-Adab Al-Mufrad", name_ar="الأدب المفرد",
        author_en="Muhammad ibn Isma'il al-Bukhari", author_ar="محمد بن إسماعيل البخاري", died_ah=256,
        authenticity="graded", group="anthology", primary="openiti",
        description="Al-Bukhari's book on manners and character; not part of his Sahih. Al-Albani's grades included.",
        hadithjson="other_books/aladab_almufrad.json", sunnah_slug="adab",
        aliases=("adab al mufrad", "al-adab al-mufrad", "الأدب المفرد"),
        openiti=OpenITISource(
            repo="0275AH", path="0256Bukhari/0256Bukhari.AdabMufrad/0256Bukhari.AdabMufrad.Shamela0012991-ara1",
            edition="Dar al-Basha'ir al-Islamiyya, Beirut, ed. Muhammad Fu'ad 'Abd al-Baqi (with al-Albani's grades), 1 vol",
            volumes=1, page_style="start", grade_source="al-Albani"),
    ),
    Collection(
        slug="shamail", name_en="Shama'il Muhammadiyah", name_ar="الشمائل المحمدية",
        author_en="Abu 'Isa Muhammad ibn 'Isa al-Tirmidhi", author_ar="أبو عيسى محمد بن عيسى الترمذي", died_ah=279,
        authenticity="graded", group="anthology", primary="openiti",
        description="Al-Tirmidhi's collection on the Prophet's appearance, character and daily life.",
        hadithjson="other_books/shamail_muhammadiyah.json", sunnah_slug="shamail",
        aliases=("shamail", "shama'il", "الشمائل"),
        openiti=OpenITISource(
            repo="0300AH", path="0279Tirmidhi/0279Tirmidhi.ShamailMuhammadiyya/0279Tirmidhi.ShamailMuhammadiyya.Shamela0013037-ara1",
            edition="al-Maktaba al-Tijariyya, Makka, ed. Sayyid ibn 'Abbas al-Julaymi, 1 vol",
            volumes=1, page_style="start"),
    ),
    Collection(
        slug="mishkat", name_en="Mishkat al-Masabih", name_ar="مشكاة المصابيح",
        author_en="Al-Khatib al-Tabrizi", author_ar="الخطيب التبريزي", died_ah=741,
        authenticity="selection", group="anthology", primary="openiti",
        description="Al-Tabrizi's expansion of al-Baghawi's Masabih al-Sunna, citing the source collection for each hadith.",
        hadithjson="other_books/mishkat_almasabih.json", sunnah_slug="mishkat",
        aliases=("mishkat", "mishkat al masabih", "مشكاة المصابيح"),
        openiti=OpenITISource(
            repo="0750AH", path="0741KhatibTabrizi/0741KhatibTabrizi.MishkatMasabih/0741KhatibTabrizi.MishkatMasabih.Shamela0008360-ara1",
            edition="al-Maktab al-Islami, Beirut, 3rd ed. 1985, ed. Muhammad Nasir al-Din al-Albani, 3 vols",
            volumes=3, page_style="start", grade_source="al-Albani",
            text_grade_regex=r"^\s*\[\d+\]\s*\(([^)]{1,60})\)\s*"),
    ),
    Collection(
        slug="nawawi40", name_en="The Forty Hadith of al-Nawawi", name_ar="الأربعون النووية",
        author_en="Yahya ibn Sharaf al-Nawawi", author_ar="يحيى بن شرف النووي", died_ah=676,
        authenticity="selection", group="anthology", primary="fawaz",
        description="Forty-two foundational hadith on which the religion revolves.",
        fawaz="nawawi", hadithjson="forties/nawawi40.json", sunnah_slug="nawawi40",
        aliases=("nawawi 40", "40 nawawi", "forty nawawi", "arbain", "الأربعون النووية"),
    ),
    Collection(
        slug="qudsi40", name_en="The Forty Hadith Qudsi", name_ar="الأربعون القدسية",
        author_en="Compiled", author_ar="", died_ah=None,
        authenticity="selection", group="anthology", primary="fawaz",
        description="Forty hadith qudsi (sayings of the Prophet relating words of Allah).",
        fawaz="qudsi", hadithjson="forties/qudsi40.json", sunnah_slug="qudsi40",
        aliases=("qudsi", "hadith qudsi", "40 qudsi", "الأحاديث القدسية"),
    ),
    Collection(
        slug="shahwaliullah40", name_en="The Forty Hadith of Shah Waliullah", name_ar="أربعون الشاه ولي الله",
        author_en="Shah Wali Allah al-Dihlawi", author_ar="شاه ولي الله الدهلوي", died_ah=1176,
        authenticity="selection", group="anthology", primary="fawaz",
        description="Forty short comprehensive hadith selected by Shah Waliullah Dehlawi.",
        fawaz="dehlawi", hadithjson="forties/shahwaliullah40.json", sunnah_slug="shahwaliullah40",
        aliases=("shah waliullah", "dehlawi 40", "أربعون الدهلوي"),
    ),
]

BY_SLUG = {c.slug: c for c in COLLECTIONS}
