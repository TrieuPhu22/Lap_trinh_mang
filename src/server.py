import socket

def ask_continue(conn, player_num):
    conn.sendall("Bạn có muốn chơi lại không? (y/n): ".encode('utf-8'))
    resp = conn.recv(1024).decode('utf-8').strip().lower()
    print(f"Người chơi {player_num} chọn: {resp}")
    return resp == 'y'

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
            while True:
                # Nhận từ người chơi 1 (X)
                try:
                    move1 = conn1.recv(1024)
                    if not move1:
                        print("❌ Người chơi 1 đã ngắt kết nối.")
                        break
                    conn2.sendall(move1)
                    if move1.decode().strip() == "-1 -1":
                        break
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
                    if move2.decode().strip() == "-1 -1":
                        break
                except Exception as e:
                    print("❌ Lỗi khi nhận dữ liệu từ người chơi 2:", e)
                    break

            # Hỏi tiếp tục
            cont1 = ask_continue(conn1, 1)
            cont2 = ask_continue(conn2, 2)
            if cont1 and cont2:
                conn1.sendall("Cả hai đồng ý chơi lại. Bắt đầu ván mới!".encode('utf-8'))
                conn2.sendall("Cả hai đồng ý chơi lại. Bắt đầu ván mới!".encode('utf-8'))
                continue
            else:
                conn1.sendall("Một trong hai không đồng ý. Kết thúc trận đấu.".encode('utf-8'))
                conn2.sendall("Một trong hai không đồng ý. Kết thúc trận đấu.".encode('utf-8'))
                break

    finally:
        conn1.close()
        conn2.close()
        server.close()
        print("🔌 Kết thúc trận đấu.")

if __name__ == "__main__":
    main()
