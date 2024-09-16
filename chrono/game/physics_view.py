from math import sqrt
from arcade import View, Sprite, SpriteList, Vec2, XYWH, draw_line, draw_sprite

from chrono.game.physics import (
    Physics,
    Body,
    StaticGravity,
    StaticDrag,
    Spring,
    StaticBounds,
)
from resources import load_texture
from chrono.game.lerp import perc, lerp

SPRING_TENSION = 100.0


class PhysicsView(View):

    def __init__(self, window=None) -> None:
        super().__init__(window)

        self.physics = Physics()
        self.sprites: SpriteList = SpriteList()

        self.box_sprite: Sprite = Sprite(load_texture("square"))
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

        self._bg = Sprite(load_texture("bg"))
        self._bg.position = Vec2(*self.window.center)
        self.mouse_pos: Vec2 | None = None

    def reset(self):
        self.box_body.position = Vec2(*self.window.center)
        self.box_body.velocity = Vec2()

        self.spring = None

    def on_fixed_update(self, delta_time: float):
        self.physics.fixed_update()

    def on_draw(self) -> bool | None:
        self.clear()
        draw_sprite(self._bg)
        self.physics.update()
        self.box_sprite.position = self.physics[self.box_body].position
        if self.mouse_pos:
            dist = sqrt((self.mouse_pos.x - self.box_sprite.position.x) ** 2 + (self.mouse_pos.y - self.box_sprite.position.y) ** 2)
            p = perc(0, 1000, dist)
            r = lerp(0, 255, p)
            g = lerp(255, 0, p)
            draw_line(self.box_sprite.position.x, self.box_sprite.position.y, self.mouse_pos.x, self.mouse_pos.y, (r, g, 0), 3)
        self.sprites.draw()

    def on_mouse_press(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        p = Vec2(x, y)
        s = self.physics[self.box_body]
        b = XYWH(*s.position, *self.box_body.size)
        if b.point_in_bounds(p):
            self.mouse_pos = p
            d = (s.position - p).length()
            self.spring = Spring([self.box_body], p, SPRING_TENSION, d)
            self.physics.add_force(self.spring)

    def on_mouse_release(
        self, x: int, y: int, button: int, modifiers: int
    ) -> bool | None:
        self.mouse_pos = None
        if self.spring is not None:
            self.physics.remove_force(self.spring)
            self.spring = None

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> bool | None:
        if self.spring is not None:
            self.spring.source = Vec2(x, y)
