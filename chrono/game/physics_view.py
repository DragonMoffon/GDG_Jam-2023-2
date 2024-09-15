from arcade import View, Sprite, SpriteList

from chrono.game.physics import Body, StaticGravity, Physics


class PhysicsView(View):

    def __init__(self, window: Window | None = None) -> None:
        super().__init__(window)

        self.physics = Physics()
