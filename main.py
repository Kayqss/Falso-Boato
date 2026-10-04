import os
import threading
import time
import customtkinter as ctk

from core.constants import COLOR_BG, TEMP_FRAME, TEMP_PROXY
from core.config import load_config, save_config
from services.hardware import get_system_metrics
from views.sidebar import SidebarView
from views.cortador_view import CortadorView
from views.postador_view import PostadorView
from views.config_view import ConfigView

ctk.set_appearance_mode("dark")

class FalsoBoatoSuiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FalsoBoato — Suite de Vídeo")
        self.geometry("1180x880")
        self.minsize(1040, 780)
        self.configure(fg_color=COLOR_BG)

        self.config_data = load_config()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = SidebarView(self, on_navigate=self.switch_main_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.views = {
            "cortador": CortadorView(self, self),
            "postador": PostadorView(self, self),
            "config": ConfigView(self, self)
        }

        self.switch_main_view("cortador")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.monitoring_active = True
        threading.Thread(target=self.hardware_monitor_loop, daemon=True).start()

    def persist_config(self):
        save_config(self.config_data)

    def log_all(self, text, tag="normal"):
        if "cortador" in self.views:
            self.views["cortador"].log(text, tag=tag)
        if "postador" in self.views:
            self.views["postador"].log(text, tag=tag)

    def switch_main_view(self, view_key):
        self.sidebar.set_active(view_key)
        for key, view in self.views.items():
            if key == view_key:
                view.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
                if hasattr(view, "on_show"):
                    view.on_show()
            else:
                view.grid_remove()

    def hardware_monitor_loop(self):
        while self.monitoring_active:
            try:
                metrics = get_system_metrics()
                self.sidebar.update_metrics(metrics)
                time.sleep(1)
            except Exception:
                time.sleep(1)

    def on_closing(self):
        self.monitoring_active = False
        for f in [TEMP_FRAME, TEMP_PROXY]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
        self.destroy()

if __name__ == "__main__":
    app = FalsoBoatoSuiteApp()
    app.mainloop()