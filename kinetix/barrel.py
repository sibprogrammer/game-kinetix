from random import choice

from . import runtime
from .actor import Actor
from .constants import BALL_RADIUS, HEIGHT, SHADOW_OFFSET
from .impact import Impact
from .types import POWERUP_BAT_TYPES, POWERUP_SOUNDS, Powerup


class Barrel(Actor):
    def __init__(self, pos):
        super().__init__("blank", pos)
        weights = {
            Powerup.EXTEND_BAT: 6,
            Powerup.GUN: 6,
            Powerup.SMALL_BAT: 6,
            Powerup.MAGNET: 6,
            Powerup.MULTI_BALL: 6,
            Powerup.FAST_BALLS: 6,
            Powerup.SLOW_BALLS: 6,
            Powerup.EXTRA_LIFE: 2,
            Powerup.PORTAL: 0
            if runtime.game.bricks_remaining > 20 or runtime.game.portal_active
            else 20,
        }
        types = [powerup for powerup, weight in weights.items() for _ in range(weight)]
        self.type = choice(types)
        self.time = 0
        self.shadow = Actor("barrels", (self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET))

    def update(self):
        self.time += 1
        self.y += 1
        bat = next(
            (
                candidate
                for candidate in runtime.game.bats
                if candidate.y - 10 <= self.y <= candidate.y + 30
                and abs(self.x - candidate.x)
                < (candidate.width // 2) + BALL_RADIUS
            ),
            None,
        )
        if bat is not None:
            runtime.game.impacts.append(Impact((self.x, self.y - 11), 14))
            if self.type in POWERUP_SOUNDS:
                runtime.game.play_sound(POWERUP_SOUNDS[self.type])
            self.y = HEIGHT + 100
            if self.type in POWERUP_BAT_TYPES:
                for player_bat in runtime.game.bats:
                    player_bat.change_type(POWERUP_BAT_TYPES[self.type])
            elif self.type == Powerup.MULTI_BALL:
                runtime.game.balls = [
                    new
                    for ball in runtime.game.balls
                    for new in ball.generate_multiballs()
                ]
            elif self.type == Powerup.FAST_BALLS:
                runtime.game.change_all_ball_speeds(3)
            elif self.type == Powerup.SLOW_BALLS:
                runtime.game.change_all_ball_speeds(-3)
            elif self.type == Powerup.PORTAL:
                runtime.game.activate_portal()
            elif self.type == Powerup.EXTRA_LIFE:
                runtime.game.lives += 1
        self.image = f"barrel{int(self.type)}{self.time // 10 % 10}"
        self.shadow.pos = (self.x + SHADOW_OFFSET, self.y + SHADOW_OFFSET)
