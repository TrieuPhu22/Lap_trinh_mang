import socket
import threading
import json
import time

# Game state
ball = {'x': 300, 'y': 200, 'dx': 3, 'dy': 3}
paddles = {1: {'y': 150, 'score': 0}, 2: {'y': 150, 'score': 0}}
clients = []

# Server setup
HOST = '0.0.0.0'
PORT = 23456
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)

def handle_client(conn, player_id):
    global paddles
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            msg = json.loads(data)
            if msg['action'] == 'move':
                direction = msg['direction']
                if direction == 'up':
                    paddles[player_id]['y'] -= 10
                elif direction == 'down':
                    paddles[player_id]['y'] += 10
        except:
            break
    conn.close()

def broadcast_game_state():
    while True:
        # Move ball
        ball['x'] += ball['dx']
        ball['y'] += ball['dy']

        # Bounce on top/bottom
        if ball['y'] <= 0 or ball['y'] >= 400:
            ball['dy'] *= -1

        # Bounce on paddles
        if ball['x'] <= 20 and paddles[1]['y'] <= ball['y'] <= paddles[1]['y'] + 60:
            ball['dx'] *= -1
        elif ball['x'] >= 580 and paddles[2]['y'] <= ball['y'] <= paddles[2]['y'] + 60:
            ball['dx'] *= -1

        # Scoring
        if ball['x'] < 0:
            paddles[2]['score'] += 1
            ball['x'], ball['y'] = 300, 200
        elif ball['x'] > 600:
            paddles[1]['score'] += 1
            ball['x'], ball['y'] = 300, 200

        state = {
            'ball': ball,
            'players': paddles
        }

        msg = json.dumps(state).encode()
        for c in clients:
            try:
                c.sendall(msg)
            except:
                continue
        time.sleep(0.03)

print("Waiting for players...")
for i in range(2):
    conn, addr = server.accept()
    print(f"Player {i+1} connected from {addr}")
    clients.append(conn)
    threading.Thread(target=handle_client, args=(conn, i+1)).start()

threading.Thread(target=broadcast_game_state).start()
