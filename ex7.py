#/**************************************************************
# * Exercise: Ex7 - python connect-N
# * Author: Guy Kejzman
# * ID: kejzmag
# **************************************************************/

import random

EMPTY = '.'
TOKEN_P1 = 'X'
TOKEN_P2 = 'O'

HUMAN = 1
RANDOM_COMP = 2
STRATEGIC_COMP = 3


def print_board(board, rows, cols, show_col_numbers=True):
    print()
    for r in range(rows):
        print("|" + "|".join(board[r]) + "|")

    if show_col_numbers:
        for c in range(1, cols + 1):
            print(f" {c % 10}", end="")
        print()
    print()


def init_board(rows, cols):
    return [[EMPTY for _ in range(cols)] for _ in range(rows)]


def is_in_bounds(rows, cols, r, c):
    return 0 <= r < rows and 0 <= c < cols


def is_column_full(board, rows, col):
    for r in range(rows):
        if board[r][col] == EMPTY:
            return False
    return True


def is_board_full(board, rows, cols):
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == EMPTY:
                return False
    return True


def get_free_row(board, rows, col):
    for r in range(rows - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def make_move(board, rows, cols, col, token):
    if col < 0 or col >= cols:
        return -1
    r = get_free_row(board, rows, col)
    if r == -1:
        return -1
    board[r][col] = token
    return r


def check_victory(board, rows, cols, row, col, token, connect_n):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue

            count = 1

            r, c = row + dr, col + dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r -= dr
                c -= dc

            if count >= connect_n:
                return True
    return False


def has_sequence_n(board, rows, cols, row, col, token, target):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue

            count = 1

            r, c = row + dr, col + dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r -= dr
                c -= dc

            if count >= target:
                return True
    return False


def get_player_type(player_number):
    while True:
        ch = input(
            f"Choose type for player {player_number}: h - human, r - random/simple computer, s - strategic computer: "
        ).strip().lower()

        if ch == 'h':
            return HUMAN
        if ch == 'r':
            return RANDOM_COMP
        if ch == 's':
            return STRATEGIC_COMP

        print("Invalid selection. Enter h, r or s.")


def human_choose_column(board, rows, cols):
    while True:
        try:
            val = int(input(f"Enter column (1-{cols}): "))
        except ValueError:
            print("Invalid input. Enter a number.")
            continue

        if not (1 <= val <= cols):
            print(f"Invalid column. Choose between 1 and {cols}.")
            continue

        col0 = val - 1
        if is_column_full(board, rows, col0):
            print(f"Column {val} is full. Choose another column.")
            continue

        return col0


def random_choose(board, rows, cols):
    choices = [c for c in range(cols) if not is_column_full(board, rows, c)]
    return random.choice(choices) if choices else -1


def strategic_choose(board, rows, cols, my_token, opp_token, connect_n):
    # center-first ordering
    order = []
    if cols % 2 == 1:
        center = cols // 2
        order.append(center)
        for d in range(1, center + 1):
            left = center - d
            right = center + d
            if left >= 0:
                order.append(left)
            if right < cols:
                order.append(right)
    else:
        center_left = cols // 2 - 1
        center_right = center_left + 1
        order.append(center_left)
        order.append(center_right)
        d = 1
        while True:
            left = center_left - d
            right = center_right + d
            if left < 0 and right >= cols:
                break
            if left >= 0:
                order.append(left)
            if right < cols:
                order.append(right)
            d += 1

    # 1. win now
    for col in order:
        if is_column_full(board, rows, col):
            continue
        r = get_free_row(board, rows, col)
        board[r][col] = my_token
        win = check_victory(board, rows, cols, r, col, my_token, connect_n)
        board[r][col] = EMPTY
        if win:
            return col

    # 2. block opponent win
    for col in order:
        if is_column_full(board, rows, col):
            continue
        r = get_free_row(board, rows, col)
        board[r][col] = opp_token
        block = check_victory(board, rows, cols, r, col, opp_token, connect_n)
        board[r][col] = EMPTY
        if block:
            return col

    # 3. create a sequence of three
    for col in order:
        if is_column_full(board, rows, col):
            continue
        r = get_free_row(board, rows, col)
        board[r][col] = my_token
        good = has_sequence_n(board, rows, cols, r, col, my_token, 3)
        board[r][col] = EMPTY
        if good:
            return col

    # 4. block opponent sequence of three
    for col in order:
        if is_column_full(board, rows, col):
            continue
        r = get_free_row(board, rows, col)
        board[r][col] = opp_token
        good = has_sequence_n(board, rows, cols, r, col, opp_token, 3)
        board[r][col] = EMPTY
        if good:
            return col

    # 5. fallback
    for col in order:
        if not is_column_full(board, rows, col):
            return col

    return -1


def run_connect(board, rows, cols, p1_type, p2_type, connect_n):
    current_player = 1

    while not is_board_full(board, rows, cols):
        token = TOKEN_P1 if current_player == 1 else TOKEN_P2
        opp = TOKEN_P2 if current_player == 1 else TOKEN_P1
        ptype = p1_type if current_player == 1 else p2_type

        print(f"Player {current_player} ({token}) turn.")

        if ptype == HUMAN:
            col = human_choose_column(board, rows, cols)
        elif ptype == RANDOM_COMP:
            col = random_choose(board, rows, cols)
            print(f"Computer chose column {col + 1}")
        else:
            col = strategic_choose(board, rows, cols, token, opp, connect_n)
            print(f"Computer chose column {col + 1}")

        row = make_move(board, rows, cols, col, token)
        print_board(board, rows, cols, show_col_numbers=True)

        if row >= 0 and check_victory(board, rows, cols, row, col, token, connect_n):
            print(f"Player {current_player} ({token}) wins!")
            return

        current_player = 2 if current_player == 1 else 1

    print("Board full and no winner. It's a tie!")


def run_tic_tac_toe():
    board = init_board(3, 3)
    print("Tic Tac Toe (Human vs Human)")
    print_board(board, 3, 3, show_col_numbers=False)

    current_token = TOKEN_P1  # X starts

    while not is_board_full(board, 3, 3):
        while True:
            try:
                pos = int(input("Enter position (1-9): "))
            except ValueError:
                continue
            if 1 <= pos <= 9:
                break

        r = (pos - 1) // 3
        c = (pos - 1) % 3
        board[r][c] = current_token  # assume they don't choose a taken cell

        print_board(board, 3, 3, show_col_numbers=False)

        if check_victory(board, 3, 3, r, c, current_token, 3):
            winner_player = 1 if current_token == TOKEN_P1 else 2
            print(f"Player {winner_player} ({current_token}) wins!")
            return

        current_token = TOKEN_P2 if current_token == TOKEN_P1 else TOKEN_P1

    print("Board full and no winner. It's a tie!")


def compute_connect_rule(rows, cols):
    if rows < 2 or cols < 2 or rows >= 101 or cols >= 101:
        return None

    if rows == 3 or cols == 3:
        return "TIC_TAC_TOE"

    if rows == 2 or cols == 2:
        return 2

    m = max(rows, cols)
    if 4 <= m <= 5:
        return 3
    if 6 <= m <= 10:
        return 4
    return 5


def main():
    try:
        rows = int(input("Enter number of rows\n"))
        cols = int(input("Enter number of columns\n"))
    except ValueError:
        return

    rule = compute_connect_rule(rows, cols)
    if rule is None:
        print("Invalid board size.")
        return

    if rule == "TIC_TAC_TOE":
        run_tic_tac_toe()
        return

    connect_n = rule

    # Required title line:
    print(f"Connect Four - Or More [Or Less] ({rows} rows x {cols} cols, connect {connect_n})")

    p1_type = get_player_type(1)
    p2_type = get_player_type(2)

    board = init_board(rows, cols)
    print_board(board, rows, cols, show_col_numbers=True)
    run_connect(board, rows, cols, p1_type, p2_type, connect_n)


if __name__ == "__main__":
    main()
