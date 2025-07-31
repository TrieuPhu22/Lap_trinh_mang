import socket
import threading

BOARD_SIZE = 15
board = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_board():
    for row in board:
        print(" ".join(row))
    print()

def handle_server_recv(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if data.startswith("MOVE"):
                _, x, y = data.strip().split()
                board[int(x)][int(y)] = "O"
                print("\nĐối thủ đánh:")
                print_board()
        except:
            break

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 8888))
    threading.Thread(target=handle_server_recv, args=(s,), daemon=True).start()

    print("Đã kết nối. Bạn là X. Nhập tọa độ (x y):")
    while True:
        try:
            print_board()
            x, y = map(int, input("Tọa độ x y: ").split())
            board[x][y] = "X"
            s.sendall(f"MOVE {x} {y}".encode())
        except:
            break

if __name__ == "__main__":
    main()
