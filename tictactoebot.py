import asyncio
import logging
import os

from aiogram import F, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv

from tictactoebot import *
from tictactoebot.modules.inline_queries import router as InlineQueriesRouter
from tictactoebot.modules.callback_queries import router as CallbackQueriesRouter
from tictactoebot.modules.commands import router as  CommandsRouter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

load_dotenv()

api_token = os.environ.get("TTT_API_TOKEN")

bot = Bot(token=api_token)
dp = Dispatcher()

game_data = DATA_GAME


def init_game(chat_id: int, player_symbol, bot_symbol) -> None:
    """Заполняет игровое поле пустыми символами"""
    if not game_data.has_user(chat_id):
        game_data.add_user(chat_id)

    user = game_data.get_user(chat_id)
    user.player = player_symbol
    user.bot = bot_symbol
    user.clear()


def make_reply_keyboard(chat_id: int):
    """
    Cоздает пользовательскую клавиатуру.
    Клавиатура состоит из сетки кнопок 3x3,
    каждая из которых имеет индекс от 1 до 9.
    """
    keyboard = list()
    index = 0
    user = game_data.get_user(chat_id)
    for row in range(3):
        line = list()
        for column in range(3):
            index += 1
            text = user.get_cell(index)
            btn_filter = FieldFilter(
                index= index, status= text,
                user1 = chat_id, user2=0
                )
        keyboard.append(line)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def start_game(player_symbol, bot_symbol, message: types.Message):
    chat_id = message.chat.id
    init_game(chat_id, player_symbol, bot_symbol)
    username = message.chat.full_name
    user = game_data.get_user(chat_id)
    score = user.score

    message_text = translate(
        user.language, 'main_reply'
    ).format(username, 'bot')
    
      
    await message.edit_text(
        text=message_text,
        reply_markup=make_reply_keyboard(chat_id),
    )

async def send_menu(message, code):
    await message.edit_text(
        text=translate(code, "menu"), reply_markup=make_menu_keyboard(code)
    )

@dp.callback_query(MenuFilter.filter())
async def on_menu_btn(query: CallbackQuery, callback_data: MenuFilter) :
    message = query.message
    user_id = query.from_user.id
    user = game_data.get_user(user_id)
    username = message.chat.full_name
    action = callback_data.action
    
    if action == 'singleplayer':
        await message.edit_text(
            text=translate(user.language, 'welcome'),
            reply_markup=make_choice_keyboard()
        )
    elif action == 'multiplayer':
        await query.answer('Этот раздел еще не готов!')
    elif action == 'profile':
        text = translate(user.language, 'profile')
        text = text.format(username, user.language, user.difficulty)
        await message.edit_text(text, reply_markup=make_back_kb(user.language))
 
    elif action == 'language':
       text = translate(user.language,"pick_lang")
       await message.edit_text(text, reply_markup=make_lang_kb(get_languages_dict()))    
    
    elif action == 'difficulty':
       text = translate(user.language,"difficulty")
       await message.edit_text(text, reply_markup=make_difficulty_kb(user.language))
    elif action == 'back':
        await send_menu(message, user.language)

@dp.callback_query(LanguageFilter.filter())
async def on_language_picked(query: CallbackQuery, callback_data: LanguageFilter):
    if query.message is None:
        return
    code = callback_data.code
    user_id = query.from_user.id

    game_data.change_user_language(user_id, code)

    await send_menu(query.message, code)

@dp.callback_query(DifficultyFilter.filter())
async def on_difficulty_picked(query: CallbackQuery, callback_data: DifficultyFilter):
    if query.message is None:
        return

    level = callback_data.level
    user_id = query.from_user.id
    game_data.change_user_difficulty(user_id, level)
    user = game_data.get_user(user_id)
    language = user.language

    await send_menu (query.message, language)


@dp.callback_query(FieldFilter.filter(F.index == -1))
async def on_choice_key_pressed(query: CallbackQuery, callback_data: FieldFilter):
    if query.message is None:
        return

    player_symbol = callback_data.status
    if player_symbol == Symbol.CROSS:
        bot_symbol = Symbol.ZERO
    else:
        bot_symbol = Symbol.CROSS

    await start_game(player_symbol, bot_symbol, query.message)


@dp.callback_query(FieldFilter.filter(F.index > 0))
async def on_board_pressed(query: CallbackQuery, callback_data: FieldFilter):
    message = query.message
    if message is None:
        return

    chat_id = message.chat.id
    player_name = message.chat.full_name
    user = game_data.get_user(chat_id)
    # TODO Load user score from db
    score = user.score

    if not user.is_cell_empty(callback_data.index):
         return

    user.user_step(callback_data.index)
    user.bot_step()
    await message.edit_reply_markup(reply_markup=make_reply_keyboard(chat_id))
    winner = user.end_game(player_name)
    if winner:
        await message.delete_reply_markup()
        score_text = get_translate(user.language)["main_reply"]
        await message.edit_text(
            winner
            + "\n"
            + score_text.format(player_name, score.player, score.bot, score.draw)
        )


async def main():
    dp.include_router(InlineQueriesRouter)
    dp.include_router(CallbackQueriesRouter)
    dp.include_router(CommandsRouter)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
