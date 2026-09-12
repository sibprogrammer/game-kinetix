from pgzero.keyboard import keyboard

from .constants import BAT_SPEED
from .controls_base import Controls


class KeyboardControls(Controls):
    def __init__(self, left_key="left", right_key="right", fire_key="space"):
        super().__init__()
        self.left_key = left_key
        self.right_key = right_key
        self.fire_key = fire_key

    def get_x(self):
        if getattr(keyboard, self.left_key):
            return -BAT_SPEED
        if getattr(keyboard, self.right_key):
            return BAT_SPEED
        return 0

    def fire_down(self):
        return getattr(keyboard, self.fire_key)
