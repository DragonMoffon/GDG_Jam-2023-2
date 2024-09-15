from arcade import View, Text

# - TEMP -
from chrono.unused.combat import Action, Combat, Combatant


class Game(View):

    def __init__(self) -> None:
        super().__init__()
        self.current_scene = None

        self.text = Text("GAME TIME!", self.window.center_x, self.window.center_y, anchor_x='center', anchor_y='center')

        self.player: Combatant = Combatant()
        self.enemy: Combatant = Combatant()
        self.combat = Combat()

    def reset(self):
        self.current_scene = None

    def on_update(self, delta_time: float) -> bool | None:
        self.combat.update(delta_time)

    def on_draw(self) -> bool | None:
        self.clear()
        self.text.draw()