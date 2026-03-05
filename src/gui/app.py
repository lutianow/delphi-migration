# src/gui/app.py

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from src.core.migrator_engine import DelphiMigratorEngine
from src.core.i18n import I18N

# Theme Configuration based on Dribbble "Pods" UI
ctk.set_appearance_mode("Dark")
BG_MAIN = "#0D0D11"
BG_SIDEBAR = "#15151A"
BG_INPUT = "#1F1F26"
COLOR_PRIMARY = "#FFFFFF"
COLOR_SECONDARY = "#8E8E93"
CARD_1 = "#5D5DFF"  # Purple/Blue
CARD_2 = "#FF9B70"  # Peach/Orange

class DelphiMigratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config_file = "migrador_config.json"
        self.app_settings = self._load_settings()

        self.i18n = I18N(self.app_settings.get('lang', 'en'))
        self._ = self.i18n._

        self.title(self._("app_title"))
        self.geometry("1150x720")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)

        self.source_dir = ctk.StringVar(value=self.app_settings.get("source_dir", ""))
        self.dest_dir = ctk.StringVar(value=self.app_settings.get("dest_dir", ""))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Grid layout (2 columns)
        # Prevent Sidebar from expanding during long language values
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_sidebar()
        
        # Container for swappable frames (Dashboard & Settings)
        self.container_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.container_frame.grid(row=0, column=1, sticky="nsew", padx=60, pady=50)
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(0, weight=1)

        self._create_dashboard_frame()
        self._create_settings_frame()
        
        self.show_dashboard()

    def change_language(self, choice):
        self.i18n.set_language(choice)
        self._ = self.i18n._
        self._update_all_texts()
        self.save_settings()

    def _update_all_texts(self):
        # Window & Sidebar
        self.title(self._("app_title"))
        self.logo_label.configure(text=self._("logo_title"))
        self.lbl_menu.configure(text=self._("lbl_menu"))
        self.btn_nav1.configure(text=self._("nav_dashboard"))
        self.btn_nav2.configure(text=self._("nav_settings"))
        self.lbl_user_title.configure(text=self._("user_title"))
        self.lbl_user_sub.configure(text=self._("user_sub"))
        
        # Dashboard
        self.header_label.configure(text=self._("header_title"))
        self.lbl_src_title.configure(text=self._("card_src_title"))
        self.lbl_src_sub.configure(text=self._("card_src_sub"))
        self.btn_source.configure(text=self._("btn_browse"))
        self.lbl_dst_title.configure(text=self._("card_dst_title"))
        self.lbl_dst_sub.configure(text=self._("card_dst_sub"))
        self.btn_dest.configure(text=self._("btn_browse"))
        self.lbl_options.configure(text=self._("lbl_options"))
        self.chk_utf8.configure(text=self._("chk_utf8"))
        self.chk_bde.configure(text=self._("chk_bde"))
        self.chk_scopes.configure(text=self._("chk_scopes"))
        self.chk_advanced.configure(text=self._("chk_advanced"))
        
        if self.btn_start.cget("state") == "normal":
            self.btn_start.configure(text=self._("btn_start_ready"))
        else:
            self.btn_start.configure(text=self._("btn_start_busy"))
            
        # Settings
        self.lbl_settings_title.configure(text=self._("nav_settings").strip())
        self.lbl_lang_select.configure(text=self._("lbl_lang_select"))

    def show_dashboard(self):
        self.settings_frame.grid_forget()
        self.dashboard_frame.grid(row=0, column=0, sticky="nsew")
        self.btn_nav1.configure(fg_color=BG_INPUT)
        self.btn_nav2.configure(fg_color="transparent")

    def show_settings(self):
        self.dashboard_frame.grid_forget()
        self.settings_frame.grid(row=0, column=0, sticky="nsew")
        self.btn_nav2.configure(fg_color=BG_INPUT)
        self.btn_nav1.configure(fg_color="transparent")

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=BG_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.sidebar_frame.grid_propagate(False)

        # Brand Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=self._("logo_title"), font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color=COLOR_PRIMARY)
        self.logo_label.grid(row=0, column=0, padx=25, pady=(40, 50), sticky="w")

        # Fake Navigation Menu for aesthetic
        self.lbl_menu = ctk.CTkLabel(self.sidebar_frame, text=self._("lbl_menu"), font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=COLOR_SECONDARY)
        self.lbl_menu.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="w")

        self.btn_nav1 = ctk.CTkButton(self.sidebar_frame, text=self._("nav_dashboard"), font=ctk.CTkFont(size=14, weight="bold"), fg_color=BG_INPUT, text_color=COLOR_PRIMARY, anchor="w", height=45, command=self.show_dashboard)
        self.btn_nav1.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_nav2 = ctk.CTkButton(self.sidebar_frame, text=self._("nav_settings"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=self.show_settings)
        self.btn_nav2.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        # Bottom Mini-Player / Profile mimic
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color=BG_INPUT, corner_radius=16)
        self.profile_frame.grid(row=5, column=0, padx=20, pady=30, sticky="ew")
        
        self.lbl_user_title = ctk.CTkLabel(self.profile_frame, text=self._("user_title"), font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_user_title.pack(padx=15, pady=(15, 0), anchor="w")
        self.lbl_user_sub = ctk.CTkLabel(self.profile_frame, text=self._("user_sub"), font=ctk.CTkFont(size=12), text_color=COLOR_SECONDARY)
        self.lbl_user_sub.pack(padx=15, pady=(0, 15), anchor="w")

    def _create_dashboard_frame(self):
        self.dashboard_frame = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.dashboard_frame.grid_columnconfigure((0, 1), weight=1)

        # Header Title
        self.header_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 40))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text=self._("header_title"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label.grid(row=0, column=0, sticky="w")

        # Horizontal Cards Row
        # Card 1: Source
        self.card_source = ctk.CTkFrame(self.dashboard_frame, fg_color=CARD_1, corner_radius=28, height=210)
        self.card_source.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.card_source.grid_propagate(False)

        self.lbl_src_title = ctk.CTkLabel(self.card_source, text=self._("card_src_title"), font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFFFFF")
        self.lbl_src_title.pack(anchor="w", padx=30, pady=(30, 5))
        self.lbl_src_sub = ctk.CTkLabel(self.card_source, text=self._("card_src_sub"), font=ctk.CTkFont(size=14), text_color="#E0E0FF")
        self.lbl_src_sub.pack(anchor="w", padx=30, pady=(0, 25))

        ent_source = ctk.CTkEntry(self.card_source, textvariable=self.source_dir, fg_color="#4343D9", border_width=0, text_color="#FFFFFF", height=40, corner_radius=12)
        ent_source.pack(fill="x", padx=30, pady=(0, 12))

        self.btn_source = ctk.CTkButton(self.card_source, text=self._("btn_browse"), command=self.browse_source, fg_color="#FFFFFF", text_color=CARD_1, hover_color="#E0E0FF", font=ctk.CTkFont(weight="bold", size=13), corner_radius=12, height=36)
        self.btn_source.pack(anchor="w", padx=30)

        # Card 2: Destination
        self.card_dest = ctk.CTkFrame(self.dashboard_frame, fg_color=CARD_2, corner_radius=28, height=210)
        self.card_dest.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
        self.card_dest.grid_propagate(False)

        self.lbl_dst_title = ctk.CTkLabel(self.card_dest, text=self._("card_dst_title"), font=ctk.CTkFont(size=22, weight="bold"), text_color="#FFFFFF")
        self.lbl_dst_title.pack(anchor="w", padx=30, pady=(30, 5))
        self.lbl_dst_sub = ctk.CTkLabel(self.card_dest, text=self._("card_dst_sub"), font=ctk.CTkFont(size=14), text_color="#FFE0D0")
        self.lbl_dst_sub.pack(anchor="w", padx=30, pady=(0, 25))

        ent_dest = ctk.CTkEntry(self.card_dest, textvariable=self.dest_dir, fg_color="#D97A53", border_width=0, text_color="#FFFFFF", height=40, corner_radius=12)
        ent_dest.pack(fill="x", padx=30, pady=(0, 12))

        self.btn_dest = ctk.CTkButton(self.card_dest, text=self._("btn_browse"), command=self.browse_dest, fg_color="#FFFFFF", text_color=CARD_2, hover_color="#FFE0D0", font=ctk.CTkFont(weight="bold", size=13), corner_radius=12, height=36)
        self.btn_dest.pack(anchor="w", padx=30)

        # Options Section
        self.lbl_options = ctk.CTkLabel(self.dashboard_frame, text=self._("lbl_options"), font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_options.grid(row=2, column=0, columnspan=2, sticky="w", pady=(50, 20))

        self.options_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.options_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))

        self.var_utf8 = ctk.BooleanVar(value=self.app_settings.get("utf8", True))
        self.var_bde = ctk.BooleanVar(value=self.app_settings.get("bde", True))
        self.var_scopes = ctk.BooleanVar(value=self.app_settings.get("scopes", True))
        self.var_advanced = ctk.BooleanVar(value=self.app_settings.get("advanced", True))

        # Auto-save triggers
        self.source_dir.trace_add("write", lambda *args: self.save_settings())
        self.dest_dir.trace_add("write", lambda *args: self.save_settings())
        self.var_utf8.trace_add("write", lambda *args: self.save_settings())
        self.var_bde.trace_add("write", lambda *args: self.save_settings())
        self.var_scopes.trace_add("write", lambda *args: self.save_settings())
        self.var_advanced.trace_add("write", lambda *args: self.save_settings())

        chk_font = ctk.CTkFont(size=14) # Increased font size
        
        # We give checkboxes a little more width, hover colors, and border widths
        kwargs = {"text_color": COLOR_SECONDARY, "fg_color": CARD_1, "font": chk_font, "border_width": 2, "checkbox_width": 24, "checkbox_height": 24, "hover_color": "#8080FF"}
        
        self.chk_utf8 = ctk.CTkCheckBox(self.options_frame, text=self._("chk_utf8"), variable=self.var_utf8, **kwargs)
        self.chk_utf8.pack(anchor="w", pady=10)
        self.chk_bde = ctk.CTkCheckBox(self.options_frame, text=self._("chk_bde"), variable=self.var_bde, **kwargs)
        self.chk_bde.pack(anchor="w", pady=10)
        self.chk_scopes = ctk.CTkCheckBox(self.options_frame, text=self._("chk_scopes"), variable=self.var_scopes, **kwargs)
        self.chk_scopes.pack(anchor="w", pady=10)
        
        kwargs["fg_color"] = CARD_2
        kwargs["hover_color"] = "#FFB080"
        self.chk_advanced = ctk.CTkCheckBox(self.options_frame, text=self._("chk_advanced"), variable=self.var_advanced, **kwargs)
        self.chk_advanced.pack(anchor="w", pady=10)

        # Start Button & Log
        self.right_col_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.right_col_frame.grid(row=3, column=1, sticky="nsew", padx=(25, 0))

        self.btn_start = ctk.CTkButton(self.right_col_frame, text=self._("btn_start_ready"), command=self.start_migration, font=ctk.CTkFont(size=16, weight="bold"), fg_color=COLOR_PRIMARY, text_color=BG_MAIN, hover_color="#E5E5E5", corner_radius=28, height=52)
        self.btn_start.pack(fill="x", pady=(0, 20))

        self.log_textbox = ctk.CTkTextbox(self.right_col_frame, fg_color=BG_INPUT, text_color=COLOR_SECONDARY, corner_radius=20, font=ctk.CTkFont(family="Consolas", size=12), border_width=1, border_color="#2A2A35")
        self.log_textbox.pack(fill="both", expand=True)
        self.log_textbox.insert("end", self._("log_ready") + "\n")
        self.log_textbox.configure(state="disabled")

    def _create_settings_frame(self):
        self.settings_frame = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        
        # Header
        self.lbl_settings_title = ctk.CTkLabel(self.settings_frame, text=self._("nav_settings").strip(), font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_settings_title.pack(anchor="w", pady=(0, 30))

        # Settings Card
        self.settings_card = ctk.CTkFrame(self.settings_frame, fg_color=BG_INPUT, corner_radius=16)
        self.settings_card.pack(fill="x", anchor="w")

        # Language Selection row
        self.lang_row = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.lang_row.pack(fill="x", padx=25, pady=25)

        self.lbl_lang_select = ctk.CTkLabel(self.lang_row, text=self._("lbl_lang_select"), font=ctk.CTkFont(size=16, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_lang_select.pack(side="left")

        # Dropdown
        self.lang_combo = ctk.CTkOptionMenu(self.lang_row, values=["English", "Português"], command=self.change_language, fg_color=CARD_1, button_color="#4343D9", font=ctk.CTkFont(weight="bold"))
        self.lang_combo.set("English" if self.i18n.lang == 'en' else "Português")
        self.lang_combo.pack(side="right")

    def browse_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_dir.set(folder)

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_dir.set(folder)

    def log_thread_safe(self, message):
        self.after(0, lambda m=message: self._insert_log(m))

    def _insert_log(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def _enable_btn(self):
        self.btn_start.configure(state="normal", text=self._("btn_start_ready"))

    def start_migration(self):
        src = self.source_dir.get().strip()
        dst = self.dest_dir.get().strip()

        if not src or not dst:
            messagebox.showwarning(self._("tag_notice"), self._("msg_select_folders"))
            return

        if src == dst:
            messagebox.showwarning(self._("tag_notice"), self._("msg_same_folders"))
            return

        if not os.path.exists(src):
            messagebox.showerror(self._("tag_error"), self._("msg_bad_source"))
            return

        self.btn_start.configure(state="disabled", text=self._("btn_start_busy"))
        self.log_thread_safe("\n=== BOOTING MIGRATION ENGINE ===")
        
        config = {
            'utf8': self.var_utf8.get(),
            'bde': self.var_bde.get(),
            'scopes': self.var_scopes.get(),
            'advanced': self.var_advanced.get()
        }

        threading.Thread(target=self._run_engine, args=(src, dst, config), daemon=True).start()

    def _run_engine(self, src, dst, config):
        engine = DelphiMigratorEngine(src, dst, config, self.log_thread_safe)
        try:
            engine.start_migration()
        except Exception:
            pass
        finally:
            self.after(0, self._enable_btn)

    def _load_settings(self):
        import json
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def save_settings(self):
        import json
        try:
            config = {
                'lang': self.i18n.lang,
                'source_dir': self.source_dir.get(),
                'dest_dir': self.dest_dir.get(),
                'utf8': self.var_utf8.get(),
                'bde': self.var_bde.get(),
                'scopes': self.var_scopes.get(),
                'advanced': self.var_advanced.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass

    def on_closing(self):
        self.save_settings()
        self.destroy()
