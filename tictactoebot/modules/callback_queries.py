from aiogram import Bot, Router, types, F
from aiogram.types import CallbackQuery
import os

from ..constants import BOT_TOKEN, DATA_GAME
from ..filters import InviteFilter
from ..keyboards import make_board_keyboard
from ..data import Symbol
from ..keyboards import *
from ..filters import *

bot = Bot(BOT_TOKEN)
router = Router()

@router.callback_query(InviteFilter.filter())
async def on_invite_btn(query: types.CallbackQuery, callback_data: InviteFilter):
    if query.from_user.id == callback_data.author:
        await query.answer('Вы автор приглашения!')
        return

    author_obj = await bot.get_chat(callback_data.author)
    author_name = author_obj.full_name
    target_name = query.from_user.full_name

    DATA_GAME.init_game(
        callback_data.author, query.from_user.id,
        Symbol.CROSS, Symbol.ZERO
    )

    await bot.edit_message_text(
        text =f"{author_name}  vs  {target_name}",
        inline_message_id=query.inline_message_id,
        reply_markup=make_board_keyboard(query.from_user.id)
    )

async def start_game(player_symbol, bot_symbol, message: types.Message):
    chat_id = message.chat.id
    DATA_GAME.init_game(chat_id, player_symbol, bot_symbol)
    username = message.chat.full_name
    user = DATA_GAME.get_user(chat_id)
    score = user.score

    message_text = translate(
        user.language, 'main_reply'
    ).format(username, 'bot')
    
      
    await message.edit_text(
        text=message_text,
        reply_markup=make_board_keyboard(chat_id),
    )



@router.callback_query(FieldFilter.filter(F.index == -1))
async def on_choice_key_pressed(query: CallbackQuery, callback_data: FieldFilter):
    if query.message is None:
        return

    player_symbol = callback_data.status
    if player_symbol == Symbol.CROSS:
        bot_symbol = Symbol.ZERO
    else:
        bot_symbol = Symbol.CROSS

    await start_game(player_symbol, bot_symbol, query.message)

