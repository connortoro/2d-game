import json
import os

SCALE = 100
W = 15*SCALE
H= 9*SCALE

ROWS = 9
COLS = 15

TILE_SIZE = 16

CONFIG_FILE = "config.json"
def load_config():
    default_config = {
        "music_volume": 0.1,
        "game_volume": 1.0,
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        for key, val in default_config.items():
            config.setdefault(key, val)
        return config
    return default_config


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

