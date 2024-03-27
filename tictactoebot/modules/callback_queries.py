from aiogram import Bot, Router, types
import os

from ..constants import BOT_TOKEN, DATA_GAME
from ..filters import InviteFilter
from ..keyboards import make_reply_keyboard

bot = Bot(BOT_TOKEN)
router = Router()

@router.callback_query(InviteFilter.filter())
async def on_invite_btn(query: types.CallbackQuery, callback_data: InviteFilter):
    if query.from_user.id == callback_data.author:
        await query.answer('Вы автор приглашения!')

    author_obj = await bot.get_chat(callback_data.author)
    author_name = author_obj.full_name
    target_name = query.from_user.full_name

    author = DATA_GAME.get_user(callback_data.author)
    author.target_id = query.from_user.id

    target = DATA_GAME.get_user(query.from_user.id)
    target.target_id = callback_data.author



    await bot.edit_message_text(
        text =f"{author_name}  vs  {target_name}",
        inline_message_id=query.inline_message_id,
        reply_markup=make_reply_keyboard(query.from_user.id)
    )