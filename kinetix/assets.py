from functools import lru_cache
from pathlib import Path

import pygame

ROOT = Path(__file__).parent.parent

FONT_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?.,:;+-=*/()<>"
FONT_GLYPH_SIZE = (50, 50)
FONT_GLYPH_WIDTH = 38
FONT_GLYPH_ADVANCE = 34


@lru_cache
def image(name):
    return pygame.image.load(ROOT / "images" / f"{name}.png").convert_alpha()


@lru_cache
def sound(name):
    return pygame.mixer.Sound(ROOT / "sounds" / f"{name}.ogg")


@lru_cache
def font_glyph(character):
    try:
        index = FONT_CHARACTERS.index(character)
    except ValueError as error:
        raise ValueError(f"Unsupported font character: {character!r}") from error

    glyph = image("font").subsurface(
        (index * FONT_GLYPH_SIZE[0], 0, *FONT_GLYPH_SIZE)
    )
    return pygame.transform.smoothscale(glyph, (FONT_GLYPH_WIDTH, FONT_GLYPH_SIZE[1]))


def draw_text(surface, text, position):
    x, y = position
    for character in text:
        if character == " ":
            x += FONT_GLYPH_ADVANCE // 2
        else:
            surface.blit(font_glyph(character), (x, y))
            x += FONT_GLYPH_ADVANCE
