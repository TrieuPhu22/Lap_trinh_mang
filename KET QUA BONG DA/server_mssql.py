import socket
import threading
import requests
import json
from datetime import datetime, timedelta

HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

API_KEY = "b0fc31c76f204a5f81d3adfd97ecd66d"
API_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_KEY}

# ---------- API Wrappers ----------
def get_matches_by_comp(comp_id, days=7):
    today = datetime.today().date()
    dateFrom = today.strftime("%Y-%m-%d")
    dateTo = (today + timedelta(days=days)).strftime("%Y-%m-%d")
    url = f"{API_URL}/competitions/{comp_id}/matches?dateFrom={dateFrom}&dateTo={dateTo}"
    resp = requests.get(url, headers=headers)
    return resp.json()

def get_standings(comp_id):
    url = f"{API_URL}/competitions/{comp_id}/standings"
    resp = requests.get(url, headers=headers)
    return resp.json()

def get_scorers(comp_id):
    url = f"{API_URL}/competitions/{comp_id}/scorers"
    resp = requests.get(url, headers=headers)
    return resp.json()

def get_team(team_id):
    """Trả về thông tin chi tiết đội + squad (danh sách cầu thủ)"""
    url = f"{API_URL}/teams/{team_id}"
    resp = requests.get(url, headers=headers)
    return resp.json()

def get_player(player_id):
    """Trả về thông tin chi tiết cầu thủ"""
    url = f"{API_URL}/persons/{player_id}"
    resp = requests.get(url, headers=headers)
    return resp.json()

# ---------- Socket Handler ----------
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    try:
        while True:
            option = conn.recv(1024).decode(FORMAT)
            if not option:
                break

            parts = option.split()
            cmd = parts[0]

            if cmd == "matches":
                comp_id = parts[1]
                data = get_matches_by_comp(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "standings":
                comp_id = parts[1]
                data = get_standings(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "scorers":
                comp_id = parts[1]
                data = get_scorers(comp_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "team":
                team_id = parts[1]
                data = get_team(team_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            elif cmd == "player":
                player_id = parts[1]
                data = get_player(player_id)
                conn.sendall(json.dumps(data).encode(FORMAT))

            else:
                conn.sendall(b"{}")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

def run_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[LISTENING] Server on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    run_server()
