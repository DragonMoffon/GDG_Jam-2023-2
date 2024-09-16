from pyglet.input import get_controllers
from arcade.future.input import (
    InputManager,
    ActionState,
    Keys,
    MouseAxes,
    MouseButtons,
    ControllerAxes,
    ControllerButtons,
    Action,
    ActionMapping,
    Axis,
    AxisMapping,
)

__all__ = (
    "Input",
    "InputManager",
    "ActionState",
    "Keys",
    "MouseAxes",
    "MouseButtons",
    "Action",
    "ActionMapping",
    "Axis",
    "AxisMapping",
)


class Input:
    manager: InputManager = None

    @staticmethod
    def initialise():
        m: InputManager
        c = get_controllers()
        controller = None if not c else c[0]
        Input.manager = m = InputManager(controller=controller)

        m.new_action("jump")
        m.new_action("rewind")
        m.new_action("reset")
        m.new_action("left")
        m.new_action("right")
        m.new_axis("horizontal")

        m.add_action_input("jump", Keys.SPACE)
        m.add_action_input("jump", ControllerButtons.BOTTOM_FACE)
        m.add_action_input("rewind", Keys.R)
        m.add_action_input("rewind", ControllerButtons.LEFT_SHOULDER)
        m.add_action_input("rewind", ControllerButtons.RIGHT_SHOULDER)
        m.add_action_input("reset", Keys.BACKSPACE)

        m.add_action_input("left", Keys.A)
        m.add_action_input("left", ControllerAxes.LEFT_STICK_NEGATIVE_X)
        m.add_action_input("right", Keys.D)
        m.add_action_input("right", ControllerAxes.LEFT_STICK_POSITIVE_X)

        m.add_axis_input("horizontal", Keys.A, scale=-1.0)
        m.add_axis_input("horizontal", ControllerAxes.LEFT_STICK_X, scale=-1.0)
        m.add_axis_input("horizontal", Keys.D, scale=1.0)

    @staticmethod
    def __get_item__(item):
        return Input.manager.actions
