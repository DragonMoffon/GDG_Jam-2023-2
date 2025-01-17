from arcade import View, Text


class MainMenu(View):

    def __init__(self) -> None:
        super().__init__()
        self.text: Text = Text(
            "CLICK TO BEGIN or ANY BUTTON FOR PHYSICS TEST",
            self.window.center_x,
            self.window.center_y,
            anchor_x="center",
            anchor_y="center",
            font_name="VCR OSD Mono",
            font_size=24,
        )

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        self.window.nav("to_game_levelless")

    def on_key_press(self, symbol: int, modifiers: int) -> bool | None:
        self.window.nav("to_physics_demo")

    def on_draw(self) -> bool | None:
        self.clear()
        self.text.draw()
