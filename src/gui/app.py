import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import queue
from PIL import Image
from src.core.migrator_engine import DelphiMigratorEngine
from src.core.analyzer import ProjectAnalyzer
from src.core.i18n import I18N
from src.gui.views import Step1PathsView, Step2FiltersView, Step3RulesView, Step4AnalyzerView, Step5ExecutionView, Step6DiffView

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

        self.frame_step1 = Step1PathsView(self.container_frame, self)
        self.frame_step2 = Step2FiltersView(self.container_frame, self)
        self.frame_step3 = Step3RulesView(self.container_frame, self)
        self.frame_step4 = Step4AnalyzerView(self.container_frame, self)
        self.frame_step5 = Step5ExecutionView(self.container_frame, self)
        self.frame_step6 = Step6DiffView(self.container_frame, self)
        
        self._create_settings_frame()
        
        self.migrator_thread = None
        self.analyzer_thread = None
        
        # Thread-safe UI Queue
        self.ui_queue = queue.Queue()
        self._process_ui_queue()
        
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
        
        # Update Views
        if hasattr(self, 'frame_step1'): self.frame_step1.update_texts()
        if hasattr(self, 'frame_step2'): self.frame_step2.update_texts()
        if hasattr(self, 'frame_step3'): self.frame_step3.update_texts()
        if hasattr(self, 'frame_step4'): self.frame_step4.update_texts()
        if hasattr(self, 'frame_step5'): self.frame_step5.update_texts()
        if hasattr(self, 'frame_step6'): self.frame_step6.update_texts()
            
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
            if hasattr(self.frame_step6, '_refresh_diff_tree'):
                self.frame_step6._refresh_diff_tree()

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

    def _create_settings_frame(self):
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

    def _process_ui_queue(self):
        try:
            processed_count = 0
            while processed_count < 50:
                task = self.ui_queue.get_nowait()
                task()
                processed_count += 1
        except queue.Empty:
            pass
        finally:
            self.after(20, self._process_ui_queue)

    def log_thread_safe(self, message):
        self.ui_queue.put(lambda m=message: self._insert_log(m))

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
        
        try:
            config = {
                'utf8': getattr(self, "var_utf8", ctk.BooleanVar(value=True)).get(),
                'bpe': False,
                'advanced': getattr(self, "var_advanced", ctk.BooleanVar(value=True)).get(),
                'precompile': getattr(self, "var_precompile", ctk.BooleanVar(value=False)).get(),
                'scopes': getattr(self, "var_scopes", ctk.BooleanVar(value=True)).get(),
                'include_filters': self.app_settings.get("filters", []),
                'banned_files': self.app_settings.get("exceptions", []),
                'clean_dir': getattr(self, "var_clean_dir", ctk.BooleanVar(value=False)).get(),
                'db_main': getattr(self, "var_db_main", ctk.BooleanVar(value=True)).get(),
                'bde': getattr(self, "var_bde", ctk.BooleanVar(value=True)).get(),
                'dbx': getattr(self, "var_dbx", ctk.BooleanVar(value=False)).get(),
                'ibx': getattr(self, "var_ibx", ctk.BooleanVar(value=False)).get(),
                'ado': getattr(self, "var_ado", ctk.BooleanVar(value=False)).get(),
                'cds': getattr(self, "var_cds", ctk.BooleanVar(value=False)).get()
            }
        except Exception as e:
            self.log_thread_safe(f"Erro Crítico de Tela ao ler configurações:\n{e}")
            self._enable_btn()
            return
        
        def update_progress(current, total, filename):
            if total > 0:
                pct = int((current / total) * 100)
                # Thread-safe UI update
                self.ui_queue.put(lambda c=current, t=total, p=pct, f=filename: [
                    self.progress_bar.set(c / t),
                    self.lbl_progress.configure(text=f"{p}% - {(f[:40] + '...') if len(f) > 40 else f}")
                ])
        
        self.migrator_thread = threading.Thread(target=self._run_engine, args=(src, dst, config, update_progress), daemon=True)
        self.migrator_thread.start()
        
    def _run_engine(self, src, dst, config, progress_callback):
        engine = DelphiMigratorEngine(src, dst, config, self.log_thread_safe, progress_callback)
        try:
            engine.start_migration()
        except Exception as e:
            self.log_thread_safe(f"Erro ao iniciar motor:\n{e}")
        finally:
            self.ui_queue.put(self._enable_btn)

    def _enable_btn(self):
        self.btn_start.configure(state="normal", text=self._("btn_start"))

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
