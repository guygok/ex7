# **************************************************************#
# * Exercise: EX7 - python connect-N
# * Author: Guy Kejzman
# * ID: kejzmag
# **************************************************************#

EMPTY = "."
TOKEN_P1 = "X"
TOKEN_P2 = "O"

HUMAN = 1
COMPUTER = 2


def is_column_full(board, rows, cols, col):
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


def is_in_bounds(rows, cols, r, c):
    return 0 <= r < rows and 0 <= c < cols


def get_free_row(board, rows, cols, col):
    for r in range(rows - 1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return -1


def make_move_gravity(board, rows, cols, col, token):
    """Connect-style move (token falls). Return landing row, or -1 if illegal."""
    if col < 0 or col >= cols:
        return -1
    r = get_free_row(board, rows, cols, col)
    if r == -1:
        return -1
    board[r][col] = token
    return r


def make_move_direct(board, rows, cols, r, c, token):
    """Tic-tac-toe style move (direct placement). Return True if placed, else False."""
    if not is_in_bounds(rows, cols, r, c):
        return False
    # Spec says: "You can assume no one is going to mark a taken cell."
    # Still, we keep it safe:
    if board[r][c] != EMPTY:
        return False
    board[r][c] = token
    return True


def check_victory(board, rows, cols, row, col, token, connect_n):
    # Same directional logic as C code: scan all 8 directions (excluding 0,0)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue

            count = 1

            # positive direction
            r = row + dr
            c = col + dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r += dr
                c += dc

            # negative direction
            r = row - dr
            c = col - dc
            while is_in_bounds(rows, cols, r, c) and board[r][c] == token:
                count += 1
                r -= dr
                c -= dc

            if count >= connect_n:
                return True
    return False


def has_sequence_n(board, rows, cols, row, col, token, target):
    # Same as C helper
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


def computer_choose(board, rows, cols, my_token, opp_token, connect_n):
    """
    Same priority rules as C:
    1) Winning move
    2) Block opponent's win
    3) Create a sequence of three
    4) Block opponent's sequence of three
    5) Fallback: choose column by distance from center
    """
    order = []

    # Build center-first ordering (with left preference), matching the C logic
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

    # 1) Win immediately
    for col in order:
        if is_column_full(board, rows, cols, col):
            continue
        row = get_free_row(board, rows, cols, col)
        old = board[row][col]
        board[row][col] = my_token
        win = check_victory(board, rows, cols, row, col, my_token, connect_n)
        board[row][col] = old
        if win:
            return col

    # 2) Block opponent win
    for col in order:
        if is_column_full(board, rows, cols, col):
            continue
        row = get_free_row(board, rows, cols, col)
        old = board[row][col]
        board[row][col] = opp_token
        block = check_victory(board, rows, cols, row, col, opp_token, connect_n)
        board[row][col] = old
        if block:
            return col

    # 3) Create a sequence of three (if connect_n is 2, still follow same logic)
    for col in order:
        if is_column_full(board, rows, cols, col):
            continue
        row = get_free_row(board, rows, cols, col)
        old = board[row][col]
        board[row][col] = my_token
        good = has_sequence_n(board, rows, cols, row, col, my_token, 3)
        board[row][col] = old
        if good:
            return col

    # 4) Block opponent's sequence of three
    for col in order:
        if is_column_full(board, rows, cols, col):
            continue
        row = get_free_row(board, rows, cols, col)
        old = board[row][col]
        board[row][col] = opp_token
        good = has_sequence_n(board, rows, cols, row, col, opp_token, 3)
        board[row][col] = old
        if good:
            return col

    # 5) Fallback
    for col in order:
        if not is_column_full(board, rows, cols, col):
            return col

    return -1


def init_board(rows, cols):
    return [[EMPTY for _ in range(cols)] for _ in range(rows)]


def print_board_connect(board, rows, cols):
    print()
    for r in range(rows):
        print("|" + "|".join(board[r]) + "|")
    # column numbers
    print(" " + " ".join(str((c + 1) % 10) for c in range(cols)))
    print()


def print_board_ttt(board):
    """
    Tic-Tac-Toe view: cells numbered like:
    |1|2|3|
    |4|5|6|
    |7|8|9|
    Columns NOT numbered separately.
    We'll show numbers for empty cells, token for taken cells.
    """
    print()
    cell = 1
    for r in range(3):
        row_cells = []
        for c in range(3):
            if board[r][c] == EMPTY:
                row_cells.append(str(cell))
            else:
                row_cells.append(board[r][c])
            cell += 1
        print("|" + "|".join(row_cells) + "|")
    print()


def get_player_type(player_number):
    while True:
        ch = input(f"Choose type for player {player_number}: h - human, c - computer: ").strip()
        if not ch:
            print("Invalid selection. Enter h or c.")
            continue
        if ch[0] in ("h", "H"):
            return HUMAN
        if ch[0] in ("c", "C"):
            return COMPUTER
        print("Invalid selection. Enter h or c.")


def human_choose_column(board, rows, cols):
    while True:
        raw = input(f"Enter column (1-{cols}): ").strip()
        try:
            col_1 = int(raw)
        except ValueError:
            print("Invalid input. Enter a number.")
            continue

        if not (1 <= col_1 <= cols):
            print(f"Invalid column. Choose between 1 and {cols}.")
            continue

        col = col_1 - 1
        if is_column_full(board, rows, cols, col):
            print(f"Column {col_1} is full. Choose another column.")
            continue

        return col


def human_choose_cell_ttt():
    while True:
        raw = input("Enter cell (1-9): ").strip()
        try:
            cell = int(raw)
        except ValueError:
            print("Invalid input. Enter a number.")
            continue
        if 1 <= cell <= 9:
            return cell
        print("Invalid cell. Choose between 1 and 9.")


def compute_connect_n(rows, cols):
    """
    N-Connect Logic (as requested):
    - Anything less than 2 or greater than 100 (101 and above, rows or columns) -> invalid.
    - If 2 is chosen for either rows or columns, sequence is 2.
    - If either is 3 -> game becomes Tic-Tac-Toe: board is 3x3, connect_n=3, two humans.
    - 4 <= rows or columns <= 5 -> sequence 3
    - 6 <= rows or columns <= 10 -> sequence 4
    - 11 and above -> sequence 5

    Interpretation note:
    To keep behavior consistent and deterministic, we base the bracket on max(rows, cols)
    (except for the special cases "either is 2" and "either is 3").
    """
    if rows < 2 or cols < 2 or rows > 100 or cols > 100:
        return None  # invalid

    if rows == 3 or cols == 3:
        return 3  # Tic-Tac-Toe case handled by caller

    if rows == 2 or cols == 2:
        return 2

    m = max(rows, cols)
    if 4 <= m <= 5:
        return 3
    if 6 <= m <= 10:
        return 4
    return 5  # 11+


def run_connect_game(board, rows, cols, p1_type, p2_type, connect_n):
    current_player = 1
    winner = 0

    while not winner and not is_board_full(board, rows, cols):
        token = TOKEN_P1 if current_player == 1 else TOKEN_P2
        opp_token = TOKEN_P2 if current_player == 1 else TOKEN_P1
        ptype = p1_type if current_player == 1 else p2_type

        print(f"Player {current_player} ({token}) turn.")

        if ptype == HUMAN:
            col = human_choose_column(board, rows, cols)
        else:
            col = computer_choose(board, rows, cols, token, opp_token, connect_n)
            print(f"Computer chose column {col + 1}")

        row = make_move_gravity(board, rows, cols, col, token)
        print_board_connect(board, rows, cols)

        if row >= 0 and check_victory(board, rows, cols, row, col, token, connect_n):
            winner = current_player
            break

        if is_board_full(board, rows, cols):
            break

        current_player = 2 if current_player == 1 else 1

    if winner:
        token = TOKEN_P1 if winner == 1 else TOKEN_P2
        print(f"Player {winner} ({token}) wins!")
    else:
        print("Board full and no winner. It's a tie!")


def run_tic_tac_toe():
    rows, cols = 3, 3
    connect_n = 3
    board = init_board(rows, cols)

    # Per spec: two human players only.
    p1_type = HUMAN
    p2_type = HUMAN

    print("\nTic-Tac-Toe mode (3x3). Two human players.")
    print_board_ttt(board)

    current_player = 1
    winner = 0
    moves = 0

    while not winner and moves < 9:
        token = TOKEN_P1 if current_player == 1 else TOKEN_P2
        print(f"Player {current_player} ({token}) turn.")

        cell = human_choose_cell_ttt()
        r = (cell - 1) // 3
        c = (cell - 1) % 3

        # Spec says we can assume no one marks a taken cell, but we still keep it safe.
        if not make_move_direct(board, rows, cols, r, c, token):
            print("That cell is taken or invalid. Try again.")
            continue

        moves += 1
        print_board_ttt(board)

        if check_victory(board, rows, cols, r, c, token, connect_n):
            winner = current_player
            break

        current_player = 2 if current_player == 1 else 1

    if winner:
        token = TOKEN_P1 if winner == 1 else TOKEN_P2
        print(f"Player {winner} ({token}) wins!")
    else:
        print("No winner. It's a tie!")


def read_int(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Invalid input. Enter a number.")


def main():
    print("Adjustable N-Connect Game\n")

    rows = read_int("Enter number of rows (2-100): ")
    cols = read_int("Enter number of columns (2-100): ")

    connect_n = compute_connect_n(rows, cols)
    if connect_n is None:
        print("Invalid board size. Rows/columns must be between 2 and 100.")
        return

    # Special case: Tic-Tac-Toe
    if rows == 3 or cols == 3:
        run_tic_tac_toe()
        return

    print(f"\nConnect Game ({rows} rows x {cols} cols), CONNECT_N = {connect_n}\n")

    p1_type = get_player_type(1)
    p2_type = get_player_type(2)

    board = init_board(rows, cols)
    print_board_connect(board, rows, cols)
    run_connect_game(board, rows, cols, p1_type, p2_type, connect_n)


if __name__ == "__main__":
    main()
