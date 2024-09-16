from arcade import View, Sprite, SpriteList, Vec2

from chrono.game.physics import Body, StaticGravity, Physics, Spring, StaticBounds


class PhysicsView(View):

    def __init__(self, window: Window | None = None) -> None:
        super().__init__(window)

        self.physics = Physics()
        self.sprites: SpriteList = SpriteList()

        self.box_sprite: Sprite = Sprite()
        self.box_sprite.size = 32, 32
        self.sprites.append(self.box_sprite)
        self.box_body: Body = Body(Vec2(*self.window.center), Vec2(), (32, 32), 1.0)

        self.body_map: dict[Body, Sprite] = {self.box_body: self.box_sprite}

        self.gravity: StaticGravity = StaticGravity(
            [self.box_body], Vec2(0.0, -1.0), 2000.0
        )
        self.spring: Spring = None

        self.bounds: StaticBounds = StaticBounds(self.box_body, self.window.rect)

    def on_fixed_update(self, delta_time: float):
        self.physics.fixed_update()

    def on_draw(self) -> bool | None:
        self.clear()
        self.physics.update()
        self.box_sprite.position = self.physics[self.box_body].position
        self.sprites.draw()
