import customtkinter as ctk
import tkinter.ttk as ttk
from src.gui.components import SectionHeader, StyledButton
from src.gui.theme import COLOR_PRIMARY, COLOR_SECONDARY, BG_INPUT

class Step6DiffView(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self._ = controller._
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header_label = SectionHeader(self, text=self._("step_6", default="6. Diff Viewer"), size="large")
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Diff View Actions
        self.diff_action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.diff_action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.diff_action_frame.grid_columnconfigure(1, weight=1)

        self.btn_refresh_diff = StyledButton(self.diff_action_frame, text="Recarregar Diferenças", command=self._refresh_diff_tree, style_type="secondary")
        self.btn_refresh_diff.pack(side="left")
        
        self.lbl_diff_status = ctk.CTkLabel(self.diff_action_frame, text="", text_color=COLOR_SECONDARY)
        self.lbl_diff_status.pack(side="left", padx=15)

        # PanedWindow
        self.paned_diff = ttk.PanedWindow(self, orient="horizontal")
        self.paned_diff.grid(row=2, column=0, sticky="nsew")

        # Configurar Estilo do Treeview para combinar com o Dark Theme
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

        # Left Explorer
        self.tree_explorer = ttk.Treeview(self.paned_diff, show='tree')
        self.paned_diff.add(self.tree_explorer, weight=1)
        self.tree_explorer.bind('<<TreeviewSelect>>', self._on_tree_select)

        # Right Paned Code
        self.paned_code = ttk.PanedWindow(self.paned_diff, orient="horizontal")
        self.paned_diff.add(self.paned_code, weight=5)

        self.diff_text_left = ctk.CTkTextbox(self.paned_code, fg_color="#101014", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=13), border_width=1, border_color="#2A2A35", wrap="none")
        self.paned_code.add(self.diff_text_left, weight=1)

        self.diff_text_right = ctk.CTkTextbox(self.paned_code, fg_color="#101014", corner_radius=0, font=ctk.CTkFont(family="Consolas", size=13), border_width=1, border_color="#2A2A35", wrap="none")
        self.paned_code.add(self.diff_text_right, weight=1)

        # Configure tags
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
                self.diff_text_left.yview_scroll(int(-1*(event.delta/120)), "units")
                self.diff_text_right.yview_scroll(int(-1*(event.delta/120)), "units")
                return "break"

            self.diff_text_left._textbox.bind("<MouseWheel>", _on_mousewheel)
            self.diff_text_right._textbox.bind("<MouseWheel>", _on_mousewheel)
            
            if hasattr(self.diff_text_left, '_scrollbar'):
                self.diff_text_left._scrollbar.configure(command=_sync_scroll)
            if hasattr(self.diff_text_right, '_scrollbar'):
                self.diff_text_right._scrollbar.configure(command=_sync_scroll)
        except Exception:
            pass

        self.step_nav = ctk.CTkFrame(self, fg_color="transparent")
        self.step_nav.grid(row=3, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev = StyledButton(self.step_nav, text=self._("btn_prev", default="Previous Step"), command=lambda: self.controller.show_step(5), style_type="ghost")
        self.btn_prev.pack(side="left")

    def update_texts(self):
        self._ = self.controller._
        self.header_label.configure(text=self._("step_6", default="6. Diff Viewer"))
        self.btn_prev.configure(text=self._("btn_prev", default="Previous Step"))

    def _on_tree_select(self, event):
        selected = self.tree_explorer.selection()
        if not selected:
            return
        item_id = selected[0]
        item_type = self.tree_explorer.item(item_id, "values")
        if item_type and item_type[0] == "file":
            dst_path = self.controller.dest_dir.get().strip()
            src_path = self.controller.source_dir.get().strip()
            import os
            d_file = os.path.join(dst_path, item_id.replace('/', os.sep))
            s_file = os.path.join(src_path, item_id.replace('/', os.sep))
            if os.path.exists(s_file) and os.path.exists(d_file):
                self._load_diff(s_file, d_file)

    def _refresh_diff_tree(self):
        for item in self.tree_explorer.get_children():
            self.tree_explorer.delete(item)
            
        src_path = self.controller.source_dir.get().strip()
        dst_path = self.controller.dest_dir.get().strip()
        op_mode = self.controller.var_mode.get()
        if op_mode == "inplace" or op_mode == self._("mode_inplace"):
            self.tree_explorer.insert("", "end", text="Diff view não suportado no modo In-Place.")
            return
            
        import os
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
