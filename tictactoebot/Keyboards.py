from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .filters import LanguageFilter


def make_lang_kb(langs: dict):
    return make_splited_inline_kb(langs, filt=LanguageFilter)
def make_splited_inline_kb(data: dict, size: int=3, filt=None):
    parent, child = list(), list()
    parent.append(child)
    index = 0 
    for key, value in data.items():
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