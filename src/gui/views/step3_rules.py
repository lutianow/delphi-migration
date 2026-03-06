import customtkinter as ctk
from src.gui.components import SectionHeader, StyledButton, StyledCheckbox
from src.gui.theme import COLOR_PRIMARY, COLOR_SECONDARY, BG_INPUT, CARD_1

class Step3RulesView(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.controller = controller
        self._ = controller._
        
        self.grid_columnconfigure(0, weight=1)

        self.header_label = SectionHeader(self, text=self._("step_3", default="3. Migration Rules"), size="large")
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 40))

        self.lbl_options = SectionHeader(self, text=self._("lbl_options"), size="medium")
        self.lbl_options.grid(row=1, column=0, sticky="w", pady=(0, 20))

        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, sticky="nsew")

        self.controller.var_utf8 = ctk.BooleanVar(value=self.controller.app_settings.get("utf8", True))
        self.controller.var_db_main = ctk.BooleanVar(value=self.controller.app_settings.get("db_main", True))
        self.controller.var_bde = ctk.BooleanVar(value=self.controller.app_settings.get("bde", True))
        self.controller.var_dbx = ctk.BooleanVar(value=self.controller.app_settings.get("dbx", False))
        self.controller.var_ibx = ctk.BooleanVar(value=self.controller.app_settings.get("ibx", False))
        self.controller.var_ado = ctk.BooleanVar(value=self.controller.app_settings.get("ado", False))
        self.controller.var_cds = ctk.BooleanVar(value=self.controller.app_settings.get("cds", False))
        self.controller.var_scopes = ctk.BooleanVar(value=self.controller.app_settings.get("scopes", True))
        self.controller.var_advanced = ctk.BooleanVar(value=self.controller.app_settings.get("advanced", True))
        self.controller.var_clean_dir = ctk.BooleanVar(value=self.controller.app_settings.get("clean_dir", False))

        self.chk_clean_dir = StyledCheckbox(self.options_frame, text=self._("chk_clean_dir", default="Clear destination directory before starting"), variable=self.controller.var_clean_dir)
        self.chk_clean_dir.pack(anchor="w", pady=(0, 15))
        
        self.chk_utf8 = StyledCheckbox(self.options_frame, text=self._("chk_utf8"), variable=self.controller.var_utf8)
        self.chk_utf8.pack(anchor="w", pady=(0, 15))
        
        self.chk_scopes = StyledCheckbox(self.options_frame, text=self._("chk_scopes"), variable=self.controller.var_scopes)
        self.chk_scopes.pack(anchor="w", pady=(0, 15))
        
        self.chk_advanced = StyledCheckbox(self.options_frame, text=self._("chk_advanced"), variable=self.controller.var_advanced)
        self.chk_advanced.pack(anchor="w", pady=(0, 15))
        
        self.chk_db_main = StyledCheckbox(self.options_frame, text=self._("chk_db_main", default="Migrate legacy data access to FireDAC"), variable=self.controller.var_db_main, command=self._toggle_db_sub_options)
        self.chk_db_main.pack(anchor="w", pady=(15, 5))
        
        self.db_sub_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.db_sub_frame.pack(anchor="w", fill="x", padx=(30, 0), pady=(0, 15))
        
        self.chk_db_bde = StyledCheckbox(self.db_sub_frame, text="BDE \u2192 FireDAC", variable=self.controller.var_bde, size="small")
        self.chk_db_bde.pack(anchor="w", pady=(0, 8))
        self.chk_db_dbx = StyledCheckbox(self.db_sub_frame, text="DBExpress \u2192 FireDAC", variable=self.controller.var_dbx, size="small")
        self.chk_db_dbx.pack(anchor="w", pady=(0, 8))
        self.chk_db_ibx = StyledCheckbox(self.db_sub_frame, text="IBX \u2192 FireDAC", variable=self.controller.var_ibx, size="small")
        self.chk_db_ibx.pack(anchor="w", pady=(0, 8))
        self.chk_db_ado = StyledCheckbox(self.db_sub_frame, text="ADO \u2192 FireDAC", variable=self.controller.var_ado, size="small")
        self.chk_db_ado.pack(anchor="w", pady=(0, 8))
        self.chk_db_cds = StyledCheckbox(self.db_sub_frame, text="ClientDataSet \u2192 FireDAC", variable=self.controller.var_cds, size="small")
        self.chk_db_cds.pack(anchor="w", pady=(0, 8))

        self._toggle_db_sub_options()

        self.grid_rowconfigure(3, weight=1)

        self.step_nav3 = ctk.CTkFrame(self, fg_color="transparent")
        self.step_nav3.grid(row=4, column=0, sticky="sew", pady=(20, 0))
        
        self.btn_prev3 = StyledButton(self.step_nav3, text=self._("btn_prev", default="Previous Step"), command=lambda: self.controller.show_step(2), style_type="ghost")
        self.btn_prev3.pack(side="left")
        
        self.btn_next3 = StyledButton(self.step_nav3, text=self._("btn_next", default="Next Step"), command=lambda: self.controller.show_step(4))
        self.btn_next3.pack(side="right")

    def _toggle_db_sub_options(self):
        state = "normal" if self.controller.var_db_main.get() else "disabled"
        self.chk_db_bde.configure(state=state)
        self.chk_db_dbx.configure(state=state)
        self.chk_db_ibx.configure(state=state)
        self.chk_db_ado.configure(state=state)
        self.chk_db_cds.configure(state=state)

    def update_texts(self):
        self._ = self.controller._
        self.header_label.configure(text=self._("step_3", default="3. Migration Rules"))
        self.lbl_options.configure(text=self._("lbl_options"))
        self.chk_clean_dir.configure(text=self._("chk_clean_dir", default="Clear destination directory before starting"))
        self.chk_utf8.configure(text=self._("chk_utf8"))
        self.chk_scopes.configure(text=self._("chk_scopes"))
        self.chk_advanced.configure(text=self._("chk_advanced"))
        self.chk_db_main.configure(text=self._("chk_db_main", default="Migrate legacy data access to FireDAC"))
        self.btn_prev3.configure(text=self._("btn_prev", default="Previous Step"))
        self.btn_next3.configure(text=self._("btn_next", default="Next Step"))
