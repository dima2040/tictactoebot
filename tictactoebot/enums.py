from enum import StrEnum

CROSS_SYMBOL = "❌"
ZERO_SYMBOL = "⭕"
EMPTY_SYMBOL = " "

class Symbol(StrEnum):
    CROSS = CROSS_SYMBOL
    ZERO = ZERO_SYMBOL
    EMPTY = EMPTY_SYMBOL


class Language(StrEnum):
    ENGLISH = "en"
    SPANISH = "es"
    HINDI = "hi"
    INDONESIAN = "id"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    ARABIAN = "ar"


class Difficulty(StrEnum):
    EASY = "easy"
    HARD = "hard"