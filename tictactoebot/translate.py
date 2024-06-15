import json
import os
from typing import List, Dict, Optional


translations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "translations")


def get_languages() -> List[str]:
    """Retrieve the list of language codes available in the translations directory."""
    return [
        os.path.splitext(file)[0] for file in os.listdir(translations_dir) if file.endswith('.json')
    ]


def load_translation_file(language: str) -> Optional[Dict]:
    """Load and return the translation dictionary for a given language code."""
    file_path = os.path.join(translations_dir, f"{language}.json")
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def get_translate(language: str) -> Dict:
    """Get translation dictionary for a specific language, falling back to English if necessary."""
    return load_translation_file(language) or load_translation_file('en') or {}


def translate(language: str, key: str) -> str:
    """Translate a given key to the specified language, falling back to English if the key is not found."""
    translation = get_translate(language)
    return translation.get(key, get_translate('en').get(key, ''))


def get_languages_dict() -> Dict[str, str]:
    """Retrieve a dictionary of language codes and their corresponding names."""
    languages = {}
    for language in get_languages():
        data = load_translation_file(language)
        if data:
            name = data.get('name', 'Unknown')
            languages[language] = name
    return languages