import os
import threading
import time
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

from core.constants import (
    SESSION_TIKTOK,
    SESSION_YOUTUBE,
    SESSION_INSTAGRAM,
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
    COLOR_BADGE_BG,
    COLOR_BADGE_BORDER,
    COLOR_SUCCESS,
    COLOR_DANGER,
    FONT_FAMILY
)

class PostadorView(ctk.CTkScrollableFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLOR_BG, corner_radius=0)
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        self.selected_files = []
        self.total_remaining_seconds = 0
        self.timer_running = False
        self.cancel_requested = False
        self.start_timestamp = 0

        self.build_ui()

    def build_ui(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=28, pady=20)

        self.card_poster_input = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_poster_input.pack(fill="x", pady=(0, 14))

        row_h_post = ctk.CTkFrame(self.card_poster_input, fg_color="transparent")
        row_h_post.pack(fill="x", padx=16, pady=(14, 2))
        ctk.CTkLabel(row_h_post, text="Fila de vídeos", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(side="left")

        badge_p = ctk.CTkFrame(row_h_post, fg_color=COLOR_BADGE_BG, corner_radius=10, border_width=1, border_color=COLOR_BADGE_BORDER)
        badge_p.pack(side="right")
        self.lbl_post_badge = ctk.CTkLabel(badge_p, text="0 itens", font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"), text_color=COLOR_TEXT_MUTED)
        self.lbl_post_badge.pack(padx=6, pady=1)

        ctk.CTkLabel(self.card_poster_input, text="Selecione um ou múltiplos arquivos MP4 para agendamento em lote.", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 10))

        box_post_display = ctk.CTkFrame(self.card_poster_input, fg_color=COLOR_INPUT_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        box_post_display.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(box_post_display, text="🎥", font=ctk.CTkFont(size=16)).pack(side="left", padx=(12, 10), pady=10)
        frame_post_info = ctk.CTkFrame(box_post_display, fg_color="transparent")
        frame_post_info.pack(side="left", fill="both", expand=True, pady=6)

        self.lbl_poster_count_title = ctk.CTkLabel(frame_post_info, text="Nenhum vídeo adicionado à fila", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w")
        self.lbl_poster_count_title.pack(fill="x")
        self.lbl_poster_count_meta = ctk.CTkLabel(frame_post_info, text="Formatos aceitos: *.mp4", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLOR_TEXT_MUTED, anchor="w")
        self.lbl_poster_count_meta.pack(fill="x")

        row_btns_post = ctk.CTkFrame(self.card_poster_input, fg_color="transparent")
        row_btns_post.pack(fill="x", padx=16, pady=(0, 14))

        self.btn_add_files = ctk.CTkButton(row_btns_post, text="+ Adicionar vídeos", height=32, corner_radius=6, fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), command=self.select_files)
        self.btn_add_files.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.btn_clear_queue = ctk.CTkButton(row_btns_post, text="Limpar fila", width=90, height=32, corner_radius=6, fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_DANGER, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), command=self.clear_files)
        self.btn_clear_queue.pack(side="right")

        self.queue_container = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.queue_container.pack(fill="x", pady=(0, 16))

        self.queue_items_frame = ctk.CTkFrame(self.queue_container, fg_color="transparent")
        self.queue_items_frame.pack(fill="x", padx=12, pady=12)

        self.card_destinos = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_destinos.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(self.card_destinos, text="Destinos de publicação", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=16, pady=(12, 6))

        frame_checks = ctk.CTkFrame(self.card_destinos, fg_color="transparent")
        frame_checks.pack(fill="x", padx=16, pady=(0, 14))

        self.chk_tt = ctk.CTkCheckBox(frame_checks, text="TikTok", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BTN_PRM, hover_color=COLOR_BTN_PRM_HOVER, corner_radius=4)
        self.chk_tt.pack(side="left", padx=(0, 24))
        self.chk_tt.select()

        self.chk_yt = ctk.CTkCheckBox(frame_checks, text="YouTube Shorts", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BTN_PRM, hover_color=COLOR_BTN_PRM_HOVER, corner_radius=4)
        self.chk_yt.pack(side="left", padx=(0, 24))
        self.chk_yt.select()

        self.chk_ig = ctk.CTkCheckBox(frame_checks, text="Instagram Reels", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BTN_PRM, hover_color=COLOR_BTN_PRM_HOVER, corner_radius=4)
        self.chk_ig.pack(side="left")
        self.chk_ig.select()

        self.card_post_cfg = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_post_cfg.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(self.card_post_cfg, text="Configurações da publicação", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), text_color=COLOR_ACCENT_BLUE).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(self.card_post_cfg, text="Legenda padrão", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 4))
        self.txt_caption = ctk.CTkTextbox(self.card_post_cfg, height=54, fg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12), corner_radius=6, border_width=1, border_color=COLOR_INPUT_BORDER)
        self.txt_caption.pack(fill="x", padx=16, pady=(0, 10))

        self.chk_final_caption = ctk.CTkCheckBox(self.card_post_cfg, text="Usar legenda alternativa no último vídeo", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MAIN, fg_color=COLOR_BTN_PRM, hover_color=COLOR_BTN_PRM_HOVER, corner_radius=4, command=self.toggle_final_caption)
        self.chk_final_caption.pack(anchor="w", padx=16, pady=(0, 8))

        self.txt_final_caption = ctk.CTkTextbox(self.card_post_cfg, height=54, fg_color=COLOR_INPUT_BG, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=12), corner_radius=6, border_width=1, border_color=COLOR_INPUT_BORDER)

        self.frame_delay_row = ctk.CTkFrame(self.card_post_cfg, fg_color="transparent")
        self.frame_delay_row.pack(fill="x", padx=16, pady=(6, 16))

        ctk.CTkLabel(self.frame_delay_row, text="Intervalo entre postagens", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED).pack(side="left")

        frame_input_delay = ctk.CTkFrame(self.frame_delay_row, fg_color="transparent")
        frame_input_delay.pack(side="right")

        self.entry_delay = ctk.CTkEntry(
            frame_input_delay,
            width=65,
            height=28,
            justify="center",
            fg_color=COLOR_INPUT_BG,
            border_width=1,
            border_color=COLOR_INPUT_BORDER,
            corner_radius=6,
            text_color=COLOR_TEXT_MAIN,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold")
        )
        self.entry_delay.insert(0, "30")
        self.entry_delay.pack(side="left")

        ctk.CTkLabel(frame_input_delay, text="minutos", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED).pack(side="left", padx=(8, 0))

        self.card_status_poster = ctk.CTkFrame(content, fg_color=COLOR_CARD, border_width=1, border_color=COLOR_CARD_BORDER, corner_radius=6)
        self.card_status_poster.pack(fill="both", expand=True, pady=(0, 16))

        bar_top_post = ctk.CTkFrame(self.card_status_poster, fg_color="#1f242c", height=34, corner_radius=6)
        bar_top_post.pack(fill="x")
        self.lbl_status = ctk.CTkLabel(bar_top_post, text="Pronto para iniciar", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_ACCENT_BLUE)
        self.lbl_status.pack(side="left", padx=14, pady=6)
        self.lbl_count_progress = ctk.CTkLabel(bar_top_post, text="0 / 0 vídeos publicados", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED)
        self.lbl_count_progress.pack(side="right", padx=14, pady=6)

        bar_timers_post = ctk.CTkFrame(self.card_status_poster, fg_color="transparent")
        bar_timers_post.pack(fill="x", padx=14, pady=(10, 4))
        self.lbl_elapsed = ctk.CTkLabel(bar_timers_post, text="Decorrido: 00h 00m 00s", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED)
        self.lbl_elapsed.pack(side="left")
        self.lbl_timer = ctk.CTkLabel(bar_timers_post, text="Restante: 00h 00m 00s", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT_MUTED)
        self.lbl_timer.pack(side="right")

        self.progress = ctk.CTkProgressBar(self.card_status_poster, height=4, corner_radius=2, fg_color="#21262d", progress_color=COLOR_BTN_PRM)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=14, pady=(0, 10))

        frame_term_post_h = ctk.CTkFrame(self.card_status_poster, fg_color="transparent", height=28)
        frame_term_post_h.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(frame_term_post_h, text="Console log", font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"), text_color=COLOR_TEXT_MUTED).pack(side="left")

        self.btn_copy_terminal = ctk.CTkButton(frame_term_post_h, text="Copiar", width=65, height=22, corner_radius=6, fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, border_width=1, border_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MAIN, font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"), command=self.copy_terminal)
        self.btn_copy_terminal.pack(side="right")

        self.log_box = ctk.CTkTextbox(self.card_status_poster, height=120, fg_color=COLOR_INPUT_BG, text_color="#c9d1d9", font=("Consolas", 10), corner_radius=4, border_width=1, border_color=COLOR_CARD_BORDER)
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.log_box.tag_config("success", foreground=COLOR_SUCCESS)
        self.log_box.tag_config("error", foreground=COLOR_DANGER)
        self.log_box.tag_config("normal", foreground="#c9d1d9")

        frame_action_post = ctk.CTkFrame(content, fg_color="transparent")
        frame_action_post.pack(fill="x", pady=(0, 10))

        self.btn_cancel = ctk.CTkButton(
            frame_action_post,
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
            command=self.cancel_posting
        )
        self.btn_cancel.pack(side="right", padx=(8, 0))

        self.btn_start = ctk.CTkButton(frame_action_post, text="Iniciar fila de postagens", width=240, height=38, corner_radius=6, fg_color=COLOR_BTN_PRM, hover_color=COLOR_BTN_PRM_HOVER, text_color="#ffffff", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), command=self.start_posting_thread)
        self.btn_start.pack(side="right")

        self.render_file_list()

    def on_show(self):
        self.update_platform_connection_labels()

    def update_platform_connection_labels(self):
        tt_con = os.path.exists(SESSION_TIKTOK)
        yt_con = os.path.exists(SESSION_YOUTUBE)
        ig_con = os.path.exists(SESSION_INSTAGRAM)

        self.chk_tt.configure(text=f"TikTok ({'conectado' if tt_con else 'desconectado'})")
        self.chk_yt.configure(text=f"YouTube Shorts ({'conectado' if yt_con else 'desconectado'})")
        self.chk_ig.configure(text=f"Instagram Reels ({'conectado' if ig_con else 'desconectado'})")

    def log(self, text, tag="normal"):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{hora}] {text}\n", tag)
        self.log_box.see("end")
        print(f"[Postador {hora}] {text}")

    def copy_terminal(self):
        content = self.log_box.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.btn_copy_terminal.configure(text="Copiado")
        self.after(1500, lambda: self.btn_copy_terminal.configure(text="Copiar"))

    def cancel_posting(self):
        self.cancel_requested = True
        self.lbl_status.configure(text="Cancelando fila...")
        self.log("Cancelamento solicitado pelo usuário. Finalizando lote atual...", tag="error")

    def get_current_interval_minutes(self):
        val_str = self.entry_delay.get().strip()
        try:
            return max(1, int(val_str))
        except ValueError:
            return 30

    def toggle_final_caption(self):
        if self.chk_final_caption.get() == 1:
            self.txt_final_caption.pack(fill="x", padx=16, pady=(0, 10), before=self.frame_delay_row)
        else:
            self.txt_final_caption.pack_forget()

    def select_files(self):
        files = filedialog.askopenfilenames(title="Selecione os vídeos", filetypes=[("Arquivos MP4", "*.mp4")])
        if files:
            for f in files:
                if f not in self.selected_files:
                    self.selected_files.append(f)
            self.render_file_list()
            self.log(f"{len(files)} vídeo(s) adicionados à fila.")

    def clear_files(self):
        if not self.selected_files:
            return
        self.selected_files = []
        self.render_file_list()
        self.progress.set(0)
        self.lbl_status.configure(text="Pronto para iniciar")
        self.log("Fila de postagens limpa.")

    def render_file_list(self):
        for widget in self.queue_items_frame.winfo_children():
            widget.destroy()

        count = len(self.selected_files)
        self.lbl_post_badge.configure(text=f"{count} {'item' if count == 1 else 'itens'}")

        if count == 0:
            self.lbl_poster_count_title.configure(text="Nenhum vídeo adicionado à fila")
            empty_lbl = ctk.CTkLabel(self.queue_items_frame, text="Nenhum vídeo adicionado à fila ainda.", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT_MUTED)
            empty_lbl.pack(pady=20)
            self.lbl_count_progress.configure(text="0 / 0 vídeos publicados")
            return

        self.lbl_poster_count_title.configure(text=f"{count} vídeo{'s' if count > 1 else ''} aguardando publicação")
        self.lbl_count_progress.configure(text=f"0 / {count} vídeos publicados")

        for idx, file_path in enumerate(self.selected_files):
            row = ctk.CTkFrame(self.queue_items_frame, fg_color=COLOR_INPUT_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
            row.pack(fill="x", pady=2)

            name = os.path.basename(file_path)
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left", padx=12, pady=6, fill="x", expand=True)

            ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_TEXT_MAIN, anchor="w").pack(fill="x")
            ctk.CTkLabel(info_frame, text=f"Ordem {idx + 1} de {count}", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLOR_TEXT_MUTED, anchor="w").pack(fill="x")

            btn_del = ctk.CTkButton(row, text="✕", width=24, height=24, fg_color="transparent", hover_color=COLOR_CARD_BORDER, text_color=COLOR_TEXT_MUTED, corner_radius=4, command=lambda i=idx: self.remove_file(i))
            btn_del.pack(side="right", padx=(2, 8), pady=4)

            btn_down = ctk.CTkButton(row, text="▼", width=22, height=22, font=ctk.CTkFont(size=9), fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, text_color=COLOR_TEXT_MAIN, corner_radius=4, command=lambda i=idx: self.move_file_down(i))
            btn_down.pack(side="right", padx=2, pady=4)

            btn_up = ctk.CTkButton(row, text="▲", width=22, height=22, font=ctk.CTkFont(size=9), fg_color=COLOR_BTN_SEC, hover_color=COLOR_BTN_SEC_HOVER, text_color=COLOR_TEXT_MAIN, corner_radius=4, command=lambda i=idx: self.move_file_up(i))
            btn_up.pack(side="right", padx=2, pady=4)

    def move_file_up(self, index):
        if index > 0:
            self.selected_files[index], self.selected_files[index - 1] = self.selected_files[index - 1], self.selected_files[index]
            self.render_file_list()

    def move_file_down(self, index):
        if index < len(self.selected_files) - 1:
            self.selected_files[index], self.selected_files[index + 1] = self.selected_files[index + 1], self.selected_files[index]
            self.render_file_list()

    def remove_file(self, index):
        if 0 <= index < len(self.selected_files):
            removed = self.selected_files.pop(index)
            self.render_file_list()
            self.log(f"Removido: {os.path.basename(removed)}")

    def start_countdown_loop(self):
        self.timer_running = True
        self.start_timestamp = time.time()

        while self.timer_running and self.total_remaining_seconds > 0 and not self.cancel_requested:
            elapsed_sec = int(time.time() - self.start_timestamp)
            self.lbl_elapsed.configure(text=f"Decorrido: {elapsed_sec // 3600:02d}h {(elapsed_sec % 3600) // 60:02d}m {elapsed_sec % 60:02d}s")

            rh = int(self.total_remaining_seconds // 3600)
            rm = int((self.total_remaining_seconds % 3600) // 60)
            rs = int(self.total_remaining_seconds % 60)
            self.lbl_timer.configure(text=f"Restante: {rh:02d}h {rm:02d}m {rs:02d}s")

            time.sleep(1)
            self.total_remaining_seconds -= 1

        if self.cancel_requested:
            self.lbl_timer.configure(text="Restante: Interrompido")
        elif self.timer_running and self.total_remaining_seconds <= 0:
            self.lbl_timer.configure(text="Restante: Concluído")

    def start_posting_thread(self):
        post_tt = (self.chk_tt.get() == 1)
        post_yt = (self.chk_yt.get() == 1)
        post_ig = (self.chk_ig.get() == 1)

        if not (post_tt or post_yt or post_ig):
            self.log("Erro: Selecione pelo menos uma rede de destino.", tag="error")
            return

        if post_tt and not os.path.exists(SESSION_TIKTOK):
            self.log("Erro: Sessão do TikTok ausente. Salve o login primeiro em Configurações.", tag="error")
            return
        if post_yt and not os.path.exists(SESSION_YOUTUBE):
            self.log("Erro: Sessão do YouTube ausente. Salve o login primeiro em Configurações.", tag="error")
            return
        if post_ig and not os.path.exists(SESSION_INSTAGRAM):
            self.log("Erro: Sessão do Instagram ausente. Salve o login primeiro em Configurações.", tag="error")
            return

        if not self.selected_files:
            self.log("Erro: Selecione pelo menos um arquivo de vídeo.", tag="error")
            return

        timeout_min = self.get_current_interval_minutes()
        total_posts = len(self.selected_files)
        redes_ativas = sum([post_tt, post_yt, post_ig])

        tempo_por_lote = redes_ativas * 70
        tempo_total_pausas = max(0, total_posts - 1) * (timeout_min * 60)
        self.total_remaining_seconds = (total_posts * tempo_por_lote) + tempo_total_pausas

        self.cancel_requested = False
        self.btn_start.configure(state="disabled", text="Publicando fila...")
        self.btn_cancel.configure(state="normal")
        self.btn_add_files.configure(state="disabled")
        self.btn_clear_queue.configure(state="disabled")

        threading.Thread(target=self.start_countdown_loop, daemon=True).start()
        threading.Thread(target=self.process_posting_queue, daemon=True).start()

    def upload_tiktok(self, p, video_path, caption):
        self.log(f"[TikTok] A iniciar envio de {os.path.basename(video_path)}...")
        browser = p.chromium.launch(headless=False, channel="msedge", args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(storage_state=SESSION_TIKTOK, viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.goto("https://www.tiktok.com/creator-center/upload?from=upload", wait_until="domcontentloaded")
        time.sleep(6)

        target = page
        for f in page.frames:
            if "upload" in f.url or "creator" in f.url:
                target = f
                break

        file_input = target.locator('input[type="file"]')
        file_input.wait_for(state="attached", timeout=45000)
        file_input.set_input_files(os.path.normpath(video_path))
        time.sleep(12)

        for ctx in [target, page]:
            try:
                btn_entendi = ctx.locator('button:has-text("Entendi"), button:has-text("Got it"), div[role="button"]:has-text("Entendi")').first
                if btn_entendi.is_visible(timeout=3000):
                    self.log("[TikTok] Fechando pop-up informativo...")
                    btn_entendi.click(force=True)
                    time.sleep(1)
                    break
            except Exception:
                pass

        if caption:
            try:
                caption_box = target.locator('div[contenteditable="true"], .DraftEditor-root, [role="combobox"]').first
                caption_box.wait_for(timeout=15000)
                caption_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(caption, delay=25)
            except Exception as e:
                self.log(f"[TikTok] Aviso na legenda: {e}", tag="error")

        time.sleep(4)
        post_btn = target.locator('button:has-text("Publicar"), button:has-text("Post"), button.btn-post').first
        post_btn.wait_for(state="visible", timeout=30000)
        post_btn.click()
        self.log("[TikTok] Botão Publicar clicado. Aguardando confirmações...")

        for ctx in [target, page]:
            try:
                btn_confirmar = ctx.locator('button:has-text("Publicar agora"), button:has-text("Post anyway"), div[role="dialog"] button:has-text("Publicar")').first
                btn_confirmar.wait_for(state="visible", timeout=8000)
                self.log("[TikTok] Modal detectado. Clicando em 'Publicar agora'...")
                btn_confirmar.click(force=True)
                break
            except Exception:
                pass

        try:
            target.locator('text="Seu vídeo foi publicado", text="Your video has been uploaded", text="Gerenciar suas publicações"').first.wait_for(state="visible", timeout=30000)
            self.log("[TikTok] Confirmação de upload recebida na tela.", tag="success")
        except Exception:
            time.sleep(10)

        browser.close()
        self.log("[TikTok] Publicação concluída.", tag="success")

    def upload_youtube(self, p, video_path, caption):
        nome_ficheiro = os.path.basename(video_path)
        self.log(f"[YouTube] A iniciar envio: {nome_ficheiro}")

        browser = p.chromium.launch(headless=False, channel="msedge", args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(storage_state=SESSION_YOUTUBE, viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            page.goto("https://studio.youtube.com", wait_until="networkidle")
            time.sleep(4)

            if not page.locator('input[type="file"]').is_visible():
                self.log("[YouTube] A abrir janela de envio...")
                btn_criar = page.locator('#create-icon, button:has-text("Criar"), [aria-label*="Criar"]').first
                btn_criar.wait_for(state="visible", timeout=20000)
                btn_criar.click()
                time.sleep(1)

                item_enviar = page.locator('tp-yt-paper-item:has-text("Enviar vídeos"), #text-item-0').first
                item_enviar.wait_for(state="visible", timeout=10000)
                item_enviar.click()
                time.sleep(2)

            self.log("[YouTube] A enviar ficheiro para o navegador...")
            file_input = page.locator('input[type="file"]').first
            file_input.wait_for(state="attached", timeout=20000)
            file_input.set_input_files(os.path.normpath(video_path))

            self.log("[YouTube] A aguardar carregamento dos campos...")
            title_container = page.locator('#textbox[aria-label*="título"], #title-textarea #textbox').first
            title_container.wait_for(state="visible", timeout=40000)
            time.sleep(2)

            titulo_base = caption.strip() if caption else os.path.splitext(nome_ficheiro)[0]
            titulo_final = f"{titulo_base} #shorts" if "#shorts" not in titulo_base.lower() else titulo_base

            self.log(f"[YouTube] A preencher título: {titulo_final}")
            title_container.click()
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")

            titulo_sem_hashtag = titulo_final.replace("#shorts", "").strip()
            page.keyboard.type(titulo_sem_hashtag, delay=20)
            page.keyboard.type(" #shorts", delay=100)
            time.sleep(2)

            sugestao_shorts = page.get_by_text("#shorts", exact=True).last
            if sugestao_shorts.is_visible():
                sugestao_shorts.click()
                self.log("[YouTube] Hashtag #shorts selecionada.")
            else:
                self.log("[YouTube] Sugestão #shorts não encontrada.")

            page.keyboard.press("Tab")
            time.sleep(1)

            self.log("[YouTube] A marcar opção de conteúdo para crianças...")
            radio_kids = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_MFK"], [name="VIDEO_MADE_FOR_KIDS_MFK"]').first
            radio_kids.scroll_into_view_if_needed()
            radio_kids.click()
            time.sleep(2)

            for etapa in [1, 2, 3]:
                self.log(f"[YouTube] A clicar em Avançar ({etapa}/3)...")
                btn_next = page.locator('#next-button').first
                btn_next.wait_for(state="visible", timeout=20000)
                btn_next.click()
                time.sleep(3)

            self.log("[YouTube] A selecionar visibilidade 'Público'...")
            radio_public = page.locator('tp-yt-paper-radio-button[name="PUBLIC"], tp-yt-paper-radio-button:has-text("Público")').first
            radio_public.scroll_into_view_if_needed()
            radio_public.wait_for(state="visible", timeout=15000)
            radio_public.click()
            time.sleep(2)

            self.log("[YouTube] A clicar em 'Publicar'...")
            btn_done = page.locator('#done-button').first
            btn_done.wait_for(state="visible", timeout=20000)
            btn_done.click()

            self.log("[YouTube] A aguardar confirmação do servidor...")
            time.sleep(12)
            self.log(f"[YouTube] Concluído com sucesso: {nome_ficheiro}", tag="success")

        except Exception as e:
            self.log(f"[YouTube ERRO] Falha no fluxo: {str(e)}", tag="error")
            raise e
        finally:
            browser.close()

    def upload_instagram(self, p, video_path, caption):
        nome_ficheiro = os.path.basename(video_path)
        self.log(f"[Instagram] A aceder ao Instagram para enviar: {nome_ficheiro}")

        browser = p.chromium.launch(headless=False, channel="msedge", args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(storage_state=SESSION_INSTAGRAM, viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            time.sleep(5)

            self.log("[Instagram] A clicar em 'Criar' no menu lateral...")
            btn_criar = page.locator('svg[aria-label="Nova publicação"], svg[aria-label="New post"], a[role="link"]:has(svg[aria-label*="publicação"]), a[role="link"]:has(svg[aria-label*="post"]), span:text-is("Criar")').first
            btn_criar.wait_for(state="visible", timeout=25000)
            btn_criar.click()
            time.sleep(1)

            self.log("[Instagram] A selecionar opcao 'Postar'...")
            item_postar = page.locator('div[role="menu"] span:text-is("Postar"), div[role="menu"] div:has-text("Postar"), span:text-is("Postar")').first
            item_postar.wait_for(state="visible", timeout=10000)
            item_postar.click()
            time.sleep(2)

            self.log("[Instagram] A carregar ficheiro de vídeo...")
            file_input = page.locator('input[type="file"]').first
            file_input.wait_for(state="attached", timeout=20000)
            file_input.set_input_files(os.path.normpath(video_path))
            time.sleep(5)

            try:
                btn_ok = page.locator('button:has-text("OK")').first
                if btn_ok.is_visible(timeout=3000):
                    btn_ok.click()
                    time.sleep(1)
            except Exception:
                pass

            self.log("[Instagram] Tela Cortar -> A clicar em 'Avançar'...")
            btn_avancar_1 = page.locator('div[role="button"]:has-text("Avançar"), button:has-text("Avançar")').first
            btn_avancar_1.wait_for(state="visible", timeout=20000)
            btn_avancar_1.click()
            time.sleep(3)

            self.log("[Instagram] Tela Editar -> A clicar em 'Avançar'...")
            btn_avancar_2 = page.locator('div[role="button"]:has-text("Avançar"), button:has-text("Avançar")').first
            btn_avancar_2.wait_for(state="visible", timeout=20000)
            btn_avancar_2.click()
            time.sleep(3)

            if caption:
                self.log("[Instagram] A preencher legenda...")
                caption_area = page.locator('div[aria-label="Adicione uma legenda..."], div[aria-label="Write a caption..."], div[contenteditable="true"]').first
                caption_area.wait_for(state="visible", timeout=20000)
                caption_area.click()
                caption_area.fill(caption)
                time.sleep(1.5)

            self.log("[Instagram] A clicar em 'Compartilhar'...")
            btn_compartilhar = page.locator('div[role="dialog"] div[role="button"]:has-text("Compartilhar"), div[role="dialog"] button:has-text("Compartilhar")').first
            btn_compartilhar.wait_for(state="visible", timeout=20000)
            btn_compartilhar.click()

            self.log("[Instagram] Aguardando 50 segundos para conclusão do envio...")
            time.sleep(50)
            self.log(f"[Instagram] Reel publicado com sucesso: {nome_ficheiro}", tag="success")

        except Exception as e:
            self.log(f"[Instagram ERRO] Falha no fluxo: {str(e)}", tag="error")
            raise e
        finally:
            try:
                context.close()
                browser.close()
            except Exception:
                pass

    def process_posting_queue(self):
        total = len(self.selected_files)
        padrao_caption = self.txt_caption.get("1.0", "end").strip()
        usar_legenda_final = (self.chk_final_caption.get() == 1)
        final_caption = self.txt_final_caption.get("1.0", "end").strip() if usar_legenda_final else ""
        timeout_seconds = self.get_current_interval_minutes() * 60

        post_tt = (self.chk_tt.get() == 1)
        post_yt = (self.chk_yt.get() == 1)
        post_ig = (self.chk_ig.get() == 1)

        try:
            if not sync_playwright:
                raise Exception("Playwright não instalado. Execute 'pip install playwright' e 'playwright install'.")

            with sync_playwright() as p:
                for idx, video_path in enumerate(self.selected_files):
                    if self.cancel_requested:
                        self.lbl_status.configure(text="Fila cancelada")
                        self.log("Fila de postagens interrompida pelo usuário.", tag="error")
                        break

                    file_name = os.path.basename(video_path)
                    current_num = idx + 1
                    is_last = (current_num == total)

                    if is_last and usar_legenda_final and final_caption:
                        caption_to_use = final_caption
                        self.log("A usar legenda alternativa de fecho.")
                    else:
                        caption_to_use = padrao_caption

                    self.lbl_status.configure(text=f"A publicar {current_num} de {total}: {file_name}")
                    self.lbl_count_progress.configure(text=f"{idx} / {total} vídeos concluídos")
                    self.log(f"\n--- Processamento ({current_num}/{total}): {file_name} ---")

                    if post_tt and not self.cancel_requested:
                        try:
                            self.upload_tiktok(p, video_path, caption_to_use)
                        except Exception as e:
                            self.log(f"[Erro TikTok] {e}", tag="error")

                    if post_yt and not self.cancel_requested:
                        try:
                            self.upload_youtube(p, video_path, caption_to_use)
                        except Exception as e:
                            self.log(f"[Erro YouTube] {e}", tag="error")

                    if post_ig and not self.cancel_requested:
                        try:
                            self.upload_instagram(p, video_path, caption_to_use)
                        except Exception as e:
                            self.log(f"[Erro Instagram] {e}", tag="error")

                    if self.cancel_requested:
                        self.lbl_status.configure(text="Fila cancelada")
                        break

                    self.lbl_count_progress.configure(text=f"{current_num} / {total} vídeos concluídos")
                    progress_val = current_num / total
                    self.progress.set(progress_val)

                    if current_num < total and timeout_seconds > 0:
                        minutes_wait = timeout_seconds / 60
                        self.lbl_status.configure(text=f"Pausa de {minutes_wait:.1f} min...")
                        self.log(f"A aguardar {minutes_wait:.1f} minutos até ao próximo lote...")

                        step = 5
                        remaining = int(timeout_seconds)
                        while remaining > 0 and self.timer_running and not self.cancel_requested:
                            time.sleep(step)
                            remaining -= step

            if not self.cancel_requested:
                self.lbl_status.configure(text="Concluído com sucesso")
                self.log("Todas as publicações selecionadas foram concluídas.", tag="success")

        except Exception as e:
            self.log(f"Erro crítico no processamento: {str(e)}", tag="error")
        finally:
            self.timer_running = False
            self.btn_start.configure(state="normal", text="Iniciar fila de postagens")
            self.btn_cancel.configure(state="disabled")
            self.btn_add_files.configure(state="normal")
            self.btn_clear_queue.configure(state="normal")