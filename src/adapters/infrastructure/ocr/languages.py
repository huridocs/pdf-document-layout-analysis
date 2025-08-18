import subprocess

iso_to_tesseract = {
    "af": "afr",  # Afrikaans
    "all": "all",  # Allar
    "am": "amh",  # Amharic
    "ar": "ara",  # Arabic
    "as": "asm",  # Assamese
    "az": "aze",  # Azerbaijani
    "aze-cyrl": "aze-cyrl",  # Azerbaijani (Cyrillic)
    "be": "bel",  # Belarusian
    "bn": "ben",  # Bangla
    "bo": "bod",  # Tibetan
    "bs": "bos",  # Bosnian
    "br": "bre",  # Breton
    "bg": "bul",  # Bulgarian
    "ca": "cat",  # Catalan
    "ceb": "ceb",  # Cebuano
    "cs": "ces",  # Czech
    "zh-Hans": "chi_sim",  # Chinese (Simplified)
    "chi-sim-vert": "chi-sim-vert",  # Chinese (Simplified) vertical
    "zh-Hant": "chi_tra",  # Chinese (Traditional)
    "chi-tra-vert": "chi-tra-vert",  # Chinese (Traditional) vertical
    "chr": "chr",  # Cherokee
    "co": "cos",  # Corsican
    "cy": "cym",  # Welsh
    "da": "dan",  # Danish
    "de": "deu",  # German
    "dv": "div",  # Divehi
    "dz": "dzo",  # Dzongkha
    "el": "ell",  # Greek
    "en": "eng",  # English
    "enm": "enm",  # Middle English
    "eo": "epo",  # Esperanto
    "et": "est",  # Estonian
    "eu": "eus",  # Basque
    "fo": "fao",  # Faroese
    "fa": "fas",  # Persian
    "fil": "fil",  # Filipino
    "fi": "fin",  # Finnish
    "fr": "fra",  # French
    "frk": "frk",  # Frankish
    "frm": "frm",  # Middle French
    "fy": "fry",  # Western Frisian
    "gd": "gla",  # Scottish Gaelic
    "ga": "gle",  # Irish
    "gl": "glg",  # Galician
    "grc": "grc",  # Ancient Greek
    "gu": "guj",  # Gujarati
    "ht": "hat",  # Haitian Creole
    "he": "heb",  # Hebrew
    "hi": "hin",  # Hindi
    "hr": "hrv",  # Croatian
    "hu": "hun",  # Hungarian
    "hy": "hye",  # Armenian
    "iu": "iku",  # Inuktitut
    "id": "ind",  # Indonesian
    "is": "isl",  # Icelandic
    "it": "ita",  # Italian
    "ita-old": "ita-old",  # Old Italian
    "jv": "jav",  # Javanese
    "ja": "jpn",  # Japanese
    "jpn-vert": "jpn-vert",  # Japanese vertical
    "kn": "kan",  # Kannada
    "ka": "kat",  # Georgian
    "kat-old": "kat-old",  # Old Georgian
    "kk": "kaz",  # Kazakh
    "km": "khm",  # Khmer
    "ky": "kir",  # Kyrgyz
    "kmr": "kmr",  # Northern Kurdish
    "ko": "kor",  # Korean
    "kor-vert": "kor_vert",  # Korean vertical
    "lo": "lao",  # Lao
    "la": "lat",  # Latin
    "lv": "lav",  # Latvian
    "lt": "lit",  # Lithuanian
    "lb": "ltz",  # Luxembourgish
    "ml": "mal",  # Malayalam
    "mr": "mar",  # Marathi
    "mk": "mkd",  # Macedonian
    "mt": "mlt",  # Maltese
    "mn": "mon",  # Mongolian
    "mi": "mri",  # Māori
    "ms": "msa",  # Malay
    "my": "mya",  # Burmese
    "ne": "nep",  # Nepali
    "nl": "nld",  # Dutch
    "no": "nor",  # Norwegian
    "oc": "oci",  # Occitan
    "or": "ori",  # Odia
    "osd": "osd",  # Unknown language [osd]
    "pa": "pan",  # Punjabi
    "pl": "pol",  # Polish
    "pt": "por",  # Portuguese
    "ps": "pus",  # Pashto
    "qu": "que",  # Quechua
    "ro": "ron",  # Romanian
    "ru": "rus",  # Russian
    "sa": "san",  # Sanskrit
    "script-arab": "script-arab",  # Arabic script
    "script-armn": "script-armn",  # Armenian script
    "script-beng": "script-beng",  # Bengali script
    "script-cans": "script-cans",  # Canadian Aboriginal script
    "script-cher": "script-cher",  # Cherokee script
    "script-cyrl": "script-cyrl",  # Cyrillic script
    "script-deva": "script-deva",  # Devanagari script
    "script-ethi": "script-ethi",  # Ethiopic script
    "script-frak": "script-frak",  # Frankish script
    "script-geor": "script-geor",  # Georgian script
    "script-grek": "script-grek",  # Greek script
    "script-gujr": "script-gujr",  # Gujarati script
    "script-guru": "script-guru",  # Gurmukhi script
    "script-hang": "script-hang",  # Hangul script
    "script-hang-vert": "script-hang-vert",  # Hangul script vertical
    "script-hans": "script-hans",
    "script-hans-vert": "script-hans-vert",
    "script-hant": "script-hant",
    "script-hant-vert": "script-hant-vert",
    "script-hebr": "script-hebr",  # Hebrew script
    "script-jpan": "script-jpan",  # Japanese script
    "script-jpan-vert": "script-jpan-vert",  # Japanese script vertical
    "script-khmr": "script-khmr",  # Khmer script
    "script-knda": "script-knda",  # Kannada script
    "script-laoo": "script-laoo",  # Lao script
    "script-latn": "script-latn",
    "script-mlym": "script-mlym",  # Malayalam script
    "script-mymr": "script-mymr",  # Myanmar script
    "script-orya": "script-orya",  # Odia script
    "script-sinh": "script-sinh",  # Sinhala script
    "script-syrc": "script-syrc",  # Syriac script
    "script-taml": "script-taml",  # Tamil script
    "script-telu": "script-telu",  # Telugu script
    "script-thaa": "script-thaa",  # Thaana script
    "script-thai": "script-thai",  # Thai script
    "script-tibt": "script-tibt",  # Tibetan script
    "script-viet": "script-viet",  # Vietnamese script
    "si": "sin",  # Sinhala
    "sk": "slk",  # Slovak
    "sl": "slv",  # Slovenian
    "sd": "snd",  # Sindhi
    "es": "spa",  # Spanish
    "spa-old": "spa-old",  # Old Spanish
    "sq": "sqi",  # Albanian
    "sr": "srp",  # Serbian
    "srp-latn": "srp-latn",  # Serbian (Latin)
    "su": "sun",  # Sundanese
    "sw": "swa",  # Swahili
    "sv": "swe",  # Swedish
    "syr": "syr",  # Syriac
    "ta": "tam",  # Tamil
    "tt": "tat",  # Tatar
    "te": "tel",  # Telugu
    "tg": "tgk",  # Tajik
    "th": "tha",  # Thai
    "ti": "tir",  # Tigrinya
    "to": "ton",  # Tongan
    "tr": "tur",  # Turkish
    "ug": "uig",  # Uyghur
    "uk": "ukr",  # Ukrainian
    "ur": "urd",  # Urdu
    "uz": "uzb",  # Uzbek
    "uzb-cyrl": "uzb-cyrl",  # Uzbek (Cyrillic)
    "vi": "vie",  # Vietnamese
    "yi": "yid",  # Yiddish
    "yo": "yor",  # Yoruba
}


def supported_languages():
    cmd = "tesseract --list-langs | grep -v osd | awk '{if(NR>1)print}'"
    sp = subprocess.Popen(["/bin/bash", "-c", cmd], stdout=subprocess.PIPE)
    tesseract_langs = [line.strip().decode("utf-8") for line in sp.stdout.readlines()]
    inverted_iso_dict = {v: k for k, v in iso_to_tesseract.items()}
    return list({tesseract_key: inverted_iso_dict[tesseract_key] for tesseract_key in tesseract_langs}.values())
