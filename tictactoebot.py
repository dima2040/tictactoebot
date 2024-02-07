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
#langs = load_user_languages()
#difficulties = load_user_difficulty()


def init_game(chat_id: int, player_symbol, bot_symbol) -> None:
    """Заполняет игровое поле пустыми символами"""
    if not chat_id in game_data.keys():
        game_data[chat_id] = GameData(dict())
    
    data = game_data[chat_id]
    data.player = player_symbol
    data.bot = bot_symbol
    data.clear()

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
            text = game_data[chat_id].get_cell(index)
            btn_filter = ButtonFilter(index=index, status=text)
            line.append(InlineKeyboardButton(text=text, callback_data=btn_filter.pack()))
        keyboard.append(line)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def start_game(player_symbol, bot_symbol, message: types.Message):
    chat_id = str(message.chat.id)
    init_game(chat_id, player_symbol, bot_symbol)
    
    username = message.chat.full_name
    data = game_data[chat_id]
    score = data.score
    translation = get_translate(data.language)

    message_text = translation['main_reply']
    await message.edit_text(
        text=message_text.format(
            username, score.player,
            score.bot, score.draw
        ),
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
    if user_id in game_data.keys():
        code = game_data[user_id].language
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
    
    game_data[user_id] = GameData(dict())
    data = game_data[user_id]

    data.language = code
    #save_user_languages(langs)
    
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
    data = game_data[chat_id]

    data.user_step(callback_data.index)
    data.bot_step()
    await message.edit_reply_markup(reply_markup=make_reply_keyboard(chat_id))
    winner = data.end_game(player_name)
    if winner:
        await message.delete_reply_markup()
        await message.edit_text(winner)


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
