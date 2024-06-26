from aiogram import Bot, Router, types, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode

from .translate import get_languages_dict
from .config import BOT_TOKEN
from tictactoebot.data import DATA_GAME
from .filters import InviteFilter
from .keyboards import make_board_keyboard
from tictactoebot.enums import Symbol
from .keyboards import *
from .filters import *


bot = Bot(BOT_TOKEN)
router = Router()


@router.callback_query(InviteFilter.filter())
async def on_invite_btn(query: types.CallbackQuery, callback_data: InviteFilter):
    if query.from_user.id == callback_data.author:
        await query.answer('Вы не можете играть сам с собой!')
        return

    author_obj = await bot.get_chat(callback_data.author)
    author_name = author_obj.full_name
    target_name = query.from_user.full_name

    board = DATA_GAME.init_game(
        callback_data.author, query.from_user.id,
        author_name, target_name,
        Symbol.CROSS, Symbol.ZERO
    )

    await bot.edit_message_text(
        text =f"{author_name}  vs  {target_name}\n\nХодит {author_name}.",
        inline_message_id=query.inline_message_id,
        reply_markup=make_board_keyboard(board, query.from_user.id)
    )


async def _start_game(author_id, target_id, player_symbol, bot_symbol, message: types.Message):
    username = message.chat.full_name
    board = DATA_GAME.init_game(
        author_id, target_id,
        username, 'Bot',
        player_symbol, bot_symbol
    )
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

    await _start_game(query.from_user.id, 0, player_symbol, bot_symbol, query.message)


@router.callback_query(FieldFilter.filter(F.index > 0))
async def on_board_pressed(query: CallbackQuery, callback_data: FieldFilter):
    """
    Функция, запускающаяся при нажатии на любую клетку на поле
    """
    message = query.message

    # Получаем игровое поле по его айди, записанном в кнопке
    board = DATA_GAME.get_board(callback_data.board_id)
    # Получаем айди пользователя, нажавшего на кнопку
    user_id = query.from_user.id
    
    # Если айди пользователя не совпадает с игроками, записанными в поле, то 
    # пропускаем это нажатие и завершаем функцию
    if not user_id in (board.author_id, board.target_id):
        await query.answer("Вы не участвуете в игре!")
        return
    if user_id != board.next_step:
        await query.answer("Сейчас не ваш ход!")
        return

    # Получаем класс пользователя, его имя и счет
    player_name = query.from_user.full_name
    user = DATA_GAME.get_user(user_id)
    score = user.score

    # Если нажатая клетка не пустая, то пропускаем действие
    if not board.is_cell_empty(callback_data.index):
        await query.answer("Эта клетка занята!")
        return

    # Делаем ход от лица пользователя в нажатую клетку
    board.user_step(user_id, callback_data.index)
    # Если айди противника - 0 (он бот), то делаем за него ход
    if board.target_id == 0:
        board.bot_step(user.difficulty)

    if user_id == board.author_id:
        next_step_user_name = board.target_name
    else:
        next_step_user_name = board.author_name

    # Обновляем клавиатуру после хода игроков
    if message is None:
        await bot.edit_message_text(
            text=f"{board.author_name} vs {board.target_name}\n\nХодит: {next_step_user_name}",
            inline_message_id=query.inline_message_id,
            reply_markup=make_board_keyboard(board, user_id)
        )
    else:
        await message.edit_text(
            text=f"{board.author_name} vs {board.target_name}\n\nХодит: {next_step_user_name}",
            reply_markup=make_board_keyboard(board, user_id)
        ) 

    # Проверяем победителя, если кто-то победил - удаляем поле и редактируем сообщение
    winner = board.end_game(player_name, "target", user.language)
    if winner:
        score_text = get_translate(user.language)["main_reply"]
        if message is None: # Если используется inline сообщение (100% мультиплеер)
            await bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id
            )
            await bot.edit_message_text(
                winner
                + "\n"
                + score_text.format(player_name, score.player, score.bot, score.draw),
                inline_message_id=query.inline_message_id,
                reply_markup=make_restart_mp_kb(user.language),

            )
        else:
            await message.delete_reply_markup()
            await message.edit_text(
                winner
                + "\n"
                + score_text.format(player_name, score.player, score.bot, score.draw),
                 reply_markup=make_restart_sp_kb(user.language)
            )


async def _send_menu(message, code):
    await message.edit_text(
        text=translate(code, "menu"), reply_markup=make_menu_keyboard(code)
    )


@router.callback_query(MenuFilter.filter())
async def on_menu_btn(query: CallbackQuery, callback_data: MenuFilter) :
    message = query.message
    user_id = query.from_user.id
    user = DATA_GAME.get_user(user_id)
    username = message.chat.full_name
    action = callback_data.action
    
    if action == 'singleplayer':
        await message.edit_text(
            text=translate(user.language, 'welcome'),
            reply_markup=make_choice_keyboard()
        )
    elif action == 'achievements':
        await query.answer('Этот раздел еще не готов!')
    elif action == 'profile':
        text = translate(user.language, 'profile')
        text = text.format(
            username, user.language,
            user.difficulty, user.score.player,
            user.score.bot, user.score.enemy,
            user.score.draw)
        await message.edit_text(
        text, reply_markup=make_back_kb(user.language),
        parse_mode = ParseMode.HTML
        )
 
    elif action == 'language':
       text = translate(user.language,"pick_lang")
       await message.edit_text(text, reply_markup=make_lang_kb(
           user.language, get_languages_dict()
       ))

    
    elif action == 'difficulty':
       text = translate(user.language,"difficulty")
       await message.edit_text(text, reply_markup=make_difficulty_kb(user.language))
    elif action == 'back':
        await _send_menu(message, user.language)


@router.callback_query(LanguageFilter.filter())
async def on_language_picked(query: CallbackQuery, callback_data: LanguageFilter):
    if query.message is None:
        return
    code = callback_data.code
    user_id = query.from_user.id

    DATA_GAME.change_user_language(user_id, code)

    await _send_menu(query.message, code)


@router.callback_query(DifficultyFilter.filter())
async def on_difficulty_picked(query: CallbackQuery, callback_data: DifficultyFilter):
    if query.message is None:
        return

    level = callback_data.level
    user_id = query.from_user.id
    DATA_GAME.change_user_difficulty(user_id, level)
    user = DATA_GAME.get_user(user_id)
    language = user.language

    await _send_menu (query.message, language)