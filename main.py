import pgzrun

from kinetix.application import draw, initialize, on_key_down, update
from kinetix.constants import HEIGHT, WIDTH, TITLE

__all__ = ["HEIGHT", "WIDTH", "TITLE", "draw", "on_key_down", "update"]


initialize()
pgzrun.go()
