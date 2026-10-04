import os
import subprocess
import threading
import json
import time
import textwrap
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk, ImageDraw, ImageFont

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from core.constants import (
    BASE_DIR,
    TEMP_FRAME,
    TEMP_PROXY,
    COLOR_BG,
    COLOR_CARD,
    COLOR_CARD_BORDER,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_BTN_SEC,
    COLOR_BTN_SEC_HOVER,
    COLOR_BTN_PRM,
    COLOR_BTN_PRM_HOVER,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    COLOR_ACCENT_BLUE,
    COLOR_ORANGE_LINE,
    COLOR_SUCCESS,
    COLOR_DANGER,
    FONT_FAMILY,
    PRICE_INPUT_1M_BRL,
    PRICE_OUTPUT_1M_BRL
)

TAX_MULTIPLIER_BRL = 1.40

class CortadorView(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLOR_BG, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        self.video_path = ""
        self.output_dir = ""
        self.start_timestamp = 0
        self.timer_running = False
        self.cancel_requested = False
        self.active_subprocess = None
        self.preview_frame_path = ""
        self.original_video_w = 1920
        self.original_video_h = 1080
        self.preview_tk_img = None
        self.rect_id = None
        self.guide_ids = []
        self.handle_guide_ids = []
        self.current_tab = "simples"

        self.build_ui()

    def build_ui(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=24)

        frame_files = ctk.CTkFrame(content, fg_color="transparent")
        frame_files.pack(fill="x", pady=(0, 16))
        frame_files.grid_columnconfigure(0, weight=1)
        frame_files.grid_columnconfigure(1, weight=1)

        self.card_video = ctk.CTkFrame(frame_files, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_video.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        row_h_vid = ctk.CTkFrame(self.card_video, fg_color="transparent")
        row_h_vid.pack(fill="x", padx=16, pady=(14, 2))
        ctk.CTkLabel(row_h_vid, text="Vídeo original", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(side="left")

        ctk.CTkLabel(self.card_video, text="Selecione o arquivo de mídia para recorte.", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 10))

        box_file = ctk.CTkFrame(self.card_video, fg_color=COLOR_INPUT_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        box_file.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(box_file, text="🎬", font=ctk.CTkFont(size=16)).pack(side="left", padx=(12, 10), pady=10)
        frame_file_text = ctk.CTkFrame(box_file, fg_color="transparent")
        frame_file_text.pack(side="left", fill="both", expand=True, pady=6)

        self.lbl_file_name = ctk.CTkLabel(frame_file_text, text="Nenhum arquivo selecionado", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_file_name.pack(fill="x")
        self.lbl_file_meta = ctk.CTkLabel(frame_file_text, text="MP4, MKV ou MOV", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLOR_TEXT_MUTED, anchor="w")
        self.lbl_file_meta.pack(fill="x")

        self.btn_file = ctk.CTkButton(self.card_video, text="Alterar vídeo", height=30, corner_radius=6, fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), command=self.select_video)
        self.btn_file.pack(fill="x", padx=16, pady=(0, 14))

        self.card_folder = ctk.CTkFrame(frame_files, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_folder.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        row_h_fold = ctk.CTkFrame(self.card_folder, fg_color="transparent")
        row_h_fold.pack(fill="x", padx=16, pady=(14, 2))
        ctk.CTkLabel(row_h_fold, text="Pasta de saída", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(side="left")

        ctk.CTkLabel(self.card_folder, text="Diretório onde os cortes gerados serão gravados.", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 10))

        box_folder = ctk.CTkFrame(self.card_folder, fg_color=COLOR_INPUT_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        box_folder.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(box_folder, text="📁", font=ctk.CTkFont(size=16)).pack(side="left", padx=(12, 10), pady=10)
        frame_folder_text = ctk.CTkFrame(box_folder, fg_color="transparent")
        frame_folder_text.pack(side="left", fill="both", expand=True, pady=6)

        self.lbl_folder_path = ctk.CTkLabel(frame_folder_text, text="Nenhuma pasta definida", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_folder_path.pack(fill="x")
        self.lbl_folder_meta = ctk.CTkLabel(frame_folder_text, text="Diretório local", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLOR_TEXT_MUTED, anchor="w")
        self.lbl_folder_meta.pack(fill="x")

        self.btn_folder = ctk.CTkButton(self.card_folder, text="Alterar pasta", height=30, corner_radius=6, fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), command=self.select_folder)
        self.btn_folder.pack(fill="x", padx=16, pady=(0, 14))

        frame_tabs_header = ctk.CTkFrame(content, fg_color="transparent")
        frame_tabs_header.pack(fill="x", pady=(0, 2))

        self.btn_tab_simples = ctk.CTkButton(frame_tabs_header, text="Recorte simples", width=140, height=32, corner_radius=6, fg_color=COLOR_CARD, hover_color=COLOR_CARD_BORDER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), command=lambda: self.switch_clipper_tab("simples"))
        self.btn_tab_simples.pack(side="left", padx=(0, 6))

        self.btn_tab_ia = ctk.CTkButton(frame_tabs_header, text="Recorte com inteligência artificial", width=240, height=32, corner_radius=6, fg_color="transparent", hover_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MUTED, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), command=lambda: self.switch_clipper_tab("ia"))
        self.btn_tab_ia.pack(side="left")

        self.card_tab_body = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_tab_body.pack(fill="x", pady=(6, 16))

        self.build_body_simples()
        self.build_body_ia()
        self.switch_clipper_tab("simples")

        self.card_status = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_status.pack(fill="both", expand=True, pady=(0, 16))

        bar_top = ctk.CTkFrame(self.card_status, fg_color="#1f242c", height=34, corner_radius=6)
        bar_top.pack(fill="x")
        self.lbl_status = ctk.CTkLabel(bar_top, text="Pronto para iniciar", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_ACCENT_BLUE)
        self.lbl_status.pack(side="left", padx=14, pady=6)
        self.lbl_count_progress = ctk.CTkLabel(bar_top, text="0/0 partes processadas", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED)
        self.lbl_count_progress.pack(side="right", padx=14, pady=6)

        bar_timers = ctk.CTkFrame(self.card_status, fg_color="transparent")
        bar_timers.pack(fill="x", padx=14, pady=(10, 4))
        self.lbl_elapsed = ctk.CTkLabel(bar_timers, text="Decorrido: 00h 00m 00s", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED)
        self.lbl_elapsed.pack(side="left")
        self.lbl_timer = ctk.CTkLabel(bar_timers, text="Restante: 00h 00m 00s", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED)
        self.lbl_timer.pack(side="right")

        self.progress = ctk.CTkProgressBar(self.card_status, height=4, corner_radius=2, fg_color="#21262d", progress_color=COLOR_BTN_PRM)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=14, pady=(0, 10))

        frame_term_h = ctk.CTkFrame(self.card_status, fg_color="transparent", height=28)
        frame_term_h.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(frame_term_h, text="Console log", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(side="left")

        self.btn_copy_terminal = ctk.CTkButton(frame_term_h, text="Copiar", width=65, height=22, corner_radius=6, fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"), command=self.copy_terminal)
        self.btn_copy_terminal.pack(side="right")

        self.log_box = ctk.CTkTextbox(self.card_status, height=120, fg_color=COLOR_INPUT_BG, text_color="#c9d1d9", font=("Consolas", 10), corner_radius=4, border_width=1, border_color=COLOR_CARD_BORDER)
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.log_box.tag_config("success", foreground=COLOR_SUCCESS)
        self.log_box.tag_config("error", foreground=COLOR_DANGER)
        self.log_box.tag_config("normal", foreground="#c9d1d9")

        frame_action = ctk.CTkFrame(content, fg_color="transparent")
        frame_action.pack(fill="x", pady=(0, 10))

        self.btn_cancel = ctk.CTkButton(
            frame_action,
            text="Cancelar ação",
            width=150,
            height=38,
            corner_radius=6,
            fg_color=COLOR_BTN_SEC,
            hover_color=COLOR_BTN_SEC_HOVER,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_DANGER,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            state="disabled",
            command=self.cancel_processing
        )
        self.btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_start = ctk.CTkButton(frame_action, text="Iniciar cortes", width=210, height=38, corner_radius=6, fg_color=COLOR_BTN_PRM, hover_color=COLOR_BTN_PRM_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), command=self.start_clipper_thread)
        self.btn_start.pack(side="right")

    def build_body_simples(self):
        self.frame_body_simples = ctk.CTkFrame(self.card_tab_body, fg_color="transparent")
        ctk.CTkLabel(self.frame_body_simples, text="Título a ser estampado no vídeo", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=16, pady=(16, 4))
        self.entry_title = ctk.CTkEntry(self.frame_body_simples, height=32, fg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12), corner_radius=6, border_width=1, border_color=COLOR_INPUT_BORDER)
        self.entry_title.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(self.frame_body_simples, text="Duração em segundos de cada corte", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=16, pady=(0, 4))
        self.entry_dur = ctk.CTkEntry(self.frame_body_simples, width=140, height=32, fg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), corner_radius=6, border_width=1, border_color=COLOR_INPUT_BORDER)
        self.entry_dur.pack(anchor="w", padx=16, pady=(0, 16))

    def build_body_ia(self):
        self.frame_body_ia = ctk.CTkFrame(self.card_tab_body, fg_color="transparent")
        
        # 1. Secao da Webcam
        ctk.CTkLabel(self.frame_body_ia, text="Coordenadas da webcam", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=16, pady=(14, 6))

        frame_cam_master = ctk.CTkFrame(self.frame_body_ia, fg_color="transparent", corner_radius=0, border_width=0)
        frame_cam_master.pack(fill="x", padx=16, pady=(0, 14))

        self.canvas_w = 280
        self.canvas_h = 158
        self.canvas_preview = Canvas(frame_cam_master, width=self.canvas_w, height=self.canvas_h, bg="#010409", highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        self.canvas_preview.pack(side="left", padx=(0, 16), pady=4)

        f_coords_v = ctk.CTkFrame(frame_cam_master, fg_color="transparent")
        f_coords_v.pack(side="left", fill="both", expand=True, pady=4)

        def make_coord_row(parent, label_text, default_val, callback=None):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label_text, width=80, anchor="w", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(side="left")
            entry = ctk.CTkEntry(row, width=100, height=26, fg_color=COLOR_INPUT_BG, border_width=1, border_color=COLOR_INPUT_BORDER, corner_radius=6)
            entry.insert(0, default_val)
            entry.pack(side="left")
            if callback:
                entry.bind("<KeyRelease>", lambda e: callback())
            return entry

        self.entry_cam_x = make_coord_row(f_coords_v, "Posição X", self.app.config_data.get("cam_x", "35"), self.update_preview_rect)
        self.entry_cam_y = make_coord_row(f_coords_v, "Posição Y", self.app.config_data.get("cam_y", "36"), self.update_preview_rect)
        self.entry_cam_w = make_coord_row(f_coords_v, "Largura", self.app.config_data.get("cam_w", "405"), self.update_preview_rect)
        self.entry_cam_h = make_coord_row(f_coords_v, "Altura", self.app.config_data.get("cam_h", "225"), self.update_preview_rect)

        # 2. Secao da Assinatura com Canvas 9:16 e Grid Figma
        ctk.CTkLabel(self.frame_body_ia, text="Configuração da assinatura", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=16, pady=(6, 6))

        frame_handle_master = ctk.CTkFrame(self.frame_body_ia, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        frame_handle_master.pack(fill="x", padx=16, pady=(0, 16))

        # Canvas vertical 9:16 pre-renderizado (108x192 px proporcional a 1080x1920)
        self.handle_canvas_w = 108
        self.handle_canvas_h = 192
        self.canvas_handle = Canvas(frame_handle_master, width=self.handle_canvas_w, height=self.handle_canvas_h, bg="#000000", highlightthickness=1, highlightbackground=COLOR_CARD_BORDER)
        self.canvas_handle.pack(side="left", padx=(16, 18), pady=16)

        f_handle_controls = ctk.CTkFrame(frame_handle_master, fg_color="transparent")
        f_handle_controls.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=14)

        row_text_line = ctk.CTkFrame(f_handle_controls, fg_color="transparent")
        row_text_line.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(row_text_line, text="Texto do handle:", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=(0, 8))
        self.entry_handle = ctk.CTkEntry(row_text_line, height=28, width=220, fg_color=COLOR_INPUT_BG, border_width=1, border_color=COLOR_INPUT_BORDER, corner_radius=6)
        self.entry_handle.insert(0, self.app.config_data.get("handle", "@seucanal"))
        self.entry_handle.pack(side="left")
        self.entry_handle.bind("<KeyRelease>", lambda e: self.update_handle_preview())

        row_figma = ctk.CTkFrame(f_handle_controls, fg_color="transparent")
        row_figma.pack(fill="x")

        # Grid Figma 3x3
        self.frame_grid_figma = ctk.CTkFrame(row_figma, fg_color=COLOR_INPUT_BG, corner_radius=8, border_width=1, border_color=COLOR_INPUT_BORDER)
        self.frame_grid_figma.pack(side="left", padx=(0, 20), pady=2)

        self.figma_buttons = {}
        self.current_anchor = self.app.config_data.get("handle_anchor", "bottom_center")

        anchors = [
            ("top_left", 0, 0), ("top_center", 0, 1), ("top_right", 0, 2),
            ("mid_left", 1, 0), ("mid_center", 1, 1), ("mid_right", 1, 2),
            ("bottom_left", 2, 0), ("bottom_center", 2, 1), ("bottom_right", 2, 2)
        ]

        for code, r, c in anchors:
            btn = ctk.CTkButton(
                self.frame_grid_figma,
                text="•",
                width=24,
                height=24,
                corner_radius=4,
                fg_color="transparent",
                hover_color=COLOR_CARD,
                text_color=COLOR_TEXT_MUTED,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda a=code: self.select_anchor(a)
            )
            btn.grid(row=r, column=c, padx=3, pady=3)
            self.figma_buttons[code] = btn

        # Campos numéricos para ajuste fino
        f_fine_tune = ctk.CTkFrame(row_figma, fg_color="transparent")
        f_fine_tune.pack(side="left", fill="both", expand=True)

        self.entry_handle_x = make_coord_row(f_fine_tune, "Offset X", self.app.config_data.get("handle_offset_x", "0"), self.update_handle_preview)
        self.entry_handle_y = make_coord_row(f_fine_tune, "Posição Y", self.app.config_data.get("handle_y", "1710"), self.update_handle_preview)
        self.entry_handle_size = make_coord_row(f_fine_tune, "Tamanho", self.app.config_data.get("handle_size", "38"), self.update_handle_preview)

        self.select_anchor(self.current_anchor, trigger_update=False)
        self.after(100, self.update_handle_preview)

    def select_anchor(self, anchor_code, trigger_update=True):
        self.current_anchor = anchor_code
        for code, btn in self.figma_buttons.items():
            if code == anchor_code:
                btn.configure(fg_color=COLOR_ACCENT_BLUE, text_color="#ffffff", hover_color=COLOR_ACCENT_BLUE)
            else:
                btn.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED, hover_color=COLOR_CARD)

        if "top" in anchor_code and trigger_update:
            self.entry_handle_y.delete(0, "end")
            self.entry_handle_y.insert(0, "120")
        elif "mid" in anchor_code and trigger_update:
            self.entry_handle_y.delete(0, "end")
            self.entry_handle_y.insert(0, "960")
        elif "bottom" in anchor_code and trigger_update:
            self.entry_handle_y.delete(0, "end")
            self.entry_handle_y.insert(0, "1710")

        if trigger_update:
            self.update_handle_preview()

    def update_handle_preview(self):
        try:
            self.canvas_handle.delete("all")

            # Guias sutis do layout vertical (região da câmera e gameplay)
            scale = self.handle_canvas_w / 1080.0
            h_cam = 608 * scale
            self.canvas_handle.create_rectangle(0, 160 * scale, self.handle_canvas_w, (160 + 608) * scale, outline="#21262d", fill="#0d1117")
            self.canvas_handle.create_text(self.handle_canvas_w / 2, (160 + 304) * scale, text="CAM", fill="#30363d", font=("Consolas", 7))

            h_game = 1072 * scale
            self.canvas_handle.create_rectangle(0, 768 * scale, self.handle_canvas_w, (768 + 1072) * scale, outline="#21262d", fill="#05070a")
            self.canvas_handle.create_text(self.handle_canvas_w / 2, (768 + 536) * scale, text="GAME", fill="#30363d", font=("Consolas", 7))

            text = self.entry_handle.get().strip() or "@seucanal"
            y_real = float(self.entry_handle_y.get().strip() or "1710")
            offset_x = float(self.entry_handle_x.get().strip() or "0")
            font_size = float(self.entry_handle_size.get().strip() or "38")

            # Cálculo de posição baseado no ancoramento Figma
            if "left" in self.current_anchor:
                x_real = 80 + offset_x
                anchor_tk = "w"
            elif "right" in self.current_anchor:
                x_real = 1000 + offset_x
                anchor_tk = "e"
            else:
                x_real = (1080 / 2) + offset_x
                anchor_tk = "center"

            cx = x_real * scale
            cy = y_real * scale
            preview_font_size = max(6, int(font_size * scale))

            # Desenho do texto e indicadores visuais
            self.canvas_handle.create_text(cx, cy, text=text, fill="#ffffff", font=(FONT_FAMILY, preview_font_size, "bold"), anchor=anchor_tk)

            # Marcador Figma de ancoragem
            dot_size = 2
            self.canvas_handle.create_oval(cx - dot_size, cy - dot_size, cx + dot_size, cy + dot_size, fill=COLOR_ORANGE_LINE, outline="")

            # Linha guia inferior de referência
            self.canvas_handle.create_line(0, cy, self.handle_canvas_w, cy, fill=COLOR_ORANGE_LINE, dash=(1, 2))
        except Exception:
            pass

    def switch_clipper_tab(self, tab):
        self.current_tab = tab
        if tab == "simples":
            self.btn_tab_simples.configure(fg_color=COLOR_CARD, text_color=COLOR_TEXT_MAIN)
            self.btn_tab_ia.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED)
            self.frame_body_ia.pack_forget()
            self.frame_body_simples.pack(fill="x")
        else:
            self.btn_tab_simples.configure(fg_color="transparent", text_color=COLOR_TEXT_MUTED)
            self.btn_tab_ia.configure(fg_color=COLOR_CARD, text_color=COLOR_TEXT_MAIN)
            self.frame_body_simples.pack_forget()
            self.frame_body_ia.pack(fill="x")
            self.update_handle_preview()

    def copy_terminal(self):
        content = self.log_box.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.btn_copy_terminal.configure(text="Copiado")
        self.after(1500, lambda: self.btn_copy_terminal.configure(text="Copiar"))

    def log(self, text, tag="normal"):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{hora}] {text}\n", tag)
        self.log_box.see("end")
        print(f"[Cortador {hora}] {text}")

    def cancel_processing(self):
        self.cancel_requested = True
        self.log("Cancelamento solicitado pelo usuário...", tag="error")
        if self.active_subprocess:
            try:
                self.active_subprocess.terminate()
            except Exception:
                pass

    def select_video(self):
        file = filedialog.askopenfilename(filetypes=[("Arquivos de Vídeo", "*.mp4 *.mkv *.mov *.avi *.webm")])
        if file:
            self.video_path = file
            filename = os.path.basename(file)
            size_mb = os.path.getsize(file) / (1024 * 1024)
            size_str = f"{size_mb / 1024:.1f} GB" if size_mb >= 1024 else f"{size_mb:.1f} MB"
            ext = os.path.splitext(file)[1].upper().replace(".", "")
            self.lbl_file_name.configure(text=filename)
            self.lbl_file_meta.configure(text=f"{ext} • {size_str}")
            self.log(f"Vídeo de entrada selecionado: {filename}")
            threading.Thread(target=self.extract_frame_preview, daemon=True).start()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            folder_display = folder if len(folder) < 38 else "..." + folder[-35:]
            self.lbl_folder_path.configure(text=folder_display)
            self.log(f"Pasta de saída definida: {folder}")

    def get_video_duration(self, filepath):
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", filepath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])

    def extract_frame_preview(self):
        try:
            cmd_res = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", self.video_path]
            res = subprocess.run(cmd_res, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            res_data = json.loads(res.stdout)
            self.original_video_w = int(res_data["streams"][0]["width"])
            self.original_video_h = int(res_data["streams"][0]["height"])

            frame_out = TEMP_FRAME
            cmd_frame = ["ffmpeg", "-y", "-ss", "0.33", "-i", self.video_path, "-vframes", "1", "-q:v", "2", frame_out]
            subprocess.run(cmd_frame, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if os.path.exists(frame_out):
                self.preview_frame_path = frame_out
                img = Image.open(frame_out).resize((self.canvas_w, self.canvas_h), Image.Resampling.LANCZOS)
                self.preview_tk_img = ImageTk.PhotoImage(img)
                self.canvas_preview.delete("all")
                self.canvas_preview.create_image(0, 0, anchor="nw", image=self.preview_tk_img)
                self.rect_id = None
                self.guide_ids = []
                self.update_preview_rect()
                self.log("Décimo frame do vídeo carregado para calibração.")
        except Exception as e:
            self.log(f"Erro na extração de frame: {str(e)}", tag="error")

    def update_preview_rect(self):
        if not self.preview_tk_img:
            return
        try:
            x = float(self.entry_cam_x.get().strip() or 0)
            y = float(self.entry_cam_y.get().strip() or 0)
            w = float(self.entry_cam_w.get().strip() or 0)
            h = float(self.entry_cam_h.get().strip() or 0)

            scale_x = self.canvas_w / self.original_video_w
            scale_y = self.canvas_h / self.original_video_h

            x1 = x * scale_x
            y1 = y * scale_y
            x2 = (x + w) * scale_x
            y2 = (y + h) * scale_y

            if self.rect_id is None:
                self.rect_id = self.canvas_preview.create_rectangle(x1, y1, x2, y2, outline=COLOR_ORANGE_LINE, width=2)
            else:
                self.canvas_preview.coords(self.rect_id, x1, y1, x2, y2)

            for gid in self.guide_ids:
                self.canvas_preview.delete(gid)
            self.guide_ids = []

            dist_right = int(max(0, self.original_video_w - (x + w)))
            dist_bottom = int(max(0, self.original_video_h - (y + h)))

            line_r = self.canvas_preview.create_line(x2, (y1 + y2) / 2, self.canvas_w, (y1 + y2) / 2, fill=COLOR_ORANGE_LINE, dash=(2, 2))
            text_r = self.canvas_preview.create_text((x2 + self.canvas_w) / 2, (y1 + y2) / 2 - 8, text=f"{dist_right}px", fill=COLOR_ORANGE_LINE, font=("Consolas", 8, "bold"))
            self.guide_ids.extend([line_r, text_r])

            line_b = self.canvas_preview.create_line((x1 + x2) / 2, y2, (x1 + x2) / 2, self.canvas_h, fill=COLOR_ORANGE_LINE, dash=(2, 2))
            text_b = self.canvas_preview.create_text((x1 + x2) / 2 + 18, (y2 + self.canvas_h) / 2, text=f"{dist_bottom}px", fill=COLOR_ORANGE_LINE, font=("Consolas", 8, "bold"))
            self.guide_ids.extend([line_b, text_b])
        except Exception:
            pass

    def start_clipper_thread(self):
        if not self.video_path or not self.output_dir:
            self.log("Erro: Selecione o arquivo de vídeo e a pasta de destino.", tag="error")
            return

        if self.current_tab == "simples":
            title = self.entry_title.get().strip()
            dur_str = self.entry_dur.get().strip()
            if not title:
                self.log("Erro: Informe o título a ser estampado.", tag="error")
                return
            if not dur_str:
                self.log("Erro: Informe a duração em segundos de cada corte.", tag="error")
                return
            target_func = self.process_cuts_simple
        else:
            self.save_cam_config()
            target_func = self.process_cuts_ia

        self.cancel_requested = False
        self.btn_start.configure(state="disabled", text="Processando...")
        self.btn_cancel.configure(state="normal")
        self.btn_file.configure(state="disabled")
        self.btn_folder.configure(state="disabled")

        threading.Thread(target=target_func, daemon=True).start()

    def save_cam_config(self):
        self.app.config_data["cam_x"] = self.entry_cam_x.get().strip()
        self.app.config_data["cam_y"] = self.entry_cam_y.get().strip()
        self.app.config_data["cam_w"] = self.entry_cam_w.get().strip()
        self.app.config_data["cam_h"] = self.entry_cam_h.get().strip()
        
        self.app.config_data["handle"] = self.entry_handle.get().strip()
        self.app.config_data["handle_anchor"] = self.current_anchor
        self.app.config_data["handle_offset_x"] = self.entry_handle_x.get().strip()
        self.app.config_data["handle_y"] = self.entry_handle_y.get().strip()
        self.app.config_data["handle_size"] = self.entry_handle_size.get().strip()
        
        self.app.persist_config()

    def sync_config_balance(self, new_balance):
        self.app.config_data["saldo_brl"] = new_balance
        self.app.persist_config()

        config_view = getattr(self.app, "config_view", None) or getattr(self.app, "view_config", None)
        if config_view:
            if hasattr(config_view, "entry_saldo"):
                config_view.entry_saldo.delete(0, "end")
                config_view.entry_saldo.insert(0, f"{new_balance:.2f}")
            if hasattr(config_view, "lbl_saldo"):
                config_view.lbl_saldo.configure(text=f"R$ {new_balance:.2f}")
            if hasattr(config_view, "load_config_fields"):
                config_view.load_config_fields()

    def create_caption_card(self, caption_lines, output_png_path):
        font_path = "C:/Windows/Fonts/segoeuib.ttf"
        font_size = 42
        try:
            font = ImageFont.truetype(font_path, font_size)
        except Exception:
            font = ImageFont.load_default()

        full_text = "\n".join(caption_lines)
        line_spacing = 4
        pad_x = 28
        pad_y = 20

        dummy_img = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw_dummy = ImageDraw.Draw(dummy_img)

        bbox = draw_dummy.multiline_textbbox(
            (0, 0),
            full_text,
            font=font,
            spacing=line_spacing,
            align="center"
        )

        text_x0, text_y0, text_x1, text_y1 = bbox
        text_w = text_x1 - text_x0
        text_h = text_y1 - text_y0

        card_w = int(text_w + (pad_x * 2))
        card_h = int(text_h + (pad_y * 2))

        card_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card_img)

        draw.rounded_rectangle([0, 0, card_w, card_h], radius=10, fill=(255, 255, 255, 255))

        pos_x = int(pad_x - text_x0)
        pos_y = int(pad_y - text_y0)

        draw.multiline_text(
            (pos_x, pos_y),
            full_text,
            fill=(0, 0, 0, 255),
            font=font,
            spacing=line_spacing,
            align="center"
        )

        card_img.save(output_png_path, "PNG")
        return card_w, card_h

    def process_cuts_simple(self):
        self.timer_running = True
        self.start_timestamp = time.time()

        try:
            duration = self.get_video_duration(self.video_path)
            try:
                part_duration = float(self.entry_dur.get().strip().replace(",", "."))
                part_duration = max(1.0, part_duration)
            except ValueError:
                part_duration = 60.0

            total_parts = int(duration // part_duration) + (1 if duration % part_duration > 0 else 0)
            base_title = self.entry_title.get().strip()

            self.lbl_count_progress.configure(text=f"0/{total_parts} partes processadas")
            self.log(f"Iniciando recorte simples | Duração total: {duration:.1f}s | Partes: {total_parts}")

            durations_list = []

            for i in range(total_parts):
                if self.cancel_requested:
                    self.lbl_status.configure(text="Cancelado")
                    self.log("Processo cancelado pelo usuário.", tag="error")
                    break

                part_start_clock = time.time()
                part_num = i + 1
                is_last_part = (part_num == total_parts)
                start_time = i * part_duration

                if is_last_part and total_parts > 1:
                    output_filename = "parte final.mp4"
                    part_line = "PARTE FINAL"
                else:
                    output_filename = f"parte {part_num}.mp4"
                    part_line = f"PARTE {part_num}"

                output_path = os.path.normpath(os.path.join(self.output_dir, output_filename))
                self.lbl_status.configure(text=f"Renderizando: {output_filename}")
                self.log(f"Processando arquivo: {output_filename}")

                base_filter = "scale=1080:-2,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
                video_filter = (
                    f"{base_filter},"
                    f"drawtext=fontfile='C\\:/Windows/Fonts/segoeuib.ttf':"
                    f"text='{base_title}':fontcolor=white:fontsize=52:"
                    f"x=(w-text_w)/2:y=260,"
                    f"drawtext=fontfile='C\\:/Windows/Fonts/segoeuib.ttf':"
                    f"text='{part_line}':fontcolor=white:fontsize=48:"
                    f"x=(w-text_w)/2:y=340"
                )

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start_time),
                    "-t", str(part_duration),
                    "-i", os.path.normpath(self.video_path),
                    "-vf", video_filter,
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "22",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    output_path
                ]

                self.active_subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
                for line in self.active_subprocess.stdout:
                    if "Error" in line or "error" in line:
                        self.log(line.strip(), tag="error")
                self.active_subprocess.wait()
                self.active_subprocess = None

                if self.cancel_requested:
                    self.lbl_status.configure(text="Cancelado")
                    self.log("Processamento interrompido.", tag="error")
                    break

                part_elapsed = time.time() - part_start_clock
                durations_list.append(part_elapsed)

                progress_val = part_num / total_parts
                self.progress.set(progress_val)
                self.lbl_count_progress.configure(text=f"{part_num}/{total_parts} partes processadas")

                elapsed_sec = int(time.time() - self.start_timestamp)
                self.lbl_elapsed.configure(text=f"Decorrido: {elapsed_sec // 3600:02d}h {(elapsed_sec % 3600) // 60:02d}m {elapsed_sec % 60:02d}s")

                parts_remaining = total_parts - part_num
                avg_time = sum(durations_list) / len(durations_list)
                est_seconds_left = int(parts_remaining * avg_time)
                self.lbl_timer.configure(text=f"Restante: {est_seconds_left // 3600:02d}h {(est_seconds_left % 3600) // 60:02d}m {est_seconds_left % 60:02d}s")

            if not self.cancel_requested:
                self.lbl_status.configure(text="Concluído com sucesso")
                self.lbl_timer.configure(text="Restante: 00h 00m 00s")
                self.log("Todos os cortes simples foram finalizados com sucesso.", tag="success")

        except Exception as e:
            self.log(f"Erro no processamento: {str(e)}", tag="error")
        finally:
            if self.preview_frame_path and os.path.exists(self.preview_frame_path):
                try:
                    os.remove(self.preview_frame_path)
                    self.preview_frame_path = ""
                except Exception:
                    pass

            self.timer_running = False
            self.btn_start.configure(state="normal", text="Iniciar cortes")
            self.btn_cancel.configure(state="disabled")
            self.btn_file.configure(state="normal")
            self.btn_folder.configure(state="normal")

    def process_cuts_ia(self):
        self.timer_running = True
        self.start_timestamp = time.time()
        uploaded_file_name = None
        temp_proxy_video = ""

        try:
            if not genai:
                raise Exception("Biblioteca google-genai não instalada. Execute 'pip install google-genai'.")

            api_key = self.app.config_data.get("api_key", "")
            if not api_key:
                raise Exception("Chave de API do Gemini não configurada. Defina em Configurações.")

            client = genai.Client(api_key=api_key)

            total_video_dur = self.get_video_duration(self.video_path)
            self.log(f"Vídeo de entrada carregado ({total_video_dur / 60:.1f} minutos).")

            file_to_send = self.video_path

            if os.path.getsize(self.video_path) > 1.8 * 1024 * 1024 * 1024:
                self.lbl_status.configure(text="Otimizando vídeo para envio à IA...")
                self.log("Vídeo ultrapassa limite da API. Gerando espelho leve em 480p para o Gemini...")

                temp_proxy_video = TEMP_PROXY
                cmd_proxy = [
                    "ffmpeg", "-y",
                    "-i", os.path.normpath(self.video_path),
                    "-vf", "scale=-2:480",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-b:v", "600k",
                    "-maxrate", "900k",
                    "-bufsize", "1200k",
                    "-c:a", "aac",
                    "-b:a", "96k",
                    temp_proxy_video
                ]
                self.active_subprocess = subprocess.Popen(cmd_proxy, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.active_subprocess.communicate()
                self.active_subprocess = None

                if self.cancel_requested:
                    return

                if os.path.exists(temp_proxy_video) and os.path.getsize(temp_proxy_video) > 0:
                    file_to_send = temp_proxy_video
                    self.log(f"Espelho pronto ({os.path.getsize(file_to_send) / (1024*1024):.1f} MB). Iniciando upload...", tag="success")

            if self.cancel_requested:
                return

            self.lbl_status.configure(text="Enviando vídeo para o Google AI Studio...")
            self.log("Fazendo upload do arquivo de vídeo para o Gemini...")
            video_upload = client.files.upload(file=file_to_send)
            uploaded_file_name = video_upload.name

            while video_upload.state.name == "PROCESSING":
                if self.cancel_requested:
                    return
                time.sleep(5)
                video_upload = client.files.get(name=video_upload.name)

            if video_upload.state.name == "FAILED":
                raise Exception("Falha no upload do arquivo para o Gemini.")

            if self.cancel_requested:
                return

            self.lbl_status.configure(text="IA analisando melhores momentos...")
            self.log("Analisando gravação integral para isolar destaques...")

            prompt = (
                "Você é um editor de vídeos profissional para redes sociais (TikTok, Shorts, Reels).\n"
                "Analise ESTE VÍDEO COMPLETO do início ao fim e encontre os MELHORES momentos contínuos "
                "(jogadas engraçadas, sustos, erros bizarros, mortes épicas ou diálogos divertidos).\n\n"
                "Regras obrigatórias:\n"
                "1. Encontre quantos cortes forem realmente necessários e interessantes (sem limite fixo).\n"
                "2. Cada corte deve ter entre 60 e 120 segundos de duração contínua.\n"
                "3. Para cada momento, crie uma legenda curta em português (máximo 45 caracteres) explicando o acontecimento.\n"
                "4. Responda em JSON seguindo exatamente a estrutura tipada."
            )

            schema_cortes = {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "start": {"type": "NUMBER", "description": "Tempo inicial em segundos"},
                        "end": {"type": "NUMBER", "description": "Tempo final em segundos"},
                        "caption": {"type": "STRING", "description": "Legenda curta em caixa alta sobre o corte"}
                    },
                    "required": ["start", "end", "caption"]
                }
            }

            modelos_disponiveis = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-flash"]
            response = None

            for mod in modelos_disponiveis:
                if self.cancel_requested:
                    return
                self.log(f"Tentando resposta via {mod}...")
                try:
                    response = client.models.generate_content(
                        model=mod,
                        contents=[video_upload, prompt],
                        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema_cortes, temperature=0.4)
                    )
                    if response and response.text:
                        self.log(f"Análise finalizada pelo modelo {mod}.", tag="success")
                        break
                except Exception as err:
                    self.log(f"Modelo {mod} indisponível: {str(err)}.", tag="error")

            if self.cancel_requested:
                return

            if not response or not response.text:
                raise Exception("Sem retorno da IA. Verifique as cotas da sua chave.")

            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

            base_cost = ((input_tokens / 1_000_000) * PRICE_INPUT_1M_BRL) + ((output_tokens / 1_000_000) * PRICE_OUTPUT_1M_BRL)
            cost_brl = base_cost * TAX_MULTIPLIER_BRL

            current_saldo = float(self.app.config_data.get("saldo_brl", 0.0))
            new_saldo = max(0.0, current_saldo - cost_brl)

            self.sync_config_balance(new_saldo)

            self.log(f"Tokens computados: {input_tokens:,} entrada | {output_tokens:,} saída".replace(",", "."))
            self.log(f"Valor real debitado nesta operação: R$ {cost_brl:.4f}", tag="success")
            self.log(f"Saldo restante em Configurações: R$ {new_saldo:.2f}", tag="normal")

            clips_data = json.loads(response.text)
            if not isinstance(clips_data, list) or len(clips_data) == 0:
                raise Exception("Nenhum recorte qualificado foi isolado pela IA.")

            total_clips = len(clips_data)
            self.lbl_count_progress.configure(text=f"0/{total_clips} partes processadas")
            self.log(f"Foram encontrados {total_clips} momentos ideais.")

            cx = self.entry_cam_x.get().strip() or "35"
            cy = self.entry_cam_y.get().strip() or "36"
            cw = self.entry_cam_w.get().strip() or "405"
            ch = self.entry_cam_h.get().strip() or "225"
            
            # Parametros de posicionamento da assinatura
            handle_tag = self.entry_handle.get().strip()
            handle_y = self.entry_handle_y.get().strip() or "1710"
            handle_size = self.entry_handle_size.get().strip() or "38"
            offset_x = float(self.entry_handle_x.get().strip() or "0")

            if "left" in self.current_anchor:
                handle_x_expr = str(int(80 + offset_x))
            elif "right" in self.current_anchor:
                handle_x_expr = f"w-text_w-{int(80 - offset_x)}"
            else:
                handle_x_expr = f"(w-text_w)/2+{int(offset_x)}" if offset_x != 0 else "(w-text_w)/2"

            durations_list = []

            for i, clip in enumerate(clips_data):
                if self.cancel_requested:
                    self.lbl_status.configure(text="Cancelado")
                    self.log("Processo cancelado pelo usuário.", tag="error")
                    break

                clip_start_clock = time.time()
                clip_num = i + 1
                start_sec = float(clip.get("start", 0))
                end_sec = float(clip.get("end", start_sec + 60))
                dur = max(60.0, end_sec - start_sec)

                raw_caption = clip.get("caption", f"MOMENTO {clip_num}").strip().upper()
                clean_caption = raw_caption.replace("'", "").replace(":", " - ").replace("\\", "")
                caption_lines = textwrap.wrap(clean_caption, width=28)

                card_png_path = os.path.join(BASE_DIR, f"temp_card_{clip_num}.png")
                self.create_caption_card(caption_lines, card_png_path)
                card_png_escaped = card_png_path.replace("\\", "/").replace(":", "\\:")

                output_filename = f"corte_ia_{clip_num}.mp4"
                output_path = os.path.normpath(os.path.join(self.output_dir, output_filename))

                self.lbl_status.configure(text=f"Renderizando: {output_filename}")
                self.log(f"Renderizando clipe {clip_num}/{total_clips}: '{clean_caption}' ({dur:.1f}s)")

                cam_filter = f"crop={cw}:{ch}:{cx}:{cy},scale=1080:608:flags=bicubic,boxblur=2:1[cam]"

                filter_complex = (
                    f"[0:v]split=2[in_cam][in_game];"
                    f"[in_cam]{cam_filter};"
                    f"[in_game]crop=ih:ih:(iw-ih)/2:0,scale=1080:1072:flags=bicubic[game];"
                    f"color=c=black:s=1080x1920:d={dur}[base];"
                    f"[base][cam]overlay=0:160[bg1];"
                    f"[bg1][game]overlay=0:768[bg2];"
                    f"movie='{card_png_escaped}'[card];"
                    f"[bg2][card]overlay=(W-w)/2:768-(h/2)[bg_card];"
                    f"[bg_card]drawtext=fontfile='C\\:/Windows/Fonts/segoeuib.ttf':"
                    f"text='{handle_tag}':fontcolor=white:fontsize={handle_size}:"
                    f"text_align=center:x={handle_x_expr}:y={handle_y}[v]"
                )

                cmd = [
                    "ffmpeg", "-y",
                    "-ss", str(start_sec),
                    "-t", str(dur),
                    "-i", os.path.normpath(self.video_path),
                    "-filter_complex", filter_complex,
                    "-map", "[v]",
                    "-map", "0:a?",
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-crf", "22",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    output_path
                ]

                self.active_subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
                for line in self.active_subprocess.stdout:
                    if "Error" in line or "error" in line:
                        self.log(line.strip(), tag="error")
                self.active_subprocess.wait()
                self.active_subprocess = None

                if os.path.exists(card_png_path):
                    try:
                        os.remove(card_png_path)
                    except Exception:
                        pass

                if self.cancel_requested:
                    self.lbl_status.configure(text="Cancelado")
                    self.log("Processo cancelado durante a renderização.", tag="error")
                    break

                clip_elapsed = time.time() - clip_start_clock
                durations_list.append(clip_elapsed)

                progress_val = clip_num / total_clips
                self.progress.set(progress_val)
                self.lbl_count_progress.configure(text=f"{clip_num}/{total_clips} partes processadas")

                elapsed_sec = int(time.time() - self.start_timestamp)
                self.lbl_elapsed.configure(text=f"Decorrido: {elapsed_sec // 3600:02d}h {(elapsed_sec % 3600) // 60:02d}m {elapsed_sec % 60:02d}s")

                parts_remaining = total_clips - clip_num
                avg_time = sum(durations_list) / len(durations_list)
                est_seconds_left = int(parts_remaining * avg_time)
                self.lbl_timer.configure(text=f"Restante: {est_seconds_left // 3600:02d}h {(est_seconds_left % 3600) // 60:02d}m {est_seconds_left % 60:02d}s")

            if not self.cancel_requested:
                self.lbl_status.configure(text="Concluído com sucesso")
                self.lbl_timer.configure(text="Restante: 00h 00m 00s")
                self.log("Processamento IA finalizado com sucesso.", tag="success")

        except Exception as e:
            self.log(f"Erro no modo IA: {str(e)}", tag="error")
        finally:
            proxy_clean = TEMP_PROXY
            if os.path.exists(proxy_clean):
                try:
                    os.remove(proxy_clean)
                except Exception:
                    pass

            if self.preview_frame_path and os.path.exists(self.preview_frame_path):
                try:
                    os.remove(self.preview_frame_path)
                    self.preview_frame_path = ""
                except Exception:
                    pass

            if uploaded_file_name and genai:
                try:
                    client.files.delete(name=uploaded_file_name)
                    self.log("Arquivo temporário excluído da API.")
                except Exception:
                    pass

            self.timer_running = False
            self.btn_start.configure(state="normal", text="Iniciar cortes")
            self.btn_cancel.configure(state="disabled")
            self.btn_file.configure(state="normal")
            self.btn_folder.configure(state="normal")