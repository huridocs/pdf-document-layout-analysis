import subprocess

iso_to_tesseract = {
    "en": "eng",  # English
    "es": "spa",  # Spanish
    "fr": "fra",  # French
    "af": "afr",  # Afrikaans
    "ar": "ara",  # Arabic
    "as": "asm",  # Assamese
    "bn": "ben",  # Bengali (Bangla)
    "bo": "bod",  # Tibetan
    "de": "deu",  # German
    "el": "ell",  # Greek
    "he": "heb",  # Hebrew
    "hi": "hin",  # Hindi
    "hu": "hun",  # Hungarian
    "in": "ind",  # Indonesian
    "ja": "jpn",  # Japanese
    "km": "khm",  # Khmer
    "ko": "kor",  # Korean
    "ku": "kmr",  # Kurdish
    "ml": "mal",  # Malayalam
    "ms": "msa",  # Malay
    "my": "mya",  # Burmese
    "ne": "nep",  # Nepali
    "nl": "nld",  # Dutch
    "pt": "por",  # Português
    "ro": "ron",  # Romanian
    "ru": "rus",  # Russian
    "si": "sin",  # Sinhalese
    "sr": "srp",  # Serbian
    "ta": "tam",  # Tamil
    "th": "tha",  # Thai
    "tr": "tur",  # Turkish
    "uk": "ukr",  # Ukrainian
    "ur": "urd",  # Urdu
    "uz": "uzb",  # Uzbek
    "zh-Hans": "chi_sim",  # Chinese (Simplified)
    "zh-Hant": "chi_tra",  # Chinese (Traditional)
    # "zh": "not-supported", # Chinese
    # "tl": "not-supported", # Tagalog
    # "sm": "not-supported", # Samoan
    # "om": "not-supported", # Oromo (Afaan Oromo)
    # "mg": "not-supported", # Malagasy
    # "ab": "not-supported", # Abkhazian
    # "aa": "not-supported", # Afar
}


def supported_languages():
    cmd = "tesseract --list-langs | grep -v osd | awk '{if(NR>1)print}'"
    sp = subprocess.Popen(["/bin/bash", "-c", cmd], stdout=subprocess.PIPE)
    tesseract_langs = [line.strip().decode("utf-8") for line in sp.stdout.readlines()]
    inverted_iso_dict = {v: k for k, v in iso_to_tesseract.items()}
    return list({tesseract_key: inverted_iso_dict[tesseract_key] for tesseract_key in tesseract_langs}.values())
