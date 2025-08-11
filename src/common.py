# common.py

BOARD_SIZE = 15  # Kích thước bàn cờ

def create_board():
    return [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    print("   " + " ".join(f"{i:2}" for i in range(BOARD_SIZE)))
    for idx, row in enumerate(board):
        print(f"{idx:2} " + "  ".join(row))
    print()

def check_win(board, x, y, symbol):
    directions = [
        (1, 0),   # Ngang →
        (0, 1),   # Dọc ↓
        (1, 1),   # Chéo ↘
        (1, -1)   # Chéo ↗
    ]
    for dx, dy in directions:
        count = 1

        # Đếm về phía trước
        i = 1
        while True:
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == symbol:
                count += 1
                i += 1
            else:
                break

        # Đếm về phía sau
        i = 1
        while True:
            nx, ny = x - dx * i, y - dy * i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and board[nx][ny] == symbol:
                count += 1
                i += 1
            else:
                break

        if count >= 5:
            return True

    return False
