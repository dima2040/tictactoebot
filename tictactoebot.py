import asyncio
import logging
import os
from typing import Optional

from aiogram import F, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from dotenv import load_dotenv

from tictactoebot.ai import make_random_move, make_minimax_move


logging.basicConfig(level=logging.INFO)

load_dotenv()

api_token = os.environ.get("TTT_API_TOKEN")

bot = Bot(token=api_token)
dp = Dispatcher()

CROSS_SYMBOL = '❌'
ZERO_SYMBOL = '⭕'
EMPTY_SYMBOL = ' '
game_data = dict()


class ButtonFilter(CallbackData, prefix = 'btn'):
    index: int
    status: str


def clear_board(chat_id: int) -> None:
    """Заполняет игровое поле пустыми символами"""
    if not chat_id in game_data.keys():
        game_data[chat_id] = dict()

    for i in range(1, 10):
        game_data[chat_id][i] = EMPTY_SYMBOL


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
        return f"{player_name} победил!\n/start для начала новой игры"
    
    if is_winner(game_data[chat_id], bot):
        clear_board(chat_id)
        game_data[chat_id]['score']['bot'] += 1
        return "Бот победил!\n/start для начала новой игры"
    
    values = list(game_data[chat_id].values())
    if not EMPTY_SYMBOL in values:
        clear_board(chat_id)
        game_data[chat_id]['score']['tie'] += 1
        return "Ничья!\n/start для начала новой игры"

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


def bot_step(chat_id: int):
    """
    Делает ход ИИ
    """
    empty_cells = get_free_positions(chat_id)

    if len(empty_cells) == 0: 
        return

    bot = game_data[chat_id]['bot']
    move = make_random_move(empty_cells)
    # board_list = [game_data[chat_id][i] for i in range(1, 10)]
    # available_moves = [k - 1 for k, v in game_data[chat_id].items() if v == EMPTY_SYMBOL]
    # move = make_minimax_move(available_moves, board_list)
    game_data[chat_id][move] = bot


def get_free_positions(chat_id: int) -> list:
    """Получение списка доступных ходов на игровом поле"""
    return [k for k, v in game_data[chat_id].items() if v == EMPTY_SYMBOL]


def user_step(chat_id: int, index):
    """
    Проверяет есть ли уже символ отличный от пустого
    в случае если он не задан устанавливает символ игрока
    """
    try:
        player = game_data[chat_id]['player']
    except KeyError:
        return
    if game_data[chat_id][index] == EMPTY_SYMBOL:
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
    keyboard.append([
        InlineKeyboardButton(
            text=CROSS_SYMBOL, 
            callback_data=ButtonFilter(index=-1, status=CROSS_SYMBOL).pack()
        ),
        InlineKeyboardButton(
            text=ZERO_SYMBOL, 
            callback_data=ButtonFilter(index=-1, status=ZERO_SYMBOL).pack()
        )
    ])
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
    chat_id = message.chat.id
    clear_board(chat_id)
    init_score(chat_id)
    game_data[chat_id]['player'] = player_symbol
    game_data[chat_id]['bot'] = bot_symbol
    
    username = message.chat.full_name
    player_score = game_data[chat_id]['score']['player']
    bot_score = game_data[chat_id]['score']['bot']
    tie_score = game_data[chat_id]['score']['tie']
    await message.edit_text(
           text = f"Текущий счёт: \n{username}: {player_score}\nБот: {bot_score}\nНичья: {tie_score}",
           reply_markup=make_reply_keyboard(chat_id))


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    welcome_text = "Привет! Выбери, за кого хочешь играть!"
    await message.reply(welcome_text, reply_markup=make_choice_keyboard())


@dp.callback_query(ButtonFilter.filter(F.index == -1))
async def on_choice_key_pressed(query: CallbackQuery, callback_data: ButtonFilter):
    if query.message is None: 
        return
    
    player_symbol = callback_data.status
    if player_symbol == CROSS_SYMBOL:
        bot_symbol = ZERO_SYMBOL
    else:
        bot_symbol = CROSS_SYMBOL

    await start_game(player_symbol, bot_symbol, query.message)


@dp.callback_query(ButtonFilter.filter(F.index > 0))
async def on_key_pressed_new(query: CallbackQuery, callback_data: ButtonFilter):
    message = query.message
    if message is None: 
        return
    
    chat_id = message.chat.id
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
