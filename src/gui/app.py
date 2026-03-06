# src/gui/app.py

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from PIL import Image
from src.core.migrator_engine import DelphiMigratorEngine
from src.core.updater import check_for_updates
from src.core.analyzer import ProjectAnalyzer
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
        self.geometry("1440x900")
        self.resizable(False, False)
        self.configure(fg_color=BG_MAIN)
        
        # Load Application Icon
        try:
            import sys
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'src', 'assets', 'icon.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

        self.source_dir = ctk.StringVar(value=self.app_settings.get("source_dir", ""))
        self.dest_dir = ctk.StringVar(value=self.app_settings.get("dest_dir", ""))
        self.var_src = ctk.StringVar(value=self.app_settings.get("source_dir", "")) # For analyzer
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Grid layout (2 columns)
        # Prevent Sidebar from expanding during long language values
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0, minsize=45) # Topbar
        self.grid_rowconfigure(1, weight=1) # Main Content

        self._create_topbar()
        self._create_sidebar()
        
        # Container for swappable frames (Wizard Steps & Settings)
        self.container_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.container_frame.grid(row=1, column=1, sticky="nsew", padx=30, pady=25)
        self.container_frame.grid_columnconfigure(0, weight=1)
        self.container_frame.grid_rowconfigure(0, weight=1)

        self._create_step1_paths()
        self._create_step2_filters()
        self._create_step3_options()
        self._create_step4_analyzer()
        self._create_step5_execution()
        self._create_step6_comparison()
        self._create_settings_frame()
        
        self.migrator_thread = None
        self.analyzer_thread = None
        self.show_step(1)

    def change_language(self, choice):
        self.i18n.set_language(choice)
        self._ = self.i18n._
        self._update_all_texts()
        self.save_settings()

    def _update_all_texts(self):
        # Window & Topbar
        self.title(self._("app_title"))
        self.btn_settings.configure(text="⚙")
        
        # Sidebar
        self.logo_label.configure(text=self._("logo_title"))
        self.lbl_menu.configure(text=self._("lbl_menu"))
        self.btn_step1.configure(text=self._("step_1", default="1. Select Folders"))
        self.btn_step2.configure(text=self._("step_2", default="2. Filters & Exceptions"))
        self.btn_step3.configure(text=self._("step_3", default="3. Migration Rules"))
        self.btn_step4.configure(text=self._("step_4", default="4. Analisador Pré-Migração"))
        self.btn_step5.configure(text=self._("step_5", default="5. Execution & Output"))
        self.btn_step6.configure(text=self._("step_6", default="6. Diff Viewer"))
        self.lbl_user_title.configure(text=self._("user_title"))
        self.lbl_user_sub.configure(text=self._("user_sub"))
        
        # Step 1: Paths & Modes
        self.header_label_1.configure(text=self._("step_1", default="1. Select Folders"))
        self.lbl_src_title.configure(text=self._("card_src_title"))
        self.lbl_src_sub.configure(text=self._("card_src_sub"))
        self.btn_source.configure(text=self._("btn_browse"))
        self.lbl_dst_title.configure(text=self._("card_dst_title"))
        self.lbl_dst_sub.configure(text=self._("card_dst_sub"))
        self.btn_dest.configure(text=self._("btn_browse"))
        self.lbl_mode.configure(text=self._("mode_lbl"))
        
        self.combo_mode.configure(values=[self._("mode_extract"), self._("mode_inplace")])
        if self.var_mode.get() == "inplace":
            self.combo_mode.set(self._("mode_inplace"))
        else:
            self.combo_mode.set(self._("mode_extract"))
            
        self.btn_next1.configure(text=self._("btn_next", default="Next Step"))
        
        # Step 2: Filters
        try: # Failsafe during init
            self.header_label_2.configure(text=self._("step_2", default="2. Filters & Exceptions"))
            self.lbl_inc.configure(text=self._("lbl_include_only", default="Include ONLY these files"))
            self.lbl_exc.configure(text=self._("lbl_ignore", default="Ignore these files"))
            self.btn_add_inc.configure(text=self._("btn_add", default="Add"))
            self.btn_rem_inc.configure(text=self._("btn_remove", default="Remove"))
            self.btn_add_exc.configure(text=self._("btn_add", default="Add"))
            self.btn_rem_exc.configure(text=self._("btn_remove", default="Remove"))
            self.btn_prev2.configure(text=self._("btn_prev", default="Previous Step"))
            self.btn_next2.configure(text=self._("btn_next", default="Next Step"))
        except AttributeError:
            pass

        # Step 3: Migration Rules (formerly Step 2: Options)
        self.header_label_3.configure(text=self._("step_3", default="3. Migration Rules"))
        self.lbl_options.configure(text=self._("lbl_options"))
        self.chk_utf8.configure(text=self._("chk_utf8"))
        self.chk_scopes.configure(text=self._("chk_scopes"))
        self.chk_advanced.configure(text=self._("chk_advanced"))
        if hasattr(self, 'chk_clean_dir'):
            self.chk_clean_dir.configure(text=self._("chk_clean_dir", default="Limpar diretório de destino antes de iniciar"))
        
        # Update New Database Option & Sub-options
        self.chk_db_main.configure(text=self._("chk_db_main"))
        self.chk_db_bde.configure(text="BDE \u2192 FireDAC")
        self.chk_db_dbx.configure(text="DBExpress \u2192 FireDAC")
        self.chk_db_ibx.configure(text="IBX \u2192 FireDAC")
        self.chk_db_ado.configure(text="ADO \u2192 FireDAC")
        self.chk_db_cds.configure(text="ClientDataSet \u2192 FireDAC")
            
        self.btn_prev3.configure(text=self._("btn_prev", default="Previous Step"))
        self.btn_next3.configure(text=self._("btn_next", default="Next Step"))

        # Update Analyzer View
        self.header_label_4.configure(text=self._("step_4", default="4. Analisador Pré-Migração"))
        self.btn_run_analyzer.configure(text=self._("btn_run_analyzer", default="Executar Análise de Impacto"))
        self.btn_prev_analyzer.configure(text=self._("btn_prev", default="Previous Step"))
        self.btn_next_analyzer.configure(text=self._("btn_next", default="Next Step"))
        
        # Step 5: Execution
        self.header_label_5.configure(text=self._("step_5", default="5. Execution & Output"))
        self.chk_precompile.configure(text=self._("chk_precompile"))
        
        try: # Failsafe during init
            self.lbl_console.configure(text=self._("step_5_console", default="Execution Output (Verbose)"))
        except AttributeError:
            pass 
        
        if self.migrator_thread is None or not self.migrator_thread.is_alive():
            self.btn_start.configure(text=self._("btn_start_ready"))
        else:
            self.btn_start.configure(text=self._("btn_start_busy"))

        if hasattr(self, 'btn_log_actions'):
            self.btn_log_actions.configure(
                values=[self._("log_action_copy", default="Copiar Log"), self._("log_action_save", default="Salvar Log..."), self._("log_action_clear", default="Limpar Log")]
            )
            # CTkOptionMenu string trace override hack to reset title
            self.btn_log_actions.set(self._("log_action_options", default="⏬ Ações"))
            
        self.btn_prev5.configure(text=self._("btn_prev", default="Previous Step"))
        self.btn_next5.configure(text=self._("btn_next", default="Next Step"))

        # Step 6: Diff Viewer
        try:
            self.header_label_6.configure(text=self._("step_6", default="6. Diff Viewer"))
            self.btn_prev6.configure(text=self._("btn_prev", default="Previous Step"))
        except AttributeError:
            pass
            
        # Settings
        self.lbl_settings_title.configure(text=self._("nav_settings").strip())
        self.lbl_lang_select.configure(text=self._("lbl_lang_select"))

    def _create_topbar(self):
        self.topbar_frame = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color=BG_MAIN)
        self.topbar_frame.grid(row=0, column=1, sticky="ew")
        self.topbar_frame.grid_columnconfigure(0, weight=1)
        
        self.btn_settings = ctk.CTkButton(self.topbar_frame, text="⚙", width=40, height=40, font=ctk.CTkFont(size=20), fg_color="transparent", text_color=COLOR_SECONDARY, hover_color=BG_INPUT, command=self.show_settings)
        self.btn_settings.grid(row=0, column=1, padx=20, pady=5, sticky="e")

    def show_step(self, step_number):
        self.settings_frame.grid_forget()
        self.frame_step1.grid_forget()
        self.frame_step2.grid_forget()
        self.frame_step3.grid_forget()
        self.frame_step4.grid_forget()
        self.frame_step5.grid_forget()
        self.frame_step6.grid_forget()
        
        self.btn_step1.configure(fg_color="transparent", text_color=COLOR_SECONDARY)
        self.btn_step2.configure(fg_color="transparent", text_color=COLOR_SECONDARY)
        self.btn_step3.configure(fg_color="transparent", text_color=COLOR_SECONDARY)
        self.btn_step4.configure(fg_color="transparent", text_color=COLOR_SECONDARY)
        self.btn_step5.configure(fg_color="transparent", text_color=COLOR_SECONDARY)
        self.btn_step6.configure(fg_color="transparent", text_color=COLOR_SECONDARY)

        if step_number == 1:
            self.frame_step1.grid(row=0, column=0, sticky="nsew")
            self.btn_step1.configure(fg_color=BG_INPUT, text_color=COLOR_PRIMARY)
        elif step_number == 2:
            self.frame_step2.grid(row=0, column=0, sticky="nsew")
            self.btn_step2.configure(fg_color=BG_INPUT, text_color=COLOR_PRIMARY)
        elif step_number == 3:
            self.frame_step3.grid(row=0, column=0, sticky="nsew")
            self.btn_step3.configure(fg_color=BG_INPUT, text_color=COLOR_PRIMARY)
        elif step_number == 4:
            self.frame_step4.grid(row=0, column=0, sticky="nsew")
            self.btn_step4.configure(fg_color=BG_INPUT, text_color=COLOR_PRIMARY)
        elif step_number == 5:
            self.frame_step5.grid(row=0, column=0, sticky="nsew")
            self.btn_step5.configure(fg_color=BG_INPUT, text_color=COLOR_PRIMARY)
        elif step_number == 6:
            self.frame_step6.grid(row=0, column=0, sticky="nsew")
            self.btn_step6.configure(fg_color=BG_INPUT, text_color=COLOR_PRIMARY)
            self._refresh_diff_tree()

    def show_settings(self):
        self.frame_step1.grid_forget()
        self.frame_step2.grid_forget()
        self.frame_step3.grid_forget()
        self.frame_step4.grid_forget()
        self.frame_step5.grid_forget()
        self.frame_step6.grid_forget()
        self.settings_frame.grid(row=0, column=0, sticky="nsew")

    def _create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=BG_SIDEBAR)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)
        self.sidebar_frame.grid_propagate(False)

        # Brand Logo (Image + Text)
        self.logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=25, pady=(40, 50), sticky="w")
        
        try:
            import sys
            if hasattr(sys, '_MEIPASS'):
                logo_path = os.path.join(sys._MEIPASS, 'src', 'assets', 'logo_transparent.png')
            else:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'logo_transparent.png')
                
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                    dark_image=Image.open(logo_path),
                                    size=(32, 32))
            self.logo_icon = ctk.CTkLabel(self.logo_frame, image=logo_img, text="")
            self.logo_icon.pack(side="left", padx=(0, 10))
        except Exception:
            pass

        self.logo_label = ctk.CTkLabel(self.logo_frame, text=self._("logo_title"), font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color=COLOR_PRIMARY)
        self.logo_label.pack(side="left")

        # Step-by-Step Navigation Menu
        self.lbl_menu = ctk.CTkLabel(self.sidebar_frame, text=self._("lbl_menu"), font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=COLOR_SECONDARY)
        self.lbl_menu.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="w")

        self.btn_step1 = ctk.CTkButton(self.sidebar_frame, text=self._("step_1", default="1. Select Folders"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=lambda: self.show_step(1))
        self.btn_step1.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_step2 = ctk.CTkButton(self.sidebar_frame, text=self._("step_2", default="2. Filters & Exceptions"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=lambda: self.show_step(2))
        self.btn_step2.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.btn_step3 = ctk.CTkButton(self.sidebar_frame, text=self._("step_3", default="3. Migration Rules"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=lambda: self.show_step(3))
        self.btn_step3.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        self.btn_step4 = ctk.CTkButton(self.sidebar_frame, text=self._("step_4", default="4. Analisador Pré-Migração"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=lambda: self.show_step(4))
        self.btn_step4.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        self.btn_step5 = ctk.CTkButton(self.sidebar_frame, text=self._("step_5", default="5. Execution & Output"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=lambda: self.show_step(5))
        self.btn_step5.grid(row=6, column=0, padx=20, pady=8, sticky="ew")

        self.btn_step6 = ctk.CTkButton(self.sidebar_frame, text=self._("step_6", default="6. Diff Viewer"), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color=COLOR_SECONDARY, anchor="w", height=45, hover_color=BG_INPUT, command=lambda: self.show_step(6))
        self.btn_step6.grid(row=7, column=0, padx=20, pady=8, sticky="ew")

        # Bottom Mini-Player / Profile mimic
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color=BG_INPUT, corner_radius=16)
        self.profile_frame.grid(row=9, column=0, padx=20, pady=30, sticky="ew")
        
        self.lbl_user_title = ctk.CTkLabel(self.profile_frame, text=self._("user_title"), font=ctk.CTkFont(size=14, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_user_title.pack(padx=15, pady=(15, 0), anchor="w")
        self.lbl_user_sub = ctk.CTkLabel(self.profile_frame, text=self._("user_sub"), font=ctk.CTkFont(size=12), text_color=COLOR_SECONDARY)
        self.lbl_user_sub.pack(padx=15, pady=(0, 15), anchor="w")

    def _create_step1_paths(self):
        self.frame_step1 = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.frame_step1.grid_columnconfigure((0, 1), weight=1)

        # Header Title
        self.header_label_1 = ctk.CTkLabel(self.frame_step1, text=self._("step_1", default="1. Select Folders"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label_1.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 40))

        # Vertical Stacked Cards
        self.card_source = ctk.CTkFrame(self.frame_step1, fg_color=CARD_1, corner_radius=16, height=130)
        self.card_source.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.card_source.grid_propagate(False)

        self.lbl_src_title = ctk.CTkLabel(self.card_source, text=self._("card_src_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFFFFF")
        self.lbl_src_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.lbl_src_sub = ctk.CTkLabel(self.card_source, text=self._("card_src_sub"), font=ctk.CTkFont(size=12), text_color="#E0E0FF")
        self.lbl_src_sub.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        ent_source = ctk.CTkEntry(self.card_source, textvariable=self.source_dir, fg_color="#4343D9", border_width=0, text_color="#FFFFFF", height=36, corner_radius=8)
        ent_source.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(0, 15))
        self.card_source.grid_columnconfigure(0, weight=1)

        self.btn_source = ctk.CTkButton(self.card_source, text=self._("btn_browse"), command=self.browse_source, fg_color="#FFFFFF", text_color=CARD_1, hover_color="#E0E0FF", font=ctk.CTkFont(weight="bold", size=13), corner_radius=8, height=36, width=40)
        self.btn_source.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=(0, 15))

        self.card_dest = ctk.CTkFrame(self.frame_step1, fg_color=CARD_2, corner_radius=16, height=130)
        self.card_dest.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.card_dest.grid_propagate(False)

        self.lbl_dst_title = ctk.CTkLabel(self.card_dest, text=self._("card_dst_title"), font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFFFFF")
        self.lbl_dst_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.lbl_dst_sub = ctk.CTkLabel(self.card_dest, text=self._("card_dst_sub"), font=ctk.CTkFont(size=12), text_color="#FFE0D0")
        self.lbl_dst_sub.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        ent_dest = ctk.CTkEntry(self.card_dest, textvariable=self.dest_dir, fg_color="#D97A53", border_width=0, text_color="#FFFFFF", height=36, corner_radius=8)
        ent_dest.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(0, 15))
        self.card_dest.grid_columnconfigure(0, weight=1)

        self.btn_dest = ctk.CTkButton(self.card_dest, text=self._("btn_browse"), command=self.browse_dest, fg_color="#FFFFFF", text_color=CARD_2, hover_color="#FFE0D0", font=ctk.CTkFont(weight="bold", size=13), corner_radius=8, height=36, width=40)
        self.btn_dest.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=(0, 15))

        # Operation Mode
        default_mode = self.app_settings.get("op_mode", self._("mode_extract"))
        if default_mode == "extract": default_mode = self._("mode_extract")
        if default_mode == "inplace": default_mode = self._("mode_inplace")
        
        self.var_mode = ctk.StringVar(value=default_mode)
        self.var_mode.trace_add("write", lambda *_: self._toggle_destination_card())

        mode_frame = ctk.CTkFrame(self.frame_step1, fg_color="transparent")
        mode_frame.grid(row=3, column=0, columnspan=2, sticky="nw", pady=(15, 0))
        
        self.lbl_mode = ctk.CTkLabel(mode_frame, text=self._("mode_lbl"), font=ctk.CTkFont(weight="bold", size=15), text_color=COLOR_PRIMARY)
        self.lbl_mode.pack(side="left", padx=(0, 10))
        
        self.combo_mode = ctk.CTkOptionMenu(mode_frame, variable=self.var_mode, values=[self._("mode_extract"), self._("mode_inplace")], fg_color=BG_INPUT, button_color="#2A2A35", text_color=COLOR_PRIMARY, width=280)
        self.combo_mode.pack(side="left")

        # Spacer to push navigation to bottom
        self.frame_step1.grid_rowconfigure(4, weight=1)

        # Step Navigation
        self.step_nav1 = ctk.CTkFrame(self.frame_step1, fg_color="transparent")
        self.step_nav1.grid(row=5, column=0, columnspan=2, sticky="sew", pady=(20, 0))
        
        self.btn_next1 = ctk.CTkButton(self.step_nav1, text=self._("btn_next", default="Next Step"), command=lambda: self.show_step(2), font=ctk.CTkFont(size=14, weight="bold"), fg_color=CARD_1, hover_color="#8080FF", height=40)
        self.btn_next1.pack(side="right")
        
        self._toggle_destination_card()

    def _create_step2_filters(self):
        self.frame_step2 = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.frame_step2.grid_columnconfigure(0, weight=1)
        self.frame_step2.grid_columnconfigure(1, weight=1)
        self.frame_step2.grid_rowconfigure(2, weight=1)
        self.frame_step2.grid_rowconfigure(5, weight=1)

        self.header_label_2 = ctk.CTkLabel(self.frame_step2, text=self._("step_2", default="2. Filters & Exceptions"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label_2.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 40))

        # Load Default Ignores if empty
        if not self.app_settings.get("ignore_filters"):
            self.ignore_filters_list = ["*.~pas", "*.~dfm", "*.dcu", "*.identcache", "*.local", "*.stat", "__history/"]
        else:
            self.ignore_filters_list = list(self.app_settings.get("ignore_filters", []))
            
        self.include_filters_list = list(self.app_settings.get("include_filters", []))

        # --- INCLUDE LIST ---
        self.lbl_inc = ctk.CTkLabel(self.frame_step2, text=self._("lbl_include_only", default="Include ONLY these files"), font=ctk.CTkFont(weight="bold", size=15), text_color=COLOR_PRIMARY)
        self.lbl_inc.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.scroll_include = ctk.CTkScrollableFrame(self.frame_step2, width=300, height=120, fg_color=BG_INPUT, border_width=1, border_color="#333344")
        self.scroll_include.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        
        # Include Toolbar
        inc_toolbar = ctk.CTkFrame(self.frame_step2, fg_color="transparent")
        inc_toolbar.grid(row=3, column=0, sticky="ew", pady=(5, 20))
        
        self.btn_add_inc = ctk.CTkButton(inc_toolbar, text=self._("btn_add", default="Add"), width=80, fg_color=CARD_1, hover_color="#8080FF", command=lambda: self._add_filter_gui(self.include_filters_list, self.scroll_include))
        self.btn_add_inc.pack(side="left", padx=(0, 5))

        # --- IGNORE LIST ---
        self.lbl_exc = ctk.CTkLabel(self.frame_step2, text=self._("lbl_ignore", default="Ignore these files"), font=ctk.CTkFont(weight="bold", size=15), text_color=COLOR_PRIMARY)
        self.lbl_exc.grid(row=1, column=1, sticky="w", pady=(0, 5))
        
        self.scroll_ignore = ctk.CTkScrollableFrame(self.frame_step2, width=300, height=120, fg_color=BG_INPUT, border_width=1, border_color="#333344")
        self.scroll_ignore.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        
        # Ignore Toolbar
        exc_toolbar = ctk.CTkFrame(self.frame_step2, fg_color="transparent")
        exc_toolbar.grid(row=3, column=1, sticky="ew", pady=(5, 20), padx=(10, 0))
        
        self.btn_add_exc = ctk.CTkButton(exc_toolbar, text=self._("btn_add", default="Add"), width=80, fg_color=CARD_1, hover_color="#8080FF", command=lambda: self._add_filter_gui(self.ignore_filters_list, self.scroll_ignore))
        self.btn_add_exc.pack(side="left", padx=(0, 5))
        
        self._render_filter_list(self.include_filters_list, self.scroll_include)
        self._render_filter_list(self.ignore_filters_list, self.scroll_ignore)

        # Step Navigation Row (Bottom)
        self.step_nav2 = ctk.CTkFrame(self.frame_step2, fg_color="transparent")
        self.step_nav2.grid(row=4, column=0, columnspan=2, sticky="sew", pady=(20, 0))
        
        self.btn_prev2 = ctk.CTkButton(self.step_nav2, text=self._("btn_prev", default="Previous Step"), command=lambda: self.show_step(1), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", border_width=1, border_color=COLOR_SECONDARY, text_color=COLOR_SECONDARY, hover_color=BG_INPUT, height=40)
        self.btn_prev2.pack(side="left")
        
        self.btn_next2 = ctk.CTkButton(self.step_nav2, text=self._("btn_next", default="Next Step"), command=lambda: self.show_step(3), font=ctk.CTkFont(size=14, weight="bold"), fg_color=CARD_1, hover_color="#8080FF", height=40)
        self.btn_next2.pack(side="right")

    def _render_filter_list(self, data_list, scroll_frame):
        for widget in scroll_frame.winfo_children():
            widget.destroy()
            
        for idx, item in enumerate(data_list):
            item_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=0)
            
            lbl = ctk.CTkLabel(item_frame, text=item, text_color="#FFFFFF", anchor="w", font=ctk.CTkFont(size=12))
            lbl.pack(side="left", padx=(5, 0), pady=4)
            
            btn_del = ctk.CTkButton(item_frame, text="X", width=24, height=24, fg_color="transparent", hover_color="#D94343", text_color="#A4A4B5", command=lambda l=data_list, f=scroll_frame, i=idx: self._rem_filter_gui(l, f, i))
            btn_del.pack(side="right", padx=(5, 5))
            
            btn_edit = ctk.CTkButton(item_frame, text="✎", width=24, height=24, fg_color="transparent", hover_color="#5555AA", text_color="#A4A4B5", command=lambda l=data_list, f=scroll_frame, i=idx: self._edit_filter_gui(l, f, i))
            btn_edit.pack(side="right", padx=(5, 0))
            
            # Divider line below the item
            divider = ctk.CTkFrame(scroll_frame, height=1, fg_color="#4A4A5A")
            divider.pack(fill="x", pady=(0, 2))

    def _add_filter_gui(self, data_list, scroll_frame):
        dialog = ctk.CTkInputDialog(text=self._("msg_add_filter", default="Type the wildcard pattern:"), title=self._("title_add_filter", default="Add"))
        new_val = dialog.get_input()
        if new_val and new_val.strip():
            val = new_val.strip()
            if val not in data_list:
                data_list.append(val)
                self._render_filter_list(data_list, scroll_frame)
                self.save_settings()

    def _edit_filter_gui(self, data_list, scroll_frame, index):
        if 0 <= index < len(data_list):
            old_val = data_list[index]
            dialog = ctk.CTkInputDialog(text=self._("msg_add_filter", default="Type the wildcard pattern:"), title=self._("title_edit_filter", default="Edit Filter"))
            # Pre-fill isn't natively supported in CTkInputDialog cleanly without hacks, so user will be asked to re-type or we hope they know what they are editing. Let's try to pass the text to it if it supports it, else standard.
            new_val = dialog.get_input()
            if new_val and new_val.strip() and new_val.strip() != old_val:
                val = new_val.strip()
                if val not in data_list:
                    data_list[index] = val
                    self._render_filter_list(data_list, scroll_frame)
                    self.save_settings()

    def _rem_filter_gui(self, data_list, scroll_frame, index):
        if 0 <= index < len(data_list):
            data_list.pop(index)
            self._render_filter_list(data_list, scroll_frame)
            self.save_settings()

    def _create_step3_options(self): # Formerly _create_step2_options
        self.frame_step3 = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.frame_step3.grid_columnconfigure(0, weight=1)

        self.header_label_3 = ctk.CTkLabel(self.frame_step3, text=self._("step_3", default="3. Migration Rules"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label_3.grid(row=0, column=0, sticky="w", pady=(0, 40))

        self.lbl_options = ctk.CTkLabel(self.frame_step3, text=self._("lbl_options"), font=ctk.CTkFont(family="Inter", size=20, weight="bold"), text_color=COLOR_PRIMARY)
        self.lbl_options.grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.options_frame = ctk.CTkFrame(self.frame_step3, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, sticky="nsew")

        self.var_utf8 = ctk.BooleanVar(value=self.app_settings.get("utf8", True))
        
        # Main Database Toggle
        self.var_db_main = ctk.BooleanVar(value=self.app_settings.get("db_main", True))
        
        # Sub-Technologies Toggles
        self.var_bde = ctk.BooleanVar(value=self.app_settings.get("bde", True))
        self.var_dbx = ctk.BooleanVar(value=self.app_settings.get("dbx", False))
        self.var_ibx = ctk.BooleanVar(value=self.app_settings.get("ibx", False))
        self.var_ado = ctk.BooleanVar(value=self.app_settings.get("ado", False))
        self.var_cds = ctk.BooleanVar(value=self.app_settings.get("cds", False))
        
        self.var_scopes = ctk.BooleanVar(value=self.app_settings.get("scopes", True))
        self.var_advanced = ctk.BooleanVar(value=self.app_settings.get("advanced", True))
        self.var_clean_dir = ctk.BooleanVar(value=self.app_settings.get("clean_dir", False))

        chk_font = ctk.CTkFont(size=14)
        kwargs = {"text_color": COLOR_SECONDARY, "fg_color": "#101014", "font": chk_font, "border_width": 2, "border_color": "#2A2A35", "checkbox_width": 24, "checkbox_height": 24, "hover_color": "#2A2A35"}
        
        self.chk_clean_dir = ctk.CTkCheckBox(self.options_frame, text=self._("chk_clean_dir", default="Limpar diretório de destino antes de iniciar"), variable=self.var_clean_dir, **kwargs)
        self.chk_clean_dir.pack(anchor="w", pady=(0, 15))
        
        self.chk_utf8 = ctk.CTkCheckBox(self.options_frame, text=self._("chk_utf8"), variable=self.var_utf8, **kwargs)
        self.chk_utf8.pack(anchor="w", pady=(0, 15))
        
        self.chk_scopes = ctk.CTkCheckBox(self.options_frame, text=self._("chk_scopes"), variable=self.var_scopes, **kwargs)
        self.chk_scopes.pack(anchor="w", pady=(0, 15))
        
        self.chk_advanced = ctk.CTkCheckBox(self.options_frame, text=self._("chk_advanced"), variable=self.var_advanced, **kwargs)
        self.chk_advanced.pack(anchor="w", pady=(0, 15))
        
        # Data Access Migration Container
        self.chk_db_main = ctk.CTkCheckBox(self.options_frame, text=self._("chk_db_main", default="Migrar tecnologias de acesso a dados legadas para FireDAC"), variable=self.var_db_main, command=self._toggle_db_sub_options, **kwargs)
        self.chk_db_main.pack(anchor="w", pady=(15, 5))
        
        self.db_sub_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.db_sub_frame.pack(anchor="w", fill="x", padx=(30, 0), pady=(0, 15))
        
        sub_kwargs = kwargs.copy()
        sub_kwargs["checkbox_width"] = 18
        sub_kwargs["checkbox_height"] = 18
        sub_kwargs["font"] = ctk.CTkFont(size=13)
        
        self.chk_db_bde = ctk.CTkCheckBox(self.db_sub_frame, text="BDE \u2192 FireDAC", variable=self.var_bde, **sub_kwargs)
        self.chk_db_bde.pack(anchor="w", pady=(0, 8))
        self.chk_db_dbx = ctk.CTkCheckBox(self.db_sub_frame, text="DBExpress \u2192 FireDAC", variable=self.var_dbx, **sub_kwargs)
        self.chk_db_dbx.pack(anchor="w", pady=(0, 8))
        self.chk_db_ibx = ctk.CTkCheckBox(self.db_sub_frame, text="IBX \u2192 FireDAC", variable=self.var_ibx, **sub_kwargs)
        self.chk_db_ibx.pack(anchor="w", pady=(0, 8))
        self.chk_db_ado = ctk.CTkCheckBox(self.db_sub_frame, text="ADO \u2192 FireDAC", variable=self.var_ado, **sub_kwargs)
        self.chk_db_ado.pack(anchor="w", pady=(0, 8))
        self.chk_db_cds = ctk.CTkCheckBox(self.db_sub_frame, text="ClientDataSet \u2192 FireDAC", variable=self.var_cds, **sub_kwargs)
        self.chk_db_cds.pack(anchor="w", pady=(0, 8))

        # Initial toggle enforcement
        self._toggle_db_sub_options()


        # Spacer to push navigation to bottom
        self.frame_step3.grid_rowconfigure(3, weight=1)

        # Step Navigation
        self.step_nav3 = ctk.CTkFrame(self.frame_step3, fg_color="transparent")
        self.step_nav3.grid(row=4, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev3 = ctk.CTkButton(self.step_nav3, text=self._("btn_prev", default="Previous Step"), command=lambda: self.show_step(2), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", border_width=1, border_color=COLOR_SECONDARY, text_color=COLOR_SECONDARY, hover_color=BG_INPUT, height=40)
        self.btn_prev3.pack(side="left")
        
        self.btn_next3 = ctk.CTkButton(self.step_nav3, text=self._("btn_next", default="Next Step"), command=lambda: self.show_step(4), font=ctk.CTkFont(size=14, weight="bold"), fg_color=CARD_1, hover_color="#8080FF", height=40)
        self.btn_next3.pack(side="right")

    def _toggle_db_sub_options(self):
        state = "normal" if self.var_db_main.get() else "disabled"
        self.chk_db_bde.configure(state=state)
        self.chk_db_dbx.configure(state=state)
        self.chk_db_ibx.configure(state=state)
        self.chk_db_ado.configure(state=state)
        self.chk_db_cds.configure(state=state)

    def _create_step4_analyzer(self):
        self.frame_step4 = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.frame_step4.grid_columnconfigure(0, weight=1)
        self.frame_step4.grid_rowconfigure(2, weight=1)

        self.header_label_4 = ctk.CTkLabel(self.frame_step4, text=self._("step_4", default="4. Analisador Pré-Migração"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label_4.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Action Top Section
        self.analyzer_action_frame = ctk.CTkFrame(self.frame_step4, fg_color="transparent")
        self.analyzer_action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.analyzer_action_frame.grid_columnconfigure(1, weight=1)

        self.btn_run_analyzer = ctk.CTkButton(self.analyzer_action_frame, text=self._("btn_run_analyzer", default="Executar Análise de Impacto"), command=self._run_analyzer, font=ctk.CTkFont(size=14, weight="bold"), fg_color=COLOR_PRIMARY, text_color=BG_MAIN, hover_color="#E5E5E5", corner_radius=16, height=40)
        self.btn_run_analyzer.pack(side="left")

        # Console Section
        self.analyzer_console_frame = ctk.CTkFrame(self.frame_step4, fg_color="transparent")
        self.analyzer_console_frame.grid(row=2, column=0, sticky="nsew")
        self.analyzer_console_frame.grid_rowconfigure(0, weight=1)
        self.analyzer_console_frame.grid_columnconfigure(0, weight=1)

        self.analyzer_log_textbox = ctk.CTkTextbox(self.analyzer_console_frame, fg_color="#101014", text_color="#A4A4B5", corner_radius=12, font=ctk.CTkFont(family="Consolas", size=13), border_width=2, border_color="#2A2A35")
        self.analyzer_log_textbox.grid(row=0, column=0, sticky="nsew")
        self.analyzer_log_textbox.insert("end", "Clique em 'Executar Análise' para varrer o projeto de origem e gerar estatísticas de estimativa de migração.\n")
        self.analyzer_log_textbox.configure(state="disabled")

        # Step Navigation Row (Bottom)
        self.step_nav_analyzer = ctk.CTkFrame(self.frame_step4, fg_color="transparent")
        self.step_nav_analyzer.grid(row=3, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev_analyzer = ctk.CTkButton(self.step_nav_analyzer, text=self._("btn_prev", default="Previous Step"), command=lambda: self.show_step(3), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", border_width=1, border_color=COLOR_SECONDARY, text_color=COLOR_SECONDARY, hover_color=BG_INPUT, height=40)
        self.btn_prev_analyzer.pack(side="left")
        
        self.btn_next_analyzer = ctk.CTkButton(self.step_nav_analyzer, text=self._("btn_next", default="Next Step"), command=lambda: self.show_step(5), font=ctk.CTkFont(size=14, weight="bold"), fg_color=COLOR_PRIMARY, text_color=BG_MAIN, hover_color="#E5E5E5", corner_radius=16, height=40, width=200)
        self.btn_next_analyzer.pack(side="right")

    def _run_analyzer(self):
        src_path = self.source_dir.get() # Use source_dir from step 1
        if not src_path or not os.path.exists(src_path):
            messagebox.showerror("Erro", self._("msg_bad_source", default="A pasta de origem não existe."))
            return
            
        self.analyzer_log_textbox.configure(state="normal")
        self.analyzer_log_textbox.delete("1.0", "end")
        self.btn_run_analyzer.configure(state="disabled", text="Analisando...")
        self.update()
        
        def analyzer_worker():
            def ui_log(msg):
                self.analyzer_log_textbox.insert("end", msg + "\n")
                self.analyzer_log_textbox.yview_moveto(1.0)
            
            analyzer = ProjectAnalyzer(src_path, ui_log)
            analyzer.run_analysis()
            
            # Re-enable UI
            def _done():
                self.analyzer_log_textbox.configure(state="disabled")
                self.btn_run_analyzer.configure(state="normal", text=self._("btn_run_analyzer", default="Executar Análise de Impacto"))
            self.after(0, _done)
            
        self.analyzer_thread = threading.Thread(target=analyzer_worker, daemon=True)
        self.analyzer_thread.start()

    def _create_step5_execution(self): # Formerly _create_step3_execution
        self.frame_step5 = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.frame_step5.grid_columnconfigure(0, weight=1)
        self.frame_step5.grid_rowconfigure(2, weight=1)

        self.header_label_5 = ctk.CTkLabel(self.frame_step5, text=self._("step_5", default="5. Execution & Output"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label_5.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Action Top Section
        self.action_frame = ctk.CTkFrame(self.frame_step5, fg_color="transparent")
        self.action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.action_frame.grid_columnconfigure(1, weight=1)

        self.var_precompile = ctk.BooleanVar(value=self.app_settings.get("precompile", False))
        
        kwargs = {"text_color": COLOR_SECONDARY, "fg_color": "#101014", "font": ctk.CTkFont(size=14), "border_width": 2, "border_color": "#2A2A35", "checkbox_width": 24, "checkbox_height": 24, "hover_color": "#2A2A35"}
        self.chk_precompile = ctk.CTkCheckBox(self.action_frame, text=self._("chk_precompile"), variable=self.var_precompile, **kwargs)
        self.chk_precompile.pack(side="left")

        # Console Section
        self.console_frame = ctk.CTkFrame(self.frame_step5, fg_color="transparent")
        self.console_frame.grid(row=2, column=0, sticky="nsew")
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.log_header_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.log_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.lbl_console = ctk.CTkLabel(self.log_header_frame, text=self._("step_5_console", default="Execution Output (Verbose)"), font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color=COLOR_SECONDARY)
        self.lbl_console.pack(side="left")

        self.btn_log_actions = ctk.CTkOptionMenu(
            self.log_header_frame, 
            values=[self._("log_action_copy", default="Copiar Log"), self._("log_action_save", default="Salvar Log..."), self._("log_action_clear", default="Limpar Log")],
            command=self._handle_log_action,
            width=120, height=28,
            fg_color="#101014", button_color="#2A2A35", button_hover_color="#4A4A55", text_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_log_actions.pack(side="right")
        self.btn_log_actions.set(self._("log_action_options", default="⏬ Ações"))

        self.log_textbox = ctk.CTkTextbox(self.console_frame, fg_color="#101014", text_color="#A4A4B5", corner_radius=12, font=ctk.CTkFont(family="Consolas", size=13), border_width=2, border_color="#2A2A35")
        self.log_textbox.grid(row=1, column=0, sticky="nsew")
        self.log_textbox.insert("end", self._("log_ready") + "\n")
        self.log_textbox.configure(state="disabled")
        
        # --- PROGRESS BAR ROW ---
        self.progress_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.lbl_progress = ctk.CTkLabel(self.progress_frame, text="0% - Aguardando...", font=ctk.CTkFont(size=11), text_color=COLOR_SECONDARY)
        self.lbl_progress.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, corner_radius=4, progress_color=COLOR_PRIMARY, fg_color="#2A2A35")
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0) # start empty

        # Step Navigation Row (Bottom)
        self.step_nav5 = ctk.CTkFrame(self.frame_step5, fg_color="transparent")
        self.step_nav5.grid(row=3, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev5 = ctk.CTkButton(self.step_nav5, text=self._("btn_prev", default="Previous Step"), command=lambda: self.show_step(4), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", border_width=1, border_color=COLOR_SECONDARY, text_color=COLOR_SECONDARY, hover_color=BG_INPUT, height=40)
        self.btn_prev5.pack(side="left")
        
        self.btn_start = ctk.CTkButton(self.step_nav5, text=self._("btn_start_ready"), command=self.start_migration, font=ctk.CTkFont(size=16, weight="bold"), fg_color=COLOR_PRIMARY, text_color=BG_MAIN, hover_color="#E5E5E5", corner_radius=16, height=40, width=200)
        self.btn_start.pack(side="right")
        
        # Save Triggers
        self.var_precompile.trace_add("write", lambda *_: self.save_settings())

    def _handle_log_action(self, choice):
        # Reset the menu title so it still says "Actions" instead of keeping the selection text
        self.btn_log_actions.set(self._("log_action_options", default="⏬ Ações"))
        if choice == self._("log_action_copy", default="Copiar Log"):
            self._copy_log()
        elif choice == self._("log_action_save", default="Salvar Log..."):
            self._save_log()
        elif choice == self._("log_action_clear", default="Limpar Log"):
            self._clear_log()

    def _copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_textbox.get("1.0", "end"))
        self.log_callback(self._("msg_log_copied", default="✅ Log copiado para a área de transferência com sucesso."))

    def _save_log(self):
        filepath = ctk.filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("Log Files", "*.log"), ("All Files", "*.*")],
            title="Salvar Log"
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.log_textbox.get("1.0", "end"))
                self.log_callback(f"✅ {self._('msg_log_saved', default='Log salvo em:')} {filepath}")
            except Exception as e:
                self.log_callback(f"❌ Erro ao salvar log: {str(e)}")

    def _clear_log(self):
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

    def _create_step6_comparison(self):
        self.frame_step6 = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.frame_step6.grid_columnconfigure(0, weight=1)
        self.frame_step6.grid_rowconfigure(2, weight=1)

        self.header_label_6 = ctk.CTkLabel(self.frame_step6, text=self._("step_6", default="6. Diff Viewer"), font=ctk.CTkFont(family="Inter", size=36, weight="bold"), text_color=COLOR_PRIMARY)
        self.header_label_6.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Diff View Actions (Load)
        self.diff_action_frame = ctk.CTkFrame(self.frame_step6, fg_color="transparent")
        self.diff_action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.diff_action_frame.grid_columnconfigure(1, weight=1)

        self.btn_refresh_diff = ctk.CTkButton(self.diff_action_frame, text="Recarregar Diferenças", font=ctk.CTkFont(weight="bold"), fg_color="#2A2A35", text_color=COLOR_PRIMARY, hover_color="#4A4A55", command=self._refresh_diff_tree)
        self.btn_refresh_diff.pack(side="left")
        
        self.lbl_diff_status = ctk.CTkLabel(self.diff_action_frame, text="", text_color=COLOR_SECONDARY)
        self.lbl_diff_status.pack(side="left", padx=15)

        # Diff Content Section (PanedWindow for Explorer and Two Textboxes)
        import tkinter.ttk as ttk
        self.paned_diff = ttk.PanedWindow(self.frame_step6, orient="horizontal")
        self.paned_diff.grid(row=2, column=0, sticky="nsew")

        # Configurar Estilo do Treeview para combinar com o Dark Theme do CustomTkinter
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#101014",
                        foreground=COLOR_PRIMARY,
                        fieldbackground="#101014",
                        borderwidth=0,
                        font=("Inter", 10))
        style.map('Treeview', background=[('selected', '#2A2A35')])
        style.configure("Treeview.Heading", 
                        background="#2A2A35", 
                        foreground=COLOR_SECONDARY, 
                        borderwidth=0,
                        font=("Inter", 11, "bold"))
        style.map("Treeview.Heading", background=[('active', '#3A3A45')])

        # -- Left: Modern Treeview Explorer --
        self.tree_explorer = ttk.Treeview(self.paned_diff, show='tree')
        self.paned_diff.add(self.tree_explorer, weight=1)
        self.tree_explorer.bind('<<TreeviewSelect>>', self._on_tree_select)
        
        # Load directory icons dynamically if possible
        self._folder_icon = "📁 "
        self._file_icon = "📄 "

        # -- Right Side: Double Paned Window for Code --
        self.paned_code = ttk.PanedWindow(self.paned_diff, orient="horizontal")
        self.paned_diff.add(self.paned_code, weight=5) # Much larger for code

        # Text Left (Original)
        self.diff_text_left = ctk.CTkTextbox(self.paned_code, fg_color="#101014", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=13), border_width=1, border_color="#2A2A35", wrap="none")
        self.paned_code.add(self.diff_text_left, weight=1)

        # Text Right (Migrated)
        self.diff_text_right = ctk.CTkTextbox(self.paned_code, fg_color="#101014", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=13), border_width=1, border_color="#2A2A35", wrap="none")
        self.paned_code.add(self.diff_text_right, weight=1)

        # Configure tags for diff
        self.diff_text_left.tag_config("removed", background="#402020", foreground="#FF8080")
        self.diff_text_right.tag_config("added", background="#204020", foreground="#80FF80")
        self.diff_text_left.tag_config("empty", foreground="#606060")
        self.diff_text_right.tag_config("empty", foreground="#606060")

        # Synchronize scrolling
        try:
            def _sync_scroll(*args):
                self.diff_text_left.yview_moveto(args[0])
                self.diff_text_right.yview_moveto(args[0])

            def _on_mousewheel(event):
                # Synchronize mouse wheel scrolling
                self.diff_text_left.yview_scroll(int(-1*(event.delta/120)), "units")
                self.diff_text_right.yview_scroll(int(-1*(event.delta/120)), "units")
                return "break" # Prevent default scrolling behavior

            # Bind mouse wheel manually directly to the internal tkinter Text widget
            self.diff_text_left._textbox.bind("<MouseWheel>", _on_mousewheel)
            self.diff_text_right._textbox.bind("<MouseWheel>", _on_mousewheel)
            
            # Override Scrollbars
            if hasattr(self.diff_text_left, '_scrollbar'):
                self.diff_text_left._scrollbar.configure(command=_sync_scroll)
            if hasattr(self.diff_text_right, '_scrollbar'):
                self.diff_text_right._scrollbar.configure(command=_sync_scroll)
        except Exception:
            pass # Fail smoothly if CTk internals change
        # Navigation
        self.step_nav5 = ctk.CTkFrame(self.frame_step6, fg_color="transparent")
        self.step_nav5.grid(row=3, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev6 = ctk.CTkButton(self.step_nav5, text=self._("btn_prev", default="Previous Step"), command=lambda: self.show_step(5), font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", border_width=1, border_color=COLOR_SECONDARY, text_color=COLOR_SECONDARY, hover_color=BG_INPUT, height=40)
        self.btn_prev6.pack(side="left")

    def _on_tree_select(self, event):
        selected = self.tree_explorer.selection()
        if not selected:
            return
        item_id = selected[0]
        item_type = self.tree_explorer.item(item_id, "values")
        if item_type and item_type[0] == "file":
            dst_path = self.dest_dir.get().strip()
            src_path = self.source_dir.get().strip()
            # Normalize path for all OSes
            d_file = os.path.join(dst_path, item_id.replace('/', os.sep))
            s_file = os.path.join(src_path, item_id.replace('/', os.sep))
            if os.path.exists(s_file) and os.path.exists(d_file):
                self._load_diff(s_file, d_file)

    def _refresh_diff_tree(self):
        for item in self.tree_explorer.get_children():
            self.tree_explorer.delete(item)
            
        src_path = self.source_dir.get().strip()
        dst_path = self.dest_dir.get().strip()
        op_mode = self.var_mode.get()
        if op_mode == "inplace" or op_mode == self._("mode_inplace"):
            self.tree_explorer.insert("", "end", text="Diff view não suportado no modo In-Place.")
            return
            
        if not src_path or not dst_path or not os.path.exists(src_path) or not os.path.exists(dst_path):
            return

        import filecmp
        
        has_items = False
        folders_added = set()
        
        def add_folder_path(rel_dir):
            if rel_dir in folders_added or rel_dir == "." or not rel_dir:
                return
            parts = rel_dir.replace('\\', '/').split('/')
            current_path = ""
            for p in parts:
                parent = current_path
                current_path = f"{current_path}/{p}" if current_path else p
                if current_path not in folders_added:
                    self.tree_explorer.insert(parent, "end", iid=current_path, text="\U0001F4C1 " + p, open=True, values=("folder",))
                    folders_added.add(current_path)

        for root, _, files in os.walk(dst_path):
            for file in files:
                if file.lower().endswith(('.pas', '.dfm', '.dpr')):
                    d_file = os.path.join(root, file)
                    rel_path = os.path.relpath(d_file, dst_path)
                    s_file = os.path.join(src_path, rel_path)
                    
                    if os.path.exists(s_file):
                        if not filecmp.cmp(s_file, d_file, shallow=False):
                            rel_dir = os.path.dirname(rel_path)
                            add_folder_path(rel_dir)
                            
                            parent_id = rel_dir.replace('\\', '/') if rel_dir and rel_dir != "." else ""
                            iid = rel_path.replace('\\', '/')
                            self.tree_explorer.insert(parent_id, "end", iid=iid, text="\U0001F4C4 " + file, values=("file",))
                            has_items = True

        if not has_items:
            self.tree_explorer.insert("", "end", text="Nenhum arquivo modificado encontrado.")

    def _load_diff(self, src_file, dst_file):
        import difflib
        from src.utils.file_utils import read_file_content
        
        self.diff_text_left.configure(state="normal")
        self.diff_text_right.configure(state="normal")
        self.diff_text_left.delete("1.0", "end")
        self.diff_text_right.delete("1.0", "end")
        
        src_content, _ = read_file_content(src_file)
        dst_content, _ = read_file_content(dst_file)
        
        src_lines = src_content.splitlines()
        dst_lines = dst_content.splitlines()
        
        differ = difflib.ndiff(src_lines, dst_lines)
        
        for line in differ:
            code = line[:2]
            text = line[2:] + "\n"
            
            if code == "- ":
                self.diff_text_left.insert("end", text, "removed")
                self.diff_text_right.insert("end", "\n", "empty")
            elif code == "+ ":
                self.diff_text_left.insert("end", "\n", "empty")
                self.diff_text_right.insert("end", text, "added")
            elif code == "? ":
                continue
            else:
                self.diff_text_left.insert("end", text)
                self.diff_text_right.insert("end", text)
                
        self.diff_text_left.configure(state="disabled")
        self.diff_text_right.configure(state="disabled")

    def _toggle_destination_card(self):
        try:
            val = self.var_mode.get()
            if val == "inplace" or val == self._("mode_inplace"):
                self.card_dest.grid_remove()
            else:
                self.card_dest.grid()
        except AttributeError:
            pass

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
        op_mode = self.var_mode.get()
        # Accommodate combo box localized label values or pure values
        if op_mode == "inplace" or op_mode == self._("mode_inplace"):
            dst = src
            extracted_mode = "inplace"
        else:
            dst = self.dest_dir.get().strip()
            extracted_mode = "extract"

        if not src or (extracted_mode == "extract" and not dst):
            messagebox.showwarning(self._("tag_notice"), self._("msg_select_folders"))
            return

        if extracted_mode == "extract" and src == dst:
            messagebox.showwarning(self._("tag_notice"), self._("msg_same_folders"))
            return

        if not os.path.exists(src):
            messagebox.showerror(self._("tag_error"), self._("msg_bad_source"))
            return

        self.btn_start.configure(state="disabled", text=self._("btn_start_busy"))
        self.log_thread_safe("\n=== BOOTING MIGRATION ENGINE ===")
        
        config = {
            'utf8': self.var_utf8.get(),
            'bpe': False,
            'advanced': self.var_advanced.get(),
            'precompile': self.var_precompile.get(),
            'scopes': self.var_scopes.get(),
            'include_filters': self.app_settings.get("filters", []),
            'banned_files': self.app_settings.get("exceptions", []),
            'clean_dir': self.var_clean_dir.get(),
            'db_main': self.var_db_main.get(),
            'bde': self.var_db_bde.get(),
            'dbx': self.var_db_dbx.get(),
            'ibx': self.var_db_ibx.get(),
            'ado': self.var_db_ado.get(),
            'cds': self.var_db_cds.get()
        }
        
        def update_progress(current, total, filename):
            if total > 0:
                pct = int((current / total) * 100)
                self.progress_bar.set(current / total)
                self.lbl_progress.configure(text=f"{pct}% - {filename}")
        
        self.migrator_thread = threading.Thread(target=self._run_engine, args=(src, dst, config, update_progress), daemon=True)
        self.migrator_thread.start()
        
    def _run_engine(self, src, dst, config, progress_callback):
        engine = DelphiMigratorEngine(src, dst, config, self.log_thread_safe, progress_callback)
        try:
            engine.start_migration()
        except Exception as e:
            self.log_thread_safe(f"Erro ao iniciar motor:\n{e}")
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
            raw_mode = getattr(self, 'var_mode', ctk.StringVar(value='extract')).get()
            if raw_mode == self._("mode_inplace"):
                safe_mode = "inplace"
            elif raw_mode == self._("mode_extract"):
                safe_mode = "extract"
            else:
                safe_mode = raw_mode

            config = {
                'lang': self.i18n.lang,
                'op_mode': safe_mode,
                'source_dir': self.source_dir.get(),
                'dest_dir': self.dest_dir.get(),
                "clean_dir": getattr(self, "var_clean_dir", ctk.BooleanVar(value=False)).get(),
                "utf8": getattr(self, "var_utf8", ctk.BooleanVar(value=True)).get(),
                "db_main": getattr(self, "var_db_main", ctk.BooleanVar(value=True)).get(),
                "bde": getattr(self, "var_bde", ctk.BooleanVar(value=True)).get(),
                "dbx": getattr(self, "var_dbx", ctk.BooleanVar(value=False)).get(),
                "ibx": getattr(self, "var_ibx", ctk.BooleanVar(value=False)).get(),
                "ado": getattr(self, "var_ado", ctk.BooleanVar(value=False)).get(),
                "cds": getattr(self, "var_cds", ctk.BooleanVar(value=False)).get(),
                "scopes": getattr(self, "var_scopes", ctk.BooleanVar(value=True)).get(),
                "advanced": getattr(self, "var_advanced", ctk.BooleanVar(value=True)).get(),
                "precompile": getattr(self, "var_precompile", ctk.BooleanVar(value=False)).get(),
                "include_filters": getattr(self, "include_filters_list", []),
                "ignore_filters": getattr(self, "ignore_filters_list", ["*.~pas", "*.~dfm", "*.dcu", "*.identcache", "*.local", "*.stat", "__history/", "*.ddp"])
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass

    def on_closing(self):
        self.save_settings()
        self.destroy()
