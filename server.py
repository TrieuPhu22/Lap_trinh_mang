import socket

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Cho phép tái sử dụng địa chỉ

    server.bind(("0.0.0.0", 9999))
    server.listen(2)
    print("🎮 Đang chờ 2 người chơi kết nối...")

    conn1, addr1 = server.accept()
    print(f"✅ Người chơi 1 đã kết nối từ {addr1}")
    conn1.sendall("Bạn là người chơi 1".encode())

    conn2, addr2 = server.accept()
    print(f"✅ Người chơi 2 đã kết nối từ {addr2}")
    conn2.sendall("Bạn là người chơi 2".encode())

    # Vòng lặp giao tiếp giữa hai người chơi
    while True:
        try:
            # Người chơi 1 đánh
            conn1.sendall("Đến lượt bạn".encode())
            move1 = conn1.recv(1024)
            if not move1:
                break
            conn2.sendall(move1)  # Gửi cho người chơi 2 biết nước đi

            # Người chơi 2 đánh
            conn2.sendall("Đến lượt bạn".encode())
            move2 = conn2.recv(1024)
            if not move2:
                break
            conn1.sendall(move2)  # Gửi cho người chơi 1 biết nước đi

        except ConnectionResetError:
            print("🔌 Mất kết nối với một trong hai người chơi.")
            break

    conn1.close()
    conn2.close()
    server.close()

if __name__ == "__main__":
    main()
