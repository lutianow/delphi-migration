import customtkinter as ctk
from src.gui.components import SectionHeader, StyledButton
from src.gui.theme import COLOR_PRIMARY, COLOR_SECONDARY, BG_INPUT, CARD_1

class Step2FiltersView(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self._ = controller._
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.header_label = SectionHeader(self, text=self._("step_2", default="2. Filters & Exceptions"), size="large")
        self.header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 40))

        # --- INCLUDE LIST ---
        if not self.controller.app_settings.get("ignore_filters"):
            self.controller.ignore_filters_list = ["*.~pas", "*.~dfm", "*.dcu", "*.identcache", "*.local", "*.stat", "__history/"]
        else:
            self.controller.ignore_filters_list = list(self.controller.app_settings.get("ignore_filters", []))
            
        self.controller.include_filters_list = list(self.controller.app_settings.get("include_filters", []))

        self.lbl_inc = SectionHeader(self, text=self._("lbl_include_only", default="Include ONLY these files"), size="small", text_color=COLOR_PRIMARY, font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_inc.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.scroll_include = ctk.CTkScrollableFrame(self, width=300, height=120, fg_color=BG_INPUT, border_width=1, border_color="#333344")
        self.scroll_include.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        
        inc_toolbar = ctk.CTkFrame(self, fg_color="transparent")
        inc_toolbar.grid(row=3, column=0, sticky="ew", pady=(5, 20))
        
        self.btn_add_inc = StyledButton(inc_toolbar, text=self._("btn_add", default="Add"), width=80, command=lambda: self._add_filter_gui(self.controller.include_filters_list, self.scroll_include))
        self.btn_add_inc.pack(side="left", padx=(0, 5))

        # --- IGNORE LIST ---
        self.lbl_exc = SectionHeader(self, text=self._("lbl_ignore", default="Ignore these files"), size="small", text_color=COLOR_PRIMARY, font=ctk.CTkFont(weight="bold", size=15))
        self.lbl_exc.grid(row=1, column=1, sticky="w", pady=(0, 5))
        
        self.scroll_ignore = ctk.CTkScrollableFrame(self, width=300, height=120, fg_color=BG_INPUT, border_width=1, border_color="#333344")
        self.scroll_ignore.grid(row=2, column=1, sticky="nsew", padx=(10, 0))
        
        exc_toolbar = ctk.CTkFrame(self, fg_color="transparent")
        exc_toolbar.grid(row=3, column=1, sticky="ew", pady=(5, 20), padx=(10, 0))
        
        self.btn_add_exc = StyledButton(exc_toolbar, text=self._("btn_add", default="Add"), width=80, command=lambda: self._add_filter_gui(self.controller.ignore_filters_list, self.scroll_ignore))
        self.btn_add_exc.pack(side="left", padx=(0, 5))
        
        self._render_filter_list(self.controller.include_filters_list, self.scroll_include)
        self._render_filter_list(self.controller.ignore_filters_list, self.scroll_ignore)

        # Step Navigation Row (Bottom)
        self.step_nav2 = ctk.CTkFrame(self, fg_color="transparent")
        self.step_nav2.grid(row=4, column=0, columnspan=2, sticky="sew", pady=(20, 0))
        
        self.btn_prev2 = StyledButton(self.step_nav2, text=self._("btn_prev", default="Previous Step"), command=lambda: self.controller.show_step(1), style_type="ghost")
        self.btn_prev2.pack(side="left")
        
        self.btn_next2 = StyledButton(self.step_nav2, text=self._("btn_next", default="Next Step"), command=lambda: self.controller.show_step(3))
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
                self.controller.save_settings()

    def _edit_filter_gui(self, data_list, scroll_frame, index):
        if 0 <= index < len(data_list):
            old_val = data_list[index]
            dialog = ctk.CTkInputDialog(text=self._("msg_add_filter", default="Type the wildcard pattern:"), title=self._("title_edit_filter", default="Edit Filter"))
            new_val = dialog.get_input()
            if new_val and new_val.strip():
                data_list[index] = new_val.strip()
                self._render_filter_list(data_list, scroll_frame)
                self.controller.save_settings()

    def _rem_filter_gui(self, data_list, scroll_frame, index):
        if 0 <= index < len(data_list):
            del data_list[index]
            self._render_filter_list(data_list, scroll_frame)
            self.controller.save_settings()

    def update_texts(self):
        self._ = self.controller._
        self.header_label.configure(text=self._("step_2", default="2. Filters & Exceptions"))
        self.lbl_inc.configure(text=self._("lbl_include_only", default="Include ONLY these files"))
        self.lbl_exc.configure(text=self._("lbl_ignore", default="Ignore these files"))
        self.btn_add_inc.configure(text=self._("btn_add", default="Add"))
        self.btn_add_exc.configure(text=self._("btn_add", default="Add"))
        self.btn_prev2.configure(text=self._("btn_prev", default="Previous Step"))
        self.btn_next2.configure(text=self._("btn_next", default="Next Step"))
