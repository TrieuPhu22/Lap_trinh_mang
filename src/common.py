# common.py
BOARD_SIZE = 15  # Kích thước bàn cờ

def create_board():
    """Khởi tạo bàn cờ với các ô trống (.)"""
    return [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board(board):
    """In bàn cờ ra console một cách đẹp mắt"""
    # In header với số cột
    print("    " + " ".join(f"{i:2}" for i in range(BOARD_SIZE)))
    print("   " + "─" * (BOARD_SIZE * 3))  # Đường kẻ ngang
    
    # In từng hàng với số hàng
    for idx, row in enumerate(board):
        row_str = "  ".join(row)
        print(f"{idx:2} │ {row_str}")
    print()

def is_valid_move(board, x, y):
    """Kiểm tra nước đi có hợp lệ không"""
    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
        return False, "Tọa độ nằm ngoài bàn cờ!"
    
    if board[x][y] != ".":
        return False, "Ô này đã có quân cờ!"
    
    return True, "Nước đi hợp lệ"

def make_move(board, x, y, symbol):
    """Thực hiện nước đi"""
    valid, message = is_valid_move(board, x, y)
    if valid:
        board[x][y] = symbol
        return True, message
    return False, message

def check_win(board, x, y, symbol):
    """
    Kiểm tra xem người chơi có chiến thắng sau khi đi tại (x, y) không.
    Chiến thắng khi có 5 quân liên tiếp theo một trong các hướng.
    """
    directions = [
        (1, 0),   # Ngang →
        (0, 1),   # Dọc ↓
        (1, 1),   # Chéo ↘
        (1, -1)   # Chéo ↗
    ]
    
    for dx, dy in directions:
        count = 1  # Bắt đầu đếm từ quân vừa đi
        
        # Đếm về phía trước (hướng dương)
        nx, ny = x + dx, y + dy
        while (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 
               board[nx][ny] == symbol):
            count += 1
            nx += dx
            ny += dy
        
        # Đếm về phía sau (hướng âm)
        nx, ny = x - dx, y - dy
        while (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and 
               board[nx][ny] == symbol):
            count += 1
            nx -= dx
            ny -= dy
        
        # Kiểm tra thắng
        if count >= 5:
            return True
    
    return False

def check_board_full(board):
    """Kiểm tra bàn cờ đã đầy chưa (hòa)"""
    for row in board:
        for cell in row:
            if cell == ".":
                return False
    return True

def get_board_stats(board):
    """Lấy thống kê bàn cờ"""
    x_count = 0
    o_count = 0
    empty_count = 0
    
    for row in board:
        for cell in row:
            if cell == "X":
                x_count += 1
            elif cell == "O":
                o_count += 1
            else:
                empty_count += 1
    
    return {
        "X": x_count,
        "O": o_count,
        "empty": empty_count,
        "total": BOARD_SIZE * BOARD_SIZE
    }

def parse_move(move_str):
    """Phân tích chuỗi nước đi thành tọa độ x, y"""
    try:
        parts = move_str.strip().split()
        if len(parts) != 2:
            return None, None, "Định dạng không đúng! Nhập: 'x y'"
        
        x = int(parts[0])
        y = int(parts[1])
        
        return x, y, "OK"
    except ValueError:
        return None, None, "Tọa độ phải là số nguyên!"

def format_move(x, y):
    """Định dạng tọa độ thành chuỗi để gửi"""
    return f"{x} {y}"

# Test functions (chỉ chạy khi file được execute trực tiếp)
def test_functions():
    """Test các function cơ bản"""
    print("🧪 Testing common.py functions...")
    
    # Test tạo bàn cờ
    board = create_board()
    print(f"✅ Tạo bàn cờ {BOARD_SIZE}x{BOARD_SIZE}")
    
    # Test nước đi
    success, msg = make_move(board, 7, 7, "X")
    print(f"✅ Đi X tại (7,7): {msg}")
    
    success, msg = make_move(board, 7, 8, "O")
    print(f"✅ Đi O tại (7,8): {msg}")
    
    # Test nước đi không hợp lệ
    success, msg = make_move(board, 7, 7, "X")
    print(f"❌ Đi X tại (7,7) lần 2: {msg}")
    
    # Test parse move
    x, y, msg = parse_move("7 8")
    print(f"✅ Parse '7 8': ({x}, {y}) - {msg}")
    
    x, y, msg = parse_move("abc def")
    print(f"❌ Parse 'abc def': {msg}")
    
    # Test stats
    stats = get_board_stats(board)
    print(f"📊 Stats: {stats}")
    
    print("🎯 Test hoàn thành!")

if __name__ == "__main__":
    test_functions()