from chrono.window import Window
from arcade import load_font
from resources import get_font_path

def main():
    for font in ["vcr", "gohu", "cmu"]:
        p = get_font_path(font)
        load_font(p)

    Window.launch()