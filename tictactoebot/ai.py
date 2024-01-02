import random


def make_random_move(empty_cells: list[int]) -> int:
    """
    Возвращает случайную
    свободную ячейку на игровом поле
    """
    return random.choice(empty_cells)


def make_minimax_move(available_moves: list[int], board: list[str]) -> int:
    best_score = float('-inf')
    best_move = None
    depth = 3
    
    for move in available_moves:
        board[move] = 'O'  # Ход бота
        available_moves.remove(move)
        score = minimax(board, depth, False, available_moves)
        board[move] = ' '  # Отмена хода
        available_moves.append(move)
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move + 1

def check_winner(board):
    # Проверяем строчки
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] != ' ':
            return True
    
    # Проверяем колонки
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] != ' ':
            return True
    
    # Проверяем диагонали
    if board[0] == board[4] == board[8] != ' ':
        return True
    if board[2] == board[4] == board[6] != ' ':
        return True
    
    return False


def minimax(board, depth, maximizing_player, available_moves):
    if check_winner(board):
        #  Если игра окончена, возвращаем очки текущего игрока
        if maximizing_player:
            return -1  # Бот победил
        else:
            return 1  # Бот выйграл
    
    if depth == 0:
        return 0  # Ничья
    
    if maximizing_player:
        max_eval = float('-inf')
        for move in available_moves:
            board[move] = 'O'  # Ход бота
            available_moves.remove(move)
            eval = minimax(board, depth-1, False, available_moves)
            board[move] = ' '  # Отмена хода
            available_moves.append(move)
            max_eval = max(max_eval, eval)
        return max_eval
    
    else:
        min_eval = float('inf')
        for move in available_moves:
            board[move] = 'X'  # Ход игрока
            available_moves.remove(move)
            eval = minimax(board, depth-1, True, available_moves)
            board[move] = ' '  # Отмена ходя
            available_moves.append(move)
            min_eval = min(min_eval, eval)
        return min_eval