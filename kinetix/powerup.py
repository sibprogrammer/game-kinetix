from enum import IntEnum


class Powerup(IntEnum):
    EXTEND_BAT, GUN, SMALL_BAT, MAGNET, MULTI_BALL = range(5)
    FAST_BALLS, SLOW_BALLS, PORTAL, EXTRA_LIFE = range(5, 9)
