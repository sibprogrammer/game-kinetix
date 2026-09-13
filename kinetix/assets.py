from functools import lru_cache
from pathlib import Path

import pygame

ROOT = Path(__file__).parent.parent


@lru_cache
def image(name):
    return pygame.image.load(ROOT / "images" / f"{name}.png").convert_alpha()


@lru_cache
def sound(name):
    return pygame.mixer.Sound(ROOT / "sounds" / f"{name}.ogg")
