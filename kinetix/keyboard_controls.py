from pgzero.keyboard import keyboard

from .constants import BAT_SPEED
from .controls_base import Controls


class KeyboardControls(Controls):
    def get_x(self):
        if keyboard.left:
            return -BAT_SPEED
        if keyboard.right:
            return BAT_SPEED
        return 0

    def fire_down(self):
        return keyboard.space
