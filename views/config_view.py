import os
import time
import threading
import customtkinter as ctk

from core.constants import (
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
    COLOR_SUCCESS,
    COLOR_DANGER,
    FONT_FAMILY,
    SESSION_TIKTOK,
    SESSION_YOUTUBE,
    SESSION_INSTAGRAM
)
from services.auth_service import LoginSessionManager

class ConfigView(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLOR_BG, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.active_session_manager = None

        self.build_ui()

    def build_ui(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(
            content,
            text="Configurações do sistema",
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            content,
            text="Gerencie chaves de API, credenciais, enquadramento da webcam e estados de sessão.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 20))

        # Card API Gemini
        card_ai = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        card_ai.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            card_ai,
            text="Google Gemini API",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_ACCENT_BLUE
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(
            card_ai,
            text="Chave de API (Gemini):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(0, 4))

        self.cfg_entry_api_key = ctk.CTkEntry(
            card_ai,
            height=32,
            show="*",
            fg_color=COLOR_INPUT_BG,
            border_width=1,
            border_color=COLOR_INPUT_BORDER,
            corner_radius=6,
            text_color=COLOR_TEXT_MAIN
        )
        self.cfg_entry_api_key.insert(0, self.app.config_data.get("api_key", ""))
        self.cfg_entry_api_key.pack(fill="x", padx=16, pady=(0, 10))

        row_saldo_handle = ctk.CTkFrame(card_ai, fg_color="transparent")
        row_saldo_handle.pack(fill="x", padx=16, pady=(0, 16))

        frame_s = ctk.CTkFrame(row_saldo_handle, fg_color="transparent")
        frame_s.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(
            frame_s,
            text="Saldo da conta (R$):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.cfg_entry_saldo = ctk.CTkEntry(
            frame_s,
            height=32,
            fg_color=COLOR_INPUT_BG,
            border_width=1,
            border_color=COLOR_INPUT_BORDER,
            corner_radius=6,
            text_color=COLOR_TEXT_MAIN
        )
        val_saldo = self.app.config_data.get("saldo_brl", 0.0)
        self.cfg_entry_saldo.insert(0, f"{float(val_saldo):.2f}" if val_saldo else "")
        self.cfg_entry_saldo.pack(fill="x")

        frame_h = ctk.CTkFrame(row_saldo_handle, fg_color="transparent")
        frame_h.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(
            frame_h,
            text="Assinatura padrão (@):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.cfg_entry_handle = ctk.CTkEntry(
            frame_h,
            height=32,
            fg_color=COLOR_INPUT_BG,
            border_width=1,
            border_color=COLOR_INPUT_BORDER,
            corner_radius=6,
            text_color=COLOR_TEXT_MAIN
        )
        self.cfg_entry_handle.insert(0, self.app.config_data.get("handle", ""))
        self.cfg_entry_handle.pack(fill="x")

        # Card Padrão da Webcam
        card_cam = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        card_cam.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            card_cam,
            text="Padrão de enquadramento da webcam",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_ACCENT_BLUE
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            card_cam,
            text="Defina os valores padrão que serão carregados para recorte da câmera nos vídeos.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(0, 10))

        row_coords = ctk.CTkFrame(card_cam, fg_color="transparent")
        row_coords.pack(fill="x", padx=16, pady=(0, 16))
        row_coords.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def make_coord_input(parent, col, label, key, default):
            box = ctk.CTkFrame(parent, fg_color="transparent")
            box.grid(row=0, column=col, sticky="ew", padx=4)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 2))
            entry = ctk.CTkEntry(box, height=30, fg_color=COLOR_INPUT_BG, border_width=1, border_color=COLOR_INPUT_BORDER, corner_radius=6, text_color=COLOR_TEXT_MAIN)
            entry.insert(0, self.app.config_data.get(key, default))
            entry.pack(fill="x")
            return entry

        self.cfg_cam_x = make_coord_input(row_coords, 0, "Posição X", "cam_x", "35")
        self.cfg_cam_y = make_coord_input(row_coords, 1, "Posição Y", "cam_y", "36")
        self.cfg_cam_w = make_coord_input(row_coords, 2, "Largura", "cam_w", "405")
        self.cfg_cam_h = make_coord_input(row_coords, 3, "Altura", "cam_h", "225")

        # Card Sessões Sociais
        card_sessions = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        card_sessions.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            card_sessions,
            text="Status das sessões sociais",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_ACCENT_BLUE
        ).pack(anchor="w", padx=16, pady=(14, 10))

        def make_platform_row(parent, platform_key):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=6)

            lbl = ctk.CTkLabel(row, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=12), anchor="w")
            lbl.pack(side="left", fill="x", expand=True)

            btn = ctk.CTkButton(
                row,
                text="Conectar conta",
                width=120,
                height=28,
                corner_radius=6,
                fg_color=COLOR_BTN_SEC,
                hover_color=COLOR_BTN_SEC_HOVER,
                border_width=1,
                border_color=COLOR_CARD_BORDER,
                text_color=COLOR_TEXT_MAIN,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                command=lambda: self.open_login_flow(platform_key)
            )
            btn.pack(side="right")
            return lbl, btn

        self.lbl_alert_tt, self.btn_login_tt = make_platform_row(card_sessions, "tiktok")
        self.lbl_alert_yt, self.btn_login_yt = make_platform_row(card_sessions, "youtube")
        self.lbl_alert_ig, self.btn_login_ig = make_platform_row(card_sessions, "instagram")

        ctk.CTkFrame(card_sessions, height=8, fg_color="transparent").pack()

        btn_save = ctk.CTkButton(
            content,
            text="Salvar configurações",
            height=36,
            width=200,
            corner_radius=6,
            fg_color=COLOR_BTN_PRM,
            hover_color=COLOR_BTN_PRM_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=self.save_settings
        )
        btn_save.pack(side="right")

    def on_show(self):
        self.update_status_alerts()

    def update_status_alerts(self):
        tt_con = os.path.exists(SESSION_TIKTOK)
        yt_con = os.path.exists(SESSION_YOUTUBE)
        ig_con = os.path.exists(SESSION_INSTAGRAM)

        self.lbl_alert_tt.configure(
            text=f"• TikTok: {'✓ Sessão conectada' if tt_con else '✕ Sessão ausente'}",
            text_color=COLOR_SUCCESS if tt_con else COLOR_DANGER
        )
        self.btn_login_tt.configure(text="Reconectar" if tt_con else "Conectar conta")

        self.lbl_alert_yt.configure(
            text=f"• YouTube: {'✓ Sessão conectada' if yt_con else '✕ Sessão ausente'}",
            text_color=COLOR_SUCCESS if yt_con else COLOR_DANGER
        )
        self.btn_login_yt.configure(text="Reconectar" if yt_con else "Conectar conta")

        self.lbl_alert_ig.configure(
            text=f"• Instagram: {'✓ Sessão conectada' if ig_con else '✕ Sessão ausente'}",
            text_color=COLOR_SUCCESS if ig_con else COLOR_DANGER
        )
        self.btn_login_ig.configure(text="Reconectar" if ig_con else "Conectar conta")

    def open_login_flow(self, platform_key):
        try:
            self.active_session_manager = LoginSessionManager(platform_key)
        except Exception as e:
            self.app.log_all(f"Erro ao instanciar LoginSessionManager: {str(e)}", tag="error")
            return

        nome_rede = self.active_session_manager.info.get("nome", platform_key.capitalize())
        
        # Sinais de controlo de execução entre threads
        confirm_event = threading.Event()
        cancel_event = threading.Event()

        # Criação imediata do diálogo informativo
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Login no {nome_rede}")
        dialog.geometry("440x220")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLOR_BG)
        dialog.transient(self.app)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Autenticação: {nome_rede}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        ).pack(pady=(20, 8), padx=20, anchor="w")

        ctk.CTkLabel(
            dialog,
            text="1. O navegador será iniciado automaticamente em 5 segundos.\n2. Conclua a autenticação na janela aberta.\n3. Quando o painel carregar, clique em 'Confirmar login'.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED,
            justify="left"
        ).pack(pady=(0, 20), padx=20, anchor="w")

        frame_btns = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_btns.pack(fill="x", padx=20, pady=(0, 16))

        def on_confirm():
            btn_ok.configure(state="disabled", text="Salvando...")
            btn_cancel.configure(state="disabled")
            confirm_event.set()

        def on_cancel():
            cancel_event.set()
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        btn_cancel = ctk.CTkButton(
            frame_btns,
            text="Cancelar",
            width=100,
            height=32,
            fg_color=COLOR_BTN_SEC,
            hover_color=COLOR_BTN_SEC_HOVER,
            text_color=COLOR_TEXT_MAIN,
            command=on_cancel
        )
        btn_cancel.pack(side="left")

        btn_ok = ctk.CTkButton(
            frame_btns,
            text="Confirmar login",
            width=140,
            height=32,
            fg_color=COLOR_BTN_PRM,
            hover_color=COLOR_BTN_PRM_HOVER,
            text_color="#ffffff",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            command=on_confirm
        )
        btn_ok.pack(side="right")

        # Rotina isolada executada integralmente na thread de trabalho
        def worker():
            self.app.log_all(f"Aviso de login no {nome_rede} aberto. Iniciando navegador em 5 segundos...")
            
            # Pausa de 5 segundos antes de abrir a aba
            for _ in range(50):
                if cancel_event.is_set():
                    return
                time.sleep(0.1)

            try:
                self.app.log_all(f"Abrindo navegador para autenticação no {nome_rede}...")
                self.active_session_manager.start_login()

                # Aguarda até que o utilizador confirme ou cancele o diálogo
                while not confirm_event.is_set() and not cancel_event.is_set():
                    time.sleep(0.2)

                if cancel_event.is_set():
                    self.active_session_manager.close()
                    return

                # Grava a sessão garantidamente dentro da mesma thread do Playwright
                self.active_session_manager.confirm_and_save()
                self.app.log_all(f"Sessão do {nome_rede} salva com sucesso.", tag="success")

            except Exception as err:
                self.app.log_all(f"Erro ao salvar sessão: {str(err)}", tag="error")
            finally:
                self.after(0, self.update_status_alerts)
                self.after(0, lambda: dialog.destroy() if dialog.winfo_exists() else None)

        threading.Thread(target=worker, daemon=True).start()

    def save_settings(self):
        self.app.config_data["api_key"] = self.cfg_entry_api_key.get().strip()
        val_saldo = self.cfg_entry_saldo.get().strip()
        if val_saldo:
            try:
                self.app.config_data["saldo_brl"] = float(val_saldo.replace(",", "."))
            except ValueError:
                pass
        else:
            self.app.config_data["saldo_brl"] = 0.0

        self.app.config_data["handle"] = self.cfg_entry_handle.get().strip()

        self.app.config_data["cam_x"] = self.cfg_cam_x.get().strip()
        self.app.config_data["cam_y"] = self.cfg_cam_y.get().strip()
        self.app.config_data["cam_w"] = self.cfg_cam_w.get().strip()
        self.app.config_data["cam_h"] = self.cfg_cam_h.get().strip()

        self.app.persist_config()
        self.app.log_all("Configurações salvas no config.json com sucesso.", tag="success")