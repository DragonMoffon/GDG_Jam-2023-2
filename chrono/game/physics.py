from __future__ import annotations
from uuid import uuid4, UUID
from dataclasses import dataclass

from arcade import Vec2, XYWH
from arcade.clock import Clock, GLOBAL_FIXED_CLOCK
from arcade.types import Point2, Rect


@dataclass(slots=True, eq=True)
class StepState:
    # The state a body was in last fixed update for smooth interpolation
    position: Vec2
    velocity: Vec2


class Body:
    # Rotationless Physics Body
    __slots__ = (
        "position",
        "velocity",
        "acceleration",
        "size",
        "mass",
        "static",
        "UUID",
    )

    def __init__(
        self,
        position: Vec2,
        velocity: Vec2,
        size: Point2,
        mass: float = 1.0,
        static: bool = False,
    ) -> None:
        self.position = position
        self.velocity = velocity
        self.acceleration: Vec2 = Vec2()
        self.size = size
        self.mass = mass
        self.static = static
        # Probably not needed as we could just use ID, but I wanna do this anyway nya~
        self.UUID: UUID = uuid4()

    @property
    def bounds(self) -> Rect:
        x, y = self.position
        w, h = self.size
        return XYWH(x, y, w, h)

    def __eq__(self, value) -> bool:
        if type(value) is not Body:  # Not inheretence safe but eh
            raise NotImplementedError
        return self.UUID == value.UUID

    def __hash__(self) -> int:
        return hash(self.UUID)

    def apply_force(self, force: Vec2):
        if self.static:
            return
        acceleration = force / self.mass
        self.apply_acceleration(acceleration)

    def apply_acceleration(self, acceleration: Vec2):
        if self.static:
            return
        self.acceleration += acceleration

    def apply_impulse(self, velocity: Vec2):
        if self.static:
            return
        self.velocity += velocity


class BodyGroup:
    # We store groups of bodies that are currently all connecting (ending with static bodies)

    def __init__(self) -> None:
        self.bodies: list[Body]

    def __eq__(self, other: object) -> bool:
        if type[other] is BodyGroup:
            return self.bodies == other.bodies  # type: ignore - it is a BodyGroup
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(tuple(self.bodies))


class Constraint[T: tuple[Body, ...] | Body]:
    # A contraint on one or more bodies.
    # Contraints include collisions, but also motors etc

    def __init__(self, bodies: T) -> None:
        self.bodies: T = bodies
        self.impulse: float = 0.0

    def __eq__(self, value: object, /) -> bool:
        pass

    def __hash__(self) -> int:
        # If another constraint of the same type forms with the same bodies we want to use the already exsisiting constraint for warm starts
        return hash((type(self), self.bodies))

    def compute_impulse(self) -> float:
        raise NotImplementedError()

    def apply_impulse(self, impulse: float):
        raise NotImplementedError()

    def iterate(self):
        old_impulse = self.impulse
        delta = self.compute_impulse()
        self.impulse = max(0, self.impulse + delta)
        delta = self.impulse - old_impulse
        self.apply_impulse(delta)


class StaticBounds(Constraint):

    def __init__(self, bodies: tuple[Body, ...], bounds: Rect) -> None:
        super().__init__(bodies)
        self.bounds = bounds

    def compute_impulse(self) -> float:
        return super().compute_impulse()

    def apply_impulse(self, impulse: float):
        return super().apply_impulse(impulse)


class Force:
    # A force occurs as part of the normal Euler integration
    # It works on a list of Bodies which can change frame to frame
    # This is things such as boyancy, gravity etc.

    def __init__(self, bodies: list[Body]) -> None:
        self.bodies: list[Body] = bodies

    def add_body(self, body: Body):
        if body in self.bodies:
            return
        self.bodies.append(body)

    def remove_body(self, body: Body):
        if body not in self.bodies:
            return
        self.bodies.remove(body)

    def process(self):
        # A force can remove a body for any reason so we need to iteracte over
        for body in self.bodies[:]:
            self._iteration(body)

    def _iteration(self, body: Body):
        raise NotImplementedError


class StaticGravity(Force):
    # Because gravity is determined by mass its body independant and should
    # use acceleration not force

    def __init__(self, bodies: list[Body], direction: Vec2, strength: float) -> None:
        super().__init__(bodies)
        self._direction: Vec2 = direction
        self._strength: float = strength
        self._pull: Vec2 = self._direction * self._strength

    def _iteration(self, body: Body):
        body.apply_acceleration(self._pull)


# We actually break the No.1 rule of physics engines, keep the dt stable
# but we only reverse it so it should be fine???
ITERATION_NUMBER = 5


class Physics:

    def __init__(self) -> None:
        self._bodies: list[Body] = []
        self._sleeping_bodies: set[Body] = set()
        self._last_states: dict[Body, StepState] = {}
        self._current_states: dict[Body, StepState] = {}

        self._contraints: list[Constraint] = []
        self._forces: list[Force] = []

        self._core_clock: Clock

    def add_body(self, body: Body):
        if body in self._bodies:
            return
        self._bodies.append(body)

    def remove_body(self, body: Body):
        if body not in self._bodies:
            return
        self._bodies.remove(body)

    def extend_bodies(self, bodies: list[Body]):
        self._bodies.extend(body for body in bodies if body not in self._bodies)

    def _iterate(self):
        """Run a single iteration of the impulse computation"""
        pass

    def fixed_update(self):
        self._core_clock.tick(GLOBAL_FIXED_CLOCK.dt)

        # Store previous
        for body in self._bodies:
            self._last_states[body] = StepState(body.position, body.velocity)
            body.acceleration = Vec2()  # We find the acceleration every frame

        # Do standard euler integration to get tentative velocities
        # Gravity, Player Input, Force Fields etc

        for force in self._forces:
            force.process()

        for body in self._bodies:
            body.velocity += body.acceleration * self._core_clock.dt

        # Run impulse iterations
        for _ in range(ITERATION_NUMBER):
            self._iterate()

        # Apply final velocities
        for body in self._bodies:
            body.position += body.velocity * self._core_clock.dt

    def update(self):
        # interpolate between old position and new position for every body
        f = GLOBAL_FIXED_CLOCK.fraction
        for body in self._bodies:
            last = self._last_states[body]
            lp, lv = last.position, last.velocity

            p = lp + f * (body.position - lp)
            v = lv + f * (body.velocity - lv)

            self._current_states[body] = StepState(
                p, v
            )  # Also need to update sprites, don't want to do double loops
