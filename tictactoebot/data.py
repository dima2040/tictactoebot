from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional

from .translate import get_translate
from .ai import *

CROSS_SYMBOL = "❌"
ZERO_SYMBOL = "⭕"
EMPTY_SYMBOL = " "


class Symbol(StrEnum):
    CROSS = CROSS_SYMBOL
    ZERO = ZERO_SYMBOL
    EMPTY = EMPTY_SYMBOL

@dataclass
class Score:
    player: int=0
    bot: int=0
    draw: int=0

@dataclass
class GameData:
    board: dict[int, Symbol]
    player: Symbol=Symbol.CROSS
    bot: Symbol=Symbol.ZERO
    language: str="en"
    difficulty: str="easy"
    score: Score=field(
        default_factory=lambda: Score()
    )

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
            "easy": RandomAI,
            "hard": MiniMaxAI
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
            (bo[7] == le and bo[8] == le and bo[9] == le) or
            (bo[4] == le and bo[5] == le and bo[6] == le) or
            (bo[1] == le and bo[2] == le and bo[3] == le) or
            (bo[7] == le and bo[4] == le and bo[1] == le) or
            (bo[8] == le and bo[5] == le and bo[2] == le) or
            (bo[9] == le and bo[6] == le and bo[3] == le) or
            (bo[7] == le and bo[5] == le and bo[3] == le) or
            (bo[9] == le and bo[5] == le and bo[1] == le)
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
            end_game_text = get_translate(self.language)['win.player']
            return end_game_text.format(player_name)
        
        if self.is_bot_winner():
            self.clear()
            self.score.bot += 1
            end_game_text =  get_translate(self.language)['win.bot']
            return end_game_text
        
        values = list(self.board.values())
        if not Symbol.EMPTY in values:
            self.clear()
            self.score.draw += 1
            end_game_text =  get_translate(self.language)['draw']
            return end_game_text

        return None


    def copy(self):
        return deepcopy(self)
