from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .translate import get_translate
from .filters import LanguageFilter, DifficultyFilter


def make_lang_kb(langs: dict):
    return make_splited_inline_kb(langs, size=2, filt=LanguageFilter)


def make_splited_inline_kb(langs: dict, size: int=3, filt=None):
    parent, child = list(), list()
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