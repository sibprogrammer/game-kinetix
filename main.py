import pgzrun

from kinetix.application import draw, initialize, on_key_down, update

__all__ = ["draw", "on_key_down", "update"]


initialize()
pgzrun.go()
