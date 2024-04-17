from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional
import json
from .translate import get_translate
from .ai import *
from .enums import *
from .db import Database, DB_NAME

@dataclass
class Score:
    player: int = 0
    bot: int = 0
    draw: int = 0

@dataclass
class Stats:
    hard_bot_win_count: int = 0
    easy_bot_defeat_count: int = 0

@dataclass
class UserData:
    user_id: int
    board: dict[int, Symbol] = field(default_factory=lambda: dict())
    player: Symbol = Symbol.CROSS
    bot: Symbol = Symbol.ZERO
    language: str = Language.ENGLISH
    difficulty: str = Difficulty.EASY
    score: Score = field(default_factory=lambda: Score())
    stats: Stats = field(default_factory=lambda: Stats())

    target_id: int = -1


    def is_cell_empty(self, index: int) -> bool:
        if self.board[index] == Symbol.EMPTY:
            return True
        return False

    def set_cell(self, index: int, symbol: Symbol):
        self.board[index] = symbol

    def get_cell(self, index: int) -> Symbol:
        return self.board[index]

    def user_step(self, index: int):
        """
        Проверяет есть ли уже символ отличный от пустого
        в случае если он не задан устанавливает символ игрока
        """
        if self.is_cell_empty(index):
            self.set_cell(index, self.player)

    def bot_step(self):
        """
        Делает ход ИИ
        """
        empty_cells = self.get_free_positions()
        if len(empty_cells) == 0:
            return

        ai_board = {
            i: self.get_cell_value_for_ai(self.get_cell(i)) for i in range(1, 10)
        }
        ai_mapping = {
            Difficulty.EASY: RandomAI,
            Difficulty.HARD: MiniMaxAI
        }
        move = ai_mapping[self.difficulty](ai_board).move()
        self.set_cell(move, self.bot)

    def get_cell_value_for_ai(self, value: Symbol) -> int:
        if value == self.bot:
            return 1
        if value == self.player:
            return -1
        if value == Symbol.EMPTY:
            return 0
        raise ValueError

    def get_free_positions(self) -> list:
        """Получение списка доступных ходов на игровом поле"""
        return [index for index in self.board.keys() if self.is_cell_empty(index)]

    def is_bot_winner(self) -> bool:
        return self.is_winner(self.bot)

    def is_player_winner(self) -> bool:
        return self.is_winner(self.player)

    def is_winner(self, le):
        """
        При задании доски и символа игрока эта функция возвращает True, если игрок выиграл.
        Мы используем bo вместо board и le вместо letter, чтобы не набирать много текста.
        """
        bo = self.board
        return (
            (bo[7] == le and bo[8] == le and bo[9] == le)
            or (bo[4] == le and bo[5] == le and bo[6] == le)
            or (bo[1] == le and bo[2] == le and bo[3] == le)
            or (bo[7] == le and bo[4] == le and bo[1] == le)
            or (bo[8] == le and bo[5] == le and bo[2] == le)
            or (bo[9] == le and bo[6] == le and bo[3] == le)
            or (bo[7] == le and bo[5] == le and bo[3] == le)
            or (bo[9] == le and bo[5] == le and bo[1] == le)
        )

    def clear(self):
        for i in range(1, 10):
            self.set_cell(i, Symbol.EMPTY)

    def end_game(self, player_name) -> Optional[str]:
        """
        Проверяет на выйгрышную комбинацию или ничью игрока и бота,
        в случае конца игры очищает доску и возвращает текст с
        поздравлением победителя
        """
        if self.is_player_winner():
            self.clear()
            self.score.player += 1
            end_game_text = get_translate(self.language)["win.player"]
            return end_game_text.format(player_name)

        if self.is_bot_winner():
            self.clear()
            self.score.bot += 1
            end_game_text = get_translate(self.language)["win.bot"]
            return end_game_text

        values = list(self.board.values())
        if not Symbol.EMPTY in values:
            self.clear()
            self.score.draw += 1
            end_game_text = get_translate(self.language)["draw"]
            return end_game_text

        return None

    def copy(self):
        return deepcopy(self)

    @classmethod
    def from_tuple(cls, data: tuple):
        return cls(
            user_id=data[1],
            language=data[2],
            difficulty=data[3]
        )

    @classmethod
    def from_dict(cls, user_id: int, data: dict):
        return cls(
            user_id=user_id,
            language=data["language"],
            difficulty=data["difficulty"]
        )

@dataclass
class Board:
    board_id: int
    author_id: int
    target_id: int
    data: dict[int, Symbol] = field(default_factory=lambda: dict())

    @classmethod
    def create(cls, board_id: int, author_id: int,
                target_id: int):
        board = cls(
            board_id, author_id,
            target_id 
        )
        board.clear()
        return board

    def clear(self):
        for i in range(1, 10):
            self.set_cell(i, Symbol.EMPTY)

class GameData:

    def __init__(self):
        self.db = Database(DB_NAME)
        self.users = dict()
        self.boards = dict()

    def update_user_score(self, user_id: int, score: Score):
        if user_id in self.users.keys():
            self.users[user_id].score = score
        self.db.update_user_score(user_id, score.player, score.bot, score.draw)

    def get_user(self, user_id: int):
        if not self.has_user(user_id):
            return None
        
        if user_id in self.users.keys():
            return self.users[user_id]

        user = UserData.from_tuple(
            self.db.get_user_by_chat_id(user_id)
        )
        user.clear()
        self.users[user_id] = user
        return user

    def has_user(self, user_id: int):
        if user_id in self.users.keys():
            return self.users[user_id] != None
        return self.db.get_user_by_chat_id(user_id) != None

    def add_user(self, user_id: int):
        self.db.add_user(user_id)
        user = UserData(user_id)
        self.users[user_id] = user
        return user

    def change_user_language(self, user_id: int, language: Language):
        if user_id in self.users.keys():
            self.users[user_id].language = language
        self.db.change_user_language(user_id, language)
    
    def change_user_difficulty(self, user_id: int, difficulty: Difficulty):
        if user_id in self.users.keys():
            self.users[user_id].difficulty = difficulty
        self.db.change_user_difficulty(user_id, difficulty)

    def add_board(self, author_id: int, target_id: int):
        board_id = len(self.boards.keys()) + 1
        board = Board.create(board_id, author_id, target_id)
        self.boards[board_id] = board
        return board
    
    def get_board(self, board_id: int) -> Board:
        if not board_id in self.boards.keys():
            return None
        return self.boards[board_id]



    def init_game(self,
            author_id: int, target_id: int,
            author_symbol, target_symbol) -> None:
        """Проводит инициализацию игрового поля и параметров игроков"""
        author = self.get_user(author_id)
        if author is None:
            author = self.add_user(author_id)

        if target_id != 0:
            target = self.get_user(target_id)
            if target is None:
                target = self.add_user(target_id)
            author.target_id = target.user_id
            target.target_id = author.user_id
            self.add_board(author_id, target_id)
        else:
            self.add_board(author_id, 0)




