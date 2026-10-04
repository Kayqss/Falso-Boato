import os
import shutil
from core.constants import SESSION_TIKTOK, SESSION_YOUTUBE, SESSION_INSTAGRAM

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

TEMP_USER_DATA_DIR = os.path.join(
    os.path.expanduser("~"), "AppData", "Local", "Temp", "playwright_edge_profile"
)

PLATAFORMAS_INFO = {
    "tiktok": {
        "nome": "TikTok",
        "url": "https://www.tiktok.com/login",
        "arquivo": SESSION_TIKTOK
    },
    "youtube": {
        "nome": "YouTube",
        "url": "https://studio.youtube.com",
        "arquivo": SESSION_YOUTUBE
    },
    "instagram": {
        "nome": "Instagram",
        "url": "https://www.instagram.com/accounts/login/",
        "arquivo": SESSION_INSTAGRAM
    }
}

class LoginSessionManager:
    def __init__(self, platform_key):
        if not sync_playwright:
            raise Exception("Playwright não instalado. Execute 'pip install playwright' e 'playwright install'.")

        self.info = PLATAFORMAS_INFO.get(platform_key)
        if not self.info:
            raise ValueError(f"Plataforma '{platform_key}' não encontrada.")

        self.playwright = None
        self.context = None

    def start_login(self):
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=TEMP_USER_DATA_DIR,
            channel="msedge",
            headless=False,
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
                "--no-first-run"
            ],
            ignore_default_args=["--enable-automation"]
        )
        page = self.context.pages[0] if self.context.pages else self.context.new_page()
        page.goto(self.info["url"])

    def confirm_and_save(self):
        try:
            if self.context:
                self.context.storage_state(path=self.info["arquivo"])
        finally:
            self.close()

    def close(self):
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass

        try:
            shutil.rmtree(TEMP_USER_DATA_DIR, ignore_errors=True)
        except Exception:
            pass