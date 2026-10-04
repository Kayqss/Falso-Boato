import os
import json
from core.constants import CONFIG_FILE

DEFAULT_CONFIG = {
    "api_key": "",
    "saldo_brl": 0.0,
    "cam_x": "0",
    "cam_y": "0",
    "cam_w": "0",
    "cam_h": "0",
    "handle": ""
}

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass