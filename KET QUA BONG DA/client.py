import socket
import tkinter as tk
from tkinter import ttk, messagebox
import json

HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

COMPETITIONS = {
    "Premier League": "2021",
    "La Liga": "2014",
    "Bundesliga": "2002",
    "Serie A": "2019",
    "Champions League": "2001",
}

class SoccerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Soccer Data (football-data.org)")
        self.geometry("950x650")

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

        self.teams = {}     # {team_name: team_id}
        self.players = {}   # {player_name: player_id}

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.tab_matches = tk.Frame(self.notebook)
        self.tab_standings = tk.Frame(self.notebook)
        self.tab_scorers = tk.Frame(self.notebook)
        self.tab_team = tk.Frame(self.notebook)
        self.tab_player = tk.Frame(self.notebook)
        self.notebook.add(self.tab_matches, text="Matches")
        self.notebook.add(self.tab_standings, text="Standings")
        self.notebook.add(self.tab_scorers, text="Scorers")
        self.notebook.add(self.tab_team, text="Team Info")
        self.notebook.add(self.tab_player, text="Player Info")
        self.notebook.pack(expand=True, fill="both")

        # Matches tab
        self.comp_combo = ttk.Combobox(self.tab_matches, values=list(COMPETITIONS.keys()), state="readonly")
        self.comp_combo.current(0)
        self.comp_combo.pack()

        self.filter_combo = ttk.Combobox(
            self.tab_matches, values=["All", "Finished", "Live", "Upcoming"], state="readonly"
        )
        self.filter_combo.current(0)
        self.filter_combo.pack()

        tk.Button(self.tab_matches, text="Load Matches", command=self.load_matches).pack()

        self.tree_matches = ttk.Treeview(
            self.tab_matches, columns=("home","away","score","status","date"), show="headings"
        )
        for col in ("home","away","score","status","date"):
            self.tree_matches.heading(col, text=col)
        self.tree_matches.pack(fill="both", expand=True)

        # Standings tab
        self.tree_standings = ttk.Treeview(
            self.tab_standings, columns=("pos","team","played","points"), show="headings"
        )
        for col in ("pos","team","played","points"):
            self.tree_standings.heading(col, text=col)
        self.tree_standings.pack(fill="both", expand=True)
        tk.Button(self.tab_standings, text="Load Standings", command=self.load_standings).pack()

        # Scorers tab
        self.tree_scorers = ttk.Treeview(
            self.tab_scorers, columns=("player","team","goals"), show="headings"
        )
        for col in ("player","team","goals"):
            self.tree_scorers.heading(col, text=col)
        self.tree_scorers.pack(fill="both", expand=True)
        tk.Button(self.tab_scorers, text="Load Scorers", command=self.load_scorers).pack()

        # Team Info tab
        tk.Label(self.tab_team, text="Select Team:").pack()
        self.team_combo = ttk.Combobox(self.tab_team, values=[], state="readonly")
        self.team_combo.pack(pady=5)
        tk.Button(self.tab_team, text="Load Team Info", command=self.load_team).pack()
        self.team_text = tk.Text(self.tab_team, height=20)
        self.team_text.pack(fill="both", expand=True)

        # Player Info tab
        tk.Label(self.tab_player, text="Select Player:").pack()
        self.player_combo = ttk.Combobox(self.tab_player, values=[], state="readonly")
        self.player_combo.pack(pady=5)
        tk.Button(self.tab_player, text="Load Player Info", command=self.load_player).pack()
        self.player_text = tk.Text(self.tab_player)
        self.player_text.pack(fill="both", expand=True)

    def safe_recv(self):
        data = self.client.recv(65535).decode(FORMAT)
        try:
            return json.loads(data)
        except:
            return {}

    def load_matches(self):
        comp = COMPETITIONS[self.comp_combo.get()]
        self.client.sendall(f"matches {comp}".encode(FORMAT))
        data = self.safe_recv()

        self.tree_matches.delete(*self.tree_matches.get_children())
        self.teams.clear()

        filter_mode = self.filter_combo.get()

        for m in data.get("matches", []):
            status = m["status"]

            if filter_mode == "Finished" and status != "FINISHED":
                continue
            if filter_mode == "Upcoming" and status != "TIMED":
                continue
            if filter_mode == "Live" and status not in ("LIVE", "IN_PLAY", "PAUSED"):
                continue

            score = f"{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}"
            self.tree_matches.insert(
                "", "end",
                values=(m["homeTeam"]["name"], m["awayTeam"]["name"], score, status, m["utcDate"])
            )
            self.teams[m["homeTeam"]["name"]] = m["homeTeam"]["id"]
            self.teams[m["awayTeam"]["name"]] = m["awayTeam"]["id"]

        self.team_combo["values"] = list(self.teams.keys())

        # Auto refresh nếu chọn Live
        if filter_mode == "Live":
            self.after(30000, self.load_matches)

    def load_standings(self):
        comp = COMPETITIONS[self.comp_combo.get()]
        self.client.sendall(f"standings {comp}".encode(FORMAT))
        data = self.safe_recv()
        self.tree_standings.delete(*self.tree_standings.get_children())

        for table in data.get("standings", []):
            for row in table.get("table", []):
                self.tree_standings.insert(
                    "", "end",
                    values=(row["position"], row["team"]["name"], row["playedGames"], row["points"])
                )
                self.teams[row["team"]["name"]] = row["team"]["id"]

        self.team_combo["values"] = list(self.teams.keys())

    def load_scorers(self):
        comp = COMPETITIONS[self.comp_combo.get()]
        self.client.sendall(f"scorers {comp}".encode(FORMAT))
        data = self.safe_recv()
        self.tree_scorers.delete(*self.tree_scorers.get_children())
        for s in data.get("scorers", []):
            self.tree_scorers.insert("", "end", values=(s["player"]["name"], s["team"]["name"], s["goals"]))

    def load_team(self):
        team_name = self.team_combo.get()
        if not team_name:
            messagebox.showerror("Error", "Please select a team")
            return
        team_id = self.teams[team_name]
        self.client.sendall(f"team {team_id}".encode(FORMAT))
        data = self.safe_recv()

        self.team_text.delete("1.0", tk.END)
        self.team_text.insert("end", json.dumps(data, indent=2))

        # Cập nhật danh sách cầu thủ
        self.players.clear()
        squad = data.get("squad", [])
        for p in squad:
            self.players[p["name"]] = p["id"]
        self.player_combo["values"] = list(self.players.keys())

    def load_player(self):
        player_name = self.player_combo.get()
        if not player_name:
            messagebox.showerror("Error", "Please select a player")
            return
        player_id = self.players[player_name]
        self.client.sendall(f"player {player_id}".encode(FORMAT))
        data = self.safe_recv()
        self.player_text.delete("1.0", tk.END)
        self.player_text.insert("end", json.dumps(data, indent=2))


if __name__ == "__main__":
    app = SoccerApp()
    app.mainloop()
