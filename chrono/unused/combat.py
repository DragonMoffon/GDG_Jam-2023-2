"""
The Scene 
"""
from arcade.clock import Clock


class Combatant:

    def __init__(self) -> None:
        self.next_free_time: float = 0.0


class Action:

    def __init__(self, combatant: Combatant, duration: int, start_time: int) -> None:
        self.combatant: Combatant = None
        self.duration: int = 0
        self.start_time: int = 0
    
    @property
    def finish_time(self) -> int:
        return self.start_time + self.duration


class Combat:

    def __init__(self) -> None:
        self._action_queue: list[Action] = []
        self._next_action_time: float = 0.0
        self._clock: Clock = Clock(0.0, 0)

    def update(self, delta_time: float):
        self._clock.tick(delta_time)
        self._next_action()
        if self._clock.time_since(self._next_action_time) >= 0.0:
            self._clock.set_tick_speed(0.0)

    def _next_action(self):
        if not self._action_queue or self._clock.time_since(self._action_queue[0].finish_time) < 0.0 or self._clock.speed == 0.0:
            return
        next_action = self._action_queue.pop(0)
        print(next_action)

    def add_action(self, action: Action):
        if action.combatant.next_free_time > action.start_time:
            raise ValueError("Combatant is unable to act at this time")

        if action in self._action_queue:
            raise ValueError("Action already being undertaken")
        
        action.combatant.next_free_time = action.finish_time
        self._insert_action(action)

    def _insert_action(self, action: Action):
        f_time = action.finish_time
        for idx, action in enumerate(self._action_queue):
            if action.finish_time > f_time:
                self._action_queue.insert(idx, action)
                break

            
