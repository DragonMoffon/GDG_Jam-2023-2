from arcade import View, Text


class Game(View):

    def __init__(self) -> None:
        super().__init__()
        self.current_scene = None

        self.text = Text("GAME TIME!", self.window.center_x, self.window.center_y, anchor_x='center', anchor_y='center')

    def reset(self):
        self.current_scene = None

    def on_draw(self) -> bool | None:
        self.clear()
        self.text.draw()