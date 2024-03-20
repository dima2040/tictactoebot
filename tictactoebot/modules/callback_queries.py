from aiogram import Bot, Router, types
import os

from ..filters import InviteFilter

router = Router()

@router.callback_query(InviteFilter.filter())
async def on_invite_btn(query: types.CallbackQuery, callback_data: InviteFilter):
    if query.from_user.id == callback_data.author:
        await query.message.delete()

    await query.answer('Игра началась!')