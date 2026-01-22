## EX7 - python connect-N ##
import sys

EMPTY = "."
TOKEN_P1 = "X"
TOKEN_P2 = "O"

HUMAN = "h"
COMPUTER = "c"


def read_int_in_range(prompt: str, lo: int, hi: int) -> int:
    while True:
        s = input(prompt)
        try:
            v = int(s)
        except ValueError:
            print("Invalid input. Enter a number.")
            continue
        if v < lo or v > hi:
            print(f"Invalid value. Choose between {lo} and {hi}.")
            continue
        return v


def choose_connect_n(rows: int, cols: int) -> int:
    m = max(rows, cols)
    if m == 2:
        return 2
    if 4 <= m <= 5:
        return 3
    if 6 <= m <= 10:
        return 4
    return 5  # 11 and above


def get_player_type(player_number: int) -> str:
    while True:
        ch = input(f"Choose type for player {player_number}: h - human, c - computer: ").strip()
        if not ch:
            continue
        ch = ch[0].lower()
        if ch in (HUMAN, COMPUTER):
            return ch
        print("Invalid selection. Enter h or c.")


def init_board(rows: int, cols: int) -> list[list[str]]:
    return [[EMPTY for _ in range(cols)] for _ in range(rows)]


def print_board_connect(board: list[list[str]]) -> None:
    rows = len(board)
    cols = len(board[0])
    for r in range(rows):
        line = "|"
        for c in range(cols):
            line += board[r][c] + "|"
        print(line)
    # Column numbers (1..cols)
    nums = ""
    for c in range(1, cols + 1):
        nums += f" {c % 10}"
    print(nums)


def print_board_ttt(board: list[list[str]]) -> None:
    # Tic-tac-toe: columns not numbered
    rows = len(board)
    cols = len(board[0])
    for r in range(rows):
        line = "|"
        for c in range(cols):
            line += board[r][c] + "|"
        print(line)


def is_in_bounds(rows: int, cols: int, r: int, c: int) -> bool:
    return 0 <= r < rows and 0 <= c < cols


def check_victory(board: list[list[str]], row: int, col: int, token: str, connect_n: int) -> bool:
    rows = len(board)
    cols = len(board[0])

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            count = 1

            # forward
            r = row + dr
            c = col + dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r += dr
                c += dc

            # backward
            r = row - dr
            c = col - dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r -= dr
                c -= dc

            if count >= connect_n:
                return True

    return False


def board_full_connect(board: list[list[str]]) -> bool:
    # board full if top row has no EMPTY
    return all(cell != EMPTY for cell in board[0])


def column_full(board: list[list[str]], col: int) -> bool:
    return board[0][col] != EMPTY


def get_free_row(board: list[list[str]], col: int) -> int:
    # returns row index where token will land, or -1
    rows = len(board)
    for r in range(rows - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def make_move_connect(board: list[list[str]], col: int, token: str) -> int:
    row = get_free_row(board, col)
    if row == -1:
        return -1
    board[row][col] = token
    return row


def build_column_order(cols: int) -> list[int]:
    # Distance from center minimal; if tie choose left.
    # For odd: center first. For even: left-center then right-center.
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
    return order


def has_sequence_len(board: list[list[str]], row: int, col: int, token: str, target: int) -> bool:
    # Like victory check but for a shorter target (e.g., connect_n - 1).
    rows = len(board)
    cols = len(board[0])

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            count = 1

            r = row + dr
            c = col + dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r += dr
                c += dc

            r = row - dr
            c = col - dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r -= dr
                c -= dc

            if count >= target:
                return True
    return False


def computer_choose(board: list[list[str]], my_token: str, opp_token: str, connect_n: int) -> int:
    cols = len(board[0])
    order = build_column_order(cols)

    # Priority 1: winning move
    for col in order:
        if column_full(board, col):
            continue
        row = get_free_row(board, col)
        board[row][col] = my_token
        win = check_victory(board, row, col, my_token, connect_n)
        board[row][col] = EMPTY
        if win:
            return col

    # Priority 2: block opponent winning move
    for col in order:
        if column_full(board, col):
            continue
        row = get_free_row(board, col)
        board[row][col] = opp_token
        block = check_victory(board, row, col, opp_token, connect_n)
        board[row][col] = EMPTY
        if block:
            return col

    # For sequences shorter than 2, these priorities don’t make sense
    target = connect_n - 1
    if target >= 2:
        # Priority 3: create sequence of (connect_n - 1)
        for col in order:
            if column_full(board, col):
                continue
            row = get_free_row(board, col)
            board[row][col] = my_token
            good = has_sequence_len(board, row, col, my_token, target)
            board[row][col] = EMPTY
            if good:
                return col

        # Priority 4: block opponent's (connect_n - 1)
        for col in order:
            if column_full(board, col):
                continue
            row = get_free_row(board, col)
            board[row][col] = opp_token
            good = has_sequence_len(board, row, col, opp_token, target)
            board[row][col] = EMPTY
            if good:
                return col

    # Priority 5: fallback ordering
    for col in order:
        if not column_full(board, col):
            return col

    return -1


def human_choose_column(board: list[list[str]]) -> int:
    cols = len(board[0])
    while True:
        s = input(f"Enter column (1-{cols}): ")
        if s.strip() == "":
            # ignore whitespace-only
            continue
        try:
            col = int(s)
        except ValueError:
            print("Invalid input. Enter a number.")
            continue
        if col < 1 or col > cols:
            print(f"Invalid column. Choose between 1 and {cols}.")
            continue
        col0 = col - 1
        if column_full(board, col0):
            print(f"Column {col} is full. Choose another column.")
            continue
        return col0


def play_connect_n(rows: int, cols: int, connect_n: int) -> None:
    print(f"Connect Four ({rows} rows x {cols} cols)")
    p1_type = get_player_type(1)
    p2_type = get_player_type(2)

    board = init_board(rows, cols)
    print_board_connect(board)

    current = 1
    winner = 0

    while not winner and not board_full_connect(board):
        token = TOKEN_P1 if current == 1 else TOKEN_P2
        opp = TOKEN_P2 if current == 1 else TOKEN_P1
        ptype = p1_type if current == 1 else p2_type

        print(f"Player {current} ({token}) turn.")
        if ptype == HUMAN:
            col = human_choose_column(board)
        else:
            col = computer_choose(board, token, opp, connect_n)
            # In a full board this might be -1; but loop condition prevents full board
            print(f"Computer chose column {col + 1}")

        row = make_move_connect(board, col, token)
        print_board_connect(board)

        if row >= 0 and check_victory(board, row, col, token, connect_n):
            winner = current
            break

        current = 2 if current == 1 else 1

    if winner:
        token = TOKEN_P1 if winner == 1 else TOKEN_P2
        print(f"Player {winner} ({token}) wins!")
    else:
        print("Board full and no winner. It's a tie!")


def play_tic_tac_toe() -> None:
    rows = 3
    cols = 3
    connect_n = 3

    print(f"Connect Four ({rows} rows x {cols} cols)")
    # Tic-tac-toe mode: two humans only
    board = init_board(rows, cols)
    print_board_ttt(board)

    current = 1
    winner = 0
    moves = 0

    # Cells numbered:
    # |1|2|3|
    # |4|5|6|
    # |7|8|9|
    while not winner and moves < 9:
        token = TOKEN_P1 if current == 1 else TOKEN_P2
        print(f"Player {current} ({token}) turn.")
        cell = read_int_in_range("Enter cell (1-9): ", 1, 9)
        cell0 = cell - 1
        r = cell0 // 3
        c = cell0 % 3

        # You said: assume no one marks a taken cell.
        board[r][c] = token
        moves += 1

        print_board_ttt(board)

        if check_victory(board, r, c, token, connect_n):
            winner = current
            break

        current = 2 if current == 1 else 1

    if winner:
        token = TOKEN_P1 if winner == 1 else TOKEN_P2
        print(f"Player {winner} ({token}) wins!")
    else:
        print("Board full and no winner. It's a tie!")


def main() -> None:
    # Dimensions input + validation
    rows = read_int_in_range("Enter number of rows (2-100): ", 2, 100)
    cols = read_int_in_range("Enter number of cols (2-100): ", 2, 100)

    # Tic-tac-toe special case: if either is 3 => force 3x3, seq=3, two humans.
    if rows == 3 or cols == 3:
        play_tic_tac_toe()
        return

    connect_n = choose_connect_n(rows, cols)
    play_connect_n(rows, cols, connect_n)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Optional clean exit on Ctrl+C
        sys.exit(0)
