import customtkinter as ctk
from core.constants import (
    COLOR_SIDEBAR,
    COLOR_CARD,
    COLOR_CARD_BORDER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_SIDEBAR_HOVER,
    COLOR_SUCCESS,
    FONT_FAMILY
)

class SidebarView(ctk.CTkFrame):
    def __init__(self, master, on_navigate):
        super().__init__(
            master,
            width=240,
            fg_color=COLOR_SIDEBAR,
            corner_radius=0,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.on_navigate = on_navigate
        self.grid_propagate(False)

        self.build_ui()

    def build_ui(self):
        self.frame_logo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_logo.pack(fill="x", padx=18, pady=(20, 16))

        ctk.CTkLabel(
            self.frame_logo,
            text="FalsoBoato",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(anchor="w")

        ctk.CTkFrame(self, height=1, fg_color=COLOR_CARD_BORDER).pack(fill="x", padx=16, pady=(10, 14))

        self.btn_nav_cortador = ctk.CTkButton(
            self,
            text="Cortador de vídeos",
            anchor="w",
            height=36,
            corner_radius=6,
            fg_color=COLOR_CARD,
            hover_color=COLOR_CARD,
            text_color=COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=lambda: self.on_navigate("cortador")
        )
        self.btn_nav_cortador.pack(fill="x", padx=12, pady=(0, 4))

        self.btn_nav_postador = ctk.CTkButton(
            self,
            text="Postador de vídeos",
            anchor="w",
            height=36,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLOR_SIDEBAR_HOVER,
            text_color=COLOR_TEXT_MUTED,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            command=lambda: self.on_navigate("postador")
        )
        self.btn_nav_postador.pack(fill="x", padx=12, pady=(0, 4))

        self.btn_nav_config = ctk.CTkButton(
            self,
            text="Configurações",
            anchor="w",
            height=36,
            corner_radius=6,
            fg_color="transparent",
            hover_color=COLOR_SIDEBAR_HOVER,
            text_color=COLOR_TEXT_MUTED,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            command=lambda: self.on_navigate("config")
        )
        self.btn_nav_config.pack(fill="x", padx=12, pady=(0, 4))

        self.sidebar_spacer = ctk.CTkFrame(self, fg_color="transparent")
        self.sidebar_spacer.pack(fill="both", expand=True)

        self.frame_hardware = ctk.CTkFrame(
            self,
            fg_color=COLOR_CARD,
            corner_radius=6,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.frame_hardware.pack(fill="x", padx=12, pady=(0, 16))

        row_hw_title = ctk.CTkFrame(self.frame_hardware, fg_color="transparent")
        row_hw_title.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            row_hw_title,
            text="Recursos do sistema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(side="left")

        dot_live = ctk.CTkLabel(row_hw_title, text="●", font=ctk.CTkFont(size=9), text_color=COLOR_SUCCESS)
        dot_live.pack(side="right")

        def build_metric_row(parent, label_text):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            ctk.CTkLabel(
                row,
                text=label_text,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLOR_TEXT_MUTED
            ).pack(side="left")
            lbl_v = ctk.CTkLabel(
                row,
                text="--%",
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                text_color=COLOR_TEXT_MAIN
            )
            lbl_v.pack(side="right")
            return lbl_v

        self.lbl_cpu_val = build_metric_row(self.frame_hardware, "CPU:")
        self.lbl_gpu_val = build_metric_row(self.frame_hardware, "GPU:")
        self.lbl_ram_val = build_metric_row(self.frame_hardware, "RAM:")
        self.lbl_disk_val = build_metric_row(self.frame_hardware, "Disco:")

        ctk.CTkFrame(self.frame_hardware, height=4, fg_color="transparent").pack()

    def set_active(self, view_key):
        buttons = {
            "cortador": self.btn_nav_cortador,
            "postador": self.btn_nav_postador,
            "config": self.btn_nav_config
        }
        for key, btn in buttons.items():
            if key == view_key:
                btn.configure(
                    fg_color=COLOR_CARD,
                    text_color=COLOR_TEXT_MAIN,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLOR_TEXT_MUTED,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12)
                )

    def update_metrics(self, metrics):
        self.lbl_cpu_val.configure(text=metrics.get("cpu", "--%"))
        self.lbl_gpu_val.configure(text=metrics.get("gpu", "N/A"))
        self.lbl_ram_val.configure(text=metrics.get("ram", "--%"))
        self.lbl_disk_val.configure(text=metrics.get("disk", "--%"))