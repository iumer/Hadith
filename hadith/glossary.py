"""Bilingual vocabulary used for (1) English titles of Arabic kitab headings and
(2) query expansion in the search engine.

Arabic entries are written in *normalised* form (see ``normalize_arabic``):
no diacritics, alef variants -> ا, ى -> ي, ة -> ه.
"""
from __future__ import annotations

from .normalize import normalize_arabic

# --------------------------------------------------------------------------- kitab titles
# Matched against the normalised kitab heading after stripping "كتاب", "ابواب", "من", "و".
KITAB_EN: list[tuple[str, str]] = [
    ("الطهاره", "Purification"), ("الوضوء", "Ablution (Wudu)"), ("الغسل", "Ritual Bath (Ghusl)"),
    ("التيمم", "Dry Ablution (Tayammum)"), ("الحيض", "Menstruation"), ("المياه", "Water"),
    ("الصلاه", "Prayer (Salat)"), ("مواقيت الصلاه", "Prayer Times"), ("الاذان", "Call to Prayer (Adhan)"),
    ("المساجد", "Mosques"), ("الامامه", "Leading the Prayer"), ("الجمعه", "Friday Prayer"),
    ("العيدين", "The Two Eids"), ("الوتر", "Witr Prayer"), ("التطوع", "Voluntary Prayers"),
    ("صلاه الخوف", "Fear Prayer"), ("الكسوف", "Eclipse Prayer"), ("الاستسقاء", "Prayer for Rain"),
    ("السهو", "Prostration of Forgetfulness"), ("قيام الليل", "Night Prayer"), ("التهجد", "Night Prayer (Tahajjud)"),
    ("الجنائز", "Funerals"), ("الزكاه", "Zakat (Obligatory Charity)"), ("الصدقه", "Charity"),
    ("الصوم", "Fasting"), ("الصيام", "Fasting"), ("الاعتكاف", "Retreat (I'tikaf)"),
    ("المناسك", "Hajj Rites"), ("الحج", "Pilgrimage (Hajj)"), ("العمره", "Umrah"),
    ("الاضاحي", "Sacrifices (Udhiyah)"), ("الذبائح", "Slaughtering"), ("العقيقه", "Aqiqah"),
    ("الصيد", "Hunting"), ("الاطعمه", "Food"), ("الاشربه", "Drinks"), ("اللباس", "Clothing"),
    ("الزينه", "Adornment"), ("النكاح", "Marriage"), ("الرضاع", "Breastfeeding (Suckling)"),
    ("الطلاق", "Divorce"), ("اللعان", "Li'an (Oath of Condemnation)"), ("العتق", "Manumission of Slaves"),
    ("البيوع", "Sales and Trade"), ("التجارات", "Trade"), ("الاجاره", "Hiring"), ("الربا", "Usury (Riba)"),
    ("الرهن", "Pledges"), ("الشفعه", "Pre-emption"), ("الهبه", "Gifts"), ("الهبات", "Gifts"),
    ("الوصايا", "Wills"), ("الفرائض", "Inheritance"), ("الوقف", "Endowments"),
    ("الاحكام", "Judgements"), ("الاقضيه", "Judgements"), ("الشهادات", "Testimony"),
    ("الحدود", "Prescribed Punishments (Hudud)"), ("الديات", "Blood Money (Diyat)"),
    ("القصاص", "Retaliation (Qisas)"), ("القسامه", "Qasamah"), ("المحاربين", "Highway Robbers"),
    ("الايمان والنذور", "Oaths and Vows"), ("النذور والايمان", "Vows and Oaths"), ("النذور", "Vows"),
    ("الجهاد", "Jihad"), ("السير", "Military Expeditions (Siyar)"), ("الامارة", "Government"),
    ("الاماره", "Leadership and Government"), ("المغازي", "Military Campaigns"), ("الخراج", "Tribute and Spoils"),
    ("الفتن", "Trials and Tribulations (Fitan)"), ("الملاحم", "Great Battles (End Times)"),
    ("الايمان", "Faith (Iman)"), ("العلم", "Knowledge"), ("السنه", "The Sunnah"), ("القدر", "Divine Decree"),
    ("التوحيد", "Monotheism (Tawhid)"), ("الاعتصام", "Holding Fast to the Qur'an and Sunnah"),
    ("فضائل القران", "Virtues of the Qur'an"), ("التفسير", "Tafsir (Qur'an Commentary)"),
    ("الدعاء", "Supplication (Du'a)"), ("الدعوات", "Supplications"), ("الذكر", "Remembrance of Allah"),
    ("الرقاق", "Heart-Softening Narrations"), ("الزهد", "Asceticism (Zuhd)"), ("التوبه", "Repentance"),
    ("الادب", "Manners and Etiquette"), ("البر والصله", "Righteousness and Keeping Ties"),
    ("الاستئذان", "Seeking Permission"), ("السلام", "Greetings (Salam)"), ("الطب", "Medicine"),
    ("الرقي", "Ruqyah"), ("الرويا", "Dreams"), ("التعبير", "Interpretation of Dreams"),
    ("المناقب", "Virtues and Merits"), ("الفضائل", "Virtues"), ("فضائل الصحابه", "Virtues of the Companions"),
    ("معرفه الصحابه", "Knowledge of the Companions"), ("المرضي", "The Sick"), ("صفه القيامه", "Description of the Day of Judgement"),
    ("صفه الجنه", "Description of Paradise"), ("الجنه", "Paradise"), ("صفه النار", "Description of Hellfire"),
    ("الاحسان", "Excellence (Ihsan)"), ("الحظر والاباحه", "Prohibited and Permissible"),
    ("التاريخ", "History"), ("اخبار", "Reports"), ("بدء الوحي", "Revelation"), ("بدء الخلق", "Beginning of Creation"),
    ("الانبياء", "Prophets"), ("احاديث الانبياء", "Stories of the Prophets"), ("المقدمه", "Introduction"),
    ("مقدمه", "Introduction"), ("الشركه", "Partnership"), ("الوكاله", "Agency"), ("المزارعه", "Agriculture"),
    ("المساقاه", "Watering (Musaqah)"), ("الكفاله", "Guarantees"), ("الحواله", "Transfer of Debt"),
    ("اللقطه", "Lost Property"), ("المظالم", "Oppression"), ("الصلح", "Reconciliation"),
    ("الشروط", "Conditions"), ("الحيل", "Tricks"), ("الاكراه", "Coercion"), ("التمني", "Wishes"),
    ("الكفارات", "Expiations"), ("الجزيه", "Jizyah"), ("فرض الخمس", "The Khumus"), ("الاشربه والحد", "Drinks and Punishment"),
    ("العقول", "Blood Money"), ("الترجل", "Combing Hair"), ("الخاتم", "Rings"), ("الحمام", "Bathhouses"),
    ("النوم", "Sleep"), ("الصحابه", "The Companions"), ("الشعر", "Poetry"), ("الالفاظ", "Words and Expressions"),
    ("الامثال", "Parables"), ("الوصيه", "Wills"), ("القران", "The Qur'an"), ("الصبر", "Patience"),
]
_KITAB_NORM = sorted(((normalize_arabic(a), e) for a, e in KITAB_EN), key=lambda x: -len(x[0]))
_STRIP_PREFIXES = ("ومن كتاب ", "من كتاب ", "كتاب ", "ابواب ", "باب ", "جماع ابواب ", "ذكر ")


def kitab_english(arabic: str | None) -> str | None:
    if not arabic:
        return None
    n = normalize_arabic(arabic)
    for p in _STRIP_PREFIXES:
        if n.startswith(p):
            n = n[len(p):]
            break
    for ar, en in _KITAB_NORM:
        if n.startswith(ar) or n == ar:
            return f"The Book of {en}"
    for ar, en in _KITAB_NORM:
        if f" {ar}" in f" {n} ":
            return f"The Book of {en}"
    return None


# --------------------------------------------------------------------------- search topics
# Each topic: English trigger words/phrases (lower-case, transliterations allowed),
# extra English expansions, and normalised Arabic terms.
TOPICS: list[dict] = [
    {"en": ["prayer", "prayers", "pray", "praying", "salat", "salah", "namaz", "salaat"], "ar": ["صلاه", "الصلاه", "يصلي", "صلي", "صلوا", "صلاتي", "صلاته"]},
    {"en": ["fasting", "fast", "fasts", "sawm", "siyam", "roza", "ramadan"], "ar": ["صوم", "صيام", "الصيام", "صام", "يصوم", "صائم", "رمضان"]},
    {"en": ["charity", "sadaqah", "sadaqa", "alms", "donation"], "ar": ["صدقه", "الصدقه", "تصدق", "يتصدق"]},
    {"en": ["zakat", "zakah", "obligatory charity"], "ar": ["زكاه", "الزكاه"]},
    {"en": ["hajj", "pilgrimage", "pilgrim"], "ar": ["حج", "الحج", "حاج", "مناسك"]},
    {"en": ["umrah", "umra"], "ar": ["عمره", "العمره", "اعتمر"]},
    {"en": ["ablution", "wudu", "wudhu", "wuzu"], "ar": ["وضوء", "الوضوء", "توضا", "يتوضا"]},
    {"en": ["ghusl", "ritual bath", "bath", "janabah", "janaba"], "ar": ["غسل", "اغتسل", "جنابه", "جنب"]},
    {"en": ["tayammum", "dry ablution"], "ar": ["تيمم", "التيمم", "صعيد"]},
    {"en": ["mosque", "masjid", "mosques"], "ar": ["مسجد", "المسجد", "مساجد"]},
    {"en": ["adhan", "azan", "call to prayer", "muezzin", "mu'adhdhin"], "ar": ["اذان", "الاذان", "اذن", "موذن", "المنادي"]},
    {"en": ["friday", "jumuah", "jumua", "jummah", "jumu'ah"], "ar": ["جمعه", "الجمعه"]},
    {"en": ["eid"], "ar": ["عيد", "العيد", "الفطر", "الاضحي"]},
    {"en": ["night prayer", "tahajjud", "qiyam", "tarawih", "witr"], "ar": ["قيام", "تهجد", "الليل", "وتر", "الوتر"]},
    {"en": ["supplication", "dua", "du'a", "invocation", "supplicate"], "ar": ["دعاء", "الدعاء", "دعا", "ادعو", "يدعو", "اللهم"]},
    {"en": ["remembrance", "dhikr", "zikr", "tasbih", "glorify"], "ar": ["ذكر", "سبحان", "تسبيح", "الحمد لله", "الله اكبر", "لا اله الا الله"]},
    {"en": ["repentance", "repent", "tawbah", "tauba", "forgiveness", "istighfar", "forgive"], "ar": ["توبه", "تاب", "يتوب", "استغفر", "مغفره", "غفر"]},
    {"en": ["patience", "patient", "sabr", "perseverance", "endurance", "hardship", "calamity", "affliction"], "ar": ["صبر", "الصبر", "صابر", "مصيبه", "بلاء", "ابتلي"]},
    {"en": ["gratitude", "grateful", "thankful", "thanks", "shukr"], "ar": ["شكر", "يشكر", "شاكر"]},
    {"en": ["intention", "intentions", "niyyah", "niyya", "sincerity", "ikhlas"], "ar": ["نيه", "النيات", "بالنيات", "اخلاص", "مخلصا"]},
    {"en": ["faith", "iman", "belief", "believer", "believers"], "ar": ["ايمان", "الايمان", "مومن", "المومنين", "امن"]},
    {"en": ["islam", "muslim", "muslims"], "ar": ["اسلام", "الاسلام", "مسلم", "المسلمين"]},
    {"en": ["ihsan", "excellence"], "ar": ["احسان", "الاحسان"]},
    {"en": ["knowledge", "ilm", "learning", "scholar", "scholars", "teach", "seeking knowledge"], "ar": ["علم", "العلم", "عالم", "العلماء", "تعلم", "فقه"]},
    {"en": ["quran", "qur'an", "koran", "recitation", "recite"], "ar": ["قران", "القران", "قرا", "يقرا", "سوره", "ايه"]},
    {"en": ["parents", "mother", "father", "dutiful", "birr"], "ar": ["والدين", "الوالدين", "ام", "امك", "اب", "ابيك", "بر"]},
    {"en": ["kinship", "relatives", "ties of kinship", "family ties", "womb"], "ar": ["رحم", "الرحم", "صله", "قرابه"]},
    {"en": ["neighbor", "neighbour", "neighbors", "neighbours"], "ar": ["جار", "الجار", "جاره"]},
    {"en": ["orphan", "orphans"], "ar": ["يتيم", "اليتيم", "الايتام"]},
    {"en": ["marriage", "marry", "nikah", "wedding", "spouse", "husband", "wife"], "ar": ["نكاح", "النكاح", "تزوج", "زوج", "زوجه", "امراته"]},
    {"en": ["divorce", "talaq"], "ar": ["طلاق", "الطلاق", "طلق"]},
    {"en": ["women", "woman", "wives"], "ar": ["نساء", "النساء", "المراه", "امراه"]},
    {"en": ["children", "child", "son", "daughter", "daughters"], "ar": ["ولد", "اولاد", "ابن", "بنت", "بنات", "صبي"]},
    {"en": ["trade", "business", "sale", "selling", "buying", "merchant", "commerce"], "ar": ["بيع", "البيع", "تجاره", "تاجر", "اشتري", "باع"]},
    {"en": ["usury", "riba", "interest"], "ar": ["ربا", "الربا"]},
    {"en": ["debt", "loan", "debtor"], "ar": ["دين", "الدين", "قرض", "غريم"]},
    {"en": ["inheritance", "inherit", "heir", "heirs"], "ar": ["ميراث", "فرائض", "يرث", "ورثه"]},
    {"en": ["will", "bequest", "wasiyyah"], "ar": ["وصيه", "اوصي"]},
    {"en": ["food", "eating", "eat", "meal"], "ar": ["طعام", "اكل", "ياكل", "كلوا"]},
    {"en": ["drink", "drinking", "water"], "ar": ["شرب", "يشرب", "ماء"]},
    {"en": ["alcohol", "wine", "intoxicant", "intoxicants", "khamr"], "ar": ["خمر", "الخمر", "مسكر", "سكر"]},
    {"en": ["clothing", "clothes", "garment", "dress", "silk", "izar"], "ar": ["لباس", "ثوب", "ثياب", "حرير", "ازار", "لبس"]},
    {"en": ["gold", "silver"], "ar": ["ذهب", "الذهب", "فضه"]},
    {"en": ["jihad", "fighting", "battle", "martyr", "martyrdom", "shahid"], "ar": ["جهاد", "الجهاد", "قتال", "غزوه", "شهيد", "الشهاده"]},
    {"en": ["paradise", "jannah", "heaven", "garden"], "ar": ["جنه", "الجنه", "الفردوس"]},
    {"en": ["hell", "hellfire", "jahannam", "fire"], "ar": ["نار", "النار", "جهنم"]},
    {"en": ["day of judgement", "judgment", "resurrection", "qiyamah", "hereafter", "akhirah"], "ar": ["القيامه", "يوم القيامه", "الاخره", "البعث", "الحساب"]},
    {"en": ["grave", "graves", "punishment of the grave", "barzakh"], "ar": ["قبر", "القبر", "عذاب القبر"]},
    {"en": ["death", "dying", "die", "funeral", "janazah", "deceased"], "ar": ["موت", "الموت", "مات", "جنازه", "الجنائز", "ميت"]},
    {"en": ["angel", "angels", "jibril", "gabriel"], "ar": ["ملك", "ملائكه", "الملائكه", "جبريل"]},
    {"en": ["satan", "shaitan", "shaytan", "devil", "iblis", "jinn"], "ar": ["شيطان", "الشيطان", "ابليس", "جن"]},
    {"en": ["prophet", "messenger", "prophets"], "ar": ["النبي", "رسول الله", "الانبياء"]},
    {"en": ["anger", "angry", "rage"], "ar": ["غضب", "يغضب", "تغضب"]},
    {"en": ["honesty", "truthfulness", "truth", "truthful"], "ar": ["صدق", "الصدق", "صادق"]},
    {"en": ["lying", "lie", "liar", "falsehood"], "ar": ["كذب", "الكذب", "كذاب", "يكذب"]},
    {"en": ["backbiting", "gossip", "slander", "ghibah", "tale-carrying"], "ar": ["غيبه", "الغيبه", "نميمه", "نمام"]},
    {"en": ["envy", "jealousy", "hasad"], "ar": ["حسد", "الحسد", "تحاسدوا"]},
    {"en": ["arrogance", "pride", "kibr", "arrogant"], "ar": ["كبر", "الكبر", "متكبر"]},
    {"en": ["humility", "humble", "modesty"], "ar": ["تواضع", "التواضع"]},
    {"en": ["shyness", "haya", "modesty", "bashfulness"], "ar": ["حياء", "الحياء"]},
    {"en": ["good character", "character", "manners", "akhlaq", "adab", "conduct"], "ar": ["خلق", "اخلاق", "حسن الخلق", "ادب"]},
    {"en": ["kindness", "gentle", "gentleness", "mercy", "merciful", "compassion"], "ar": ["رفق", "الرفق", "رحمه", "يرحم", "الرحمه"]},
    {"en": ["justice", "just", "oppression", "injustice", "oppressor", "zulm"], "ar": ["عدل", "ظلم", "الظلم", "ظالم"]},
    {"en": ["trust", "amanah", "trustworthy", "betrayal"], "ar": ["امانه", "الامانه", "خيانه"]},
    {"en": ["promise", "covenant", "oath", "oaths", "vow"], "ar": ["وعد", "عهد", "يمين", "حلف", "نذر"]},
    {"en": ["greeting", "salam", "salaam", "peace"], "ar": ["سلام", "السلام"]},
    {"en": ["smile", "smiling", "cheerful"], "ar": ["تبسم", "تبسمك", "طلق"]},
    {"en": ["sleep", "sleeping", "bed"], "ar": ["نوم", "نام", "فراش", "مضجع"]},
    {"en": ["sickness", "illness", "sick", "disease", "visiting the sick", "cure", "medicine"], "ar": ["مرض", "مريض", "عياده", "شفاء", "دواء", "طب"]},
    {"en": ["dream", "dreams", "vision"], "ar": ["رويا", "الرويا", "منام", "حلم"]},
    {"en": ["wealth", "money", "rich", "property", "riches"], "ar": ["مال", "المال", "غني", "الغني"]},
    {"en": ["poverty", "poor", "needy", "miskin"], "ar": ["فقر", "فقير", "الفقراء", "مسكين"]},
    {"en": ["world", "dunya", "worldly", "asceticism", "zuhd"], "ar": ["دنيا", "الدنيا", "زهد"]},
    {"en": ["heart", "hearts"], "ar": ["قلب", "القلب", "قلوب"]},
    {"en": ["tongue", "speech", "speak", "silence", "silent"], "ar": ["لسان", "لسانه", "قول", "يصمت", "ليصمت"]},
    {"en": ["brotherhood", "brother", "brothers", "love for the sake of allah"], "ar": ["اخ", "اخيه", "اخوه", "المتحابين"]},
    {"en": ["love", "loves", "beloved"], "ar": ["حب", "يحب", "احب", "محبه"]},
    {"en": ["fear of allah", "taqwa", "piety", "god-conscious", "righteous"], "ar": ["تقوي", "اتق", "اتقوا", "المتقين"]},
    {"en": ["hypocrisy", "hypocrite", "hypocrites", "munafiq"], "ar": ["نفاق", "منافق", "المنافق"]},
    {"en": ["shirk", "polytheism", "idolatry", "associating partners"], "ar": ["شرك", "الشرك", "اشرك", "مشرك"]},
    {"en": ["innovation", "bid'ah", "bidah", "heresy"], "ar": ["بدعه", "البدعه", "محدثه", "محدثات"]},
    {"en": ["sunnah", "sunnah of the prophet", "follow the sunnah"], "ar": ["سنه", "سنتي", "السنه"]},
    {"en": ["divine decree", "qadar", "destiny", "predestination", "fate"], "ar": ["قدر", "القدر", "قضاء", "كتب الله"]},
    {"en": ["tawhid", "oneness", "monotheism"], "ar": ["توحيد", "لا اله الا الله", "وحده لا شريك له"]},
    {"en": ["allah's names", "names of allah", "99 names", "attributes of allah"], "ar": ["اسما", "تسعه وتسعين اسما", "الاسماء الحسني"]},
    {"en": ["end times", "signs of the hour", "dajjal", "antichrist", "mahdi", "last day", "hour"], "ar": ["الساعه", "الدجال", "المهدي", "اشراط الساعه", "عيسي ابن مريم"]},
    {"en": ["trials", "fitnah", "fitna", "tribulation", "tribulations"], "ar": ["فتنه", "الفتن", "فتن"]},
    {"en": ["leader", "ruler", "imam", "governance", "obedience", "authority", "khalifa", "caliph"], "ar": ["امير", "الامير", "امام", "الامام", "طاعه", "سلطان", "خليفه"]},
    {"en": ["witness", "testimony", "judge", "judgement", "court"], "ar": ["شهاده", "شاهد", "قاضي", "القضاء"]},
    {"en": ["theft", "thief", "stealing", "steal"], "ar": ["سرقه", "سارق", "سرق"]},
    {"en": ["adultery", "fornication", "zina"], "ar": ["زنا", "الزنا", "زاني"]},
    {"en": ["murder", "killing", "kill", "blood", "retaliation"], "ar": ["قتل", "دم", "دماء", "قصاص"]},
    {"en": ["animal", "animals", "cat", "dog", "camel", "horse"], "ar": ["هره", "كلب", "بعير", "ناقه", "فرس", "دابه", "بهيمه"]},
    {"en": ["travel", "journey", "traveler", "traveller", "safar"], "ar": ["سفر", "مسافر", "السفر"]},
    {"en": ["guest", "hospitality", "host"], "ar": ["ضيف", "الضيف", "ضيافه"]},
    {"en": ["slave", "slaves", "servant", "manumission", "freeing slaves"], "ar": ["عبد", "رقبه", "عتق", "مملوك", "خادم"]},
    {"en": ["work", "labour", "labor", "earning", "worker", "wages"], "ar": ["عمل", "كسب", "اجير", "اجره"]},
    {"en": ["mercy to animals", "kindness to animals"], "ar": ["بهيمه", "الدواب", "كلب"]},
    {"en": ["cleanliness", "purity", "purification", "tahara", "taharah"], "ar": ["طهور", "الطهور", "طهاره", "نظافه"]},
    {"en": ["miswak", "siwak", "toothstick"], "ar": ["سواك", "السواك"]},
    {"en": ["menstruation", "menses", "haid", "hayd", "istihadah"], "ar": ["حيض", "الحيض", "حائض", "مستحاضه"]},
    {"en": ["jesus", "isa", "moses", "musa", "abraham", "ibrahim", "noah", "nuh", "adam"], "ar": ["عيسي", "موسي", "ابراهيم", "نوح", "ادم"]},
    {"en": ["companions", "sahabah", "abu bakr", "umar", "uthman", "ali"], "ar": ["اصحابي", "ابو بكر", "عمر", "عثمان", "علي"]},
    {"en": ["qadr night", "laylat al-qadr", "night of power", "lailatul qadr"], "ar": ["ليله القدر"]},
    {"en": ["sacrifice", "udhiyah", "qurbani", "slaughter"], "ar": ["اضحيه", "ضحي", "ذبح", "نسك"]},
    {"en": ["music", "singing", "musical instruments"], "ar": ["معازف", "غناء", "مزمار"]},
    {"en": ["pictures", "images", "statues", "picture"], "ar": ["صوره", "الصور", "تصاوير", "تماثيل"]},
    {"en": ["beard", "moustache", "mustache", "hair"], "ar": ["لحيه", "اللحي", "الشوارب", "شعر"]},
    {"en": ["sneezing", "sneeze", "yawning"], "ar": ["عطس", "العاطس", "تثاوب"]},
    {"en": ["right hand", "left hand"], "ar": ["يمين", "بيمينه", "شمال", "بشماله"]},
    {"en": ["moon", "sun", "eclipse"], "ar": ["قمر", "شمس", "كسوف", "خسوف"]},
    {"en": ["rain", "drought"], "ar": ["مطر", "استسقاء", "غيث"]},
    {"en": ["seeking refuge", "refuge", "evil eye", "ruqyah", "magic", "sorcery"], "ar": ["اعوذ", "العين", "رقيه", "سحر"]},
    {"en": ["good deeds", "deeds", "actions", "reward"], "ar": ["عمل", "الاعمال", "اجر", "حسنه", "حسنات"]},
    {"en": ["sins", "sin", "major sins", "minor sins"], "ar": ["ذنب", "ذنوب", "الكبائر", "خطايا", "سيئه"]},
    {"en": ["prostration", "sujud", "sajdah", "bowing", "ruku"], "ar": ["سجود", "سجد", "ركوع", "ركع"]},
    {"en": ["qiblah", "qibla", "kaaba", "ka'bah", "makkah", "mecca"], "ar": ["قبله", "القبله", "الكعبه", "مكه"]},
    {"en": ["madinah", "medina"], "ar": ["المدينه"]},
    {"en": ["jerusalem", "al-aqsa", "bayt al-maqdis"], "ar": ["بيت المقدس", "الاقصي", "ايلياء"]},
    {"en": ["laughter", "laughing", "joking", "jest"], "ar": ["ضحك", "يضحك", "مزاح"]},
    {"en": ["generosity", "generous", "spending", "spend in the way of allah"], "ar": ["كرم", "جود", "انفق", "نفقه"]},
    {"en": ["miserliness", "stingy", "greed", "avarice"], "ar": ["بخل", "شح", "البخيل"]},
    {"en": ["contentment", "qana'ah", "self-sufficiency"], "ar": ["قناعه", "قنع", "غني النفس"]},
    {"en": ["reliance", "tawakkul", "trust in allah"], "ar": ["توكل", "يتوكل", "متوكل"]},
    {"en": ["hope", "fear", "khawf", "raja"], "ar": ["رجاء", "خوف", "يخاف"]},
]


def expand_query_terms(query_lower: str) -> tuple[list[str], list[str]]:
    """Return (english_expansions, arabic_terms) for topics mentioned in the query."""
    en_out: list[str] = []
    ar_out: list[str] = []
    padded = f" {query_lower} "
    for t in TOPICS:
        if any(f" {w} " in padded or (len(w) > 4 and w in query_lower) for w in t["en"]):
            en_out.extend(t["en"])
            ar_out.extend(t["ar"])
    return list(dict.fromkeys(en_out)), list(dict.fromkeys(ar_out))


def arabic_topic_expansions(norm_ar_query: str) -> tuple[list[str], list[str]]:
    """Reverse lookup: Arabic/Urdu query -> English synonyms (for bilingual search)."""
    en_out, ar_out = [], []
    toks = set(norm_ar_query.split())
    urdu_topics = {URDU_TERMS[w] for w in toks if w in URDU_TERMS}
    for t in TOPICS:
        if t["en"][0] in urdu_topics or any(a in toks or (" " in a and a in norm_ar_query) for a in t["ar"]):
            en_out.extend(t["en"][:4])
            ar_out.extend(t["ar"])
    return list(dict.fromkeys(en_out)), list(dict.fromkeys(ar_out))


# Common Urdu words (already passed through normalize_arabic) -> TOPICS key.
_URDU_RAW = {
    "نماز": "prayer", "نمازیں": "prayer", "روزہ": "fasting", "روزے": "fasting", "روزه": "fasting",
    "زکوٰۃ": "zakat", "زکات": "zakat", "خیرات": "charity", "صدقہ": "charity", "حج": "hajj", "عمرہ": "umrah",
    "وضو": "ablution", "غسل": "ghusl", "مسجد": "mosque", "اذان": "adhan", "جمعہ": "friday", "عید": "eid",
    "تہجد": "night prayer", "دعا": "supplication", "ذکر": "remembrance", "توبہ": "repentance", "صبر": "patience",
    "شکر": "gratitude", "نیت": "intention", "ایمان": "faith", "علم": "knowledge", "قرآن": "quran",
    "والدین": "parents", "ماں": "parents", "باپ": "parents", "رشتہ": "kinship", "پڑوسی": "neighbor",
    "یتیم": "orphan", "نکاح": "marriage", "شادی": "marriage", "طلاق": "divorce", "عورت": "women",
    "عورتیں": "women", "بچے": "children", "تجارت": "trade", "سود": "usury", "قرض": "debt", "وراثت": "inheritance",
    "وصیت": "will", "کھانا": "food", "پانی": "drink", "شراب": "alcohol", "لباس": "clothing", "سونا": "gold",
    "جہاد": "jihad", "جنت": "paradise", "جہنم": "hell", "دوزخ": "hell", "قیامت": "day of judgement",
    "قبر": "grave", "موت": "death", "فرشتے": "angel", "فرشتہ": "angel", "شیطان": "satan", "غصہ": "anger",
    "سچ": "honesty", "سچائی": "honesty", "جھوٹ": "lying", "غیبت": "backbiting", "حسد": "envy",
    "تکبر": "arrogance", "غرور": "arrogance", "عاجزی": "humility", "حیا": "shyness", "اخلاق": "good character",
    "نرمی": "kindness", "انصاف": "justice", "عدل": "justice", "امانت": "trust", "وعدہ": "promise",
    "سلام": "greeting", "مسکراہٹ": "smile", "نیند": "sleep", "بیماری": "sickness", "بیمار": "sickness",
    "خواب": "dream", "مال": "wealth", "دولت": "wealth", "غربت": "poverty", "دنیا": "world", "دل": "heart",
    "زبان": "tongue", "بھائی": "brotherhood", "محبت": "love", "تقویٰ": "fear of allah", "منافق": "hypocrisy",
    "منافقت": "hypocrisy", "شرک": "shirk", "بدعت": "innovation", "سنت": "sunnah", "تقدیر": "divine decree",
    "توحید": "tawhid", "فتنہ": "trials", "حکمران": "leader", "گواہی": "witness", "چوری": "theft", "زنا": "adultery",
    "قتل": "murder", "جانور": "animal", "سفر": "travel", "مہمان": "guest", "غلام": "slave", "محنت": "work",
    "صفائی": "cleanliness", "پاکیزگی": "cleanliness", "مسواک": "miswak", "حیض": "menstruation",
    "عیسیٰ": "jesus", "صحابہ": "companions", "قربانی": "sacrifice", "موسیقی": "music", "تصویر": "pictures",
    "داڑھی": "beard", "چھینک": "sneezing", "بارش": "rain", "گناہ": "sins", "سجدہ": "prostration", "قبلہ": "qiblah",
    "مدینہ": "madinah", "ہنسی": "laughter", "سخاوت": "generosity", "بخل": "miserliness", "قناعت": "contentment",
    "توکل": "reliance", "امید": "hope", "نیکی": "good deeds", "نیک": "good deeds",
}
URDU_TERMS = {normalize_arabic(k): v for k, v in _URDU_RAW.items()}


# English synonym groups used to widen each required (AND) query term.
_EN_SYNONYM_GROUPS = [
    ["action", "actions", "deed", "deeds", "work", "works"],
    ["intention", "intentions", "intend", "niyyah"],
    ["reward", "rewards", "recompense"],
    ["sin", "sins", "evil deeds", "wrongdoing"],
    ["parent", "parents", "mother", "father"],
    ["child", "children", "son", "daughter", "offspring"],
    ["wife", "wives", "spouse", "husband"],
    ["prayer", "prayers", "salat", "salah"],
    ["fast", "fasting", "fasts", "fasted", "sawm"],
    ["charity", "sadaqa", "sadaqah", "alms"],
    ["neighbor", "neighbors", "neighbour", "neighbours"],
    ["honor", "honour", "respect"],
    ["lie", "lies", "lying", "falsehood", "liar"],
    ["truth", "truthful", "truthfulness", "honesty", "honest"],
    ["kind", "kindness", "gentle", "gentleness"],
    ["paradise", "jannah", "garden"],
    ["hell", "hellfire", "fire", "jahannam"],
    ["rights", "right", "due"],
    ["patience", "patient", "sabr", "steadfast"],
    ["merciful", "mercy", "compassion", "compassionate"],
    ["knowledge", "learning", "scholar", "scholars"],
    ["dua", "duas", "supplication", "supplications", "invocation", "invoke", "supplicate"],
    ["toilet", "privy", "lavatory", "latrine", "call of nature", "relieving himself", "relieve himself"],
    ["entering", "enter", "enters", "entered"],
    ["leaving", "leave", "exit", "exiting", "coming out"],
    ["virtue", "virtues", "merit", "merits", "superiority", "excellence"],
    ["hardship", "hardships", "difficulty", "difficulties", "calamity", "affliction", "adversity"],
    ["anger", "angry", "rage", "wrath"],
    ["strong", "strength", "mighty"],
    ["consistent", "consistently", "regular", "regularly", "constant", "constantly", "continuous",
     "continuously", "persistent", "persistently"],
    ["beloved", "loved", "dearest", "dear", "liked"],
]
EN_SYNONYMS: dict[str, list[str]] = {}
for _g in _EN_SYNONYM_GROUPS:
    for _w in _g:
        EN_SYNONYMS[_w] = [x for x in _g if x != _w]
