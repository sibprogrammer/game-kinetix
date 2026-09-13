from pygame.math import Vector2

from . import runtime
from .actor import Actor
from .constants import BULLET_SPEED
from .impact import Impact
from .types import CollisionType


class Bullet(Actor):
    def __init__(self, pos, side):
        super().__init__(f"bullet{side}", pos)
        self.alive = True

    def update(self):
        self.y -= BULLET_SPEED
        collision = runtime.game.collide(self.x, self.y, Vector2(0, -1), 2)
        if collision is not None:
            self.alive = False
            runtime.game.impacts.append(Impact(self.pos, 15))
            if collision[2] in (
                CollisionType.BRICK,
                CollisionType.INDESTRUCTIBLE_BRICK,
            ):
                runtime.game.play_sound("bullet_hit", 4)
