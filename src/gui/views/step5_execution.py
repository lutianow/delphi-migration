import customtkinter as ctk
from src.gui.components import SectionHeader, StyledButton, StyledCheckbox
from src.gui.theme import COLOR_PRIMARY, COLOR_SECONDARY, BG_INPUT, BG_MAIN

class Step5ExecutionView(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self._ = controller._
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header_label = SectionHeader(self, text=self._("step_5", default="5. Execution & Output"), size="large")
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Action Top Section
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.action_frame.grid_columnconfigure(1, weight=1)

        self.controller.var_precompile = ctk.BooleanVar(value=self.controller.app_settings.get("precompile", False))
        
        self.chk_precompile = StyledCheckbox(self.action_frame, text=self._("chk_precompile"), variable=self.controller.var_precompile)
        self.chk_precompile.pack(side="left")

        # Console Section
        self.console_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.console_frame.grid(row=2, column=0, sticky="nsew")
        self.console_frame.grid_rowconfigure(1, weight=1)
        self.console_frame.grid_columnconfigure(0, weight=1)

        self.log_header_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.log_header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.lbl_console = SectionHeader(self.log_header_frame, text=self._("step_5_console", default="Execution Output (Verbose)"), size="small", text_color=COLOR_SECONDARY)
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

        self.controller.log_textbox = ctk.CTkTextbox(self.console_frame, fg_color="#101014", text_color="#A4A4B5", corner_radius=12, font=ctk.CTkFont(family="Consolas", size=13), border_width=2, border_color="#2A2A35")
        self.controller.log_textbox.grid(row=1, column=0, sticky="nsew")
        self.controller.log_textbox.insert("end", self._("log_ready") + "\n")
        self.controller.log_textbox.configure(state="disabled")
        
        # --- PROGRESS BAR ROW ---
        self.progress_frame = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.controller.lbl_progress = ctk.CTkLabel(self.progress_frame, text="0% - Aguardando...", font=ctk.CTkFont(size=11), text_color=COLOR_SECONDARY)
        self.controller.lbl_progress.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        self.controller.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, corner_radius=4, progress_color=COLOR_PRIMARY, fg_color="#2A2A35")
        self.controller.progress_bar.grid(row=1, column=0, sticky="ew")
        self.controller.progress_bar.set(0)

        # Step Navigation Row (Bottom)
        self.step_nav5 = ctk.CTkFrame(self, fg_color="transparent")
        self.step_nav5.grid(row=3, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev5 = StyledButton(self.step_nav5, text=self._("btn_prev", default="Previous Step"), command=lambda: self.controller.show_step(4), style_type="ghost")
        self.btn_prev5.pack(side="left")
        
        self.controller.btn_start = StyledButton(self.step_nav5, text=self._("btn_start_ready"), command=self.controller.start_migration, fg_color=COLOR_PRIMARY, text_color=BG_MAIN, hover_color="#E5E5E5", width=200)
        self.controller.btn_start.pack(side="right")
        
        self.controller.var_precompile.trace_add("write", lambda *_: self.controller.save_settings())

    def _handle_log_action(self, choice):
        self.btn_log_actions.set(self._("log_action_options", default="⏬ Ações"))
        if choice == self._("log_action_copy", default="Copiar Log"):
            self.controller._copy_log()
        elif choice == self._("log_action_save", default="Salvar Log..."):
            self.controller._save_log()
        elif choice == self._("log_action_clear", default="Limpar Log"):
            self.controller._clear_log()

    def update_texts(self):
        self._ = self.controller._
        self.header_label.configure(text=self._("step_5", default="5. Execution & Output"))
        self.chk_precompile.configure(text=self._("chk_precompile"))
        self.lbl_console.configure(text=self._("step_5_console", default="Execution Output (Verbose)"))
        self.btn_log_actions.configure(values=[self._("log_action_copy", default="Copiar Log"), self._("log_action_save", default="Salvar Log..."), self._("log_action_clear", default="Limpar Log")])
        self.btn_log_actions.set(self._("log_action_options", default="⏬ Ações"))
        self.btn_prev5.configure(text=self._("btn_prev", default="Previous Step"))
        if self.controller.btn_start.cget("state") == "normal":
            self.controller.btn_start.configure(text=self._("btn_start_ready"))
