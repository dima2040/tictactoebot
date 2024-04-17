from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .translate import translate, get_translate
from .data import Symbol
from .filters import *
from .constants import DATA_GAME
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
                callback_data=FieldFilter(
                    index=-1, status=Symbol.CROSS,
                    user1 = 0, user2 = 0
                ).pack(),
            ),
            InlineKeyboardButton(
                text=Symbol.ZERO,
                callback_data=FieldFilter(
                    index=-1, status=Symbol.ZERO,
                    user1 = 0, user2 = 0
            ).pack(),
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
def make_menu_keyboard(code):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=translate(code, 'menu.singleplayer'),
                    callback_data=MenuFilter(action='singleplayer').pack()
                ),
                InlineKeyboardButton(
                    text=translate(code, 'menu.multiplayer'),
                    callback_data=MenuFilter(action='multiplayer').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=translate(code, 'menu.profile'),
                    callback_data=MenuFilter(action='profile').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=translate(code, 'menu.language'),
                    callback_data=MenuFilter(action='language').pack()
                ),
                InlineKeyboardButton(
                    text=translate(code, 'menu.difficulty'),
                    callback_data=MenuFilter(action='difficulty').pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text=translate(code, 'menu.achievements'),
                    callback_data=MenuFilter(action='achievements').pack()

                )
            ]
        ]
    )  
           

      
        
def make_back_kb(language): 
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=translate(language, 'menu.back'),
                    callback_data=MenuFilter(action='back').pack()
                )
            ]
        ]
    )

def make_invite_kb(authorId, language):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=translate(language, 'mp.invite_btn'),
                    callback_data=InviteFilter(
                        author=authorId
                    ).pack()
                )
            ]
        ]
    )

def make_board_keyboard(chat_id: int):
    """
    Cоздает пользовательскую клавиатуру.
    Клавиатура состоит из сетки кнопок 3x3,
    каждая из которых имеет индекс от 1 до 9.
    """
    keyboard = list()
    index = 0
    user = DATA_GAME.get_user(chat_id)
    for row in range(3):
        line = list()
        for column in range(3):
            index += 1
            text = user.get_cell(index)
            btn_filter = FieldFilter(
                index= index, status= text,
                user1 = chat_id, user2=0
                )
            btn = InlineKeyboardButton(
                text=text,
                callback_data=btn_filter.pack()
            )
            line.append(btn)
        keyboard.append(line)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
