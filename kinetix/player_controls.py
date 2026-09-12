from .constants import BAT_SPEED
from .controls_base import Controls


class PlayerControls(Controls):
    def __init__(self, keyboard_controls, joystick_controls=None):
        super().__init__()
        self.keyboard_controls = keyboard_controls
        self.joystick_controls = joystick_controls

    def get_x(self):
        x = self.keyboard_controls.get_x()
        if self.joystick_controls is not None:
            x += self.joystick_controls.get_x()
        return max(-BAT_SPEED, min(BAT_SPEED, x))

    def fire_down(self):
        return self.keyboard_controls.fire_down() or (
            self.joystick_controls is not None and self.joystick_controls.fire_down()
        )
