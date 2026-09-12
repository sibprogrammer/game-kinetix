from pgzero.actor import Actor

from . import runtime
from .bullet import Bullet
from .constants import BAT_MAX_X, BAT_MIN_X, FIRE_INTERVAL, WIDTH
from .types import BatType


class Bat(Actor):
    def __init__(
        self,
        controls,
        x=320,
        y=590,
        min_x=BAT_MIN_X,
        max_x=BAT_MAX_X,
        portal_direction=1,
    ):
        super().__init__("blank", (x, y), anchor=("center", 15))
        self.controls = controls
        self.min_x, self.max_x = min_x, max_x
        self.portal_direction = portal_direction
        self.fire_timer = self.frame = 0
        self.current_type = self.target_type = BatType.NORMAL
        self.shadow = Actor("blank", (self.x + 16, self.y + 16), anchor=("center", 15))

    def update(self):
        if (
            self.target_type != BatType.NORMAL
            and self.target_type == self.current_type
            and self.frame < 12
        ):
            self.frame += 1
        if self.target_type != self.current_type and self.frame > 0:
            self.frame -= 1
        if self.frame == 0:
            self.current_type = self.target_type
        self.image = f"bat{int(self.current_type)}{self.frame // 4}"
        self.fire_timer -= 1
        if (
            self.controls.fire_down()
            and self.current_type == BatType.GUN
            and self.frame == 12
            and self.fire_timer <= 0
        ):
            self.fire_timer = FIRE_INTERVAL
            self.image += "f"
            runtime.game.bullets.extend(
                (Bullet((self.x - 20, self.y), 0), Bullet((self.x + 20, self.y), 1))
            )
            runtime.game.play_sound("laser")
        new_x = self.x + self.controls.get_x()
        if not runtime.game.portal_active:
            new_x = max(self.min_x + self.width // 2, new_x)
            new_x = min(self.max_x - self.width // 2, new_x)
        self.x = new_x
        self.shadow.pos = (self.x + 16, self.y + 16)
        self.shadow.image = f"bats{int(self.current_type)}{self.frame // 4}"

    def change_type(self, bat_type):
        self.target_type = bat_type

    def is_portal_transition_complete(self):
        if self.portal_direction < 0:
            return self.x + self.width // 2 <= 0
        return self.x - self.width // 2 >= WIDTH
