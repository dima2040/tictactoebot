from copy import deepcopy
from dataclasses import dataclass
from enum import StrEnum


CROSS_SYMBOL = "❌"
ZERO_SYMBOL = "⭕"
EMPTY_SYMBOL = " "


class Symbol(StrEnum):
    CROSS = CROSS_SYMBOL
    ZERO = ZERO_SYMBOL
    EMPTY = EMPTY_SYMBOL


@dataclass
class GameData:
    board: dict[int, Symbol]
    player: Symbol
    bot: Symbol

    def copy(self):
        return deepcopy(self)
