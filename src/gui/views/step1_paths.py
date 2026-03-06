import customtkinter as ctk
from src.gui.components import SectionHeader, PathSelector, StyledButton
from src.gui.theme import CARD_1, CARD_2, COLOR_PRIMARY, BG_INPUT

class Step1PathsView(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self._ = controller._
        
        self.grid_columnconfigure((0, 1), weight=1)

        # Header Title
        self.header_label = SectionHeader(self, text=self._("step_1", default="1. Select Folders"), size="large")
        self.header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 40))

        # Vertical Stacked Cards
        self.card_source = ctk.CTkFrame(self, fg_color=CARD_1, corner_radius=16, height=130)
        self.card_source.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.card_source.grid_propagate(False)

        self.lbl_src_title = SectionHeader(self.card_source, text=self._("card_src_title"), size="medium", text_color="#FFFFFF")
        self.lbl_src_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.lbl_src_sub = SectionHeader(self.card_source, text=self._("card_src_sub"), size="small", text_color="#E0E0FF", font=ctk.CTkFont(size=12))
        self.lbl_src_sub.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        ent_source = ctk.CTkEntry(self.card_source, textvariable=self.controller.source_dir, fg_color="#4343D9", border_width=0, text_color="#FFFFFF", height=36, corner_radius=8)
        ent_source.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(0, 15))
        self.card_source.grid_columnconfigure(0, weight=1)

        from tkinter import filedialog
        def browse_src():
            path = filedialog.askdirectory()
            if path: self.controller.source_dir.set(path)

        self.btn_source = StyledButton(self.card_source, text=self._("btn_browse"), command=browse_src, fg_color="#FFFFFF", text_color=CARD_1, hover_color="#E0E0FF", height=36, width=40)
        self.btn_source.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=(0, 15))

        self.card_dest = ctk.CTkFrame(self, fg_color=CARD_2, corner_radius=16, height=130)
        self.card_dest.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.card_dest.grid_propagate(False)

        self.lbl_dst_title = SectionHeader(self.card_dest, text=self._("card_dst_title"), size="medium", text_color="#FFFFFF")
        self.lbl_dst_title.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.lbl_dst_sub = SectionHeader(self.card_dest, text=self._("card_dst_sub"), size="small", text_color="#FFE0D0", font=ctk.CTkFont(size=12))
        self.lbl_dst_sub.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 10))

        ent_dest = ctk.CTkEntry(self.card_dest, textvariable=self.controller.dest_dir, fg_color="#D97A53", border_width=0, text_color="#FFFFFF", height=36, corner_radius=8)
        ent_dest.grid(row=2, column=0, sticky="ew", padx=(20, 10), pady=(0, 15))
        self.card_dest.grid_columnconfigure(0, weight=1)

        def browse_dst():
            path = filedialog.askdirectory()
            if path: self.controller.dest_dir.set(path)

        self.btn_dest = StyledButton(self.card_dest, text=self._("btn_browse"), command=browse_dst, fg_color="#FFFFFF", text_color=CARD_2, hover_color="#FFE0D0", height=36, width=40)
        self.btn_dest.grid(row=2, column=1, sticky="w", padx=(0, 20), pady=(0, 15))

        # Operation Mode
        default_mode = self.controller.app_settings.get("op_mode", self._("mode_extract"))
        if default_mode == "extract": default_mode = self._("mode_extract")
        if default_mode == "inplace": default_mode = self._("mode_inplace")
        
        self.controller.var_mode = ctk.StringVar(value=default_mode)
        self.controller.var_mode.trace_add("write", lambda *_: self._toggle_destination_card())

        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.grid(row=3, column=0, columnspan=2, sticky="nw", pady=(15, 0))
        
        self.lbl_mode = ctk.CTkLabel(mode_frame, text=self._("mode_lbl"), font=ctk.CTkFont(weight="bold", size=15), text_color=COLOR_PRIMARY)
        self.lbl_mode.pack(side="left", padx=(0, 10))
        
        self.combo_mode = ctk.CTkOptionMenu(mode_frame, variable=self.controller.var_mode, values=[self._("mode_extract"), self._("mode_inplace")], fg_color=BG_INPUT, button_color="#2A2A35", text_color=COLOR_PRIMARY, width=280)
        self.combo_mode.pack(side="left")

        # Spacer
        self.grid_rowconfigure(4, weight=1)

        # Step Navigation
        self.step_nav1 = ctk.CTkFrame(self, fg_color="transparent")
        self.step_nav1.grid(row=5, column=0, columnspan=2, sticky="sew", pady=(20, 0))
        
        self.btn_next1 = StyledButton(self.step_nav1, text=self._("btn_next", default="Next Step"), command=lambda: self.controller.show_step(2))
        self.btn_next1.pack(side="right")
        
        self._toggle_destination_card()

    def _toggle_destination_card(self):
        mode = self.controller.var_mode.get()
        if mode == "inplace" or mode == self._("mode_inplace"):
            self.card_dest.grid_remove()
        else:
            self.card_dest.grid()

    def update_texts(self):
        self._ = self.controller._
        self.header_label.configure(text=self._("step_1", default="1. Select Folders"))
        self.lbl_src_title.configure(text=self._("card_src_title"))
        self.lbl_src_sub.configure(text=self._("card_src_sub"))
        self.btn_source.configure(text=self._("btn_browse"))
        self.lbl_dst_title.configure(text=self._("card_dst_title"))
        self.lbl_dst_sub.configure(text=self._("card_dst_sub"))
        self.btn_dest.configure(text=self._("btn_browse"))
        self.lbl_mode.configure(text=self._("mode_lbl"))
        
        # update combo without triggering trace if possible
        current_mode = self.controller.var_mode.get()
        # simplified combo text refresh
        self.combo_mode.configure(values=[self._("mode_extract"), self._("mode_inplace")])
        
        self.btn_next1.configure(text=self._("btn_next", default="Next Step"))
