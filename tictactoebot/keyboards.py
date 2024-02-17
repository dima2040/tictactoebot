from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .translate import get_translate
from .filters import LanguageFilter, DifficultyFilter, ButtonFilter
from .data import Symbol


def make_lang_kb(langs: dict):
    return make_splited_inline_kb(langs, size=2, filt=LanguageFilter)


def make_splited_inline_kb(langs: dict, size: int=3, filt=None):
    parent: list = list()
    child: list = list()
    parent.append(child)
    index = 0 
    for key, value in langs.items():
        child.append(
            InlineKeyboardButton(
                text=value,
                callback_data=filt(code=key).pack()
            )
        )
        index += 1
        if index > size:
            child = list()
            parent.append(child)
            index = 0

    return InlineKeyboardMarkup(
        inline_keyboard=parent
    )

def make_choice_keyboard() -> InlineKeyboardMarkup:
    """
    Создает пользовательскую клавиатуру.
    Клавиатура состоит из крестика и нолика.
    """
    keyboard = list()
    keyboard.append(
        [
            InlineKeyboardButton(
                text=Symbol.CROSS,
                callback_data=ButtonFilter(index=-1, status=Symbol.CROSS).pack(),
            ),
            InlineKeyboardButton(
                text=Symbol.ZERO,
                callback_data=ButtonFilter(index=-1, status=Symbol.ZERO).pack(),
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def make_difficulty_kb(code):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=get_translate(code)['difficulty.easy'],
                    callback_data=DifficultyFilter(level='easy').pack()
                ),
                InlineKeyboardButton(
                    text=get_translate(code)['difficulty.hard'],
                    callback_data=DifficultyFilter(level='hard').pack()
                )
            ]
        ]
    )