import customtkinter as ctk
from src.gui.components.buttons import StyledButton
from src.gui.theme import BG_INPUT, COLOR_SECONDARY, get_font
from tkinter import filedialog

class PathSelector(ctk.CTkFrame):
    def __init__(self, master, label_text="Select Path:", variable=None, mode="dir", i18n_instance=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        
        self.mode = mode
        self.variable = variable
        self._ = i18n_instance._ if i18n_instance else lambda x, default=x: default

        # Label
        self.lbl = ctk.CTkLabel(
            self, 
            text=label_text, 
            font=get_font(14, "bold"), 
            text_color=COLOR_SECONDARY
        )
        self.lbl.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Input row
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        self.entry = ctk.CTkEntry(
            self.input_frame,
            textvariable=self.variable,
            fg_color=BG_INPUT,
            border_color="#2A2A35",
            border_width=2,
            height=40,
            font=get_font(13),
            text_color="#FFFFFF"
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.btn = StyledButton(
            self.input_frame,
            text=self._("btn_browse", default="..."),
            command=self._browse,
            width=60,
            style_type="secondary"
        )
        self.btn.grid(row=0, column=1)

    def _browse(self):
        if self.mode == "dir":
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()
            
        if path and self.variable:
            self.variable.set(path)
