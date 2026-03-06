import customtkinter as ctk
from src.gui.theme import BG_INPUT, COLOR_PRIMARY, COLOR_ACCENT, get_font

class StyledButton(ctk.CTkButton):
    def __init__(self, master, text="", command=None, style_type="primary", **kwargs):
        # Base config defaults to strong primary
        fg_color = kwargs.pop('fg_color', COLOR_ACCENT)
        text_color = kwargs.pop('text_color', "#FFFFFF")
        hover_color = kwargs.pop('hover_color', "#4B4BE5")
        border_width = kwargs.pop('border_width', 0)
        border_color = kwargs.pop('border_color', None)
        
        if style_type == "secondary":
            fg_color = kwargs.pop('fg_color', "transparent")
            text_color = kwargs.pop('text_color', COLOR_PRIMARY)
            border_width = kwargs.pop('border_width', 1)
            border_color = kwargs.pop('border_color', COLOR_PRIMARY)
            hover_color = kwargs.pop('hover_color', BG_INPUT)
        elif style_type == "danger":
            fg_color = kwargs.pop('fg_color', "transparent")
            text_color = kwargs.pop('text_color', "#FF4B4B")
            border_width = kwargs.pop('border_width', 1)
            border_color = kwargs.pop('border_color', "#FF4B4B")
            hover_color = kwargs.pop('hover_color', "#3A1010")
        elif style_type == "ghost":
            fg_color = kwargs.pop('fg_color', "transparent")
            text_color = kwargs.pop('text_color', COLOR_PRIMARY)
            hover_color = kwargs.pop('hover_color', BG_INPUT)

        font = kwargs.pop('font', get_font(14, "bold"))
        height = kwargs.pop('height', 40)
        corner_radius = kwargs.pop('corner_radius', 8)

        super().__init__(
            master=master,
            text=text,
            command=command,
            font=font,
            fg_color=fg_color,
            text_color=text_color,
            hover_color=hover_color,
            border_width=border_width,
            border_color=border_color,
            height=height,
            corner_radius=corner_radius,
            **kwargs
        )
