# common.py - Shared utilities for Caro game

BOARD_SIZE = 15  # Kích thước bàn cờ

def create_board():
    """
    Tạo bàn cờ mới với kích thước BOARD_SIZE x BOARD_SIZE
    
    Returns:
        list: Bàn cờ 2D với tất cả ô trống ('.')
    """
    return [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    """
    In bàn cờ ra console với định dạng đẹp
    
    Args:
        board (list): Bàn cờ 2D cần in
    """
    if not board or len(board) != BOARD_SIZE:
        print("❌ Invalid board!")
        return
        
    # In header với số cột
    print("   " + " ".join(f"{i:2}" for i in range(BOARD_SIZE)))
    
    # In từng hàng với số hàng
    for idx, row in enumerate(board):
        if len(row) != BOARD_SIZE:
            print(f"❌ Invalid row {idx}!")
            return
        print(f"{idx:2} " + "  ".join(row))
    print()

def is_valid_position(x, y):
    """
    Kiểm tra tọa độ có hợp lệ không
    
    Args:
        x (int): Tọa độ hàng
        y (int): Tọa độ cột
        
    Returns:
        bool: True nếu tọa độ hợp lệ
    """
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

def check_win(board, x, y, symbol):
    """
    Kiểm tra xem có thắng không sau khi đặt quân cờ tại (x, y)
    
    Args:
        board (list): Bàn cờ hiện tại
        x (int): Tọa độ hàng vừa đặt
        y (int): Tọa độ cột vừa đặt
        symbol (str): Ký hiệu quân cờ ('X' hoặc 'O')
        
    Returns:
        bool: True nếu thắng (có 5 quân liên tiếp)
    """
    # Validation
    if not is_valid_position(x, y):
        return False
        
    if board[x][y] != symbol:
        return False
    
    # Các hướng cần kiểm tra: ngang, dọc, chéo xuống, chéo lên
    directions = [
        (1, 0),   # Ngang →
        (0, 1),   # Dọc ↓
        (1, 1),   # Chéo ↘
        (1, -1)   # Chéo ↗
    ]
    
    for dx, dy in directions:
        count = 1  # Đã có 1 quân tại vị trí hiện tại

        # Đếm về phía trước
        i = 1
        while True:
            nx, ny = x + dx * i, y + dy * i
            if is_valid_position(nx, ny) and board[nx][ny] == symbol:
                count += 1
                i += 1
            else:
                break

        # Đếm về phía sau
        i = 1
        while True:
            nx, ny = x - dx * i, y - dy * i
            if is_valid_position(nx, ny) and board[nx][ny] == symbol:
                count += 1
                i += 1
            else:
                break

        # Kiểm tra thắng (5 quân liên tiếp)
        if count >= 5:
            return True

    return False

def is_board_full(board):
    """
    Kiểm tra xem bàn cờ đã đầy chưa (hòa)
    
    Args:
        board (list): Bàn cờ cần kiểm tra
        
    Returns:
        bool: True nếu bàn cờ đầy
    """
    if not board:
        return False
        
    for row in board:
        if "." in row:
            return False
    return True

def get_valid_moves(board):
    """
    Lấy danh sách các nước đi hợp lệ
    
    Args:
        board (list): Bàn cờ hiện tại
        
    Returns:
        list: Danh sách các tuple (x, y) là nước đi hợp lệ
    """
    valid_moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == ".":
                valid_moves.append((i, j))
    return valid_moves
