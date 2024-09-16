import arcade

from arcade import (
    View,
    Sprite,
    Window,
    Vec2,
    SpriteList,
    Text,
)
from arcade.clock import GLOBAL_CLOCK, Clock

from chrono.input import Input, ActionState

# -- TEMP --
from math import tau, sin, cos
from resources import get_shader_path, load_texture
from arcade.experimental import Shadertoy

PLAYER_GROUND_SPEED = 2000.0  # How fast the player accelerates left and right
PLAYER_AIR_SPEED = 1200.0  # How fast the player accelerates left and right in the air
PLAYER_JUMP_SPEED = 1000.0  # The velocity impules the player recieves upwards
# The acceleration of the player due to gravity while they are falling
PLAYER_JUMP_FALL = 2000.0
PLAYER_JUMP_RELEASE = 1500.0  # The acceleration of the player due to gravity while they are rising, but not jumping
PLAYER_JUMP_HOLD = 1000.0  # The acceleration of the player due to gravity while they are rising and jumping
PLAYER_DRAG = 0.005  # how much the air drags on the player, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_FRICTION_HOLD = 0.04  # how much the ground resists player movement when they are travelling in that direction, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_FRICTION_RELEASE = 0.9  # how much the ground resists player movement, assumes the player is 100kg so we only deal with acceleration no forces

PLAYER_CAYOTE = 1 / 15.0  # ~4 frames

SQUISH_FACTOR = 1500


class GameView(View):

    def __init__(self, window: Window | None = None) -> None:
        super().__init__(window)

        self.level_sprites: SpriteList[Sprite] = SpriteList()  # For rendering
        self.terrain_sprites: SpriteList[Sprite] = SpriteList(
            lazy=True
        )  # For player-ground colliusions

        self._manipulation_clock: Clock = Clock(GLOBAL_CLOCK.time, GLOBAL_CLOCK.ticks)
        self._player_clock: Clock = Clock(GLOBAL_CLOCK.time, GLOBAL_CLOCK.ticks)

        self._bg = Sprite(load_texture("bg"))
        self._bg.position = Vec2(*self.window.center)

        self._noise = Sprite(load_texture("noise"))
        self._noise.position = Vec2(*self.window.center)

        self._shadertoy = Shadertoy.create_from_file(
            (1280, 720), get_shader_path("vhs")
        )
        self.channel0 = self._shadertoy.ctx.framebuffer(
            color_attachments=[self._shadertoy.ctx.texture((1280, 720), components=4)]
        )
        self.channel1 = self._shadertoy.ctx.framebuffer(
            color_attachments=[self._shadertoy.ctx.texture((1280, 720), components=4)]
        )
        self._shadertoy.channel_0 = self.channel0.color_attachments[0]
        self._shadertoy.channel_1 = self.channel1.color_attachments[0]

        # -- TEMP PLAYER --
        self._left_tex = load_texture("jiggycat")
        self._right_tex = load_texture("jiggycat").flip_horizontally()
        self._player: Sprite = Sprite(self._left_tex)
        self._player.size = 32, 32
        self._player.position = Vec2(*self.window.center)
        self._player_velocity: Vec2 = Vec2()
        self._player_jumping: bool = False
        self._player_reversing_time: bool = False
        self._player_jump_time: float = 0.0
        self._player_on_ground: bool = False
        self._player_last_ground_time: float = 0.0

        # -- TEMP PLATFORM --
        self._platform: Sprite = Sprite(load_texture("rectangle"))
        self._platform.size = 64, 16
        self._platform_start_pos = Vec2(48.0, 0.0)
        self._platform_end_pos = Vec2(48.0, 128.0)
        self._platform.position = self._platform_start_pos

        self._platform_2: Sprite = Sprite(load_texture("square"))
        self._platform_2.size = 64, 64
        self._platform_2_core = Vec2(*self.window.center)
        self._platform_2_radius = self.window.center_y  # half screen height
        self._platform_2.position = (
            self._platform_2_core + Vec2(cos(0.0), sin(0.0)) * self._platform_2_radius
        )

        self._platform_period = 8.0

        self._contact_platform: Sprite = None

        # -- TEMP TERRAIN --
        self._ground: Sprite = Sprite(load_texture("floor"))
        self._ground.size = self.window.width, 16
        self._ground.position = self.window.center_x, 8
        self._ground.velocity = Vec2()

        self._wall_1: Sprite = Sprite(load_texture("wall"))
        self._wall_1.size = 16, self.window.height
        self._wall_1.position = 8, self.window.center_y
        self._wall_1.velocity = Vec2()

        self._wall_2: Sprite = Sprite(load_texture("wall"))
        self._wall_2.size = 16, self.window.height
        self._wall_2.position = self.window.width - 8, self.window.center_y
        self._wall_2.velocity = Vec2()

        # -- TEMP TEXT --
        self._reverse_text = Text(
            "REW <<",
            self.window.center_x,
            self.window.center_y,
            font_size=72,
            anchor_x="center",
            font_name="VCR OSD Mono",
        )

        self.level_sprites.extend(
            (
                self._bg,
                self._wall_1,
                self._wall_2,
                self._platform,
                self._platform_2,
                self._ground,
                self._player,
            )
        )
        self.terrain_sprites.extend(
            (self._platform, self._platform_2, self._ground, self._wall_1, self._wall_2)
        )

    def reset(self):
        pass

    def on_action(self, action: str, action_state: ActionState):
        match action:
            case "jump":
                self._player_jumping = action_state == ActionState.PRESSED
                if not self._player_jumping:
                    return
                self._player_jump_time = self._player_clock.time
                if (
                    not self._player_on_ground
                    and self._player_clock.time_since(self._player_last_ground_time)
                    > PLAYER_CAYOTE
                ):
                    return
            case "left":
                return
            case "right":
                return
            case "rewind":
                self._player_reversing_time = action_state == ActionState.PRESSED
                if self._player_reversing_time:
                    self._manipulation_clock.set_tick_speed(-1.0)
                    self._player_clock.set_tick_speed(0.0)
                else:
                    self._manipulation_clock.set_tick_speed(1.0)
                    self._player_clock.set_tick_speed(1.0)

    def draw(self):
        self.level_sprites.draw(pixelated=True)
        # self.level_sprites.draw_hit_boxes(color=(255, 255, 255, 64))
        if self._player_reversing_time:
            self._reverse_text.color = (
                int(255 * cos(tau * GLOBAL_CLOCK.time) ** 2),
            ) * 4
            self._reverse_text.draw()
            arcade.draw_text(
                f"({self._player_velocity.x:.3f}, {self._player_velocity.y:.3f})",
                self._player.position.x,
                self._player.position.y + 25,
                font_name="CMU Classical Serif",
                italic=True,
                font_size=18,
            )
            arcade.draw_line(
                self._player.position.x,
                self._player.position.y,
                self._player.position.x + self._player_velocity.x / 10,
                self._player.position.y + self._player_velocity.y / 10,
                color=arcade.color.WHITE,
                line_width=3,
            )
            # TODO: Dragon, I'd love this to have an arrowhead, but that's going to need vector math.

    def on_draw(self) -> bool | None:
        if self._player_reversing_time:
            self.channel0.use()
            self.channel0.clear()
            self.draw()

            self.channel1.use()
            self.channel1.clear()
            arcade.draw_sprite(self._noise)

            self.window.use()
            self.clear()
            self._shadertoy.render()
        else:
            self.clear()
            self.draw()

    def on_update(self, delta_time: float) -> bool | None:
        self._manipulation_clock.tick(GLOBAL_CLOCK.delta_time)
        self._player_clock.tick(GLOBAL_CLOCK.delta_time)
        t = (
            self._manipulation_clock.time % self._platform_period
        ) / self._platform_period
        c, s = cos(tau * t), sin(tau * t)

        next_pos = self._platform_start_pos + s * (
            self._platform_end_pos - self._platform_start_pos
        )
        diff = next_pos - self._platform.position
        self._platform.velocity = diff / (
            self._manipulation_clock.dt or 1.0
        )  # The difference is over one frame so the equvalent velocity requires a division by the frame time
        self._platform.position = next_pos

        next_pos = self._platform_2_core + Vec2(c, s) * self._platform_2_radius
        diff = next_pos - self._platform_2.position
        self._platform_2.velocity = diff / (
            self._manipulation_clock.dt or 1.0
        )  # The difference is over one frame so the equvalent velocity requires a division by the frame time
        self._platform_2.position = next_pos

        # Acceleration
        if self._player_velocity.y >= 0:
            fall_acceleration = -Vec2(
                0.0, PLAYER_JUMP_HOLD if self._player_jumping else PLAYER_JUMP_RELEASE
            )
        else:
            fall_acceleration = -Vec2(0.0, PLAYER_JUMP_FALL)
        self._player_velocity += fall_acceleration * self._player_clock.dt

        horizontal = Input.manager.axes_state["horizontal"]
        self._player_velocity += Vec2(
            horizontal
            * (PLAYER_GROUND_SPEED if self._player_on_ground else PLAYER_AIR_SPEED)
            * self._player_clock.dt,
            0.0,
        )

        v_length_sqr = self._player_velocity.length_squared()
        v_dir = self._player_velocity.normalize()

        # Drag

        self._player_velocity += (
            0.5 * v_length_sqr * PLAYER_DRAG * self._player_clock.dt * -v_dir
        )  # Air Resistance
        if self._player_on_ground:
            # Assuming horizontal
            drag_vel = self._contact_platform.velocity.x
            holding = horizontal / (abs(horizontal) or 1) == self._player_velocity.x / (
                abs(self._player_velocity.x) or 1.0
            )
            drag = (
                PLAYER_FRICTION_HOLD
                if horizontal and holding
                else PLAYER_FRICTION_RELEASE
            )

            v = self._player_velocity.x - drag_vel
            v_dir = v / (abs(v) or 1)
            self._player_velocity += (
                drag * PLAYER_JUMP_FALL * self._player_clock.dt * -v_dir
            )

        # Resolving Collisions
        px, py = self._player.position
        pw, ph, *_ = self._player.size
        pl, pr, pb, pt = px - pw / 2.0, px + pw / 2.0, py - ph / 2.0, py + ph / 2.0
        on_ground = False
        contact_platform: Sprite = None
        for terrain in self.terrain_sprites:
            x, y = terrain.position
            w, h, *_ = terrain.size
            l, r, b, t = x - w / 2.0, x + w / 2.0, y - h / 2.0, y + h / 2.0

            if not (pl < r and l < pr and pb < t and b < pt):
                continue

            if (
                contact_platform is None
                or contact_platform.velocity.length_squared()
                < terrain.velocity.length_squared()
            ):
                contact_platform = terrain

            x_diff = 2.0 * (px - x) / w
            y_diff = 2.0 * (py - y) / h

            if y_diff >= abs(x_diff):
                # Collides on top
                on_ground = True
                normal = Vec2(0.0, 1.0)
                collision_depth = 0.5 * (ph + h) - abs(y - py)
            elif -y_diff >= abs(x_diff):
                # Collides on bottom
                normal = Vec2(0.0, -1.0)
                collision_depth = 0.5 * (ph + h) - abs(y - py)
            elif x_diff > abs(y_diff):
                # Collides on the right
                normal = Vec2(1.0, 0.0)
                collision_depth = 0.5 * (pw + w) - abs(x - px)
            elif -x_diff > abs(y_diff):
                # Collids on the left
                normal = Vec2(-1.0, 0.0)
                collision_depth = 0.5 * (pw + w) - abs(x - px)
            else:
                print("??????")
                raise ValueError()

            impulse = -1 * normal.dot(self._player_velocity - terrain.velocity)
            self._player_velocity += max(0.0, impulse) * normal
            self._player.position += collision_depth * normal

        # Player is on the 'ground'
        if on_ground and not self._player_on_ground:
            if self._player_clock.time_since(self._player_jump_time) < PLAYER_CAYOTE:
                self._player_velocity += Vec2(0.0, PLAYER_JUMP_SPEED)

        if not on_ground and self._player_on_ground:
            self._player_last_ground_time = self._player_clock.time
        self._player_on_ground = on_ground
        self._contact_platform = contact_platform
        # Applying Velocity
        self._player.position += self._player_velocity * self._player_clock.dt

        self._player.scale_y = (
            max(1 + -self._player_velocity[1] / SQUISH_FACTOR, 0.5) * 0.25
        )
