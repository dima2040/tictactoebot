from contextlib import contextmanager
import random
from abc import ABC, abstractmethod


class AI(ABC):
    def __init__(self, board: dict[int, int]):
        """
        Инициализирует игровое поле вида
        board (dict[int, int]): {
            1:-1, 2: 1, 3: 0,
            4: 0, 5: 0, 6: 0,
            7: 0, 8: 0, 9:-1}

        1 всегда обозначает текущего игрока,
        0 пустую ячейку,
        -1 ячейку занятую оппонентом
        """
        self.board: dict[int, int] = board

    @abstractmethod
    def move(self) -> int:
        """
        Возвращает индекс следующего хода на доске
        """


class RandomAI(AI):
    """
    Возвращает индекс случайной
    свободной ячейки на игровом поле
    """

    def _get_empty_indexes(self) -> list[int]:
        return [i for i, v in self.board.items() if v == 0]

    def move(self) -> int:
        return random.choice(self._get_empty_indexes())


class MiniMaxAI(AI):
    WINNING_COMBINATIONS = {
        (1, 2, 3), (4, 5, 6), (7, 8, 9),
        (1, 4, 7), (2, 5, 8), (3, 6, 9),
        (1, 5, 9), (3, 5, 7),
    }

    def move(self) -> int:
        """
        Возвращает оптимальный следующий ход на основе алгоритма MiniMax.

        Возвращает:
            int: Индекс оптимального следующего хода на игровой доске.
        """
        best_score = float("-inf")
        best_move = None

        for i in self.board.keys():
            if self.board[i] == 0:
                with self.set_board(i, 1):
                    score = self.minimax(self.board, 0, False)
                if score > best_score:
                    best_score = score
                    best_move = i

        return best_move

    @contextmanager
    def set_board(self, index: int, value: int):
        """
        Временно изменяет игровое поле, устанавливая значение по указанному индексу.
        Исходное значение сохраняется и восстанавливается после оператора yield.
        """
        original_value = self.board[index]
        self.board[index] = value
        try:
            yield
        finally:
            self.board[index] = original_value


    def minimax(self, board: dict[int, int], depth: int, is_maximizing: bool):
        """
        Метод minimax реализует алгоритм MiniMax для определения оптимального следующего хода на игровой доске.
        
        Параметры:
            board (dict[int, int]): Текущее состояние игровой доски в виде словаря, где ключи - индексы ячеек, 
                                    значения - символы, обозначающие состояние ячейки (-1, 0, 1).
            depth (int): Текущая глубина рекурсии.
            is_maximizing (bool): Флаг, указывающий, является ли текущий ход максимизирующим или минимизирующим.
            
        Возвращает:
            int: Оценочный счет лучшего хода для текущего игрока.
            
        Алгоритм:
            1. Проверяем, является ли текущее состояние доски выигрышным для одного из игроков.
            Если да, возвращаем соответствующий счет (1 для победы, -1 для проигрыша).
            2. Проверяем, является ли текущее состояние доски ничьей.
            Если да, возвращаем счет 0.
            3. Если текущий ход максимизирующий:
            - Инициализируем переменную best_score с отрицательной бесконечностью.
            - Для каждой свободной ячейки на доске:
                - Устанавливаем значение ячейки равным 1 (символ текущего игрока).
                - Вызываем рекурсивно метод minimax для следующего хода с флагом is_maximizing=False.
                - Восстанавливаем значение ячейки.
                - Если полученный счет больше, чем best_score, обновляем best_score.
            - Возвращаем best_score.
            4. Если текущий ход минимизирующий:
            - Инициализируем переменную best_score с положительной бесконечностью.
            - Для каждой свободной ячейки на доске:
                - Устанавливаем значение ячейки равным -1 (символ оппонента).
                - Вызываем рекурсивно метод minimax для следующего хода с флагом is_maximizing=True.
                - Восстанавливаем значение ячейки.
                - Если полученный счет меньше, чем best_score, обновляем best_score.
            - Возвращаем best_score.
        """
        if self.check_is_win(1):
            return 1
        elif self.check_is_win(-1):
            return -1
        elif self.check_draw():
            return 0

        if is_maximizing:
            best_score = float("-inf")
            for i in board.keys():
                if board[i] == 0:
                    board[i] = 1
                    score = self.minimax(board, depth + 1, False)
                    board[i] = 0
                    if score > best_score:
                        best_score = score
            return best_score
        else:
            best_score = float("inf")
            for i in board.keys():
                if board[i] == 0:
                    board[i] = -1
                    score = self.minimax(board, depth + 1, True)
                    board[i] = 0
                    if score < best_score:
                        best_score = score
            return best_score

    def check_is_win(self, symbol: int):
        """
        Проверяет, выиграл ли указанный символ в игре.

        Параметры:
            symbol (int): Символ, который нужно проверить на выигрыш (-1 или 1).

        Возвращает:
            bool: True, если символ выиграл игру, False - в противном случае.
        """
        for combination in self.WINNING_COMBINATIONS:
            if all(self.board[i] == symbol for i in combination):
                return True
        return False

    def check_draw(self):
        """
        Проверяет, является ли игра ничьей.

        Возвращает:
            bool: True, если игра закончилась ничьей, False - в противном случае.
        """
        for v in self.board.values():
            if v == 0:
                return False
        return True


def test1():
    board = {
        1: -1, 2: 1, 3: 0, 
        4: 0,  5: 0, 6: 0, 
        7: 0,  8: 0, 9: -1
    }
    move = MiniMaxAI(board).move()
    assert move == 5


def test2():
    board = {
        1: -1, 2: 1, 3: 0, 
        4: -1, 5: 1, 6: 0, 
        7: 0,  8: 0, 9: -1
    }
    move = MiniMaxAI(board).move()
    assert move == 7


if __name__ == "__main__":
    test1()
    test2()
