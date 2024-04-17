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

    board = DATA_GAME.init_game(
        callback_data.author, query.from_user.id,
        Symbol.CROSS, Symbol.ZERO
    )

    await bot.edit_message_text(
        text =f"{author_name}  vs  {target_name}",
        inline_message_id=query.inline_message_id,
        reply_markup=make_board_keyboard(board, query.from_user.id)
    )

async def start_game(author_id, target_id, player_symbol, bot_symbol, message: types.Message):
    board = DATA_GAME.init_game(
    author_id, target_id, player_symbol, bot_symbol
    )
    username = message.chat.full_name
    user = DATA_GAME.get_user(author_id)
    score = user.score

    message_text = translate(
        user.language, 'main_reply'
    ).format(username, 'bot')
    
      
    await message.edit_text(
        text=message_text,
        reply_markup=make_board_keyboard(board, author_id),
    )



@router.callback_query(PickFilter.filter())
async def on_choice_key_pressed(query: CallbackQuery, callback_data: PickFilter):
    if query.message is None:
        return

    player_symbol = callback_data.value
    if player_symbol == Symbol.CROSS:
        bot_symbol = Symbol.ZERO
    else:
        bot_symbol = Symbol.CROSS

    await start_game(query.from_user.id, 0, player_symbol, bot_symbol, query.message)

@router.callback_query(FieldFilter.filter(F.index > 0))
async def on_board_pressed(query: CallbackQuery, callback_data: FieldFilter):
    """
    Функция, запускающаяся при нажатии на любую клетку на поле
    """
    message = query.message
    if message is None:
        return

    # Получаем игровое поле по его айди, записанном в кнопке
    board = DATA_GAME.get_board(callback_data.board_id)
    # Получаем айди пользователя, нажавшего на кнопку
    user_id = query.from_user.id
    
    # Если айди пользователя не совпадает с игроками, записанными в поле, то 
    # пропускаем это нажатие и завершаем функцию
    if not user_id in (board.author_id, board.target_id):
        return

    # Получаем класс пользователя, его имя и счет
    player_name = message.chat.full_name
    user = DATA_GAME.get_user(user_id)
    score = user.score

    # Если нажатая клетка не пустая, то пропускаем действие
    if not board.is_cell_empty(callback_data.index):
        return

    # Делаем ход от лица пользователя в нажатую клетку
    board.user_step(user_id, callback_data.index)
    # Если айди противника - 0 (он бот), то делаем за него ход
    if board.target_id == 0:
        user.bot_step()

    # Обновляем клавиатуру после хода игроков
    await message.edit_reply_markup(reply_markup=make_board_keyboard(board, user_id))

    # Проверяем победителя, если кто-то победил - удаляем поле и редактируем сообщение
    winner = board.end_game(player_name)
    if winner:
        await message.delete_reply_markup()
        score_text = get_translate(user.language)["main_reply"]
        await message.edit_text(
            winner
            + "\n"
            + score_text.format(player_name, score.player, score.bot, score.draw)
        )