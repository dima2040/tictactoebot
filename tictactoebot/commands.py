from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from . import get_translate, get_languages_dict, translate, make_lang_kb, make_difficulty_kb, make_menu_keyboard
from tictactoebot.data import DATA_GAME


router = Router()


async def _send_pick_lang(message: types.Message, code: str):
    text = get_translate(code)["pick_lang"]
    await message.reply(text, reply_markup=make_lang_kb(code, get_languages_dict()))


async def _send_pick_difficulty(message: types.Message, code: str):
    text = get_translate(code)["difficulty"]
    await message.reply(text, reply_markup=make_difficulty_kb(code))


@router.message(Command("profile"))
async def on_profile(message:types.Message) :
    user = DATA_GAME.get_user(message.from_user.id)
    username = message.chat.full_name

    text = translate(user.language, 'profile')
    text = text.format (username, user.language, user.difficulty)
    await message.reply(text)

@router.message(Command("languages"))
async def on_change_lang(message: types.Message):
    code = DATA_GAME.get_user(message.from_user.id).language
    await _send_pick_lang(message, code)


@router.message(Command("difficulty"))
async def on_change_difficulty(message: types.Message):
    code = DATA_GAME.get_user(message.from_user.id).difficulty
    await _send_pick_difficulty(message, code)

@router.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if DATA_GAME.has_user(user_id):
        code = DATA_GAME.get_user(user_id).language
        await message.answer(
            text=translate(code, "welcome"), reply_markup=make_menu_keyboard(code)
        )
    else:
        DATA_GAME.add_user(message.from_user.id)
        await _send_pick_lang(message, message.from_user.language_code)