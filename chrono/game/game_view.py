from arcade import View, Sprite, Window, Vec2
from arcade.clock import GLOBAL_CLOCK

from chrono.input import Input, ActionState

# -- TEMP --
from arcade.draw import draw_sprite

PLAYER_MOVE_SPEED = 2000.0 # How fast the player accelerates left and right
PLAYER_JUMP_SPEED = 1000.0 # The velocity impules the player recieves upwards
PLAYER_JUMP_FALL = 2000.0 # The acceleration of the player due to gravity while they are falling
PLAYER_JUMP_RELEASE = 1250.0 # The acceleration of the player due to gravity while they are rising, but not jumping
PLAYER_JUMP_HOLD = 1000.0 # The acceleration of the player due to gravity while they are rising and jumping
PLAYER_DRAG = 0.05  # how much the air drags on the player, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_FRICTION_HOLD = 0.001 # how much the ground resists player movement when they are travelling in that direction, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_FRICTION_RELEASE = 0.8  # how much the ground resists player movement, assumes the player is 100kg so we only deal with acceleration no forces
PLAYER_PENETRATION_MULTIPLIER = 10.0 # How much of a velocity impulse the player recieves while intersecting surfaces


class GameView(View):

    def __init__(self, window: Window | None = None) -> None:
        super().__init__(window)

        # -- TEMP --
        self._player: Sprite = Sprite()
        self._player.position = Vec2(*self.window.center)
        self._player_velocity: Vec2 = Vec2()
        self._player_jumping: bool = False
        self._player_on_ground: bool = False

    def reset(self):
        pass

    def on_action(self, action: str, action_state: ActionState): 
        match action:
            case 'jump':
                self._player_jumping = action_state == ActionState.PRESSED
                if not self._player_jumping or not self._player_on_ground:
                    return
                self._player_velocity += Vec2(0.0, PLAYER_JUMP_SPEED)
            case 'left':
                print('hmmm')
            case 'right':
                print('wahahh')
                

    def on_draw(self) -> bool | None:
        self.clear()
        draw_sprite(self._player)


    def on_update(self, delta_time: float) -> bool | None:
        if self._player_velocity.y >= 0:
            fall_acceleration = -Vec2(0.0, PLAYER_JUMP_HOLD if self._player_jumping else PLAYER_JUMP_RELEASE)
        else:
            fall_acceleration = -Vec2(0.0, PLAYER_JUMP_FALL)
        self._player_velocity += fall_acceleration * delta_time

        if self._player.center_y <= self._player.height/2.0:
            collision_depth = Vec2(0.0, 1.0).dot(Vec2(0.0, self._player.height/2.0) - self._player.position)
            print(collision_depth)
            impulse = -1 * Vec2(0.0, 1.0).dot(self._player_velocity)
            penetration_impulse = (1 + collision_depth * PLAYER_PENETRATION_MULTIPLIER)
            self._player_velocity += (max(0.0, impulse) + penetration_impulse) * Vec2(0.0, 1.0)

        horizontal = Input.manager.axes_state['horizontal']
        self._player_velocity += Vec2(horizontal * PLAYER_MOVE_SPEED * delta_time, 0.0)

        v_length_sqr = self._player_velocity.length_squared()
        v_dir = self._player_velocity.normalize()

        self._player_velocity += 0.5 * v_length_sqr * PLAYER_DRAG * delta_time * -v_dir  # Air Resistance
        if self._player_on_ground:
            drag = PLAYER_FRICTION_HOLD if Vec2(horizontal, 0.0).dot(self._player_velocity) > 0 else PLAYER_FRICTION_RELEASE
            self._player_velocity += drag * PLAYER_JUMP_FALL * delta_time * -v_dir

        self._player.position += self._player_velocity * delta_time
        self._player_on_ground = self._player.center_y <= self._player.height/2.0


    