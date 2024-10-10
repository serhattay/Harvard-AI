"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    number_of_x = 0
    number_of_o = 0

    for row in board:
        for mark in row:
            if mark == X:
                number_of_x += 1
            elif mark == O:
                number_of_o += 1

    return X if number_of_x == number_of_o else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    actions_set= set()

    for row_index, row in enumerate(board):
        for col_index, col in enumerate(row):
            if col == EMPTY:
                actions_set.add((row_index, col_index))

    return actions_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if (terminal(board) or board[action[0]][action[1]] != EMPTY or not 0 <= action[0] < len(board) or
            not 0 <= action[1] < len(board[action[0]])):
        raise Exception("Invalid move")

    copy_board = copy.deepcopy(board)

    copy_board[action[0]][action[1]] = player(copy_board)

    return copy_board


def check_horizontals(board):
    for row in board:
        row_total = 0

        for col in row:
            if col == EMPTY:
                break
            elif col == X:
                row_total += 1
            elif col == O:
                row_total += 10

        if row_total == 3:
            return X
        elif row_total == 30:
            return O

    return None


def check_verticals(board):
    for i in range(len(board[0])):
        col_total = 0
        for j in range(len(board)):
            if board[j][i] == X:
                col_total += 1
            elif board[j][i] == O:
                col_total += 10

        if col_total == 3:
            return X
        elif col_total == 30:
            return O

    return None


def check_diagonals(board):
    first_diagonal = 0
    second_diagonal = 0

    for i in range(len(board)):
        if board[i][i] == X:
            first_diagonal += 1
        elif board[i][i] == O:
            first_diagonal += 10

        if board[2-i][i] == X:
            second_diagonal += 1
        elif board[2-i][i] == O:
            second_diagonal += 10

    if first_diagonal == 3 or second_diagonal == 3:
        return X
    elif first_diagonal == 30 or second_diagonal == 30:
        return O

    return None


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    horizontal = check_horizontals(board)
    vertical = check_verticals(board)
    diagonal = check_diagonals(board)

    if horizontal is not None:
        return horizontal
    elif vertical is not None:
        return vertical
    return diagonal


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) is None:
        for row in board:
            for cell in row:
                if cell == EMPTY:
                    return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        winner_player = winner(board)
        if winner_player == X:
            return 1
        elif winner_player == O:
            return -1

        return 0

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    current_player = player(board)
    if current_player == X:
        return minimax_max_player(board)[1]
    elif current_player == O:
        return minimax_min_player(board)[1]


def minimax_min_player(board):
    if terminal(board):
        return (utility(board), None)

    next_player = player(board)
    lowest_utility = float('inf')
    lowest_action = None

    for action in actions(board):
        action_result = minimax_max_player(result(board, action))[0]
        if action_result < lowest_utility:
            lowest_action = action
            lowest_utility = action_result

    return (lowest_utility, lowest_action)

def minimax_max_player(board):
    if terminal(board):
        return (utility(board), None)

    next_player = player(board)
    highest_utility = float('-inf')
    highest_action = None

    for action in actions(board):
        action_result = minimax_min_player(result(board, action))[0]
        if action_result > highest_utility:
            highest_action = action
            highest_utility = action_result

    return (highest_utility, highest_action)

