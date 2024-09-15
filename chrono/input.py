from arcade.future.input import InputManager, ActionState, Keys, MouseAxes, MouseButtons, Action, ActionMapping, Axis, AxisMapping

__all__ = (
    'Input',
    'InputManager',
    'ActionState',
    'Keys',
    'MouseAxes',
    'MouseButtons',
    'Action',
    'ActionMapping',
    'Axis',
    'AxisMapping'
)

class Input:
    manager: InputManager = None

    @staticmethod
    def initialise():
        m: InputManager
        Input.manager = m = InputManager()

        m.new_action('jump')
        m.new_action('rewind')
        m.new_action('reset')
        m.new_action('left')
        m.new_action('right')
        m.new_axis('horizontal')

        m.add_action_input('jump', Keys.SPACE)
        m.add_action_input('rewind', Keys.R)
        m.add_action_input('reset', Keys.BACKSPACE)
        
        m.add_action_input('left', Keys.A)
        m.add_action_input('right', Keys.D)

        m.add_axis_input('horizontal', Keys.A, scale=-1.)
        m.add_axis_input('horizontal', Keys.D, scale=1.0)

    @staticmethod
    def __get_item__(item):
        return Input.manager.actions
        