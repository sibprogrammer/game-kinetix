from enum import Enum


class CollisionType(Enum):
    WALL = 0
    BAT = 1
    BAT_EDGE = 2
    BRICK = 3
    INDESTRUCTIBLE_BRICK = 4
