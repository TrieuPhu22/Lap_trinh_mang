import socket

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", 9999))  # Port đã dùng bên client
    server.listen(2)
    print("🎮 Đang chờ 2 người chơi kết nối...")

    try:
        conn1, addr1 = server.accept()
        print(f"✅ Người chơi 1 đã kết nối từ {addr1}")
        conn1.sendall("Bạn là X".encode('utf-8'))

        conn2, addr2 = server.accept()
        print(f"✅ Người chơi 2 đã kết nối từ {addr2}")
        conn2.sendall("Bạn là O".encode('utf-8'))

        while True:
            # Nhận từ người chơi 1 (X)
            try:
                move1 = conn1.recv(1024)
                if not move1:
                    print("❌ Người chơi 1 đã ngắt kết nối.")
                    break
                conn2.sendall(move1)
            except Exception as e:
                print("❌ Lỗi khi nhận dữ liệu từ người chơi 1:", e)
                break

            # Nhận từ người chơi 2 (O)
            try:
                move2 = conn2.recv(1024)
                if not move2:
                    print("❌ Người chơi 2 đã ngắt kết nối.")
                    break
                conn1.sendall(move2)
            except Exception as e:
                print("❌ Lỗi khi nhận dữ liệu từ người chơi 2:", e)
                break

    finally:
        conn1.close()
        conn2.close()
        server.close()
        print("🔌 Kết thúc trận đấu.")

if __name__ == "__main__":
    main()
