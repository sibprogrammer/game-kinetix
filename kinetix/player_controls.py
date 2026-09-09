from . import runtime
from .constants import BAT_SPEED
from .controls_base import Controls


class PlayerControls(Controls):
    def __init__(self, keyboard_controls):
        super().__init__()
        self.keyboard_controls = keyboard_controls

    def get_x(self):
        x = self.keyboard_controls.get_x()
        if runtime.joystick_controls is not None:
            x += runtime.joystick_controls.get_x()
        return max(-BAT_SPEED, min(BAT_SPEED, x))

    def fire_down(self):
        return self.keyboard_controls.fire_down() or (
            runtime.joystick_controls is not None
            and runtime.joystick_controls.fire_down()
        )
