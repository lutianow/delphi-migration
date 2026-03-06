import customtkinter as ctk
from src.gui.theme import COLOR_SECONDARY, BG_INPUT, COLOR_ACCENT, get_font

class StyledCheckbox(ctk.CTkCheckBox):
    def __init__(self, master, text="", variable=None, command=None, size="normal", **kwargs):
        font_size = 14 if size == "normal" else 13
        chk_size = 24 if size == "normal" else 18
        
        font = kwargs.pop('font', get_font(font_size))
        text_color = kwargs.pop('text_color', COLOR_SECONDARY)
        fg_color = kwargs.pop('fg_color', COLOR_ACCENT)
        hover_color = kwargs.pop('hover_color', "#4B4BE5")
        border_color = kwargs.pop('border_color', "#2A2A35")
        border_width = kwargs.pop('border_width', 2)

        super().__init__(
            master=master,
            text=text,
            variable=variable,
            command=command,
            font=font,
            text_color=text_color,
            fg_color=fg_color,
            hover_color=hover_color,
            border_color=border_color,
            border_width=border_width,
            checkbox_width=chk_size,
            checkbox_height=chk_size,
            **kwargs
        )
