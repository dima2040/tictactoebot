import json
import os

translations_dir = os.path.dirname(os.path.dirname(__file__)) + "/translations/"
def get_languages() -> list:
    langs = list()
    for file in os.listdir(translations_dir):
        name = file.replace(".json", "")
        langs.append(name)
    return langs

def get_languages_dict() -> dict:
    langs = dict()
    for file in os.listdir(translations_dir):
        code = file.replace(".json", "")
        data = json.load(open(f"{translations_dir}{file}"))
        name = data['name']
        langs[code] = name
    return langs





def is_lang_supported(name: str) -> bool:
    return name in get_languages()

def find_translate(name: str) -> dict:
    for file in os.listdir(translations_dir):
        filename = file.replace(".json", "")
        if name == filename:
            return json.load(open(f"{translations_dir}{file}"))
    return {}

def get_translate(name: str) -> dict:
    if is_lang_supported(name):
        return find_translate(name)
    else:
        return find_translate('en')