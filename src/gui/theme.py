import customtkinter as ctk

# Application Theme Colors
# Modern Dark UI "Pods" Dribbble Inspiration
BG_MAIN = "#0D0D11"
BG_SIDEBAR = "#15151A"
BG_INPUT = "#1F1F26"
COLOR_PRIMARY = "#FFFFFF"
COLOR_SECONDARY = "#8E8E93"
COLOR_ACCENT = "#5D5DFF"  # Purple/Blue
COLOR_WARNING = "#FF9B70" # Peach/Orange
CARD_1 = COLOR_ACCENT
CARD_2 = COLOR_WARNING

# Global Font Specs
FONT_FAMILY = "Inter"

def get_font(size=14, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)
