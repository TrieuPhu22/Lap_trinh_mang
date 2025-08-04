import socket
import sys
import threading # Sử dụng threading để xử lý mỗi cặp client trong một luồng riêng

# Hàm xử lý một cặp client
def handle_clients(conn1, addr1, conn2, addr2):
    print(f"✅ Bắt đầu xử lý cặp người chơi: {addr1} (X) và {addr2} (O)")
    try:
        conn1.sendall("Bạn là X".encode('utf-8'))
        conn2.sendall("Bạn là O".encode('utf-8'))

        while True: # Vòng lặp cho nhiều ván chơi trong cùng một cặp kết nối
            print(f"\n--- Bắt đầu ván mới giữa {addr1} và {addr2} ---")
            game_over = False
            while not game_over: # Vòng lặp cho 1 ván chơi
                # Nhận từ người chơi 1 (X)
                try:
                    move1 = conn1.recv(1024)
                    if not move1:
                        print(f"❌ Người chơi 1 ({addr1}) đã ngắt kết nối. Kết thúc trò chơi.")
                        game_over = True
                        break
                    
                    move_str1 = move1.decode().strip()
                    print(f"Người chơi 1 (X) gửi: {move_str1}")
                    conn2.sendall(move1) # Chuyển tiếp nước đi cho người chơi 2
                    if move_str1 == "-1 -1": # Tín hiệu thắng
                        game_over = True
                        break
                except Exception as e:
                    print(f"❌ Lỗi khi nhận dữ liệu từ người chơi 1 ({addr1}): {e}")
                    game_over = True
                    break

                if game_over: break 

                # Nhận từ người chơi 2 (O)
                try:
                    move2 = conn2.recv(1024)
                    if not move2:
                        print(f"❌ Người chơi 2 ({addr2}) đã ngắt kết nối. Kết thúc trò chơi.")
                        game_over = True
                        break
                    
                    move_str2 = move2.decode().strip()
                    print(f"Người chơi 2 (O) gửi: {move_str2}")
                    conn1.sendall(move2) # Chuyển tiếp nước đi cho người chơi 1
                    if move_str2 == "-1 -1": # Tín hiệu thắng
                        game_over = True
                        break
                except Exception as e:
                    print(f"❌ Lỗi khi nhận dữ liệu từ người chơi 2 ({addr2}): {e}")
                    game_over = True
                    break
            
            # Sau khi một ván kết thúc, hỏi chơi lại
            if not game_over: # Chỉ hỏi nếu game kết thúc bình thường (có người thắng)
                cont1 = ask_continue(conn1, 1)
                cont2 = ask_continue(conn2, 2)

                if cont1 and cont2:
                    conn1.sendall("Cả hai đồng ý chơi lại. Bắt đầu ván mới!".encode('utf-8'))
                    conn2.sendall("Cả hai đồng ý chơi lại. Bắt đầu ván mới!".encode('utf-8'))
                    # Vòng lặp ngoài (của handle_clients) sẽ tiếp tục để bắt đầu ván mới
                else:
                    conn1.sendall("Một trong hai không đồng ý. Kết thúc trận đấu.".encode('utf-8'))
                    conn2.sendall("Một trong hai không đồng ý. Kết thúc trận đấu.".encode('utf-8'))
                    break # Thoát vòng lặp ngoài, kết thúc cặp client này
            else:
                # Nếu game_over là True do mất kết nối, không hỏi chơi lại nữa
                break

    except Exception as e:
        print(f"❌ Lỗi trong quá trình xử lý cặp client ({addr1}, {addr2}): {e}")
    finally:
        print(f"🔌 Đóng kết nối cho cặp người chơi: {addr1} và {addr2}")
        if conn1:
            conn1.close()
        if conn2:
            conn2.close()

def ask_continue(conn, player_num):
    """Hỏi người chơi có muốn chơi lại không và trả về lựa chọn của họ."""
    try:
        conn.sendall("Bạn có muốn chơi lại không? (y/n): ".encode('utf-8'))
        resp = conn.recv(1024).decode('utf-8').strip().lower()
        print(f"Người chơi {player_num} chọn: {resp}")
        return resp == 'y'
    except Exception as e:
        print(f"Lỗi khi hỏi người chơi {player_num} chơi lại: {e}")
        return False # Coi như không đồng ý nếu có lỗi

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    HOST = "0.0.0.0"
    PORT = 9999
    
    try:
        server.bind((HOST, PORT))
        server.listen(2) # Có thể lắng nghe nhiều hơn 2 kết nối nếu muốn hàng đợi
        print(f"🎮 Máy chủ Gomoku đang chạy trên {HOST}:{PORT}")
        print("🎮 Đang chờ người chơi kết nối...")
    except Exception as e:
        print(f"❌ Lỗi khởi tạo máy chủ: {e}")
        sys.exit(1)

    # Vòng lặp vô hạn để server luôn lắng nghe các kết nối mới
    while True:
        try:
            print("Đang chờ người chơi 1...")
            conn1, addr1 = server.accept()
            print(f"✅ Người chơi 1 đã kết nối từ {addr1}")

            print("Đang chờ người chơi 2...")
            conn2, addr2 = server.accept()
            print(f"✅ Người chơi 2 đã kết nối từ {addr2}")

            # Tạo một luồng mới để xử lý cặp client này
            client_thread = threading.Thread(target=handle_clients, args=(conn1, addr1, conn2, addr2))
            client_thread.start()
            
        except KeyboardInterrupt:
            print("\nServer bị ngắt bởi người dùng.")
            break # Thoát vòng lặp chính
        except Exception as e:
            print(f"❌ Lỗi trong vòng lặp chấp nhận kết nối: {e}")
            # Có thể thêm logic để tiếp tục hoặc thoát tùy vào loại lỗi

    server.close() # Đóng socket lắng nghe khi server dừng
    print("🔌 Máy chủ đã tắt.")

if __name__ == "__main__":
    main()
