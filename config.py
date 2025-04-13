import json
import os

SCALE = 100
W = 15*SCALE
H= 9*SCALE

ROWS = 9
COLS = 15

TILE_SIZE = 16

#used to save settings
CONFIG_FILE = "config.json"
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"music_volume": 0.1}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

