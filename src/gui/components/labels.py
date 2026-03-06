import customtkinter as ctk
from src.gui.theme import COLOR_PRIMARY, COLOR_SECONDARY, get_font

class SectionHeader(ctk.CTkLabel):
    def __init__(self, master, text="", size="large", **kwargs):
        text_color = kwargs.pop('text_color', COLOR_PRIMARY)
        
        if size == "large":
            font = get_font(36, "bold")
        elif size == "medium":
            font = get_font(20, "bold")
        elif size == "small":
            font = get_font(16, "bold")
            text_color = kwargs.pop('text_color', COLOR_SECONDARY)
        else:
            font = get_font(14)
            
        font = kwargs.pop('font', font)
        
        super().__init__(
            master=master,
            text=text,
            font=font,
            text_color=text_color,
            **kwargs
        )
