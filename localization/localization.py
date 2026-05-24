# 配置多语言的方式

import json
import locale
import os
import sys


def load_language_config():
    base_dir = getattr(sys, "_MEIPASS", os.getcwd())
    path = os.path.join(base_dir, "localization", "localization.json")
    if not os.path.exists(path):
        path = os.path.join(os.getcwd(), "localization", "localization.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_system_language():
    language, encoding = locale.getlocale()
    if language:
        return language
    return os.environ.get("LANG", "未知")


def get_localized_text(lang_key, **kwargs):
    language_config = load_language_config()
    system_lang = get_system_language()
    # print("Detected system language:", system_lang)
    lang_code = "en"
    if "zh" in system_lang:
        lang_code = "zh"
    text = language_config.get(lang_code, {}).get(lang_key, lang_key)
    return text.format(**kwargs)
