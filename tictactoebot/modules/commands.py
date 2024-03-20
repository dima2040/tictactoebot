from aiogram import Bot, Router, types
import os


#bot = Bot(token=os.environ.get("TTT_API_TOKEN"))
router = Router()

async def send_pick_lang(message: types.Message, code: str):
    text = get_translate(code)["pick_lang"]
    await message.reply(text, reply_markup=make_lang_kb(get_languages_dict()))

async def send_pick_difficulty(message: types.Message, code: str):
    text = get_translate(code)["difficulty"]
    await message.reply(text, reply_markup=make_difficulty_kb(code))

@dp.message(Command("profile"))
async def on_profile(message:types.Message) :
    user = game_data.get_user(message.from_user.id)
    username = message.chat.full_name

    text = translate(user.language, 'profile')
    text = text.format (username, user.language, user.difficulty)
    await message.reply(text)

@dp.message(Command("languages"))
async def on_change_lang(message: types.Message):
    code = game_data.get_user(message.from_user.id).language
    await send_pick_lang(message, code)


@dp.message(Command("difficulty"))
async def on_change_difficulty(message: types.Message):
    code = game_data.get_user(message.from_user.id).difficulty
    await send_pick_difficulty(message, code)

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if game_data.has_user(user_id):
        code = game_data.get_user(user_id).language
        await message.answer(
            text=translate(code, "welcome"), reply_markup=make_menu_keyboard(code)
        )
    else:
        game_data.add_user(message.from_user.id)
        await send_pick_lang(message, message.from_user.language_code)