import socket
import threading

clients = []

def client_thread(conn, addr, opponent_conn):
    conn.sendall(b"Game Start. You are X.\n")
    while True:
        try:
            move = conn.recv(1024)
            if not move:
                break
            if opponent_conn:
                opponent_conn.sendall(move)
        except:
            break
    conn.close()

def accept_clients(server_socket):
    while True:
        conn, addr = server_socket.accept()
        print(f"[+] New connection from {addr}")
        clients.append(conn)
        if len(clients) % 2 == 0:
            threading.Thread(target=client_thread, args=(clients[-2], addr, clients[-1])).start()
            threading.Thread(target=client_thread, args=(clients[-1], addr, clients[-2])).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen()
    print("[*] Server listening on port 8888...")
    accept_clients(server)

if __name__ == "__main__":
    main()
