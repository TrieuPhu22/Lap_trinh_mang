import pygame
import socket
import threading
import json

WIDTH, HEIGHT = 640, 400
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

HOST = '127.0.0.1'
PORT = 12345
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

ball = {'x': 300, 'y': 200}
players = {1: {'y': 150, 'score': 0}, 2: {'y': 150, 'score': 0}}

def receive_data():
    global ball, players
    while True:
        try:
            data = client.recv(1024).decode()
            if not data:
                break
            state = json.loads(data)
            ball = state['ball']
            players = state['players']
        except:
            break

threading.Thread(target=receive_data).start()

running = True
while running:
    win.fill((0, 0, 0))

    # Draw ball
    pygame.draw.circle(win, (255, 255, 255), (ball['x'], ball['y']), 10)

    # Draw paddles
    pygame.draw.rect(win, (0, 255, 0), (10, players[1]['y'], 10, 60))
    pygame.draw.rect(win, (0, 0, 255), (620, players[2]['y'], 10, 60))

    # Draw scores
    font = pygame.font.SysFont(None, 36)
    s1 = font.render(str(players[1]['score']), True, (255, 255, 255))
    s2 = font.render(str(players[2]['score']), True, (255, 255, 255))
    win.blit(s1, (250, 10))
    win.blit(s2, (370, 10))

    pygame.display.flip()
    clock.tick(60)

    # Key events
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        client.sendall(json.dumps({'action': 'move', 'direction': 'up'}).encode())
    if keys[pygame.K_DOWN]:
        client.sendall(json.dumps({'action': 'move', 'direction': 'down'}).encode())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
client.close()
