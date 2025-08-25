import socket
import threading
import time
from common import create_board, print_board, check_win

# Biến toàn cục để theo dõi thời gian
time_left = 40
timer_running = False
timer_thread = None

def countdown_timer():
    global time_left, timer_running
    while timer_running and time_left > 0:
        time.sleep(1)
        time_left -= 1
        # In thời gian còn lại mỗi 5 giây hoặc 10 giây cuối
        if time_left <= 10 or time_left % 5 == 0:
            print(f"⏱️ Còn {time_left} giây")
    
    # Nếu hết giờ và timer vẫn chạy
    if timer_running and time_left <= 0:
        print("⏰ HẾT GIỜ!")

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
            print("⛔ Mất kết nối với đối thủ.")
            return None
        
        # Kiểm tra nếu là thông báo hết giờ từ đối thủ
        if data == "TIMEOUT":
            print("🕒 Đối thủ đã hết thời gian!")
            return (-2, -2)  # Mã đặc biệt cho hết giờ
        
        x, y = map(int, data.split())
        return x, y
    except:
        print("⛔ Lỗi khi nhận dữ liệu từ đối thủ.")
        return None

def send_move(sock, x, y):
    try:
        sock.send(f"{x} {y}".encode())
    except:
        print("⛔ Gửi dữ liệu thất bại.")


def send_timeout(sock):
    try:
        sock.send("TIMEOUT".encode())
    except:
        print("⛔ Gửi thông báo hết giờ thất bại.")

def get_valid_move(board, symbol):
    global time_left, timer_running
    
    # Bắt đầu đếm giờ
    start_timer()
    
    print(f"Bạn ({symbol}) có {time_left} giây để nhập tọa độ (x y): ")
    
    # Sử dụng cơ chế thay thế thay vì select
    while timer_running:
        if time_left <= 0:
            stop_timer()
            print("⏰ Bạn đã hết thời gian!")
            return (-2, -2)  # Mã đặc biệt cho hết giờ
        
        # Sử dụng cơ chế input thông thường với timeout kiểm soát bằng thread
        try:
            # Tạo thread riêng để đọc input
            input_value = [None]
            input_provided = [False]
            
            def get_input():
                try:
                    value = input().strip()
                    if value:
                        input_value[0] = value
                        input_provided[0] = True
                except Exception as e:
                    print(f"Lỗi khi đọc input: {e}")
            
            input_thread = threading.Thread(target=get_input)
            input_thread.daemon = True
            input_thread.start()
            
            # Đợi trong khi kiểm tra thời gian
            max_wait = min(1, time_left)  # Đợi tối đa 1 giây hoặc thời gian còn lại
            wait_until = time.time() + max_wait
            
            while time.time() < wait_until and timer_running and time_left > 0 and not input_provided[0]:
                time.sleep(0.1)
            
            if input_provided[0]:
                move = input_value[0]
                try:
                    x, y = map(int, move.split())
                    if not (0 <= x < len(board) and 0 <= y < len(board[0])):
                        print("⚠️ Tọa độ nằm ngoài bàn cờ.")
                        continue
                    if board[x][y] != ".":
                        print("⚠️ Ô đã được đánh.")
                        continue
                    
                    stop_timer()
                    return x, y
                except ValueError:
                    print("⚠️ Nhập sai định dạng. Hãy nhập x y (vd: 1 2)")
            else:
                # Nếu không có input trong khoảng thời gian chờ
                # Hiển thị thông báo định kỳ
                if time_left % 5 == 0 or time_left <= 10:
                    print(f"⏱️ Còn {time_left} giây để đánh. Nhập tọa độ (x y): ", end="", flush=True)
                    
        except Exception as e:
            print(f"⚠️ Lỗi: {e}")

def ask_continue(sock):
    msg = sock.recv(1024).decode('utf-8')
    print(msg)
    ans = input().strip().lower()
    sock.send(ans.encode('utf-8'))
    return ans == 'y'

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9999))

    start_msg = s.recv(1024).decode('utf-8')
    print(start_msg)

    symbol = "X" if "X" in start_msg else "O"
    enemy_symbol = "O" if symbol == "X" else "X"

    while True:
        board = create_board()
        print_board(board)
        is_my_turn = symbol == "X"

        # Vòng lặp chơi 1 ván
        while True:
            if is_my_turn:
                print(f"🕒 Lượt của bạn! Bạn có 40 giây để đánh.")
                x, y = get_valid_move(board, symbol)
                
                # Kiểm tra hết giờ
                if x == -2 and y == -2:
                    print("⏰ Bạn đã thua do hết thời gian!")
                    send_timeout(s)
                    break
                
                board[x][y] = symbol
                print_board(board)
                if check_win(board, x, y, symbol):
                    print("🎉 Bạn đã thắng!")
                    send_move(s, -1, -1)
                    break
                send_move(s, x, y)
            else:
                print("⏳ Đang chờ đối thủ đánh...")
                move = recv_move(s)
                if move is None:
                    return
                
                x, y = move
                if x == -1 and y == -1:
                    print("❌ Đối thủ đã thắng. Bạn đã thua!")
                    break
                elif x == -2 and y == -2:
                    print("🎉 Đối thủ đã hết thời gian! Bạn thắng!")
                    break
                
                board[x][y] = enemy_symbol
                print("📍 Đối thủ đã đánh:")
                print_board(board)
                if check_win(board, x, y, enemy_symbol):
                    print("❌ Bạn đã thua!")
                    break

            is_my_turn = not is_my_turn

        # Sau khi kết thúc ván, hỏi chơi lại
        while True:
            cont_msg = s.recv(1024).decode('utf-8')
            print(cont_msg)
            if "chơi lại" in cont_msg:
                ans = input().strip().lower()
                s.send(ans.encode('utf-8'))
                # Chờ xác nhận từ server
                confirm_msg = s.recv(1024).decode('utf-8')
                print(confirm_msg)
                if "Bắt đầu ván mới" in confirm_msg:
                    break  # Thoát vòng hỏi để bắt đầu lại ván mới
                elif "Kết thúc" in confirm_msg:
                    s.close()
                    return
            elif "Kết thúc" in cont_msg:
                s.close()
                return
            else:
                ans = input().strip().lower()
                s.send(ans.encode('utf-8'))

if __name__ == "__main__":
    main()