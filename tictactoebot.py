import asyncio
import logging
import os

from aiogram import F, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

from tictactoebot import *
from tictactoebot.modules.inline_queries import router as InlineQueriesRouter
from tictactoebot.modules.callback_queries import router as CallbackQueriesRouter
from tictactoebot.modules.commands import router as  CommandsRouter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

game_data = DATA_GAME




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
    await message.edit_reply_markup(reply_markup=make_board_keyboard(chat_id))
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
