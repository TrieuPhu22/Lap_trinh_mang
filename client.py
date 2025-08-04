import socket
from common import create_board, print_board, check_win

def recv_move(sock):
    try:
        data = sock.recv(1024).decode().strip()
        if not data:
            print("⛔ Mất kết nối với đối thủ.")
            return None
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

def get_valid_move(board, symbol):
    while True:
        try:
            x, y = map(int, input(f"Bạn ({symbol}) nhập tọa độ (x y): ").split())
            if not (0 <= x < len(board) and 0 <= y < len(board[0])):
                print("⚠️ Tọa độ nằm ngoài bàn cờ.")
                continue
            if board[x][y] != ".":
                print("⚠️ Ô đã được đánh.")
                continue
            return x, y
        except ValueError:
            print("⚠️ Nhập sai định dạng. Hãy nhập x y (vd: 1 2)")

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
                x, y = get_valid_move(board, symbol)
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