import time
import psutil
import json
from datetime import datetime
import csv
import os
import tempfile
import threading
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import sys
import ctypes
import logging


# CONFIG
DOCUMENTS = os.path.join(os.environ["USERPROFILE"], "Documents")
APP_DIR = os.path.join(DOCUMENTS, "GameTimeCounter")
os.makedirs(APP_DIR, exist_ok=True)

GAMES_CSV = os.path.join(APP_DIR, "games.csv")
DATA_FILE = os.path.join(APP_DIR, "playtime.txt")
POLL_INTERVAL = 5
paused = False
active = {}
data = {}

# LOGGING
logging.basicConfig(
    filename=os.path.join(APP_DIR, "debug.log"),
    level=logging.ERROR,
    format="%(asctime)s %(message)s"
)

# DEFAULT CSV
if not os.path.exists(GAMES_CSV):
    with open(GAMES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["exe_name", "proc_name"])
        # Add default example entries (optional)
        writer.writerow(["acr.exe", "Assetto Corsa Rally"])
        writer.writerow(["sekiro.exe", "Sekiro"])

# LOAD
def load_games(csv_file=GAMES_CSV):
    games = {}
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            if not row.get("exe_name") or not row.get("proc_name"):
                raise ValueError(f"Invalid row {i} in {csv_file}")    
            exe_path = row["exe_name"]
            exe_name = os.path.basename(exe_path).lower()
            games[exe_name] = row["proc_name"]
    return games


GAMES = load_games()

# SAVE MUTEX

def save_data_atomic(data, filename=DATA_FILE):
    try:
        dir_name = os.path.dirname(filename) or "."
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False) as tmp:
            for name, seconds in data.items():
                tmp.write(f"{name}:{seconds}\n")
            temp_name = tmp.name
        os.replace(temp_name, filename)  # atomic
    except Exception as e:
        logging.exception("Save failed: ", e)

def load_data(filename=DATA_FILE):
    data = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    name, value = line.strip().split(":", 1)
                    data[name] = float(value)
    except FileNotFoundError:
        pass
    return data

data = load_data()



# AUX
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}h {m}m {s}s"


def tracker_loop():
    global active
    while True:
        try:
            if not paused:
                running = set()
                for p in psutil.process_iter():
                    try:
                        running.add(p.name.lower())
                    except:
                        pass
                        
                now = time.time()
                
                for exe, name in GAMES.items():
                    if exe in running:
                        if exe not in active:
                            active[exe] = now
                    else:
                        if exe in active:
                            duration = now - active.pop(exe)
                            data[name] = data.get(name, 0) + duration
                            save_data_atomic(data)
        except Exception as e:
            logging.exception("Tracker error: ", e)
            
            
        time.sleep(POLL_INTERVAL)


# ---------- TRAY MENU ----------
def show_playtime_tray(icon, item):
    if not data:
        text = "No playtime recorded yet."
    else:
        text = "\n".join(
            f"{game}: {format_time(seconds)}"
            for game, seconds in data.items()
        )

    icon.notify(text, "Game Time Counter")


def toggle_pause(icon, item):
    global paused
    paused = not paused

def quit_app(icon, item):
    for exe, start in active.items():
        data[GAMES[exe]] = data.get(GAMES[exe], 0) + (time.time() - start)
    save_data_atomic(data)
    icon.stop()

# ---------- ICON ----------
def create_icon():
    img = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(img)
    d.rectangle((16, 16, 48, 48), fill="white")
    return img

# ---------- MAIN ----------
threading.Thread(target=tracker_loop, daemon=True).start()

icon = Icon(
    "GameTracker",
    create_icon(),
    menu=Menu(
        MenuItem(
            "Show Playtime (tray)",
            show_playtime_tray,
            enabled=lambda item: not paused
        ),
        MenuItem(
            lambda item: "Resume" if paused else "Pause",
            toggle_pause
        ),
        MenuItem("Exit", quit_app)
    )
)

icon.run()