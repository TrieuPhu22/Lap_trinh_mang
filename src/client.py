import socket
import threading
import time
import pygame
from common import create_board, check_win

class CaroClient:
    def __init__(self, host="127.0.0.1", port=9999, timeout=30):
        # Khởi tạo pygame
        pygame.init()
        
        # Cấu hình màn hình
        self.WIDTH, self.HEIGHT = 600, 700
        self.BOARD_SIZE = 15
        self.CELL_SIZE = 35
        self.GRID_OFFSET_X = (self.WIDTH - self.BOARD_SIZE * self.CELL_SIZE) // 2
        self.GRID_OFFSET_Y = 100
        self.WINDOW = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Caro Game")
        
        # Màu sắc
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 180, 0)
        
        # Font chữ
        self.FONT = pygame.font.SysFont('Arial', 24)
        self.SMALL_FONT = pygame.font.SysFont('Arial', 18)
        
        # Game state
        self.time_left = 40
        self.timer_running = False
        self.timer_thread = None
        self.game_status = "Connecting to server..."
        self.my_symbol = ""
        self.enemy_symbol = ""
        
        # Network
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        
    def safe_send(self, message):
        """Gửi dữ liệu an toàn"""
        try:
            self.socket.send(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"❌ Lỗi khi gửi dữ liệu: {e}")
            self.game_status = "Connection lost!"
            return False
            
    def safe_recv(self):
        """Nhận dữ liệu an toàn với timeout"""
        try:
            self.socket.settimeout(self.timeout)
            data = self.socket.recv(1024).decode('utf-8').strip()
            if not data:
                self.game_status = "Lost connection with server."
                return None
            return data
        except socket.timeout:
            self.game_status = "Connection timeout!"
            return None
        except Exception as e:
            print(f"❌ Lỗi khi nhận dữ liệu: {e}")
            self.game_status = "Connection error!"
            return None
            
    def draw_board(self, board):
        """Vẽ bàn cờ"""
        self.WINDOW.fill(self.WHITE)
        
        # Vẽ tiêu đề và thông tin
        title = self.FONT.render(f"Caro Game - You are {self.my_symbol}", True, self.BLACK)
        self.WINDOW.blit(title, (self.WIDTH//2 - title.get_width()//2, 20))
        
        # Hiển thị thời gian
        if self.timer_running:
            timer_text = self.FONT.render(f"Time: {self.time_left}s", True, self.RED if self.time_left <= 10 else self.BLACK)
        else:
            timer_text = self.FONT.render("Waiting...", True, self.GRAY)
        self.WINDOW.blit(timer_text, (self.WIDTH//2 - timer_text.get_width()//2, 50))
        
        # Hiển thị trạng thái
        status_text = self.FONT.render(self.game_status, True, self.BLUE)
        self.WINDOW.blit(status_text, (self.WIDTH//2 - status_text.get_width()//2, self.HEIGHT - 50))
        
        # Vẽ lưới bàn cờ
        for i in range(self.BOARD_SIZE + 1):
            # Vẽ đường ngang
            pygame.draw.line(self.WINDOW, self.BLACK, 
                             (self.GRID_OFFSET_X, self.GRID_OFFSET_Y + i * self.CELL_SIZE), 
                             (self.GRID_OFFSET_X + self.BOARD_SIZE * self.CELL_SIZE, self.GRID_OFFSET_Y + i * self.CELL_SIZE))
            # Vẽ đường dọc
            pygame.draw.line(self.WINDOW, self.BLACK, 
                             (self.GRID_OFFSET_X + i * self.CELL_SIZE, self.GRID_OFFSET_Y), 
                             (self.GRID_OFFSET_X + i * self.CELL_SIZE, self.GRID_OFFSET_Y + self.BOARD_SIZE * self.CELL_SIZE))
        
        # Vẽ quân cờ
        for i in range(self.BOARD_SIZE):
            for j in range(self.BOARD_SIZE):
                if board[i][j] == "X":
                    pygame.draw.line(self.WINDOW, self.RED, 
                                     (self.GRID_OFFSET_X + j * self.CELL_SIZE + 5, self.GRID_OFFSET_Y + i * self.CELL_SIZE + 5),
                                     (self.GRID_OFFSET_X + j * self.CELL_SIZE + self.CELL_SIZE - 5, self.GRID_OFFSET_Y + i * self.CELL_SIZE + self.CELL_SIZE - 5), 3)
                    pygame.draw.line(self.WINDOW, self.RED, 
                                     (self.GRID_OFFSET_X + j * self.CELL_SIZE + self.CELL_SIZE - 5, self.GRID_OFFSET_Y + i * self.CELL_SIZE + 5),
                                     (self.GRID_OFFSET_X + j * self.CELL_SIZE + 5, self.GRID_OFFSET_Y + i * self.CELL_SIZE + self.CELL_SIZE - 5), 3)
                elif board[i][j] == "O":
                    pygame.draw.circle(self.WINDOW, self.BLUE, 
                                      (self.GRID_OFFSET_X + j * self.CELL_SIZE + self.CELL_SIZE//2, self.GRID_OFFSET_Y + i * self.CELL_SIZE + self.CELL_SIZE//2), 
                                      self.CELL_SIZE//2 - 5, 3)
        
        pygame.display.update()
        
    def countdown_timer(self):
        """Đếm ngược thời gian"""
        while self.timer_running and self.time_left > 0:
            time.sleep(1)
            self.time_left -= 1
        
        if self.timer_running and self.time_left <= 0:
            self.game_status = "TIME'S UP!"
            
    def start_timer(self):
        """Bắt đầu đếm giờ"""
        self.time_left = 40
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.countdown_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
    def stop_timer(self):
        """Dừng đếm giờ"""
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join(0.1)
            
    def recv_move(self):
        """Nhận nước đi từ đối thủ"""
        data = self.safe_recv()
        if data is None:
            return None
        
        # Kiểm tra timeout từ đối thủ
        if data == "TIMEOUT":
            self.game_status = "Opponent ran out of time!"
            return (-2, -2)
        
        try:
            x, y = map(int, data.split())
            return x, y
        except ValueError:
            self.game_status = "Invalid data received!"
            return None
            
    def send_move(self, x, y):
        """Gửi nước đi"""
        return self.safe_send(f"{x} {y}")
        
    def send_timeout(self):
        """Gửi thông báo hết giờ"""
        return self.safe_send("TIMEOUT")
        
    def get_valid_move(self, board, symbol):
        """Lấy nước đi hợp lệ từ người chơi"""
        self.start_timer()
        self.game_status = f"Your turn ({symbol})! Click to make a move."
        
        running = True
        while running and self.timer_running and self.time_left > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return (-1, -1)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Kiểm tra click vào bàn cờ
                    if (self.GRID_OFFSET_X <= mouse_x <= self.GRID_OFFSET_X + self.BOARD_SIZE * self.CELL_SIZE and
                        self.GRID_OFFSET_Y <= mouse_y <= self.GRID_OFFSET_Y + self.BOARD_SIZE * self.CELL_SIZE):
                        
                        # Tính toán tọa độ ô
                        board_x = (mouse_y - self.GRID_OFFSET_Y) // self.CELL_SIZE
                        board_y = (mouse_x - self.GRID_OFFSET_X) // self.CELL_SIZE
                        
                        if 0 <= board_x < self.BOARD_SIZE and 0 <= board_y < self.BOARD_SIZE:
                            if board[board_x][board_y] == ".":
                                self.stop_timer()
                                return board_x, board_y
                            else:
                                self.game_status = "This cell is already taken!"
            
            self.draw_board(board)
            pygame.time.delay(50)
            
        if self.time_left <= 0:
            self.game_status = "You ran out of time!"
            self.stop_timer()
            return (-2, -2)
        
        return (-1, -1)
        
    def ask_continue(self):
        """Hỏi người chơi có muốn chơi lại không"""
        msg = self.safe_recv()
        if msg is None:
            return False
            
        # Convert message to English
        if "Bạn có muốn chơi lại không?" in msg:
            msg = "Do you want to play again?"
        elif "Cả hai đồng ý chơi lại" in msg:
            msg = "Both agreed to play again. Starting new game!"
        elif "Một trong hai không đồng ý" in msg:
            msg = "One player declined. Game over."
        
        self.game_status = msg + " (y/n)"
        
        waiting_answer = True
        answer = 'n'
        
        while waiting_answer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.safe_send('n')
                    return False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        answer = 'y'
                        waiting_answer = False
                    elif event.key == pygame.K_n:
                        answer = 'n'
                        waiting_answer = False
            
            # Vẽ màn hình chờ
            self.WINDOW.fill(self.WHITE)
            prompt = self.FONT.render(self.game_status, True, self.BLACK)
            instruction = self.SMALL_FONT.render("Press Y to play again, N to exit", True, self.BLUE)
            self.WINDOW.blit(prompt, (self.WIDTH//2 - prompt.get_width()//2, self.HEIGHT//2 - 30))
            self.WINDOW.blit(instruction, (self.WIDTH//2 - instruction.get_width()//2, self.HEIGHT//2 + 10))
            pygame.display.update()
            pygame.time.delay(50)
        
        self.safe_send(answer)
        return answer == 'y'
        
    def show_game_result(self, board, result):
        """Hiển thị kết quả game"""
        # Vẽ bàn cờ cuối cùng
        self.draw_board(board)
        
        # Tạo overlay cho thông báo kết quả
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(180)  # Semi-transparent
        overlay.fill(self.BLACK)
        self.WINDOW.blit(overlay, (0, 0))
        
        # Hiển thị thông báo kết quả
        if result == "WIN":
            result_text = "YOU WON!"
            color = self.GREEN
        else:  # LOSS
            result_text = "YOU LOST"
            color = self.RED
        
        # Vẽ text kết quả
        result_surface = self.FONT.render(result_text, True, color)
        result_rect = result_surface.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
        self.WINDOW.blit(result_surface, result_rect)
        
        # Vẽ thông báo chờ
        wait_text = "Press any key to continue..."
        wait_surface = self.SMALL_FONT.render(wait_text, True, self.WHITE)
        wait_rect = wait_surface.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 20))
        self.WINDOW.blit(wait_surface, wait_rect)
        
        pygame.display.update()
        
        # Chờ người chơi nhấn phím
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    break
            pygame.time.delay(50)
        
    def connect_to_server(self):
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            start_msg = self.safe_recv()
            if start_msg is None:
                return False
                
            # Convert message to English
            if "Bạn là X" in start_msg:
                start_msg = "You are X"
            elif "Bạn là O" in start_msg:
                start_msg = "You are O"
            
            self.game_status = start_msg
            self.my_symbol = "X" if "X" in start_msg else "O"
            self.enemy_symbol = "O" if self.my_symbol == "X" else "X"
            
            return True
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            self.game_status = "Failed to connect to server!"
            return False
            
    def play_game_round(self):
        """Chơi một ván game"""
        board = create_board()
        is_my_turn = self.my_symbol == "X"
        
        if is_my_turn:
            self.game_status = "Your turn!"
        else:
            self.game_status = "Waiting for opponent..."
        
        game_running = True
        game_result = None  # Lưu kết quả game
        
        while game_running:
            self.draw_board(board)
            
            if is_my_turn:
                self.game_status = f"Your turn! You have {self.time_left} seconds to move."
                x, y = self.get_valid_move(board, self.my_symbol)
                
                if x == -2 and y == -2:
                    game_result = "LOSS"  # Thua do timeout
                    self.game_status = "You lost due to timeout!"
                    self.send_timeout()
                    game_running = False
                elif x == -1 and y == -1:
                    pygame.quit()
                    return False
                else:
                    board[x][y] = self.my_symbol
                    if check_win(board, x, y, self.my_symbol):
                        game_result = "WIN"  # Thắng
                        self.game_status = "🎉 You won!"
                        self.send_move(-1, -1)
                        game_running = False
                    else:
                        self.send_move(x, y)
            else:
                self.game_status = "Waiting for opponent's move..."
                self.draw_board(board)
                
                move = self.recv_move()
                if move is None:
                    pygame.quit()
                    return False
                
                x, y = move
                if x == -1 and y == -1:
                    game_result = "LOSS"  # Thua do đối thủ thắng
                    self.game_status = "Opponent won. You lost!"
                    game_running = False
                elif x == -2 and y == -2:
                    game_result = "WIN"  # Thắng do đối thủ timeout
                    self.game_status = "Opponent ran out of time! You win!"
                    game_running = False
                else:
                    board[x][y] = self.enemy_symbol
                    self.game_status = "Opponent made a move"
                    if check_win(board, x, y, self.enemy_symbol):
                        game_result = "LOSS"  # Thua do đối thủ thắng
                        self.game_status = "You lost!"
                        game_running = False
            
            is_my_turn = not is_my_turn
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
        
        # Hiển thị kết quả game trước khi hỏi chơi lại
        if game_result:
            self.show_game_result(board, game_result)
        
        return True
        
    def run(self):
        """Chạy client"""
        try:
            if not self.connect_to_server():
                return
            
            while True:
                if not self.play_game_round():
                    break
                
                # Hỏi chơi lại
                if not self.ask_continue():
                    break
                
                # Chờ xác nhận từ server
                confirm_msg = self.safe_recv()
                if confirm_msg is None:
                    break
                
                # Convert confirmation message
                if "Cả hai đồng ý chơi lại" in confirm_msg:
                    confirm_msg = "Both agreed to play again. Starting new game!"
                elif "Một trong hai không đồng ý" in confirm_msg:
                    confirm_msg = "One player declined. Game over."
                
                self.game_status = confirm_msg
                
                # Hiển thị thông báo xác nhận
                self.WINDOW.fill(self.WHITE)
                confirm_text = self.FONT.render(confirm_msg, True, self.BLACK)
                self.WINDOW.blit(confirm_text, (self.WIDTH//2 - confirm_text.get_width()//2, self.HEIGHT//2))
                pygame.display.update()
                pygame.time.delay(2000)
                
                if "Game over" in confirm_msg:
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Client bị dừng bởi người dùng.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        pygame.quit()
        print("🔌 Đã đóng kết nối và thoát game.")

def main():
    client = CaroClient()
    client.run()

if __name__ == "__main__":
    main()