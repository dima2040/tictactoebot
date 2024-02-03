import asyncio
import logging
import os
import random
from typing import Optional

from aiogram import F, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv

from tictactoebot import *

     
logging.basicConfig(level=logging.INFO)

load_dotenv()

api_token = os.environ.get("TTT_API_TOKEN")

bot = Bot(token=api_token)
dp = Dispatcher()

game_data = dict()

langs = load_user_languages()
difficulties = load_user_difficulty()


def clear_board(chat_id: int) -> None:
    """Заполняет игровое поле пустыми символами"""
    if not chat_id in game_data.keys():
        game_data[chat_id] = dict()

    for i in range(1, 10):
        game_data[chat_id][i] = Symbol.EMPTY


def end_game(chat_id: int, player_name) -> Optional[str]:
    """
    Проверяет на выйгрышную комбинацию или ничью игрока и бота,
    в случае конца игры очищает доску и возвращает текст с
    поздравлением победителя
    """
    player = game_data[chat_id]['player']
    bot = game_data[chat_id]['bot']
    if is_winner(game_data[chat_id], player):
        clear_board(chat_id)
        game_data[chat_id]['score']['player'] += 1
        end_game_text =  get_translate(langs[chat_id])['win.player']
        return end_game_text.format(player_name)
    
    if is_winner(game_data[chat_id], bot):
        clear_board(chat_id)
        game_data[chat_id]['score']['bot'] += 1
        end_game_text =  get_translate(langs[chat_id])['win.bot']
        return end_game_text
    
    values = list(game_data[chat_id].values())
    if not Symbol.EMPTY in values:
        clear_board(chat_id)
        game_data[chat_id]['score']['tie'] += 1
        end_game_text =  get_translate(langs[chat_id])['draw']
        return end_game_text

    return None


def is_winner(bo, le):
    """
    При задании доски и символа игрока эта функция возвращает True, если игрок выиграл.
    Мы используем bo вместо board и le вместо letter, чтобы не набирать много текста.
    """
    return (
        (bo[7] == le and bo[8] == le and bo[9] == le) or
        (bo[4] == le and bo[5] == le and bo[6] == le) or
        (bo[1] == le and bo[2] == le and bo[3] == le) or
        (bo[7] == le and bo[4] == le and bo[1] == le) or
        (bo[8] == le and bo[5] == le and bo[2] == le) or
        (bo[9] == le and bo[6] == le and bo[3] == le) or
        (bo[7] == le and bo[5] == le and bo[3] == le) or
        (bo[9] == le and bo[5] == le and bo[1] == le)
    )


def bot_step(chat_id):
    """
    Делает ход ИИ
    """
    empty_cells = get_free_positions(chat_id)
    if len(empty_cells) == 0: 
        return
    
    bot = game_data[chat_id]['bot']
    current_player_data = game_data[chat_id]
    ai_board = {i: get_cell_value_for_ai(current_player_data, current_player_data[i]) for i in range(1, 10)}
    ai_mapping = {
        "easy": RandomAI,
        "hard": MiniMaxAI
    }
    move = ai_mapping[difficulties[chat_id]](ai_board).move()
    game_data[chat_id][move] = bot 


def get_cell_value_for_ai(current_player_data: dict, value: Symbol) -> int:
    if value == current_player_data["bot"]:
        return 1
    if value == current_player_data["player"]:
        return -1
    if value == Symbol.EMPTY:
        return 0
    raise ValueError


def get_free_positions(chat_id: int) -> list:
    """Получение списка доступных ходов на игровом поле"""
    return [k for k, v in game_data[chat_id].items() if v == Symbol.EMPTY]


def user_step(chat_id: int, index):
    """
    Проверяет есть ли уже символ отличный от пустого
    в случае если он не задан устанавливает символ игрока
    """
    try:
        player = game_data[chat_id]['player']
    except KeyError:
        return
    if game_data[chat_id][index] == Symbol.EMPTY:
        game_data[chat_id][index] = player


def make_reply_keyboard(chat_id: int):
    """
    Cоздает пользовательскую клавиатуру.
    Клавиатура состоит из сетки кнопок 3x3,
    каждая из которых имеет индекс от 1 до 9.
    """
    keyboard = list()
    index = 0
    for row in range(3):
        line = list()
        for column in range(3):
            index += 1
            text = game_data[chat_id][index]
            btn_filter = ButtonFilter(index=index, status=text)
            line.append(InlineKeyboardButton(text=text, callback_data=btn_filter.pack()))
        keyboard.append(line)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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


def init_score(chat_id: int):
    """
    Инициализирует подсчет очков для конкретного пользователя
    """
    if not 'score' in game_data[chat_id]:
        game_data[chat_id]['score'] = {
            'bot' : 0,
            'player' : 0,
            'tie': 0
        }


async def start_game(player_symbol, bot_symbol, message: types.Message):
    chat_id = str(message.chat.id)
    clear_board(chat_id)
    init_score(chat_id)
    game_data[chat_id]['player'] = player_symbol
    game_data[chat_id]['bot'] = bot_symbol
    
    username = message.chat.full_name
    player_score = game_data[chat_id]['score']['player']
    bot_score = game_data[chat_id]['score']['bot']
    tie_score = game_data[chat_id]['score']['tie']
    message_text = get_translate(langs[chat_id])['main_reply']
    await message.edit_text(
        text=message_text.format(username, player_score, bot_score, tie_score),
        reply_markup=make_reply_keyboard(chat_id),
    )


@dp.message(Command('languages'))
async def on_change_lang(message: types.Message):
    code = langs[str(message.from_user.id)]
    await send_pick_lang(message, code)


@dp.message(Command('difficulty'))
async def on_change_difficulty(message: types.Message):
    code = langs[str(message.from_user.id)]
    await send_pick_difficulty(message, code)


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id in langs.keys():
        code = langs[user_id]
        await message.reply(
            text=get_translate(code)['welcome'], 
            reply_markup=make_choice_keyboard()
        )
    else:
        text = get_translate(message.from_user.language_code)['pick_lang']
        await send_pick_lang(message, text)


async def send_pick_lang(message: types.Message, code: str):
    text = get_translate(code)['pick_lang']
    await message.reply(
        text, 
        reply_markup=make_lang_kb(get_languages_dict())
    )


async def send_pick_difficulty(message: types.Message, code: str):
    text = get_translate(code)['difficulty']
    await message.reply(
        text,
        reply_markup=make_difficulty_kb(code)
    )


@dp.callback_query(LanguageFilter.filter())
async def on_language_picked(query: CallbackQuery, callback_data: LanguageFilter):
    if query.message is None: return
    code = callback_data.code
    user_id = str(query.from_user.id)
    
    langs[user_id] = code
    save_user_languages(langs)
    
    await query.message.edit_text(
        text=get_translate(code)['welcome'], 
        reply_markup=make_choice_keyboard()
    )


@dp.callback_query(DifficultyFilter.filter())
async def on_difficulty_picked(query: CallbackQuery, callback_data: DifficultyFilter):
    if query.message is None: return
    level = callback_data.level
    user_id = str(query.from_user.id)
    
    difficulties[user_id] = level
    save_user_difficulty(difficulties)
    code = langs[user_id]

    await query.message.edit_text(
        text=get_translate(code)['welcome'], 
        reply_markup=make_choice_keyboard()
    )


@dp.callback_query(ButtonFilter.filter(F.index == -1))
async def on_choice_key_pressed(query: CallbackQuery, callback_data: ButtonFilter):
    if query.message is None: 
        return
    
    player_symbol = callback_data.status
    if player_symbol == Symbol.CROSS:
        bot_symbol = Symbol.ZERO
    else:
        bot_symbol = Symbol.CROSS

    await start_game(player_symbol, bot_symbol, query.message)


@dp.callback_query(ButtonFilter.filter(F.index > 0))
async def on_key_pressed_new(query: CallbackQuery, callback_data: ButtonFilter):
    message = query.message
    if message is None: 
        return
    
    chat_id =str(message.chat.id)
    player_name = message.chat.full_name
    user_step(chat_id, callback_data.index)
    bot_step(chat_id)
    await message.edit_reply_markup(reply_markup=make_reply_keyboard(chat_id))
    winner = end_game(chat_id, player_name)
    if winner:
        await message.delete_reply_markup()
        await message.edit_text(winner)


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
