from arcade import View, Sprite, SpriteList, Vec2, XYWH

from chrono.game.physics import (
    Physics,
    Body,
    StaticGravity,
    StaticDrag,
    Spring,
    StaticBounds,
)

SPRING_TENSION = 100.0


class PhysicsView(View):

    def __init__(self, window=None) -> None:
        super().__init__(window)

        self.physics = Physics()
        self.sprites: SpriteList = SpriteList()

        self.box_sprite: Sprite = Sprite()
        self.box_sprite.size = 32, 32
        self.sprites.append(self.box_sprite)

        self.box_body: Body = Body(Vec2(*self.window.center), Vec2(), (32, 32), 1.0)
        self.physics.add_body(self.box_body)

        self.body_map: dict[Body, Sprite] = {self.box_body: self.box_sprite}

        self.gravity: StaticGravity = StaticGravity(
            [self.box_body], Vec2(0.0, -1.0), 2000.0
        )
        self.physics.add_force(self.gravity)
        self.drag: StaticDrag = StaticDrag([self.box_body], 0.005)
        self.physics.add_force(self.drag)
        self.spring: Spring = None

        self.bounds: StaticBounds = StaticBounds(self.box_body, self.window.rect)
        self.physics.add_contraint(self.bounds)

    def reset(self):
        self.box_body.position = Vec2(*self.window.center)
        self.box_body.velocity = Vec2()

        self.spring = None

    def on_fixed_update(self, delta_time: float):
        self.physics.fixed_update()

    def on_draw(self) -> bool | None:
        self.clear()
        self.physics.update()
        self.box_sprite.position = self.physics[self.box_body].position
        self.sprites.draw()

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        p = Vec2(x, y)
        s = self.physics[self.box_body]
        b = XYWH(*s.position, *self.box_body.size)
        if b.point_in_bounds(p):
            d = (s.position - p).length()
            self.spring = Spring([self.box_body], p, SPRING_TENSION, d)
            self.physics.add_force(self.spring)

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        if self.spring is not None:
            self.physics.remove_force(self.spring)
            self.spring = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.spring is not None:
            self.spring.source = Vec2(x, y)