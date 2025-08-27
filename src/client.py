import socket
import threading
import time
import pygame
from common import create_board, print_board, check_win

# Khởi tạo pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 600, 700
BOARD_SIZE = 15
CELL_SIZE = 35
GRID_OFFSET_X = (WIDTH - BOARD_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 100
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caro Game")

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 180, 0)

# Font chữ
FONT = pygame.font.SysFont('Arial', 24)
SMALL_FONT = pygame.font.SysFont('Arial', 18)

# Biến toàn cục để theo dõi thời gian
time_left = 40
timer_running = False
timer_thread = None
game_status = "Waiting for opponent..."
my_symbol = ""
enemy_symbol = ""

def draw_board(board):
    WINDOW.fill(WHITE)
    
    # Vẽ tiêu đề và thông tin
    title = FONT.render(f"Caro Game - You are {my_symbol}", True, BLACK)
    WINDOW.blit(title, (WIDTH//2 - title.get_width()//2, 20))
    
    # Hiển thị thời gian
    if timer_running:
        timer_text = FONT.render(f"Time: {time_left}s", True, RED if time_left <= 10 else BLACK)
    else:
        timer_text = FONT.render("Waiting...", True, GRAY)
    WINDOW.blit(timer_text, (WIDTH//2 - timer_text.get_width()//2, 50))
    
    # Hiển thị trạng thái
    status_text = FONT.render(game_status, True, BLUE)
    WINDOW.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 50))
    
    # Vẽ lưới bàn cờ
    for i in range(BOARD_SIZE + 1):
        # Vẽ đường ngang
        pygame.draw.line(WINDOW, BLACK, 
                         (GRID_OFFSET_X, GRID_OFFSET_Y + i * CELL_SIZE), 
                         (GRID_OFFSET_X + BOARD_SIZE * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE))
        # Vẽ đường dọc
        pygame.draw.line(WINDOW, BLACK, 
                         (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y), 
                         (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE))
    
    # Vẽ quân cờ
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == "X":
                pygame.draw.line(WINDOW, RED, 
                                 (GRID_OFFSET_X + j * CELL_SIZE + 5, GRID_OFFSET_Y + i * CELL_SIZE + 5),
                                 (GRID_OFFSET_X + j * CELL_SIZE + CELL_SIZE - 5, GRID_OFFSET_Y + i * CELL_SIZE + CELL_SIZE - 5), 3)
                pygame.draw.line(WINDOW, RED, 
                                 (GRID_OFFSET_X + j * CELL_SIZE + CELL_SIZE - 5, GRID_OFFSET_Y + i * CELL_SIZE + 5),
                                 (GRID_OFFSET_X + j * CELL_SIZE + 5, GRID_OFFSET_Y + i * CELL_SIZE + CELL_SIZE - 5), 3)
            elif board[i][j] == "O":
                pygame.draw.circle(WINDOW, BLUE, 
                                  (GRID_OFFSET_X + j * CELL_SIZE + CELL_SIZE//2, GRID_OFFSET_Y + i * CELL_SIZE + CELL_SIZE//2), 
                                  CELL_SIZE//2 - 5, 3)
    
    pygame.display.update()

def countdown_timer():
    global time_left, timer_running
    while timer_running and time_left > 0:
        time.sleep(1)
        time_left -= 1
    
    # Nếu hết giờ và timer vẫn chạy
    if timer_running and time_left <= 0:
        global game_status
        game_status = "TIME'S UP!"

def start_timer():
    global time_left, timer_running, timer_thread
    time_left = 40
    timer_running = True
    timer_thread = threading.Thread(target=countdown_timer)
    timer_thread.daemon = True
    timer_thread.start()

def stop_timer():
    global timer_running
    timer_running = False
    if timer_thread and timer_thread.is_alive():
        # Đợi thread kết thúc
        timer_thread.join(0.1)

def recv_move(sock):
    try:
        data = sock.recv(1024).decode().strip()
        if not data:
            global game_status
            game_status = "Lost connection with opponent."
            return None
        
        # Kiểm tra nếu là thông báo hết giờ từ đối thủ
        if data == "TIMEOUT":
            game_status = "Opponent ran out of time!"
            return (-2, -2)  # Mã đặc biệt cho hết giờ
        
        x, y = map(int, data.split())
        return x, y
    except:
        game_status = "Error receiving data from opponent."
        return None

def send_move(sock, x, y):
    try:
        sock.send(f"{x} {y}".encode())
    except:
        global game_status
        game_status = "Failed to send data."

def send_timeout(sock):
    try:
        sock.send("TIMEOUT".encode())
    except:
        global game_status
        game_status = "Failed to send timeout notification."

def get_valid_move(board, symbol):
    global time_left, timer_running, game_status
    
    # Bắt đầu đếm giờ
    start_timer()
    game_status = f"Your turn ({symbol})! Click to make a move."
    
    running = True
    while running and timer_running and time_left > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return (-1, -1)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Kiểm tra xem người chơi có nhấp vào bàn cờ không
                if (GRID_OFFSET_X <= mouse_x <= GRID_OFFSET_X + BOARD_SIZE * CELL_SIZE and
                    GRID_OFFSET_Y <= mouse_y <= GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE):
                    
                    # Tính toán tọa độ ô
                    board_x = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE
                    board_y = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                    
                    if 0 <= board_x < BOARD_SIZE and 0 <= board_y < BOARD_SIZE:
                        if board[board_x][board_y] == ".":
                            stop_timer()
                            return board_x, board_y
                        else:
                            game_status = "This cell is already taken!"
        
        # Vẽ bàn cờ trong quá trình chờ
        draw_board(board)
        
        # Tránh tiêu tốn CPU
        pygame.time.delay(50)
        
    if time_left <= 0:
        game_status = "You ran out of time!"
        stop_timer()
        return (-2, -2)  # Mã đặc biệt cho hết giờ
    
    return (-1, -1)  # Mã cho lỗi không xác định

def ask_continue(sock):
    global game_status
    
    msg = sock.recv(1024).decode('utf-8')
    # Convert the received message to English
    if "Bạn có muốn chơi lại không?" in msg:
        msg = "Do you want to play again?"
    elif "Cả hai đồng ý chơi lại" in msg:
        msg = "Both agreed to play again. Starting new game!"
    elif "Một trong hai không đồng ý" in msg:
        msg = "One player declined. Game over."
    
    game_status = msg + " (y/n)"
    
    waiting_answer = True
    answer = 'n'  # Mặc định là không
    
    while waiting_answer:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sock.send('n'.encode('utf-8'))
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    answer = 'y'
                    waiting_answer = False
                elif event.key == pygame.K_n:
                    answer = 'n'
                    waiting_answer = False
        
        # Vẽ màn hình chờ
        WINDOW.fill(WHITE)
        prompt = FONT.render(game_status, True, BLACK)
        instruction = SMALL_FONT.render("Press Y to play again, N to exit", True, BLUE)
        WINDOW.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT//2 - 30))
        WINDOW.blit(instruction, (WIDTH//2 - instruction.get_width()//2, HEIGHT//2 + 10))
        pygame.display.update()
        pygame.time.delay(50)
    
    sock.send(answer.encode('utf-8'))
    return answer == 'y'

def main():
    global game_status, my_symbol, enemy_symbol
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9999))

    start_msg = s.recv(1024).decode('utf-8')
    if "Bạn là X" in start_msg:
        start_msg = "You are X"
    elif "Bạn là O" in start_msg:
        start_msg = "You are O"
    
    game_status = start_msg

    my_symbol = "X" if "X" in start_msg else "O"
    enemy_symbol = "O" if my_symbol == "X" else "X"

    while True:
        board = create_board()
        is_my_turn = my_symbol == "X"

        if is_my_turn:
            game_status = "Your turn!"
        else:
            game_status = "Waiting for opponent..."

        # Vòng lặp chơi 1 ván
        game_running = True
        while game_running:
            draw_board(board)
            
            if is_my_turn:
                game_status = f"Your turn! You have {time_left} seconds to move."
                x, y = get_valid_move(board, my_symbol)
                
                # Kiểm tra hết giờ
                if x == -2 and y == -2:
                    game_status = "You lost due to timeout!"
                    send_timeout(s)
                    game_running = False
                elif x == -1 and y == -1:
                    # Người chơi đóng cửa sổ hoặc lỗi
                    pygame.quit()
                    return
                else:
                    board[x][y] = my_symbol
                    if check_win(board, x, y, my_symbol):
                        game_status = "🎉 You won!"
                        send_move(s, -1, -1)
                        game_running = False
                    else:
                        send_move(s, x, y)
            else:
                game_status = "Waiting for opponent's move..."
                draw_board(board)
                
                move = recv_move(s)
                if move is None:
                    pygame.quit()
                    return
                
                x, y = move
                if x == -1 and y == -1:
                    game_status = "Opponent won. You lost!"
                    game_running = False
                elif x == -2 and y == -2:
                    game_status = "Opponent ran out of time! You win!"
                    game_running = False
                else:
                    board[x][y] = enemy_symbol
                    game_status = "Opponent made a move"
                    if check_win(board, x, y, enemy_symbol):
                        game_status = "You lost!"
                        game_running = False

            is_my_turn = not is_my_turn
            
            # Xử lý sự kiện thoát
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

        # Sau khi kết thúc ván, hỏi chơi lại
        draw_board(board)  # Vẽ bàn cờ cuối cùng
        
        cont_result = ask_continue(s)
        
        # Chờ xác nhận từ server
        confirm_msg = s.recv(1024).decode('utf-8')
        
        # Convert confirmation message to English
        if "Cả hai đồng ý chơi lại" in confirm_msg:
            confirm_msg = "Both agreed to play again. Starting new game!"
        elif "Một trong hai không đồng ý" in confirm_msg:
            confirm_msg = "One player declined. Game over."
        
        game_status = confirm_msg
        
        # Hiển thị thông báo xác nhận
        WINDOW.fill(WHITE)
        confirm_text = FONT.render(confirm_msg, True, BLACK)
        WINDOW.blit(confirm_text, (WIDTH//2 - confirm_text.get_width()//2, HEIGHT//2))
        pygame.display.update()
        pygame.time.delay(2000)  # Hiển thị 2 giây
        
        if "Game over" in confirm_msg:
            pygame.quit()
            s.close()
            return

if __name__ == "__main__":
    main()