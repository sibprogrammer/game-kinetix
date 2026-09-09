from .bat_type import BatType
from .collision_type import CollisionType
from .powerup import Powerup
from .state import State

__all__ = ["BatType", "CollisionType", "Powerup", "State"]

POWERUP_BAT_TYPES = {
    Powerup.EXTEND_BAT: BatType.EXTENDED,
    Powerup.GUN: BatType.GUN,
    Powerup.SMALL_BAT: BatType.SMALL,
    Powerup.MAGNET: BatType.MAGNET,
}

POWERUP_SOUNDS = {
    Powerup.EXTEND_BAT: "bat_extend",
    Powerup.GUN: "bat_gun",
    Powerup.MAGNET: "magnet",
    Powerup.SMALL_BAT: "bat_small",
    Powerup.EXTRA_LIFE: "extra_life",
    Powerup.FAST_BALLS: "speed_up",
    Powerup.SLOW_BALLS: "powerup",
    Powerup.MULTI_BALL: "multiball",
}
