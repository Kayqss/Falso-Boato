import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

SESSION_TIKTOK = os.path.join(BASE_DIR, "sessao_tiktok.json")
SESSION_YOUTUBE = os.path.join(BASE_DIR, "sessao_youtube.json")
SESSION_INSTAGRAM = os.path.join(BASE_DIR, "sessao_instagram.json")

TEMP_FRAME = os.path.join(BASE_DIR, "temp_frame10.jpg")
TEMP_PROXY = os.path.join(BASE_DIR, "temp_ia_proxy.mp4")

COLOR_BG = "#0d1117"
COLOR_SIDEBAR = "#010409"
COLOR_SIDEBAR_HOVER = "#161b22"
COLOR_CARD = "#161b22"
COLOR_CARD_BORDER = "#30363d"
COLOR_INPUT_BG = "#0d1117"
COLOR_INPUT_BORDER = "#30363d"
COLOR_BTN_SEC = "#21262d"
COLOR_BTN_SEC_HOVER = "#30363d"
COLOR_BTN_PRM = "#238636"
COLOR_BTN_PRM_HOVER = "#2ea043"
COLOR_TEXT_MAIN = "#e6edf3"
COLOR_TEXT_MUTED = "#848d97"
COLOR_ACCENT_BLUE = "#58a6ff"
COLOR_BADGE_BG = "#21262d"
COLOR_BADGE_BORDER = "#30363d"
COLOR_ORANGE_LINE = "#f78166"
COLOR_SUCCESS = "#3fb950"
COLOR_DANGER = "#f85149"

FONT_FAMILY = "Segoe UI"

PRICE_INPUT_1M_BRL = 0.15 * 5.70
PRICE_OUTPUT_1M_BRL = 0.60 * 5.70