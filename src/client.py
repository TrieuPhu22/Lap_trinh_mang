import socket
import sys
from common import create_board, print_board, check_win, BOARD_SIZE

def recv_move(sock):
    """Nhận nước đi từ đối thủ"""
    try:
        data = sock.recv(1024).decode('utf-8').strip()
        if not data:
            print("⛔ Mất kết nối với đối thủ.")
            return None
        
        x, y = map(int, data.split())
        return x, y
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print("⛔ Đối thủ đã ngắt kết nối.")
        return None
    except ValueError:
        print("⛔ Dữ liệu từ đối thủ không hợp lệ.")
        return None
    except Exception as e:
        print(f"⛔ Lỗi khi nhận dữ liệu: {e}")
        return None

def send_move(sock, x, y):
    """Gửi nước đi cho đối thủ"""
    try:
        message = f"{x} {y}"
        sock.send(message.encode('utf-8'))
        print(f"📤 Đã gửi nước đi: ({x}, {y})")
        return True
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print("⛔ Không thể gửi - đối thủ đã ngắt kết nối.")
        return False
    except Exception as e:
        print(f"⛔ Gửi dữ liệu thất bại: {e}")
        return False

def get_valid_move(board, symbol):
    """Nhập nước đi hợp lệ từ người chơi"""
    while True:
        try:
            print(f"\n💡 Nhập tọa độ từ 0 đến {BOARD_SIZE-1}")
            move_input = input(f"🎯 Bạn ({symbol}) nhập tọa độ (x y): ").strip()
            
            if move_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Bạn đã thoát game.")
                return -1, -1
            
            x, y = map(int, move_input.split())
            
            if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                print(f"⚠️ Tọa độ phải từ 0 đến {BOARD_SIZE-1}.")
                continue
                
            if board[x][y] != ".":
                print("⚠️ Ô này đã có quân cờ. Chọn ô khác.")
                continue
                
            return x, y
            
        except ValueError:
            print("⚠️ Định dạng không đúng. Nhập hai số cách nhau bởi dấu cách (vd: 7 8)")
        except KeyboardInterrupt:
            print("\n👋 Bạn đã thoát game.")
            return -1, -1

def safe_recv(sock, timeout=30):
    """Nhận dữ liệu an toàn với timeout"""
    try:
        sock.settimeout(timeout)
        data = sock.recv(1024).decode('utf-8')
        sock.settimeout(None)  # Reset timeout
        return data
    except socket.timeout:
        print(f"⏰ Timeout sau {timeout} giây.")
        return None
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print("⛔ Kết nối bị ngắt.")
        return None
    except Exception as e:
        print(f"⛔ Lỗi nhận dữ liệu: {e}")
        return None

def handle_continue_game(sock):
    """Xử lý hỏi chơi lại"""
    try:
        # Nhận câu hỏi từ server
        question = safe_recv(sock, 30)
        if question is None:
            return False
            
        print(f"\n🤔 {question}")
        
        while True:
            answer = input("👉 Nhập lựa chọn: ").strip().lower()
            if answer in ['y', 'yes', 'có', 'c']:
                sock.send('y'.encode('utf-8'))
                break
            elif answer in ['n', 'no', 'không', 'k']:
                sock.send('n'.encode('utf-8'))
                break
            else:
                print("⚠️ Chỉ nhập 'y' (có) hoặc 'n' (không)")
        
        # Nhận phản hồi từ server
        response = safe_recv(sock, 10)
        if response:
            print(f"📨 {response}")
            
            if "Bắt đầu ván mới" in response or "Bắt đầu ván" in response:
                return True
            elif "Kết thúc" in response:
                return False
                
        return False
        
    except Exception as e:
        print(f"⛔ Lỗi xử lý chơi lại: {e}")
        return False

def main():
    sock = None
    
    try:
        # Kết nối đến server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("🔗 Đang kết nối đến server...")
        sock.connect(("127.0.0.1", 9999))
        print("✅ Đã kết nối thành công!")
        
        # Nhận thông tin vai trò (X hoặc O)
        start_msg = safe_recv(sock, 10)
        if start_msg is None:
            print("❌ Không nhận được thông tin từ server.")
            return
            
        print(f"🎭 {start_msg}")
        symbol = "X" if "X" in start_msg else "O"
        enemy_symbol = "O" if symbol == "X" else "X"
        
        print(f"🎯 Bạn chơi với ký hiệu: {symbol}")
        print(f"🎯 Đối thủ chơi với ký hiệu: {enemy_symbol}")
        
        game_count = 1
        
        while True:
            print(f"\n🎲 =================== VÁN {game_count} ===================")
            
            # Khởi tạo bàn cờ mới
            board = create_board()
            print(f"📋 Bàn cờ {BOARD_SIZE}x{BOARD_SIZE} đã được tạo:")
            print_board(board)
            
            # Xác định ai đi trước (X luôn đi trước)
            is_my_turn = (symbol == "X")
            move_count = 0
            game_over = False
            
            print(f"🚀 {'Bạn đi trước!' if is_my_turn else 'Đối thủ đi trước!'}")
            
            # Vòng lặp chơi một ván
            while not game_over:
                if is_my_turn:
                    print(f"\n🎯 === LƯỢT CỦA BẠN ({symbol}) ===")
                    
                    # Người chơi nhập nước đi
                    x, y = get_valid_move(board, symbol)
                    
                    # Kiểm tra thoát game
                    if x == -1 and y == -1:
                        print("📤 Gửi tín hiệu thoát...")
                        send_move(sock, -1, -1)
                        return
                    
                    # Thực hiện nước đi
                    board[x][y] = symbol
                    move_count += 1
                    
                    print(f"✅ Bạn đã đánh tại ({x}, {y})")
                    print_board(board)
                    
                    # Kiểm tra thắng
                    if check_win(board, x, y, symbol):
                        print("🎉🎉🎉 CHÚC MỪNG! BẠN ĐÃ THẮNG! 🎉🎉🎉")
                        send_move(sock, -1, -1)  # Gửi tín hiệu kết thúc
                        game_over = True
                        break
                    
                    # Gửi nước đi cho đối thủ
                    if not send_move(sock, x, y):
                        print("❌ Không thể gửi nước đi. Kết thúc game.")
                        return
                    
                else:
                    print(f"\n⏳ === LƯỢT CỦA ĐỐI THỦ ({enemy_symbol}) ===")
                    print("⏳ Đang chờ đối thủ đánh...")
                    
                    # Nhận nước đi từ đối thủ
                    move = recv_move(sock)
                    if move is None:
                        print("❌ Mất kết nối với đối thủ.")
                        return
                    
                    x, y = move
                    
                    # Kiểm tra tín hiệu kết thúc (đối thủ thắng)
                    if x == -1 and y == -1:
                        print("💔💔💔 ĐỐI THỦ ĐÃ THẮNG! BẠN THUA! 💔💔💔")
                        game_over = True
                        break
                    
                    # Thực hiện nước đi của đối thủ
                    board[x][y] = enemy_symbol
                    move_count += 1
                    
                    print(f"📍 Đối thủ đã đánh tại ({x}, {y})")
                    print_board(board)
                    
                    # Kiểm tra đối thủ có thắng không
                    if check_win(board, x, y, enemy_symbol):
                        print("💔💔💔 ĐỐI THỦ ĐÃ THẮNG! BẠN THUA! 💔💔💔")
                        game_over = True
                        break
                
                # Chuyển lượt
                is_my_turn = not is_my_turn
            
            print(f"\n✅ Ván {game_count} kết thúc sau {move_count} nước đi.")
            game_count += 1
            
            # Hỏi chơi lại
            print("\n🔄 =================== HỎI CHƠI LẠI ===================")
            continue_game = handle_continue_game(sock)
            
            if not continue_game:
                print("👋 Kết thúc trò chơi. Cảm ơn bạn đã chơi!")
                break
            
            print("\n🎊 Chuẩn bị ván mới...")
    
    except KeyboardInterrupt:
        print("\n⚠️ Bạn đã dừng game (Ctrl+C)")
    except ConnectionRefusedError:
        print("❌ Không thể kết nối đến server. Kiểm tra server đã chạy chưa?")
    except Exception as e:
        print(f"❌ Lỗi không mong muốn: {e}")
    
    finally:
        if sock:
            try:
                sock.close()
                print("🔌 Đã đóng kết nối.")
            except:
                pass

if __name__ == "__main__":
    main()