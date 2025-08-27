import socket
import threading
import time

class GameServer:
    def __init__(self, host="0.0.0.0", port=9999, timeout=30):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connections = []
        self.server = None
        
    def setup_server(self):
        """Thiết lập server socket"""
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(2)
        self.server.settimeout(60)  # Timeout cho accept
        print(f"🎮 Server đang chờ 2 người chơi kết nối tại {self.host}:{self.port}...")
        
    def safe_send(self, conn, message):
        """Gửi dữ liệu an toàn với error handling"""
        try:
            conn.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"❌ Lỗi khi gửi dữ liệu: {e}")
            return False
            
    def safe_recv(self, conn, player_num):
        """Nhận dữ liệu an toàn với timeout"""
        try:
            conn.settimeout(self.timeout)
            data = conn.recv(1024)
            if not data:
                print(f"❌ Người chơi {player_num} đã ngắt kết nối.")
                return None
            return data.decode('utf-8').strip()
        except socket.timeout:
            print(f"⏰ Timeout khi nhận dữ liệu từ người chơi {player_num}")
            return "TIMEOUT"
        except Exception as e:
            print(f"❌ Lỗi khi nhận dữ liệu từ người chơi {player_num}: {e}")
            return None
            
    def ask_continue(self, conn, player_num):
        """Hỏi người chơi có muốn chơi lại không"""
        if not self.safe_send(conn, "Bạn có muốn chơi lại không? (y/n): "):
            return False
            
        resp = self.safe_recv(conn, player_num)
        if resp is None:
            return False
            
        print(f"Người chơi {player_num} chọn: {resp}")
        return resp.lower() == 'y'
        
    def handle_player_turn(self, sender_conn, receiver_conn, player_num):
        """Xử lý lượt của một người chơi"""
        move_data = self.safe_recv(sender_conn, player_num)
        if move_data is None:
            return False
            
        # Gửi nước đi cho người chơi khác
        if not self.safe_send(receiver_conn, move_data):
            return False
            
        # Kiểm tra kết thúc ván
        if move_data in ["-1 -1", "TIMEOUT"]:
            return False
            
        return True
        
    def run_game_loop(self):
        """Vòng lặp chính của game"""
        while True:
            # Vòng lặp cho một ván game
            game_ended = False
            while not game_ended:
                # Lượt người chơi 1 (X)
                if not self.handle_player_turn(self.connections[0], self.connections[1], 1):
                    game_ended = True
                    break
                    
                # Lượt người chơi 2 (O)
                if not self.handle_player_turn(self.connections[1], self.connections[0], 2):
                    game_ended = True
                    break
                    
            # Hỏi tiếp tục
            cont1 = self.ask_continue(self.connections[0], 1)
            cont2 = self.ask_continue(self.connections[1], 2)
            
            if cont1 and cont2:
                message = "Cả hai đồng ý chơi lại. Bắt đầu ván mới!"
                self.safe_send(self.connections[0], message)
                self.safe_send(self.connections[1], message)
                print("🔄 Bắt đầu ván mới!")
                continue
            else:
                message = "Một trong hai không đồng ý. Kết thúc trận đấu."
                self.safe_send(self.connections[0], message)
                self.safe_send(self.connections[1], message)
                print("🏁 Kết thúc trận đấu.")
                break
                
    def accept_connections(self):
        """Chấp nhận kết nối từ 2 người chơi"""
        try:
            # Chấp nhận người chơi 1
            conn1, addr1 = self.server.accept()
            print(f"✅ Người chơi 1 đã kết nối từ {addr1}")
            self.safe_send(conn1, "Bạn là X")
            self.connections.append(conn1)
            
            # Chấp nhận người chơi 2
            conn2, addr2 = self.server.accept()
            print(f"✅ Người chơi 2 đã kết nối từ {addr2}")
            self.safe_send(conn2, "Bạn là O")
            self.connections.append(conn2)
            
            return True
        except socket.timeout:
            print("⏰ Timeout khi chờ kết nối")
            return False
        except Exception as e:
            print(f"❌ Lỗi khi chấp nhận kết nối: {e}")
            return False
            
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        for conn in self.connections:
            try:
                conn.close()
            except:
                pass
        if self.server:
            try:
                self.server.close()
            except:
                pass
        print("🔌 Đã đóng tất cả kết nối.")
        
    def run(self):
        """Chạy server"""
        try:
            self.setup_server()
            
            if not self.accept_connections():
                return
                
            self.run_game_loop()
            
        except KeyboardInterrupt:
            print("\n🛑 Server bị dừng bởi người dùng.")
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")
        finally:
            self.cleanup()

def main():
    server = GameServer()
    server.run()

if __name__ == "__main__":
    main()