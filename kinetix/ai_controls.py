from random import randint

from . import runtime
from .constants import BAT_SPEED
from .controls_base import Controls


class AIControls(Controls):
    def __init__(self):
        super().__init__()
        self.offset = 0

    def get_x(self):
        if runtime.game.portal_active:
            return BAT_SPEED
        self.offset = min(max(-40, self.offset + randint(-1, 1)), 40)
        return min(
            BAT_SPEED,
            max(
                -BAT_SPEED,
                runtime.game.balls[0].x - (runtime.game.bat.x + self.offset),
            ),
        )

    def fire_down(self):
        return randint(0, 5) == 0
